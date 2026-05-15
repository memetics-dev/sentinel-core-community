from contextlib import asynccontextmanager
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import app.state as runtime_state
from app.behaviour_engine import build_household_rhythm_profile, list_behavioural_anomalies
from app.db import (
    create_pilot_session_note,
    create_trial_session,
    create_operator_feedback,
    create_incident_note,
    end_trial_session,
    get_current_trial_session,
    get_incident,
    get_incident_model,
    list_escalation_history,
    list_event_history,
    list_identity_history,
    list_incidents,
    list_incident_history,
    list_incident_notes,
    list_narrative_history,
    list_operator_feedback,
    list_pilot_session_notes,
    list_recent_correlated_signals,
    list_response_history,
    list_trial_sessions,
    list_threat_history,
    persist_trial_metric_snapshot,
    setup_db,
    update_incident_status,
)
from app.incident_engine import transition_incident_status
from app.incident_timeline_engine import build_incident_replay, build_incident_timeline
from app.incidents import IncidentNoteCreate, IncidentStatus
from app.event_engine import ingest_sensor_event
from app.health_engine import get_health_report, get_trial_readiness_report
from app.modes import SystemModeState
from app.models import SensorEvent
from app.narrative_engine import list_current_narratives
from app.operations_feed import (
    build_ops_snapshot,
    publish_ops_event,
    sse_event_stream,
)
from app.pilot_notes import (
    PilotSessionNoteCreate,
    build_session_conclusions,
    new_pilot_session_note,
)
from app.presence_engine import build_household_presence_state
from app.response_engine import list_active_response_assessments
from app.state import (
    escalation_state,
    identity_state,
    occupants,
    occupancy_state,
    sensor_events,
    system_mode,
    threat_state,
    trusted_devices,
    zones,
    load_runtime_config,
)
from app.trial_feedback import OperatorFeedback, OperatorFeedbackCreate
from app.trial_metrics import (
    build_evaluation_summary,
    build_trial_export,
    build_trial_metric_snapshot,
)
from app.trial_report import build_trial_report
from app.trial_session import (
    TrialSession,
    TrialSessionEnd,
    TrialSessionStart,
    TrialSessionStatus,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_db()
    load_runtime_config()
    yield


app = FastAPI(
    title="Sentinel Core Edge Core",
    version="0.1.0",
    lifespan=lifespan,
)

LOCAL_DEV_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3004",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:3003",
    "http://127.0.0.1:3004",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=LOCAL_DEV_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def root():
    return {
        "service": "sentinel-core-edge-core",
        "status": "running",
    }


@app.get("/health")
def get_health():
    return get_health_report()


@app.get("/trial/readiness")
def get_trial_readiness():
    route_paths = [route.path for route in app.routes if hasattr(route, "path")]
    return get_trial_readiness_report(route_paths)

@app.post("/events")
def ingest_event(event: SensorEvent):
    return ingest_sensor_event(event, system_mode)

@app.get("/events")
def list_events():
    return {
        "events": sensor_events,
        "total_events": len(sensor_events),
    }


@app.get("/occupancy")
def get_occupancy():
    return {
        "zones": occupancy_state,
        "total_zones": len(occupancy_state),
    }


@app.get("/threats")
def get_threats():
    return {
        "threats": threat_state,
        "total_threats": len(threat_state),
    }

@app.get("/mode")
def get_mode():
    return system_mode


@app.post("/mode")
def set_mode(mode_state: SystemModeState):
    system_mode.mode = mode_state.mode
    system_mode.description = mode_state.description

    return {
        "status": "updated",
        "mode": system_mode,
    }

@app.get("/identity")
def get_identity():
    return {
        "identity": identity_state,
        "total_zones": len(identity_state),
    }

@app.get("/escalations")
def get_escalations():
    return {
        "escalations": escalation_state,
        "total_escalations": len(escalation_state),
    }

@app.get("/zones")
def get_zones():
    return {
        "zones": zones,
        "total_zones": len(zones),
    }


@app.get("/config")
def get_config():
    return runtime_state.household_config


@app.get("/occupants")
def get_occupants():
    return {
        "occupants": occupants,
        "total_occupants": len(occupants),
    }


@app.get("/devices")
def get_devices():
    return {
        "devices": trusted_devices,
        "total_devices": len(trusted_devices),
    }


@app.get("/presence")
def get_presence():
    presence = build_household_presence_state(
        occupants=occupants,
        trusted_devices=trusted_devices,
        identity_history=list_identity_history(),
        recent_events=list_event_history(),
        current_mode=system_mode.mode,
        occupancy_state=occupancy_state,
    )
    return presence


@app.get("/presence/occupants")
def get_presence_occupants():
    presence = build_household_presence_state(
        occupants=occupants,
        trusted_devices=trusted_devices,
        identity_history=list_identity_history(),
        recent_events=list_event_history(),
        current_mode=system_mode.mode,
        occupancy_state=occupancy_state,
    )
    return {
        "occupants": presence.occupants,
        "total_occupants": len(presence.occupants),
    }


@app.get("/correlation/recent")
def get_recent_correlations():
    correlations = list_recent_correlated_signals()
    return {
        "correlations": correlations,
        "total_correlations": len(correlations),
    }


@app.get("/behaviour/baseline")
def get_behaviour_baseline():
    events = list_event_history()
    return build_household_rhythm_profile(events)


@app.get("/behaviour/anomalies")
def get_behaviour_anomalies():
    events = list_event_history()
    anomalies = list_behavioural_anomalies(events, zones)
    return {
        "anomalies": anomalies,
        "total_anomalies": len(anomalies),
    }


@app.get("/ops/snapshot")
def get_ops_snapshot():
    return build_ops_snapshot()


@app.get("/ops/feed")
async def get_ops_feed():
    return StreamingResponse(
        sse_event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/response/active")
def get_active_responses():
    session_id = _get_active_trial_session_id()
    history = list_response_history(session_id=session_id)
    incidents = list_incidents(session_id=session_id)
    responses = list_active_response_assessments(history, incidents)
    return {
        "responses": responses,
        "total_responses": len(responses),
    }


@app.get("/response/history")
def get_response_history():
    responses = list_response_history(session_id=_get_active_trial_session_id())
    return {
        "responses": responses,
        "total_responses": len(responses),
    }


@app.get("/trial/metrics")
def get_trial_metrics():
    metrics = _build_and_persist_trial_metrics(session_id=_get_active_trial_session_id())
    return metrics


@app.get("/trial/evaluation")
def get_trial_evaluation():
    session_id = _get_active_trial_session_id()
    metrics = _build_and_persist_trial_metrics(session_id=session_id)
    feedback = list_operator_feedback(session_id=session_id)
    return build_evaluation_summary(
        metrics=metrics,
        feedback=feedback,
    )


@app.post("/trial/feedback")
def post_trial_feedback(feedback: OperatorFeedbackCreate):
    session_id = _get_active_trial_session_id()
    feedback_record = OperatorFeedback(
        incident_id=feedback.incident_id,
        narrative_id=feedback.narrative_id,
        feedback_type=feedback.feedback_type,
        note=feedback.note,
        created_at=datetime.now(UTC),
    )
    feedback_record.id = create_operator_feedback(feedback_record, session_id=session_id)
    metrics = _build_and_persist_trial_metrics(session_id=session_id)
    publish_ops_event(
        "trial_feedback_recorded",
        {
            "feedback_id": feedback_record.id,
            "incident_id": feedback_record.incident_id,
            "narrative_id": feedback_record.narrative_id,
            "feedback_type": feedback_record.feedback_type.value,
            "note": feedback_record.note,
        },
    )
    return {
        "status": "recorded",
        "feedback": feedback_record,
        "metrics": metrics,
    }


@app.get("/trial/export")
def get_trial_export():
    current_session = get_current_trial_session()
    session_id = current_session.session_id if current_session is not None else None
    incidents = list_incidents(session_id=session_id)
    responses = list_response_history(session_id=session_id)
    narratives = list_narrative_history(session_id=session_id)
    feedback = list_operator_feedback(session_id=session_id)
    pilot_notes = list_pilot_session_notes(session_id)
    session_conclusions = build_session_conclusions(pilot_notes)
    metrics = _build_and_persist_trial_metrics(
        incidents=incidents,
        responses=responses,
        narratives=narratives,
        feedback=feedback,
        session_id=session_id,
    )
    evaluation = build_evaluation_summary(
        metrics=metrics,
        feedback=feedback,
    )
    return build_trial_export(
        incidents=incidents,
        responses=responses,
        narratives=narratives,
        feedback=feedback,
        metrics=metrics,
        evaluation=evaluation,
        session=current_session,
        pilot_notes=pilot_notes,
        session_conclusions=session_conclusions,
    )


@app.get("/trial/report")
def get_trial_report():
    current_session = get_current_trial_session()
    session_id = current_session.session_id if current_session is not None else None
    incidents = list_incidents(session_id=session_id)
    responses = list_response_history(session_id=session_id)
    narratives = list_narrative_history(session_id=session_id)
    feedback = list_operator_feedback(session_id=session_id)
    pilot_notes = list_pilot_session_notes(session_id)
    session_conclusions = build_session_conclusions(pilot_notes)
    metrics = _build_and_persist_trial_metrics(
        incidents=incidents,
        responses=responses,
        narratives=narratives,
        feedback=feedback,
        session_id=session_id,
    )
    evaluation = build_evaluation_summary(
        metrics=metrics,
        feedback=feedback,
    )
    config = runtime_state.household_config
    household_id = config.household_id if config else "unknown_household"
    household_label = config.household_label if config else "Unknown Household"
    return build_trial_report(
        household_id=household_id,
        household_label=household_label,
        incidents=incidents,
        responses=responses,
        narratives=narratives,
        feedback=feedback,
        pilot_notes=pilot_notes,
        session_conclusions=session_conclusions,
        metrics=metrics,
        evaluation=evaluation,
        session=current_session,
    )


@app.get("/narratives/current")
def get_current_narratives():
    session_id = _get_active_trial_session_id()
    history = list_narrative_history(session_id=session_id)
    incidents = list_incidents(session_id=session_id)
    narratives = list_current_narratives(history, incidents)
    return {
        "narratives": narratives,
        "total_narratives": len(narratives),
    }


@app.get("/narratives/history")
def get_narrative_history():
    narratives = list_narrative_history(session_id=_get_active_trial_session_id())
    return {
        "narratives": narratives,
        "total_narratives": len(narratives),
    }


@app.post("/trial/session/start")
def start_trial_session(payload: TrialSessionStart):
    existing_session = get_current_trial_session()
    if existing_session is not None:
        raise HTTPException(
            status_code=409,
            detail="A trial session is already active.",
        )
    session_label = payload.label.strip()
    if not session_label:
        raise HTTPException(status_code=422, detail="Trial session label cannot be empty")

    session = TrialSession(
        session_id=f"trial-session-{uuid4().hex[:12]}",
        label=session_label,
        started_at=datetime.now(UTC),
        ended_at=None,
        status=TrialSessionStatus.ACTIVE,
        notes=payload.notes,
    )
    create_trial_session(session)
    publish_ops_event(
        "trial_session_started",
        {
            "session_id": session.session_id,
            "label": session.label,
            "started_at": session.started_at.isoformat(),
            "notes": session.notes,
        },
    )
    return {
        "status": "started",
        "session": session,
    }


@app.post("/trial/session/end")
def end_current_trial_session(payload: TrialSessionEnd | None = None):
    current_session = get_current_trial_session()
    if current_session is None:
        raise HTTPException(status_code=404, detail="No active trial session found")

    ended_session = end_trial_session(
        session_id=current_session.session_id,
        ended_at=datetime.now(UTC),
        notes=payload.notes if payload is not None else None,
    )
    if ended_session is None:
        raise HTTPException(status_code=404, detail="No active trial session found")

    publish_ops_event(
        "trial_session_ended",
        {
            "session_id": ended_session.session_id,
            "label": ended_session.label,
            "ended_at": ended_session.ended_at.isoformat()
            if ended_session.ended_at is not None
            else None,
            "notes": ended_session.notes,
        },
    )
    return {
        "status": "ended",
        "session": ended_session,
    }


@app.get("/trial/session/current")
def get_current_trial_session_endpoint():
    return {
        "session": get_current_trial_session(),
    }


@app.get("/trial/session/history")
def get_trial_session_history():
    sessions = list_trial_sessions()
    return {
        "sessions": sessions,
        "total_sessions": len(sessions),
    }


@app.post("/trial/session/note")
def post_trial_session_note(payload: PilotSessionNoteCreate):
    current_session = get_current_trial_session()
    if current_session is None:
        raise HTTPException(status_code=404, detail="No active trial session found")

    note = new_pilot_session_note(
        session_id=current_session.session_id,
        note_type=payload.note_type,
        content=payload.content,
    )
    note.id = create_pilot_session_note(note)
    conclusions = build_session_conclusions(
        list_pilot_session_notes(current_session.session_id)
    )
    publish_ops_event(
        "pilot_note_recorded",
        {
            "note_id": note.id,
            "session_id": note.session_id,
            "note_type": note.note_type.value,
            "content": note.content,
            "created_at": note.created_at.isoformat(),
        },
    )
    return {
        "status": "recorded",
        "note": note,
        "session_conclusions": conclusions,
    }


@app.get("/trial/session/notes")
def get_trial_session_notes():
    current_session = get_current_trial_session()
    if current_session is None:
        return {
            "session": None,
            "notes": [],
            "session_conclusions": [],
            "total_notes": 0,
        }

    notes = list_pilot_session_notes(current_session.session_id)
    return {
        "session": current_session,
        "notes": notes,
        "session_conclusions": build_session_conclusions(notes),
        "total_notes": len(notes),
    }


def _build_and_persist_trial_metrics(
    *,
    incidents: list[dict] | None = None,
    responses: list[dict] | None = None,
    narratives: list[dict] | None = None,
    feedback: list[dict] | None = None,
    session_id: str | None = None,
):
    metrics = build_trial_metric_snapshot(
        incidents=incidents if incidents is not None else list_incidents(session_id=session_id),
        responses=responses if responses is not None else list_response_history(session_id=session_id),
        narratives=narratives if narratives is not None else list_narrative_history(session_id=session_id),
        feedback=feedback if feedback is not None else list_operator_feedback(session_id=session_id),
    )
    metrics.id = persist_trial_metric_snapshot(metrics, session_id=session_id)
    return metrics


def _get_active_trial_session_id() -> str | None:
    current_session = get_current_trial_session()
    if current_session is None:
        return None
    return current_session.session_id


@app.get("/history/events")
def get_event_history():
    events = list_event_history()
    return {
        "events": events,
        "total_events": len(events),
    }


@app.get("/history/identity")
def get_identity_history():
    identity = list_identity_history()
    return {
        "identity": identity,
        "total_identity": len(identity),
    }


@app.get("/history/threats")
def get_threat_history():
    threats = list_threat_history()
    return {
        "threats": threats,
        "total_threats": len(threats),
    }


@app.get("/history/escalations")
def get_escalation_history():
    escalations = list_escalation_history()
    return {
        "escalations": escalations,
        "total_escalations": len(escalations),
    }


@app.get("/history/incidents")
def get_incident_history():
    incidents = list_incident_history()
    return {
        "incidents": incidents,
        "total_incidents": len(incidents),
    }


@app.get("/incidents")
def get_incidents():
    incidents = list_incidents()
    return {
        "incidents": incidents,
        "total_incidents": len(incidents),
    }


@app.get("/incidents/open")
def get_open_incidents():
    incidents = list_incidents(
        statuses={IncidentStatus.OPEN, IncidentStatus.MONITORING}
    )
    return {
        "incidents": incidents,
        "total_incidents": len(incidents),
    }


@app.get("/incidents/{incident_id}")
def get_incident_by_id(incident_id: str):
    incident = get_incident(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


@app.get("/incidents/{incident_id}/timeline")
def get_incident_timeline(incident_id: str):
    timeline = build_incident_timeline(incident_id)
    if timeline is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "incident_id": incident_id,
        "timeline": timeline,
        "total_entries": len(timeline),
    }


@app.get("/incidents/{incident_id}/replay")
def get_incident_replay(incident_id: str):
    replay = build_incident_replay(incident_id)
    if replay is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return replay


@app.post("/incidents/{incident_id}/monitor")
def monitor_incident(incident_id: str):
    return transition_incident_response(
        incident_id=incident_id,
        target_status=IncidentStatus.MONITORING,
    )


@app.post("/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: str):
    return transition_incident_response(
        incident_id=incident_id,
        target_status=IncidentStatus.RESOLVED,
    )


@app.post("/incidents/{incident_id}/dismiss")
def dismiss_incident(incident_id: str):
    return transition_incident_response(
        incident_id=incident_id,
        target_status=IncidentStatus.DISMISSED,
    )


@app.post("/incidents/{incident_id}/notes")
def add_incident_note(incident_id: str, payload: IncidentNoteCreate):
    incident = require_incident(incident_id)
    note = create_incident_note(incident.incident_id, payload.note)
    updated_incident = require_incident(incident_id)
    publish_ops_event(
        "incident_note_added",
        {
            "incident_id": incident.incident_id,
            "note_id": note["id"],
            "note": note["note"],
            "created_at": note["created_at"],
        },
    )
    return {
        "status": "created",
        "incident": updated_incident,
        "note": note,
    }


@app.get("/incidents/{incident_id}/notes")
def get_incident_notes(incident_id: str):
    incident = require_incident(incident_id)
    notes = list_incident_notes(incident.incident_id)
    return {
        "incident_id": incident.incident_id,
        "notes": notes,
        "total_notes": len(notes),
    }


def transition_incident_response(
    incident_id: str,
    target_status: IncidentStatus,
):
    incident = require_incident(incident_id)
    updated_incident = transition_incident_status(incident, target_status)
    if updated_incident is None:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot transition incident from {incident.status.value} "
                f"to {target_status.value}"
            ),
        )

    update_incident_status(
        incident_id=updated_incident.incident_id,
        status=updated_incident.status,
        updated_at=updated_incident.updated_at,
    )
    publish_ops_event(
        "incident_status_changed",
        {
            "incident_id": updated_incident.incident_id,
            "status": updated_incident.status.value,
            "updated_at": updated_incident.updated_at.isoformat(),
        },
    )
    return {
        "status": "updated",
        "incident": require_incident(incident_id),
    }


def require_incident(incident_id: str):
    incident = get_incident_model(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident
