from datetime import UTC, datetime, timedelta

from app.identity import IdentityState
from app.models import (
    HouseholdActivityState,
    HouseholdPresenceState,
    Occupant,
    OccupantPresenceState,
    SensorEvent,
    TrustedDevice,
)
from app.modes import OperatingMode
from app.occupancy import OccupancyState

TRUSTED_OCCUPANT_WINDOW = timedelta(minutes=20)
RECENT_ACTIVITY_WINDOW = timedelta(minutes=15)
SETTLED_WINDOW = timedelta(minutes=30)


def build_household_presence_state(
    *,
    occupants: dict[str, Occupant],
    trusted_devices: dict[str, TrustedDevice],
    identity_history: list[dict],
    recent_events: list[dict],
    current_mode: OperatingMode,
    occupancy_state: dict[str, OccupancyState],
    now: datetime | None = None,
) -> HouseholdPresenceState:
    current_time = now.astimezone(UTC) if now else _resolve_now(identity_history, recent_events)
    recent_trusted_identity = _recent_trusted_identity(identity_history, current_time)
    recent_movement_events = _recent_movement_events(recent_events, current_time)

    occupant_states: list[OccupantPresenceState] = []
    seen_occupants: set[str] = set()
    for occupant_id, occupant in occupants.items():
        occupant_identity = [
            event
            for event in recent_trusted_identity
            if event.get("occupant_id") == occupant_id
        ]
        last_seen = occupant_identity[-1] if occupant_identity else None
        recent_zone_id = last_seen["zone_id"] if last_seen else None
        recently_active = bool(
            last_seen
            and any(
                event["zone_id"] == recent_zone_id
                and _coerce_timestamp(event["timestamp"]) >= current_time - RECENT_ACTIVITY_WINDOW
                for event in recent_movement_events
            )
        )
        reasoning: list[str] = []
        if last_seen:
            reasoning.append(
                f"Trusted occupant activity was recently observed in {recent_zone_id}."
            )
            seen_occupants.add(occupant_id)
        else:
            reasoning.append("No recent trusted presence observed for this occupant.")

        occupant_states.append(
            OccupantPresenceState(
                occupant_id=occupant.id,
                occupant_label=occupant.label,
                likely_home=last_seen is not None,
                recently_active=recently_active,
                last_seen_at=_coerce_timestamp(last_seen["created_at"]) if last_seen else None,
                recent_zone_id=recent_zone_id,
                reasoning=reasoning,
            )
        )

    no_trusted_occupants_detected = len(seen_occupants) == 0
    all_occupants_likely_home = bool(occupants) and len(seen_occupants) == len(occupants)
    partial_occupancy = 0 < len(seen_occupants) < len(occupants)
    trusted_occupant_recently_active = any(
        occupant.recently_active for occupant in occupant_states
    )
    unknown_presence_detected = bool(recent_movement_events) and no_trusted_occupants_detected

    activity_state = _build_household_activity_state(
        recent_events=recent_events,
        current_mode=current_mode,
        current_time=current_time,
    )

    reasoning: list[str] = []
    if no_trusted_occupants_detected:
        reasoning.append("No trusted occupants have been observed recently.")
    if trusted_occupant_recently_active:
        active_occupant = next(
            (
                occupant
                for occupant in occupant_states
                if occupant.recently_active and occupant.recent_zone_id
            ),
            None,
        )
        if active_occupant and active_occupant.recent_zone_id:
            reasoning.append(
                f"Trusted occupant activity was recently observed in {active_occupant.recent_zone_id}."
            )
    if partial_occupancy:
        reasoning.append("Only some configured occupants have recent trusted presence.")
    if activity_state.settled and current_mode == OperatingMode.NIGHT_LOCK:
        reasoning.append("Household appears settled during Night Lock.")
    if unknown_presence_detected:
        reasoning.append("Unknown presence is being inferred from recent occupied zones.")

    summary = _build_presence_summary(
        all_occupants_likely_home=all_occupants_likely_home,
        no_trusted_occupants_detected=no_trusted_occupants_detected,
        partial_occupancy=partial_occupancy,
        trusted_occupant_recently_active=trusted_occupant_recently_active,
        unknown_presence_detected=unknown_presence_detected,
        activity_state=activity_state,
    )

    return HouseholdPresenceState(
        summary=summary,
        all_occupants_likely_home=all_occupants_likely_home,
        no_trusted_occupants_detected=no_trusted_occupants_detected,
        partial_occupancy=partial_occupancy,
        trusted_occupant_recently_active=trusted_occupant_recently_active,
        unknown_presence_detected=unknown_presence_detected,
        household_activity=activity_state,
        occupants=occupant_states,
        reasoning=_unique_reasoning(reasoning),
        generated_at=current_time,
    )


def evaluate_presence_modifier(
    *,
    event: SensorEvent,
    presence_state: HouseholdPresenceState,
    known_occupant: bool,
    current_mode: OperatingMode,
) -> tuple[int, list[str]]:
    modifier = 0
    reasoning: list[str] = []

    if presence_state.no_trusted_occupants_detected and not known_occupant:
        modifier += 2
        reasoning.append("No trusted occupants have been observed recently.")

    if presence_state.unknown_presence_detected and not known_occupant:
        modifier += 1
        reasoning.append("Unknown presence is being inferred from recent occupied zones.")

    if presence_state.trusted_occupant_recently_active and known_occupant:
        modifier -= 6
        active_state = next(
            (
                occupant
                for occupant in presence_state.occupants
                if occupant.recently_active and occupant.recent_zone_id
            ),
            None,
        )
        if active_state and active_state.recent_zone_id:
            reasoning.append(
                f"Trusted occupant activity was recently observed in {active_state.recent_zone_id}."
            )

    if presence_state.household_activity.settled and current_mode == OperatingMode.NIGHT_LOCK:
        modifier += 1 if not known_occupant else -1
        reasoning.append("Household appears settled during Night Lock.")

    return modifier, _unique_reasoning(reasoning)


def _build_household_activity_state(
    *,
    recent_events: list[dict],
    current_mode: OperatingMode,
    current_time: datetime,
) -> HouseholdActivityState:
    movement_events = _movement_events(recent_events)
    recent_movement = [
        event
        for event in movement_events
        if _coerce_timestamp(event["timestamp"]) >= current_time - RECENT_ACTIVITY_WINDOW
    ]
    settled = not any(
        _coerce_timestamp(event["timestamp"]) >= current_time - SETTLED_WINDOW
        for event in movement_events
    )
    reasoning: list[str] = []
    state = "quiet"

    if len(recent_movement) >= 2:
        state = "active"
        reasoning.append("Recent movement indicates the household is active.")
    elif settled and current_mode == OperatingMode.NIGHT_LOCK:
        state = "settled"
        reasoning.append("Household appears settled during Night Lock.")
    elif recent_movement:
        state = "light_activity"
        reasoning.append("Limited recent movement suggests light household activity.")
    else:
        reasoning.append("No recent movement has been observed.")

    return HouseholdActivityState(
        state=state,
        recent_movement_count=len(recent_movement),
        settled=settled,
        reasoning=reasoning,
    )


def _build_presence_summary(
    *,
    all_occupants_likely_home: bool,
    no_trusted_occupants_detected: bool,
    partial_occupancy: bool,
    trusted_occupant_recently_active: bool,
    unknown_presence_detected: bool,
    activity_state: HouseholdActivityState,
) -> str:
    if unknown_presence_detected:
        return "Unknown presence detected without recent trusted occupant continuity."
    if all_occupants_likely_home:
        return "All configured occupants were recently observed at home."
    if partial_occupancy:
        return "Partial household occupancy is being inferred from recent trusted presence."
    if trusted_occupant_recently_active:
        return "Trusted occupant activity was recently observed."
    if no_trusted_occupants_detected and activity_state.state == "settled":
        return "No trusted occupants detected and the household appears settled."
    if no_trusted_occupants_detected:
        return "No trusted occupants have been observed recently."
    return "Household presence is currently stable."


def _recent_trusted_identity(identity_history: list[dict], now: datetime) -> list[dict]:
    recent = []
    for evaluation in identity_history:
        if not evaluation.get("known_occupant"):
            continue
        created_at = _coerce_timestamp(evaluation["created_at"])
        if created_at < now - TRUSTED_OCCUPANT_WINDOW:
            continue
        recent.append(evaluation)
    return recent


def _recent_events(events: list[dict], now: datetime) -> list[dict]:
    return [
        event
        for event in events
        if _coerce_timestamp(event["timestamp"]) >= now - SETTLED_WINDOW
    ]


def _recent_movement_events(events: list[dict], now: datetime) -> list[dict]:
    return [
        event
        for event in _movement_events(events)
        if _coerce_timestamp(event["timestamp"]) >= now - SETTLED_WINDOW
    ]


def _movement_events(events: list[dict]) -> list[dict]:
    return [
        event
        for event in events
        if event["sensor_type"] == "mmwave"
    ]


def _resolve_now(identity_history: list[dict], recent_events: list[dict]) -> datetime:
    timestamps = [
        _coerce_timestamp(event["created_at"])
        for event in identity_history
    ] + [
        _coerce_timestamp(event["timestamp"])
        for event in recent_events
    ]
    if not timestamps:
        return datetime.now(UTC)
    return max(timestamps).astimezone(UTC)


def _coerce_timestamp(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(UTC)
    return datetime.fromisoformat(value).astimezone(UTC)


def _unique_reasoning(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
