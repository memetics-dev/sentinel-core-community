from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta

from app.models import ActivityWindow, HouseholdRhythmProfile, SensorEvent, ZoneActivityBaseline
from app.zones import Zone

MOVEMENT_SENSOR_TYPES = {"mmwave"}
LONG_INACTIVITY_THRESHOLD = timedelta(hours=6)
RECENT_CONTINUITY_WINDOW = timedelta(hours=24)


def build_household_rhythm_profile(events: list[dict]) -> HouseholdRhythmProfile:
    movement_events = _movement_events(events)
    zone_events: dict[str, list[dict]] = defaultdict(list)
    household_hour_counts: Counter[int] = Counter()

    for event in movement_events:
        zone_events[event["zone_id"]].append(event)
        household_hour_counts[_event_hour(event)] += 1

    zone_baselines = {
        zone_id: _build_zone_baseline(zone_id, zone_history)
        for zone_id, zone_history in zone_events.items()
    }
    common_active_hours = [
        hour for hour, _ in household_hour_counts.most_common() if household_hour_counts[hour] > 0
    ]

    return HouseholdRhythmProfile(
        generated_at=datetime.now(UTC),
        total_events=len(movement_events),
        common_active_hours=sorted(common_active_hours[:8]),
        zone_baselines=zone_baselines,
    )


def evaluate_behavioural_modifier(
    event: SensorEvent,
    zone: Zone | None,
    historical_events: list[dict],
) -> tuple[int, list[str]]:
    movement_history = _movement_events(historical_events)
    if len(movement_history) < 3 or event.sensor_type.value not in MOVEMENT_SENSOR_TYPES:
        return 0, []

    profile = build_household_rhythm_profile(movement_history)
    zone_baseline = profile.zone_baselines.get(event.zone_id)
    if zone_baseline is None:
        return 0, []

    modifier = 0
    reasoning: list[str] = []
    event_hour = event.timestamp.astimezone(UTC).hour

    if zone and not zone.night_access_expected and event_hour < 6:
        modifier += 8
        reasoning.append(
            f"{zone.label} activity is unusual for this household at this hour."
        )

    if event_hour not in zone_baseline.active_hours:
        modifier += 7
        reasoning.append(
            f"{event.zone_id.capitalize()} activity falls outside typical zone active hours."
        )

    last_zone_event = _latest_zone_event_before(event.zone_id, event.timestamp, movement_history)
    if last_zone_event is not None:
        gap = event.timestamp - _event_timestamp(last_zone_event)
        if gap >= LONG_INACTIVITY_THRESHOLD:
            modifier += 5
            reasoning.append(
                f"{event.zone_id.capitalize()} movement resumed after a long inactivity gap."
            )

    if profile.common_active_hours and event_hour not in profile.common_active_hours:
        modifier += 5
        reasoning.append(
            "Activity timing is inconsistent with the recent household rhythm."
        )

    if zone and zone.id in {"hallway", "living_room"} and event_hour < 6:
        modifier += 2
        reasoning.append(
            f"{zone.label} activity suggests unusual overnight movement continuity."
        )

    return modifier, reasoning


def list_behavioural_anomalies(events: list[dict], zones: dict[str, Zone]) -> list[dict]:
    anomalies: list[dict] = []
    prior_events: list[dict] = []

    for event in sorted(events, key=lambda item: (_event_timestamp(item), item["id"])):
        event_model = SensorEvent(
            sensor_id=event["sensor_id"],
            sensor_type=event["sensor_type"],
            zone_id=event["zone_id"],
            value=event["value"],
            confidence=event["confidence"],
            timestamp=_event_timestamp(event),
        )
        modifier, reasons = evaluate_behavioural_modifier(
            event=event_model,
            zone=zones.get(event_model.zone_id),
            historical_events=prior_events,
        )
        if reasons:
            anomalies.append(
                {
                    "event_id": event["id"],
                    "zone_id": event["zone_id"],
                    "timestamp": event["timestamp"],
                    "modifier": modifier,
                    "reasons": reasons,
                }
            )
        prior_events.append(event)

    return anomalies


def _build_zone_baseline(zone_id: str, zone_history: list[dict]) -> ZoneActivityBaseline:
    hour_counts: Counter[int] = Counter(_event_hour(event) for event in zone_history)
    active_hours = sorted(hour for hour, count in hour_counts.items() if count > 0)
    windows = _build_activity_windows(active_hours, hour_counts)
    movement_frequency = len(zone_history) / max(len({_event_date(event) for event in zone_history}), 1)
    latest_timestamp = max(_event_timestamp(event) for event in zone_history)
    recent_continuity = sum(
        1
        for event in zone_history
        if latest_timestamp - _event_timestamp(event) <= RECENT_CONTINUITY_WINDOW
    )

    return ZoneActivityBaseline(
        zone_id=zone_id,
        active_hours=active_hours,
        normal_movement_windows=windows,
        movement_frequency=round(movement_frequency, 2),
        recent_continuity=recent_continuity,
    )


def _build_activity_windows(
    active_hours: list[int],
    hour_counts: Counter[int],
) -> list[ActivityWindow]:
    if not active_hours:
        return []

    windows: list[ActivityWindow] = []
    window_start = active_hours[0]
    previous_hour = active_hours[0]
    event_count = hour_counts[active_hours[0]]

    for hour in active_hours[1:]:
        if hour == previous_hour + 1:
            previous_hour = hour
            event_count += hour_counts[hour]
            continue

        windows.append(
            ActivityWindow(
                start_hour=window_start,
                end_hour=previous_hour,
                event_count=event_count,
            )
        )
        window_start = hour
        previous_hour = hour
        event_count = hour_counts[hour]

    windows.append(
        ActivityWindow(
            start_hour=window_start,
            end_hour=previous_hour,
            event_count=event_count,
        )
    )
    return windows


def _movement_events(events: list[dict]) -> list[dict]:
    return [
        event
        for event in events
        if event["sensor_type"] in MOVEMENT_SENSOR_TYPES
    ]


def _event_timestamp(event: dict) -> datetime:
    timestamp = event["timestamp"]
    if isinstance(timestamp, datetime):
        return timestamp
    return datetime.fromisoformat(timestamp)


def _event_hour(event: dict) -> int:
    return _event_timestamp(event).astimezone(UTC).hour


def _event_date(event: dict):
    return _event_timestamp(event).astimezone(UTC).date()


def _latest_zone_event_before(
    zone_id: str,
    timestamp: datetime,
    events: list[dict],
) -> dict | None:
    zone_events = [
        event
        for event in events
        if event["zone_id"] == zone_id and _event_timestamp(event) < timestamp
    ]
    if not zone_events:
        return None

    return max(zone_events, key=_event_timestamp)
