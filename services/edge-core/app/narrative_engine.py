from datetime import UTC, datetime, timedelta

from app.incidents import Incident, IncidentSeverity, IncidentStatus, IncidentTimelineEntry
from app.models import CorrelatedSignal, HouseholdPresenceState, SensorEvent
from app.modes import OperatingMode
from app.narrative import NarrativeConfidence, OperationalNarrative
from app.response import ResponseAssessment, ResponseState

CURRENT_NARRATIVE_WINDOW = timedelta(minutes=30)
HOSTILE_CORRELATION_PATTERNS = {
    "perimeter_to_garage_progression",
    "indoor_after_perimeter_progression",
}
INTRUSION_RESPONSE_STATES = {
    ResponseState.EMERGENCY_RESPONSE,
}


def build_operational_narrative(
    *,
    event_id: int,
    event: SensorEvent,
    incident: Incident | None,
    correlated_signals: list[CorrelatedSignal],
    behaviour_reasoning: list[str],
    response_assessment: ResponseAssessment,
    presence_state: HouseholdPresenceState,
    known_occupant: bool,
    mode: OperatingMode,
) -> OperationalNarrative:
    trusted_continuity_active = _trusted_continuity_active(
        correlated_signals=correlated_signals,
        response_assessment=response_assessment,
        incident=incident,
        presence_state=presence_state,
        known_occupant=known_occupant,
    )
    hostile_progression_active = _hostile_progression_active(
        correlated_signals=correlated_signals,
        response_assessment=response_assessment,
        incident=incident,
    )
    summary = _build_summary(
        incident=incident,
        correlated_signals=correlated_signals,
        response_assessment=response_assessment,
        presence_state=presence_state,
        known_occupant=known_occupant,
        mode=mode,
        trusted_continuity_active=trusted_continuity_active,
        hostile_progression_active=hostile_progression_active,
    )
    household_interpretation = _build_household_interpretation(
        presence_state=presence_state,
        known_occupant=known_occupant,
        mode=mode,
        trusted_continuity_active=trusted_continuity_active,
        hostile_progression_active=hostile_progression_active,
    )
    progression_summary = _build_progression_summary(
        correlated_signals=correlated_signals,
        known_occupant=known_occupant,
        trusted_continuity_active=trusted_continuity_active,
    )
    confidence = _build_confidence(
        response_assessment=response_assessment,
        incident=incident,
        known_occupant=known_occupant,
    )

    reasoning: list[str] = []
    if any(
        signal.pattern_type == "perimeter_to_garage_progression"
        for signal in correlated_signals
    ):
        reasoning.append(
            "No trusted occupants were observed before perimeter-originated movement progressed into the garage."
        )
    if any(
        signal.pattern_type in {
            "connected_zone_progression",
            "indoor_after_perimeter_progression",
        }
        for signal in correlated_signals
    ):
        reasoning.append("Movement continuity across connected zones increased intrusion confidence.")
    if trusted_continuity_active:
        reasoning.append("Trusted occupant continuity reduced escalation confidence.")
    if (
        presence_state.household_activity.settled
        and mode == OperatingMode.NIGHT_LOCK
        and not trusted_continuity_active
        and not hostile_progression_active
    ):
        reasoning.append("Household appeared settled prior to anomalous nighttime activity.")
    if behaviour_reasoning:
        reasoning.extend(
            reason
            for reason in behaviour_reasoning
            if "unusual" in reason or "inactivity gap" in reason
        )
    if response_assessment.response_state == ResponseState.MONITOR_ONLY:
        reasoning.append("Current response posture remains monitoring-focused.")
    else:
        reasoning.append(response_assessment.operator_recommendation)

    return OperationalNarrative(
        event_id=event_id,
        incident_id=incident.incident_id if incident else None,
        zone_id=event.zone_id,
        summary=summary,
        household_interpretation=household_interpretation,
        progression_summary=progression_summary,
        confidence=confidence,
        reasoning=_unique(reasoning),
        created_at=event.timestamp.astimezone(UTC),
    )


def list_current_narratives(
    history: list[dict],
    incidents: list[dict],
) -> list[dict]:
    open_incident_ids = {
        incident["incident_id"]
        for incident in incidents
        if incident["status"] in {IncidentStatus.OPEN.value, IncidentStatus.MONITORING.value}
    }
    latest_by_key: dict[str, dict] = {}
    for narrative in history:
        key = narrative["incident_id"] or narrative["zone_id"] or f"narrative_{narrative['id']}"
        latest_by_key[key] = narrative

    window_start = datetime.now(UTC) - CURRENT_NARRATIVE_WINDOW
    current: list[dict] = []
    for narrative in latest_by_key.values():
        created_at = _coerce_datetime(narrative["created_at"])
        if narrative["incident_id"] in open_incident_ids:
            current.append(narrative)
            continue
        if created_at >= window_start:
            current.append(narrative)

    current.sort(
        key=lambda item: (_coerce_datetime(item["created_at"]), item["id"]),
        reverse=True,
    )
    return current


def latest_narrative_for_incident(incident_id: str, narratives: list[dict]) -> dict | None:
    if not narratives:
        return None
    return narratives[-1]


def build_operator_narrative_interpretation(
    incident: Incident,
    latest_narrative: dict | None,
) -> str:
    if latest_narrative:
        return latest_narrative["summary"]
    if incident.status == IncidentStatus.RESOLVED:
        return "Incident has been resolved after local operator review."
    if incident.status == IncidentStatus.DISMISSED:
        return "Incident has been dismissed as non-actionable."
    return "Review the operational timeline in order and confirm the current household state."


def build_narrative_timeline_entries(
    narratives: list[dict],
) -> list[IncidentTimelineEntry]:
    return [
        IncidentTimelineEntry(
            entry_type="operational_narrative",
            timestamp=narrative["created_at"],
            details=narrative,
        )
        for narrative in narratives
    ]


def _build_summary(
    *,
    incident: Incident | None,
    correlated_signals: list[CorrelatedSignal],
    response_assessment: ResponseAssessment,
    presence_state: HouseholdPresenceState,
    known_occupant: bool,
    mode: OperatingMode,
    trusted_continuity_active: bool,
    hostile_progression_active: bool,
) -> str:
    pattern_types = {signal.pattern_type for signal in correlated_signals}

    if "perimeter_to_garage_progression" in pattern_types:
        return "No trusted occupants were observed before perimeter-originated movement progressed into the garage."
    if hostile_progression_active and {
        "connected_zone_progression",
        "indoor_after_perimeter_progression",
    } & pattern_types:
        return "Movement continuity across connected zones increased intrusion confidence."
    if trusted_continuity_active:
        return "Trusted occupant continuity reduced escalation concern."
    if (
        presence_state.household_activity.settled
        and mode == OperatingMode.NIGHT_LOCK
        and not hostile_progression_active
    ):
        return "Household appeared settled prior to anomalous nighttime activity."
    if response_assessment.response_state == ResponseState.EMERGENCY_RESPONSE:
        return "Unknown household activity requires immediate operator review."
    if response_assessment.response_state == ResponseState.MONITOR_ONLY:
        return "Low-confidence household activity remains under monitoring."
    if incident and incident.status in {IncidentStatus.OPEN, IncidentStatus.MONITORING}:
        return "Unknown household activity remains under operator review."
    return "Household activity was summarised for local operator review."


def _build_household_interpretation(
    *,
    presence_state: HouseholdPresenceState,
    known_occupant: bool,
    mode: OperatingMode,
    trusted_continuity_active: bool,
    hostile_progression_active: bool,
) -> str:
    if trusted_continuity_active:
        return "Trusted occupant activity was recently observed and reduced escalation concern."
    if hostile_progression_active:
        return "No trusted occupants were observed before activity was detected."
    if presence_state.no_trusted_occupants_detected:
        return "No trusted occupants were observed before activity was detected."
    if presence_state.partial_occupancy:
        return "Partial household occupancy is currently inferred."
    if (
        presence_state.household_activity.settled
        and mode == OperatingMode.NIGHT_LOCK
        and not hostile_progression_active
    ):
        return "Household appeared settled during Night Lock before activity was detected."
    return presence_state.summary


def _build_progression_summary(
    *,
    correlated_signals: list[CorrelatedSignal],
    known_occupant: bool,
    trusted_continuity_active: bool,
) -> str:
    pattern_types = {signal.pattern_type for signal in correlated_signals}

    if "perimeter_to_garage_progression" in pattern_types and "indoor_after_perimeter_progression" in pattern_types:
        return "Perimeter-originated movement progressed from driveway to garage and then indoors."
    if "perimeter_to_garage_progression" in pattern_types:
        return "Perimeter-originated movement progressed into the garage."
    if {
        "connected_zone_progression",
        "indoor_after_perimeter_progression",
    } & pattern_types:
        return "Movement continuity across connected zones was observed."
    if trusted_continuity_active and known_occupant:
        return "Trusted presence was observed before follow-on movement."
    return "No significant multi-zone progression was observed."


def _build_confidence(
    *,
    response_assessment: ResponseAssessment,
    incident: Incident | None,
    known_occupant: bool,
) -> NarrativeConfidence:
    if known_occupant or response_assessment.response_confidence <= 40:
        return NarrativeConfidence.LOW
    if (
        response_assessment.response_confidence >= 75
        or (
            incident
            and incident.severity in {IncidentSeverity.HIGH_THREAT, IncidentSeverity.CRITICAL}
        )
    ):
        return NarrativeConfidence.HIGH
    return NarrativeConfidence.MEDIUM


def _trusted_continuity_active(
    *,
    correlated_signals: list[CorrelatedSignal],
    response_assessment: ResponseAssessment,
    incident: Incident | None,
    presence_state: HouseholdPresenceState,
    known_occupant: bool,
) -> bool:
    if not (known_occupant or presence_state.trusted_occupant_recently_active):
        return False
    if _hostile_progression_active(
        correlated_signals=correlated_signals,
        response_assessment=response_assessment,
        incident=incident,
    ):
        return False
    if response_assessment.response_confidence > 55:
        return False
    return response_assessment.response_state in {
        ResponseState.MONITOR_ONLY,
        ResponseState.OCCUPANT_VERIFICATION,
        ResponseState.SILENT_OPERATOR_REVIEW,
    }


def _hostile_progression_active(
    *,
    correlated_signals: list[CorrelatedSignal],
    response_assessment: ResponseAssessment,
    incident: Incident | None,
) -> bool:
    pattern_types = {signal.pattern_type for signal in correlated_signals}
    if pattern_types & HOSTILE_CORRELATION_PATTERNS:
        return True
    if incident and incident.severity == IncidentSeverity.CRITICAL:
        return True
    return False


def _coerce_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(UTC)
    return datetime.fromisoformat(value).astimezone(UTC)


def _unique(items: list[str]) -> list[str]:
    ordered: list[str] = []
    for item in items:
        if item and item not in ordered:
            ordered.append(item)
    return ordered
