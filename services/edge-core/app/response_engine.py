from datetime import UTC, datetime, timedelta

from app.incidents import Incident, IncidentSeverity, IncidentStatus
from app.models import CorrelatedSignal, HouseholdPresenceState, SensorEvent
from app.modes import OperatingMode
from app.response import (
    OccupantSafetyState,
    ResponseAssessment,
    ResponseState,
    ResponseUrgency,
)
from app.threats import ThreatClassification, ThreatState
from app.zones import Zone

LOW_CONFIDENCE_EVENT_THRESHOLD = 60
LOW_CONFIDENCE_RESPONSE_SCORE = 45
RESPONSE_COOLDOWN_WINDOW = timedelta(minutes=15)
ACTIVE_RESPONSE_WINDOW = timedelta(minutes=30)


def build_response_assessment(
    *,
    event_id: int,
    event: SensorEvent,
    threat: ThreatState,
    incident: Incident | None,
    behaviour_reasoning: list[str],
    correlated_signals: list[CorrelatedSignal],
    known_occupant: bool,
    mode: OperatingMode,
    zone: Zone | None,
    presence_state: HouseholdPresenceState,
    recent_responses: list[dict],
) -> ResponseAssessment:
    response_confidence = threat.threat_score
    urgency = _base_urgency(threat, incident)
    response_state = _base_response_state(urgency)
    occupant_safety_state = _base_occupant_safety_state(urgency)
    reasoning: list[str] = []
    cooldown_applied = False

    if _has_high_confidence_intrusion_pattern(threat, incident, correlated_signals, known_occupant):
        response_confidence += 10
        urgency = _max_urgency(urgency, ResponseUrgency.URGENT)
        response_state = _max_response_state(
            response_state,
            ResponseState.ACTIVE_SECURITY_RESPONSE,
        )
        occupant_safety_state = OccupantSafetyState.POSSIBLE_RISK
        reasoning.append("High confidence intrusion pattern detected.")

    if behaviour_reasoning:
        response_confidence += min(10, 4 * len(behaviour_reasoning))
        reasoning.append("Behavioural anomalies increased operator concern.")

    if correlated_signals:
        response_confidence += min(15, sum(min(signal.modifier, 6) for signal in correlated_signals))
        reasoning.extend(signal.reasoning for signal in correlated_signals)

    if zone and zone.sensitivity == "high" and mode == OperatingMode.NIGHT_LOCK and not known_occupant:
        response_confidence += 6
        urgency = _raise_urgency(urgency)
        response_state = _max_response_state(response_state, ResponseState.SILENT_OPERATOR_REVIEW)
        reasoning.append("High-sensitivity zone activity during Night Lock increased response priority.")

    if known_occupant:
        response_confidence -= 25
        urgency = _lower_urgency(urgency)
        response_state = _response_state_for_continuity(urgency)
        occupant_safety_state = OccupantSafetyState.LIKELY_SAFE
        reasoning.append("Possible occupant movement continuity detected.")

    if presence_state.no_trusted_occupants_detected and not known_occupant:
        response_confidence += 6
        reasoning.append("No trusted occupants have been observed recently.")

    if presence_state.trusted_occupant_recently_active and known_occupant:
        response_confidence -= 4
        reasoning.append("Trusted occupant activity was recently observed in the household.")

    if presence_state.household_activity.settled and mode == OperatingMode.NIGHT_LOCK:
        reasoning.append("Household appears settled during Night Lock.")

    if (
        event.confidence < LOW_CONFIDENCE_EVENT_THRESHOLD
        and threat.threat_score <= 55
        and not correlated_signals
    ):
        response_confidence = min(response_confidence, 35)
        urgency = ResponseUrgency.LOW
        response_state = ResponseState.MONITOR_ONLY
        occupant_safety_state = (
            OccupantSafetyState.LIKELY_SAFE
            if known_occupant
            else OccupantSafetyState.VERIFY_OCCUPANT
        )
        reasoning.append("Low-confidence anomaly cluster; continue monitoring.")

    if (
        event.confidence < LOW_CONFIDENCE_EVENT_THRESHOLD
        and threat.threat_score <= LOW_CONFIDENCE_RESPONSE_SCORE
        and correlated_signals
    ):
        response_confidence = min(response_confidence, 35)
        urgency = ResponseUrgency.LOW
        response_state = ResponseState.MONITOR_ONLY
        occupant_safety_state = (
            OccupantSafetyState.LIKELY_SAFE
            if known_occupant
            else OccupantSafetyState.VERIFY_OCCUPANT
        )
        reasoning.append("Low-confidence anomaly cluster; continue monitoring.")

    if _should_apply_cooldown(
        zone_id=event.zone_id,
        event_timestamp=event.timestamp,
        recent_responses=recent_responses,
        response_state=response_state,
        threat_score=threat.threat_score,
    ):
        cooldown_applied = True
        response_confidence = min(response_confidence, 30)
        urgency = ResponseUrgency.LOW
        response_state = ResponseState.MONITOR_ONLY
        occupant_safety_state = (
            OccupantSafetyState.LIKELY_SAFE
            if known_occupant
            else OccupantSafetyState.VERIFY_OCCUPANT
        )
        reasoning.append(
            "Recent similar low-confidence activity already assessed; continue monitoring."
        )

    response_confidence = max(0, min(response_confidence, 100))
    operator_recommendation = _build_operator_recommendation(
        response_state=response_state,
        known_occupant=known_occupant,
        cooldown_applied=cooldown_applied,
    )
    if response_state == ResponseState.EMERGENCY_RESPONSE:
        occupant_safety_state = OccupantSafetyState.HIGH_RISK
    elif response_state == ResponseState.ACTIVE_SECURITY_RESPONSE:
        occupant_safety_state = _max_occupant_safety(
            occupant_safety_state,
            OccupantSafetyState.POSSIBLE_RISK,
        )

    return ResponseAssessment(
        event_id=event_id,
        incident_id=incident.incident_id if incident else None,
        zone_id=event.zone_id,
        response_confidence=response_confidence,
        urgency=urgency,
        response_state=response_state,
        occupant_safety_state=occupant_safety_state,
        operator_recommendation=operator_recommendation,
        reasoning=_unique_reasoning(reasoning),
        cooldown_applied=cooldown_applied,
        created_at=event.timestamp.astimezone(UTC),
    )


def list_active_response_assessments(history: list[dict], incidents: list[dict]) -> list[dict]:
    open_incident_ids = {
        incident["incident_id"]
        for incident in incidents
        if incident["status"] in {IncidentStatus.OPEN.value, IncidentStatus.MONITORING.value}
    }
    latest_by_key: dict[str, dict] = {}

    for assessment in history:
        key = assessment["incident_id"] or assessment["zone_id"]
        latest_by_key[key] = assessment

    window_start = datetime.now(UTC) - ACTIVE_RESPONSE_WINDOW
    active: list[dict] = []
    for assessment in latest_by_key.values():
        created_at = _coerce_datetime(assessment["created_at"])
        if assessment["incident_id"] in open_incident_ids:
            active.append(assessment)
            continue
        if created_at >= window_start and assessment["response_state"] != ResponseState.MONITOR_ONLY.value:
            active.append(assessment)

    active.sort(key=lambda item: (_coerce_datetime(item["created_at"]), item["id"]), reverse=True)
    return active


def _base_urgency(threat: ThreatState, incident: Incident | None) -> ResponseUrgency:
    if incident and incident.severity == IncidentSeverity.CRITICAL:
        return ResponseUrgency.CRITICAL
    if threat.classification in {ThreatClassification.CRITICAL, ThreatClassification.HIGH_THREAT}:
        return ResponseUrgency.URGENT
    if threat.classification == ThreatClassification.SUSPICIOUS:
        return ResponseUrgency.ELEVATED
    return ResponseUrgency.LOW


def _base_response_state(urgency: ResponseUrgency) -> ResponseState:
    if urgency == ResponseUrgency.CRITICAL:
        return ResponseState.EMERGENCY_RESPONSE
    if urgency == ResponseUrgency.URGENT:
        return ResponseState.ACTIVE_SECURITY_RESPONSE
    if urgency == ResponseUrgency.ELEVATED:
        return ResponseState.SILENT_OPERATOR_REVIEW
    return ResponseState.MONITOR_ONLY


def _base_occupant_safety_state(urgency: ResponseUrgency) -> OccupantSafetyState:
    if urgency == ResponseUrgency.CRITICAL:
        return OccupantSafetyState.HIGH_RISK
    if urgency == ResponseUrgency.URGENT:
        return OccupantSafetyState.POSSIBLE_RISK
    return OccupantSafetyState.VERIFY_OCCUPANT


def _has_high_confidence_intrusion_pattern(
    threat: ThreatState,
    incident: Incident | None,
    correlated_signals: list[CorrelatedSignal],
    known_occupant: bool,
) -> bool:
    if known_occupant:
        return False
    if threat.threat_score >= 88:
        return True
    if incident and incident.severity == IncidentSeverity.CRITICAL:
        return True

    critical_patterns = {
        "perimeter_to_garage_progression",
        "indoor_after_perimeter_progression",
    }
    return any(signal.pattern_type in critical_patterns for signal in correlated_signals)


def _should_apply_cooldown(
    *,
    zone_id: str,
    event_timestamp: datetime,
    recent_responses: list[dict],
    response_state: ResponseState,
    threat_score: int,
) -> bool:
    if threat_score > 55:
        return False
    if response_state not in {
        ResponseState.MONITOR_ONLY,
        ResponseState.SILENT_OPERATOR_REVIEW,
    }:
        return False

    for assessment in reversed(recent_responses):
        if assessment["zone_id"] != zone_id:
            continue
        if assessment["response_state"] not in {
            ResponseState.MONITOR_ONLY.value,
            ResponseState.SILENT_OPERATOR_REVIEW.value,
        }:
            continue
        if event_timestamp.astimezone(UTC) - _coerce_datetime(assessment["created_at"]) > RESPONSE_COOLDOWN_WINDOW:
            continue
        return True

    return False


def _build_operator_recommendation(
    *,
    response_state: ResponseState,
    known_occupant: bool,
    cooldown_applied: bool,
) -> str:
    if cooldown_applied:
        return "Escalation should remain silent pending verification."
    if response_state == ResponseState.EMERGENCY_RESPONSE:
        return "High confidence intrusion pattern detected. Prioritise emergency response."
    if response_state == ResponseState.ACTIVE_SECURITY_RESPONSE:
        return "Prioritise active security review and continue immediate operator assessment."
    if response_state == ResponseState.OCCUPANT_VERIFICATION:
        return "Possible occupant movement continuity detected. Request occupant verification."
    if response_state == ResponseState.SILENT_OPERATOR_REVIEW:
        return "Escalation should remain silent pending verification."
    if known_occupant:
        return "Possible occupant movement continuity detected. Continue quiet monitoring."
    return "Low-confidence anomaly cluster; continue monitoring."


def _response_state_for_continuity(urgency: ResponseUrgency) -> ResponseState:
    if urgency in {ResponseUrgency.URGENT, ResponseUrgency.CRITICAL}:
        return ResponseState.OCCUPANT_VERIFICATION
    return ResponseState.MONITOR_ONLY


def _raise_urgency(urgency: ResponseUrgency) -> ResponseUrgency:
    if urgency == ResponseUrgency.LOW:
        return ResponseUrgency.ELEVATED
    if urgency == ResponseUrgency.ELEVATED:
        return ResponseUrgency.URGENT
    return urgency


def _lower_urgency(urgency: ResponseUrgency) -> ResponseUrgency:
    if urgency == ResponseUrgency.CRITICAL:
        return ResponseUrgency.URGENT
    if urgency == ResponseUrgency.URGENT:
        return ResponseUrgency.ELEVATED
    if urgency == ResponseUrgency.ELEVATED:
        return ResponseUrgency.LOW
    return urgency


def _max_urgency(left: ResponseUrgency, right: ResponseUrgency) -> ResponseUrgency:
    order = {
        ResponseUrgency.LOW: 1,
        ResponseUrgency.ELEVATED: 2,
        ResponseUrgency.URGENT: 3,
        ResponseUrgency.CRITICAL: 4,
    }
    return left if order[left] >= order[right] else right


def _max_response_state(left: ResponseState, right: ResponseState) -> ResponseState:
    order = {
        ResponseState.MONITOR_ONLY: 1,
        ResponseState.SILENT_OPERATOR_REVIEW: 2,
        ResponseState.OCCUPANT_VERIFICATION: 3,
        ResponseState.ACTIVE_SECURITY_RESPONSE: 4,
        ResponseState.EMERGENCY_RESPONSE: 5,
    }
    return left if order[left] >= order[right] else right


def _max_occupant_safety(
    left: OccupantSafetyState,
    right: OccupantSafetyState,
) -> OccupantSafetyState:
    order = {
        OccupantSafetyState.LIKELY_SAFE: 1,
        OccupantSafetyState.VERIFY_OCCUPANT: 2,
        OccupantSafetyState.POSSIBLE_RISK: 3,
        OccupantSafetyState.HIGH_RISK: 4,
    }
    return left if order[left] >= order[right] else right


def _unique_reasoning(reasoning: list[str]) -> list[str]:
    unique: list[str] = []
    for item in reasoning:
        if item and item not in unique:
            unique.append(item)
    return unique


def _coerce_datetime(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(UTC)
    return datetime.fromisoformat(value).astimezone(UTC)
