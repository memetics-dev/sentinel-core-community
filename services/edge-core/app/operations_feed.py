import json
import queue
from collections import deque
from datetime import UTC, datetime
from typing import AsyncIterator

import anyio

from app.db import (
    get_current_trial_session,
    list_incidents,
    list_narrative_history,
    list_operator_feedback,
    list_response_history,
)
from app.narrative_engine import list_current_narratives
from app.presence_engine import build_household_presence_state
from app.incidents import IncidentStatus
from app.trial_metrics import build_trial_metric_snapshot
from app.state import (
    escalation_state,
    identity_state,
    occupancy_state,
    occupants,
    sensor_events,
    system_mode,
    threat_state,
    trusted_devices,
)

FEED_BUFFER_SIZE = 200
SSE_WAIT_TIMEOUT_SECONDS = 15

_recent_events: deque[dict] = deque(maxlen=FEED_BUFFER_SIZE)
_subscribers: list[queue.Queue] = []


def publish_ops_event(event_type: str, payload: dict) -> dict:
    event = {
        "event_type": event_type,
        "timestamp": datetime.now(UTC).isoformat(),
        "payload": payload,
    }
    _recent_events.append(event)
    stale_subscribers: list[queue.Queue] = []
    for subscriber in _subscribers:
        try:
            subscriber.put_nowait(event)
        except queue.Full:
            stale_subscribers.append(subscriber)

    for subscriber in stale_subscribers:
        unsubscribe(subscriber)

    return event


def subscribe() -> queue.Queue:
    subscriber: queue.Queue = queue.Queue(maxsize=FEED_BUFFER_SIZE)
    _subscribers.append(subscriber)
    return subscriber


def unsubscribe(subscriber: queue.Queue) -> None:
    if subscriber in _subscribers:
        _subscribers.remove(subscriber)


def list_recent_ops_events(limit: int | None = None) -> list[dict]:
    events = list(_recent_events)
    if limit is None:
        return events
    return events[-limit:]


def build_ops_snapshot() -> dict:
    current_session = get_current_trial_session()
    session_id = current_session.session_id if current_session is not None else None
    open_incidents = list_incidents(
        statuses={IncidentStatus.OPEN, IncidentStatus.MONITORING},
        session_id=session_id,
    )
    narrative_history = list_narrative_history(session_id=session_id)
    identity_history = []
    for zone_id, identity in identity_state.items():
        identity_history.append(
            {
                "zone_id": zone_id,
                "occupant_id": identity.occupant_id,
                "known_occupant": identity.known_occupant,
                "created_at": occupancy_state[zone_id].last_updated
                if zone_id in occupancy_state
                else datetime.now(UTC),
            }
        )
    event_history = [
        {
            "sensor_id": event.sensor_id,
            "sensor_type": event.sensor_type.value,
            "zone_id": event.zone_id,
            "value": event.value,
            "confidence": event.confidence,
            "timestamp": event.timestamp,
        }
        for event in sensor_events
    ]
    presence = build_household_presence_state(
        occupants=occupants,
        trusted_devices=trusted_devices,
        identity_history=identity_history,
        recent_events=event_history,
        current_mode=system_mode.mode,
        occupancy_state=occupancy_state,
    )
    current_narratives = list_current_narratives(narrative_history, open_incidents)
    trial_metrics = build_trial_metric_snapshot(
        incidents=list_incidents(session_id=session_id),
        responses=list_response_history(session_id=session_id),
        narratives=narrative_history,
        feedback=list_operator_feedback(session_id=session_id),
    )
    return {
        "mode": system_mode,
        "current_session": current_session,
        "presence": presence,
        "threats": threat_state,
        "total_threats": len(threat_state),
        "escalations": escalation_state,
        "total_escalations": len(escalation_state),
        "open_incidents": open_incidents,
        "total_open_incidents": len(open_incidents),
        "current_narratives": current_narratives,
        "total_current_narratives": len(current_narratives),
        "trial_metrics": trial_metrics,
        "recent_events_count": len(sensor_events),
    }


def reset_ops_feed() -> None:
    _recent_events.clear()
    _subscribers.clear()


async def sse_event_stream() -> AsyncIterator[str]:
    subscriber = subscribe()
    try:
        while True:
            try:
                event = await anyio.to_thread.run_sync(
                    subscriber.get,
                    True,
                    SSE_WAIT_TIMEOUT_SECONDS,
                )
                yield format_sse_event(event)
            except queue.Empty:
                yield ": keepalive\n\n"
    finally:
        unsubscribe(subscriber)


def format_sse_event(event: dict) -> str:
    return (
        f"event: {event['event_type']}\n"
        f"data: {json.dumps(event)}\n\n"
    )
