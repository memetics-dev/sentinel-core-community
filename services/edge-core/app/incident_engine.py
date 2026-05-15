from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.escalation import EscalationState
from app.incidents import Incident, IncidentSeverity, IncidentStatus
from app.models import SensorEvent
from app.modes import OperatingMode
from app.threats import ThreatClassification, ThreatState
from app.zones import Zone

INCIDENT_GROUPING_WINDOW = timedelta(minutes=15)

SEVERITY_ORDER = {
    IncidentSeverity.SUSPICIOUS: 1,
    IncidentSeverity.HIGH_THREAT: 2,
    IncidentSeverity.CRITICAL: 3,
}


def should_open_incident(classification: ThreatClassification) -> bool:
    return classification in {
        ThreatClassification.SUSPICIOUS,
        ThreatClassification.HIGH_THREAT,
        ThreatClassification.CRITICAL,
    }


def build_incident_from_event(
    existing_incident: Incident | None,
    event: SensorEvent,
    mode: OperatingMode,
    threat: ThreatState,
    escalation: EscalationState,
    known_occupant: bool,
    zone: Zone | None,
    current_timestamp: datetime,
) -> Incident | None:
    if not should_open_incident(threat.classification):
        return None

    severity = map_incident_severity(threat.classification)
    created_at = (
        existing_incident.created_at if existing_incident else current_timestamp
    )
    related_event_count = (
        existing_incident.related_event_count + 1 if existing_incident else 1
    )
    related_escalation_count = (
        existing_incident.related_escalation_count + 1 if existing_incident else 1
    )
    highest_severity = max_severity(
        existing_incident.severity if existing_incident else severity,
        severity,
    )
    status = (
        IncidentStatus.MONITORING
        if existing_incident or related_event_count > 1
        else IncidentStatus.OPEN
    )

    return Incident(
        incident_id=existing_incident.incident_id if existing_incident else new_incident_id(),
        zone_id=event.zone_id,
        severity=highest_severity,
        status=status,
        created_at=created_at,
        updated_at=current_timestamp,
        related_event_count=related_event_count,
        related_escalation_count=related_escalation_count,
        reasoning_summary=build_incident_summary(
            event=event,
            mode=mode,
            known_occupant=known_occupant,
            zone=zone,
            related_event_count=related_event_count,
        ),
    )


def get_incident_window_start(current_timestamp: datetime) -> datetime:
    return current_timestamp - INCIDENT_GROUPING_WINDOW


def map_incident_severity(
    classification: ThreatClassification,
) -> IncidentSeverity:
    if classification == ThreatClassification.CRITICAL:
        return IncidentSeverity.CRITICAL
    if classification == ThreatClassification.HIGH_THREAT:
        return IncidentSeverity.HIGH_THREAT
    return IncidentSeverity.SUSPICIOUS


def max_severity(
    left: IncidentSeverity,
    right: IncidentSeverity,
) -> IncidentSeverity:
    if SEVERITY_ORDER[left] >= SEVERITY_ORDER[right]:
        return left
    return right


def build_incident_summary(
    event: SensorEvent,
    mode: OperatingMode,
    known_occupant: bool,
    zone: Zone | None,
    related_event_count: int,
) -> str:
    zone_label = zone.label.lower() if zone else event.zone_id
    repeated_prefix = "Repeated " if related_event_count > 1 else ""
    identity_phrase = "unknown " if not known_occupant else ""

    if event.sensor_type.value == "mmwave" and mode == OperatingMode.NIGHT_LOCK:
        return sentence_case_first_char(
            f"{repeated_prefix}{identity_phrase}nighttime movement detected in "
            f"{zone_label} during {mode_label(mode)}."
        )

    if event.sensor_type.value == "mmwave":
        return sentence_case_first_char(
            f"{repeated_prefix}{identity_phrase}movement detected in {zone_label}."
        )

    return sentence_case_first_char(
        f"{repeated_prefix}{identity_phrase}security activity detected in {zone_label}."
    )


def new_incident_id() -> str:
    return f"incident_{uuid4().hex[:12]}"


def mode_label(mode: OperatingMode) -> str:
    if mode == OperatingMode.NIGHT_LOCK:
        return "Night Lock"
    if mode == OperatingMode.AWAY_GUARD:
        return "Away Guard"

    return mode.value.replace("_", " ")


def sentence_case_first_char(text: str) -> str:
    if not text:
        return text

    return text[0].upper() + text[1:]


def transition_incident_status(
    incident: Incident,
    target_status: IncidentStatus,
) -> Incident | None:
    valid_transitions = {
        IncidentStatus.OPEN: {
            IncidentStatus.MONITORING,
            IncidentStatus.RESOLVED,
            IncidentStatus.DISMISSED,
        },
        IncidentStatus.MONITORING: {
            IncidentStatus.RESOLVED,
            IncidentStatus.DISMISSED,
        },
    }

    allowed_targets = valid_transitions.get(incident.status, set())
    if target_status not in allowed_targets:
        return None

    return Incident(
        incident_id=incident.incident_id,
        zone_id=incident.zone_id,
        severity=incident.severity,
        status=target_status,
        created_at=incident.created_at,
        updated_at=datetime.now(UTC),
        related_event_count=incident.related_event_count,
        related_escalation_count=incident.related_escalation_count,
        reasoning_summary=incident.reasoning_summary,
    )
