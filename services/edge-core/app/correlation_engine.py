from datetime import UTC, datetime, timedelta

from app.models import CorrelatedSignal, SensorEvent
from app.zones import Zone

PERIMETER_ZONES = {"driveway", "yard", "porch", "perimeter", "front_door"}
CORRELATION_WINDOW = timedelta(minutes=10)
LOW_CONFIDENCE_THRESHOLD = 60


def evaluate_correlated_signals(
    event: SensorEvent,
    zone: Zone | None,
    known_occupant: bool,
    historical_events: list[dict],
    behaviour_reasoning: list[str],
    zones: dict[str, Zone],
) -> list[CorrelatedSignal]:
    current_timestamp = event.timestamp.astimezone(UTC)
    recent_events = _recent_events_before(event, historical_events)
    signals: list[CorrelatedSignal] = []

    connected_signal = _connected_zone_signal(
        event, zone, known_occupant, recent_events, current_timestamp, zones
    )
    if connected_signal:
        signals.append(connected_signal)

    perimeter_signal = _perimeter_progression_signal(
        event, recent_events, current_timestamp
    )
    if perimeter_signal:
        signals.append(perimeter_signal)

    sensitivity_signal = _sensitivity_timing_signal(
        event, zone, behaviour_reasoning, current_timestamp
    )
    if sensitivity_signal:
        signals.append(sensitivity_signal)

    low_conf_signal = _low_confidence_cluster_signal(
        event, recent_events, current_timestamp
    )
    if low_conf_signal:
        signals.append(low_conf_signal)

    return signals


def summarize_correlation(signals: list[CorrelatedSignal]) -> tuple[int, list[str]]:
    modifier = sum(signal.modifier for signal in signals)
    reasoning = [signal.reasoning for signal in signals]
    return modifier, reasoning


def _connected_zone_signal(
    event: SensorEvent,
    zone: Zone | None,
    known_occupant: bool,
    recent_events: list[dict],
    current_timestamp: datetime,
    zones: dict[str, Zone],
) -> CorrelatedSignal | None:
    for prior_event in reversed(recent_events):
        prior_zone_id = prior_event["zone_id"]
        if prior_zone_id == event.zone_id:
            continue
        if not _zones_are_correlated(event.zone_id, prior_zone_id, zone, zones):
            continue

        modifier = 6
        reasoning = "Repeated movement across connected zones suggests coordinated progression."
        if not known_occupant:
            modifier += 4
            reasoning = (
                "No trusted identity continuity detected across correlated zones."
            )

        return CorrelatedSignal(
            pattern_type="connected_zone_progression",
            zone_id=event.zone_id,
            modifier=modifier,
            reasoning=reasoning,
            contributing_event_ids=[prior_event["id"]],
            created_at=current_timestamp,
        )

    return None


def _perimeter_progression_signal(
    event: SensorEvent,
    recent_events: list[dict],
    current_timestamp: datetime,
) -> CorrelatedSignal | None:
    for prior_event in reversed(recent_events):
        prior_zone_id = prior_event["zone_id"]
        if event.zone_id == "garage" and prior_zone_id in PERIMETER_ZONES:
            return CorrelatedSignal(
                pattern_type="perimeter_to_garage_progression",
                zone_id=event.zone_id,
                modifier=8,
                reasoning="Movement progression suggests entry from perimeter into garage.",
                contributing_event_ids=[prior_event["id"]],
                created_at=current_timestamp,
            )
        if event.zone_id not in PERIMETER_ZONES and prior_zone_id == "garage":
            return CorrelatedSignal(
                pattern_type="indoor_after_perimeter_progression",
                zone_id=event.zone_id,
                modifier=7,
                reasoning="Indoor movement followed recent garage-originated activity.",
                contributing_event_ids=[prior_event["id"]],
                created_at=current_timestamp,
            )

    return None


def _sensitivity_timing_signal(
    event: SensorEvent,
    zone: Zone | None,
    behaviour_reasoning: list[str],
    current_timestamp: datetime,
) -> CorrelatedSignal | None:
    if not zone or zone.sensitivity != "high":
        return None
    if not any("unusual for this household at this hour" in reason for reason in behaviour_reasoning):
        return None

    return CorrelatedSignal(
        pattern_type="high_sensitivity_unusual_timing",
        zone_id=event.zone_id,
        modifier=6,
        reasoning="Unusual activity timing combined with a high-sensitivity zone increased concern.",
        contributing_event_ids=[],
        created_at=current_timestamp,
    )


def _low_confidence_cluster_signal(
    event: SensorEvent,
    recent_events: list[dict],
    current_timestamp: datetime,
) -> CorrelatedSignal | None:
    if event.confidence >= LOW_CONFIDENCE_THRESHOLD:
        return None

    low_conf_events = [
        prior_event
        for prior_event in recent_events
        if prior_event["confidence"] < LOW_CONFIDENCE_THRESHOLD
    ]
    if len(low_conf_events) < 2:
        return None

    return CorrelatedSignal(
        pattern_type="multi_low_confidence_anomaly_cluster",
        zone_id=event.zone_id,
        modifier=20,
        reasoning="Multiple unusual low-confidence events increased overall concern.",
        contributing_event_ids=[event_record["id"] for event_record in low_conf_events[-2:]],
        created_at=current_timestamp,
    )


def _recent_events_before(event: SensorEvent, historical_events: list[dict]) -> list[dict]:
    current_timestamp = event.timestamp.astimezone(UTC)
    return [
        historical_event
        for historical_event in historical_events
        if current_timestamp - _event_timestamp(historical_event) <= CORRELATION_WINDOW
        and _event_timestamp(historical_event) < current_timestamp
    ]


def _zones_are_correlated(
    current_zone_id: str,
    prior_zone_id: str,
    current_zone: Zone | None,
    zones: dict[str, Zone],
) -> bool:
    if current_zone and prior_zone_id in current_zone.connected_zones:
        return True

    prior_zone = zones.get(prior_zone_id)
    if prior_zone and current_zone_id in prior_zone.connected_zones:
        return True

    if current_zone and prior_zone:
        return bool(set(current_zone.connected_zones) & set(prior_zone.connected_zones))

    return False


def _event_timestamp(event: dict) -> datetime:
    timestamp = event["timestamp"]
    if isinstance(timestamp, datetime):
        return timestamp.astimezone(UTC)
    return datetime.fromisoformat(timestamp).astimezone(UTC)
