from datetime import UTC, datetime, timedelta

from app.correlation_engine import evaluate_correlated_signals, summarize_correlation
from app.behaviour_engine import evaluate_behavioural_modifier
from app.db import (
    get_current_trial_session,
    get_recent_active_incident,
    list_event_history,
    list_identity_history,
    persist_operational_narrative,
    persist_correlated_signal,
    persist_escalation_evaluation,
    persist_identity_evaluation,
    persist_response_assessment,
    persist_sensor_event,
    persist_threat_evaluation,
    list_response_history,
    upsert_incident,
)
from app.escalation import EscalationState
from app.escalation_engine import determine_escalation
from app.identity import IdentityState
from app.incident_engine import (
    build_incident_from_event,
    get_incident_window_start,
)
from app.models import SensorEvent, TrustedDevice
from app.modes import SystemModeState
from app.narrative_engine import build_operational_narrative
from app.operations_feed import publish_ops_event
from app.presence_engine import build_household_presence_state, evaluate_presence_modifier
from app.response_engine import build_response_assessment
from app.occupancy import OccupancyState
from app.state import (
    escalation_state,
    occupants,
    identity_state,
    occupancy_state,
    sensor_events,
    threat_state,
    trusted_devices,
    zones,
)
from app.threat_engine import calculate_threat_score, classify_threat
from app.threats import ThreatState

TRUSTED_PRESENCE_WINDOW = timedelta(minutes=10)


def ingest_sensor_event(
    event: SensorEvent,
    system_mode: SystemModeState,
) -> dict:
    sensor_events.append(event)
    current_timestamp = event.timestamp.astimezone(UTC)
    current_session = get_current_trial_session()
    current_session_id = (
        current_session.session_id if current_session is not None else None
    )
    event_id = persist_sensor_event(event)
    publish_ops_event(
        "sensor_event_accepted",
        {
            "event_id": event_id,
            "sensor_id": event.sensor_id,
            "sensor_type": event.sensor_type.value,
            "zone_id": event.zone_id,
            "value": event.value,
            "confidence": event.confidence,
            "timestamp": event.timestamp.isoformat(),
        },
    )

    occupancy_state[event.zone_id] = OccupancyState(
        zone_id=event.zone_id,
        occupied=True,
        occupancy_confidence=event.confidence,
        movement_state="active",
        last_updated=current_timestamp,
    )

    prior_known_occupant, trusted_presence_reasoning = get_trusted_presence_context(
        event.zone_id,
        event.timestamp,
    )
    current_identity = evaluate_identity(event)
    identity_state[event.zone_id] = current_identity
    persist_identity_evaluation(
        event_id=event_id,
        zone_id=event.zone_id,
        identity=current_identity,
        created_at=current_timestamp.isoformat(),
    )

    known_occupant = current_identity.known_occupant or prior_known_occupant
    zone = zones.get(event.zone_id)

    threat_score, reasoning = calculate_threat_score(
        event=event,
        mode=system_mode.mode,
        known_occupant=known_occupant,
        zone=zone,
    )
    historical_events = [
        history_event
        for history_event in list_event_history()
        if history_event["id"] != event_id
    ]
    behaviour_modifier, behaviour_reasoning = evaluate_behavioural_modifier(
        event=event,
        zone=zone,
        historical_events=historical_events,
    )
    reasoning.extend(behaviour_reasoning)
    correlated_signals = evaluate_correlated_signals(
        event=event,
        zone=zone,
        known_occupant=known_occupant,
        historical_events=historical_events,
        behaviour_reasoning=behaviour_reasoning,
        zones=zones,
    )
    correlation_modifier, correlation_reasoning = summarize_correlation(correlated_signals)
    presence_state = build_household_presence_state(
        occupants=occupants,
        trusted_devices=trusted_devices,
        identity_history=list_identity_history(),
        recent_events=historical_events,
        current_mode=system_mode.mode,
        occupancy_state=occupancy_state,
        now=current_timestamp,
    )
    presence_modifier, presence_reasoning = evaluate_presence_modifier(
        event=event,
        presence_state=presence_state,
        known_occupant=known_occupant,
        current_mode=system_mode.mode,
    )
    threat_score = max(
        0,
        min(
            threat_score
            + behaviour_modifier
            + correlation_modifier
            + presence_modifier,
            100,
        ),
    )
    reasoning.extend(correlation_reasoning)
    reasoning.extend(presence_reasoning)
    reasoning.extend(trusted_presence_reasoning)

    classification = classify_threat(threat_score)
    threat_state[event.zone_id] = ThreatState(
        zone_id=event.zone_id,
        threat_score=threat_score,
        classification=classification,
        reasoning=reasoning,
        last_updated=current_timestamp,
    )
    persist_threat_evaluation(event_id, threat_state[event.zone_id])
    publish_ops_event(
        "threat_evaluated",
        {
            "event_id": event_id,
            "zone_id": event.zone_id,
            "threat_score": threat_state[event.zone_id].threat_score,
            "classification": threat_state[event.zone_id].classification.value,
            "reasoning": threat_state[event.zone_id].reasoning,
        },
    )

    escalation_stage, recommended_action = determine_escalation(threat_score)
    escalation_state[event.zone_id] = EscalationState(
        zone_id=event.zone_id,
        stage=escalation_stage,
        recommended_action=recommended_action,
        reasoning=reasoning,
        last_updated=current_timestamp,
    )
    persist_escalation_evaluation(event_id, escalation_state[event.zone_id])
    publish_ops_event(
        "escalation_updated",
        {
            "event_id": event_id,
            "zone_id": event.zone_id,
            "stage": escalation_state[event.zone_id].stage.value,
            "recommended_action": escalation_state[event.zone_id].recommended_action,
            "reasoning": escalation_state[event.zone_id].reasoning,
        },
    )
    existing_incident = get_recent_active_incident(
        event.zone_id,
        get_incident_window_start(current_timestamp),
        session_id=current_session_id,
    )
    incident = build_incident_from_event(
        existing_incident=existing_incident,
        event=event,
        mode=system_mode.mode,
        threat=threat_state[event.zone_id],
        escalation=escalation_state[event.zone_id],
        known_occupant=known_occupant,
        zone=zone,
        current_timestamp=current_timestamp,
    )
    if incident is not None:
        upsert_incident(incident, session_id=current_session_id)
        publish_ops_event(
            "incident_opened" if existing_incident is None else "incident_updated",
            {
                "incident_id": incident.incident_id,
                "zone_id": incident.zone_id,
                "severity": incident.severity.value,
                "status": incident.status.value,
                "related_event_count": incident.related_event_count,
                "related_escalation_count": incident.related_escalation_count,
                "reasoning_summary": incident.reasoning_summary,
            },
        )

    for signal in correlated_signals:
        persist_correlated_signal(
            event_id=event_id,
            incident_id=incident.incident_id if incident is not None else None,
            signal=signal,
        )
        publish_ops_event(
            "correlation_detected",
            {
                "event_id": event_id,
                "incident_id": incident.incident_id if incident is not None else None,
                "zone_id": signal.zone_id,
                "pattern_type": signal.pattern_type,
                "modifier": signal.modifier,
                "reasoning": signal.reasoning,
                "contributing_event_ids": signal.contributing_event_ids,
            },
        )

    response_assessment = build_response_assessment(
        event_id=event_id,
        event=event,
        threat=threat_state[event.zone_id],
        incident=incident,
        behaviour_reasoning=behaviour_reasoning,
        correlated_signals=correlated_signals,
        known_occupant=known_occupant,
        mode=system_mode.mode,
        zone=zone,
        presence_state=presence_state,
        recent_responses=list_response_history(session_id=current_session_id),
    )
    response_assessment.id = persist_response_assessment(
        response_assessment,
        session_id=current_session_id,
    )
    publish_ops_event(
        "response_assessed",
        {
            "assessment_id": response_assessment.id,
            "event_id": event_id,
            "incident_id": response_assessment.incident_id,
            "zone_id": response_assessment.zone_id,
            "response_confidence": response_assessment.response_confidence,
            "urgency": response_assessment.urgency.value,
            "response_state": response_assessment.response_state.value,
            "occupant_safety_state": response_assessment.occupant_safety_state.value,
            "operator_recommendation": response_assessment.operator_recommendation,
            "cooldown_applied": response_assessment.cooldown_applied,
            "reasoning": response_assessment.reasoning,
        },
    )
    operational_narrative = build_operational_narrative(
        event_id=event_id,
        event=event,
        incident=incident,
        correlated_signals=correlated_signals,
        behaviour_reasoning=behaviour_reasoning,
        response_assessment=response_assessment,
        presence_state=presence_state,
        known_occupant=known_occupant,
        mode=system_mode.mode,
    )
    operational_narrative.id = persist_operational_narrative(
        operational_narrative,
        session_id=current_session_id,
    )
    publish_ops_event(
        "narrative_generated",
        {
            "narrative_id": operational_narrative.id,
            "event_id": event_id,
            "incident_id": operational_narrative.incident_id,
            "zone_id": operational_narrative.zone_id,
            "summary": operational_narrative.summary,
            "household_interpretation": operational_narrative.household_interpretation,
            "progression_summary": operational_narrative.progression_summary,
            "confidence": operational_narrative.confidence.value,
            "reasoning": operational_narrative.reasoning,
        },
    )

    return {
        "status": "accepted",
        "event": event,
        "identity": identity_state[event.zone_id],
        "threat": threat_state[event.zone_id],
        "escalation": escalation_state[event.zone_id],
        "response": response_assessment,
        "narrative": operational_narrative,
        "total_events": len(sensor_events),
    }


def evaluate_identity(event: SensorEvent) -> IdentityState:
    identity_reasoning = []
    known_occupant = False
    identity_confidence = 0
    occupant_id = None
    trusted_device = resolve_trusted_device(event)

    if trusted_device and event.value == "resident_device_detected":
        known_occupant = True
        identity_confidence = 90
        occupant_id = trusted_device.occupant_id
        occupant = occupants.get(occupant_id)
        occupant_label = occupant.label if occupant else occupant_id
        identity_reasoning.append(
            f"Configured resident device detected for {occupant_label}"
        )
    elif trusted_device and event.sensor_type.value == "ble":
        known_occupant = True
        identity_confidence = 70
        occupant_id = trusted_device.occupant_id
        occupant = occupants.get(occupant_id)
        occupant_label = occupant.label if occupant else occupant_id
        identity_reasoning.append(
            f"Configured BLE trusted device suggests occupant {occupant_label}"
        )
    else:
        identity_confidence = 15
        if event.sensor_type.value == "ble" or event.value == "resident_device_detected":
            identity_reasoning.append(
                "Observed device is not in configured trusted devices"
            )
        else:
            identity_reasoning.append("No trusted identity signals detected")

    return IdentityState(
        occupant_id=occupant_id,
        identity_confidence=identity_confidence,
        known_occupant=known_occupant,
        reasoning=identity_reasoning,
    )


def resolve_trusted_device(event: SensorEvent) -> TrustedDevice | None:
    trusted_device = trusted_devices.get(event.sensor_id)
    if not trusted_device:
        return None
    if trusted_device.sensor_type != event.sensor_type:
        return None

    return trusted_device


def get_trusted_presence_context(
    zone_id: str,
    event_timestamp: datetime,
) -> tuple[bool, list[str]]:
    candidate_zone_ids = {zone_id}
    zone = zones.get(zone_id)
    if zone:
        candidate_zone_ids.update(zone.connected_zones)

    for candidate_zone_id in candidate_zone_ids:
        zone_identity = identity_state.get(candidate_zone_id)
        zone_occupancy = occupancy_state.get(candidate_zone_id)

        if not zone_identity or not zone_identity.known_occupant:
            continue
        if not zone_occupancy:
            continue
        if event_timestamp - zone_occupancy.last_updated > TRUSTED_PRESENCE_WINDOW:
            continue

        if candidate_zone_id == zone_id:
            return True, ["Trusted identity recently observed in this zone"]

        return True, [
            f"Trusted identity recently observed in connected zone {candidate_zone_id}"
        ]

    return False, []
