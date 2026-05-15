import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app.escalation import EscalationState
from app.identity import IdentityState
from app.incidents import Incident, IncidentStatus
from app.models import CorrelatedSignal, SensorEvent
from app.narrative import OperationalNarrative
from app.response import ResponseAssessment
from app.threats import ThreatState
from app.pilot_notes import PilotSessionNote
from app.trial_feedback import OperatorFeedback
from app.trial_metrics import TrialMetricSnapshot
from app.trial_session import TrialSession, TrialSessionStatus

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DB_PATH = DATA_DIR / "sentinel_core.db"

SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS sensor_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_id TEXT NOT NULL,
        sensor_type TEXT NOT NULL,
        zone_id TEXT NOT NULL,
        value TEXT NOT NULL,
        confidence INTEGER NOT NULL,
        timestamp TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS identity_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        zone_id TEXT NOT NULL,
        occupant_id TEXT,
        identity_confidence INTEGER NOT NULL,
        known_occupant INTEGER NOT NULL,
        reasoning_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(event_id) REFERENCES sensor_events(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS threat_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        zone_id TEXT NOT NULL,
        threat_score INTEGER NOT NULL,
        classification TEXT NOT NULL,
        reasoning_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(event_id) REFERENCES sensor_events(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS escalation_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        zone_id TEXT NOT NULL,
        stage TEXT NOT NULL,
        recommended_action TEXT NOT NULL,
        reasoning_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(event_id) REFERENCES sensor_events(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS incidents (
        incident_id TEXT PRIMARY KEY,
        session_id TEXT,
        zone_id TEXT NOT NULL,
        severity TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        related_event_count INTEGER NOT NULL,
        related_escalation_count INTEGER NOT NULL,
        reasoning_summary TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS incident_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id TEXT NOT NULL,
        note TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(incident_id) REFERENCES incidents(incident_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS incident_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(incident_id) REFERENCES incidents(incident_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS correlated_signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        incident_id TEXT,
        zone_id TEXT NOT NULL,
        pattern_type TEXT NOT NULL,
        modifier INTEGER NOT NULL,
        reasoning TEXT NOT NULL,
        contributing_event_ids_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(event_id) REFERENCES sensor_events(id),
        FOREIGN KEY(incident_id) REFERENCES incidents(incident_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS response_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        incident_id TEXT,
        session_id TEXT,
        zone_id TEXT NOT NULL,
        response_confidence INTEGER NOT NULL,
        urgency TEXT NOT NULL,
        response_state TEXT NOT NULL,
        occupant_safety_state TEXT NOT NULL,
        operator_recommendation TEXT NOT NULL,
        reasoning_json TEXT NOT NULL,
        cooldown_applied INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(event_id) REFERENCES sensor_events(id),
        FOREIGN KEY(incident_id) REFERENCES incidents(incident_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS operational_narratives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER,
        incident_id TEXT,
        session_id TEXT,
        zone_id TEXT,
        summary TEXT NOT NULL,
        household_interpretation TEXT NOT NULL,
        progression_summary TEXT NOT NULL,
        confidence TEXT NOT NULL,
        reasoning_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(event_id) REFERENCES sensor_events(id),
        FOREIGN KEY(incident_id) REFERENCES incidents(incident_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS operator_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id TEXT,
        narrative_id INTEGER,
        session_id TEXT,
        feedback_type TEXT NOT NULL,
        note TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(incident_id) REFERENCES incidents(incident_id),
        FOREIGN KEY(narrative_id) REFERENCES operational_narratives(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS trial_metric_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        total_incidents INTEGER NOT NULL,
        critical_incidents INTEGER NOT NULL,
        suppressed_incidents INTEGER NOT NULL,
        response_escalations INTEGER NOT NULL,
        narrative_generations INTEGER NOT NULL,
        trusted_presence_suppressions INTEGER NOT NULL,
        active_response_recommendations INTEGER NOT NULL,
        false_positive_candidate_count INTEGER NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS trial_sessions (
        session_id TEXT PRIMARY KEY,
        label TEXT NOT NULL,
        started_at TEXT NOT NULL,
        ended_at TEXT,
        status TEXT NOT NULL,
        notes TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS pilot_session_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        note_type TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(session_id) REFERENCES trial_sessions(session_id)
    )
    """,
)

SESSION_COLUMN_MIGRATIONS = {
    "incidents": ("session_id", "TEXT"),
    "response_assessments": ("session_id", "TEXT"),
    "operational_narratives": ("session_id", "TEXT"),
    "operator_feedback": ("session_id", "TEXT"),
    "trial_metric_snapshots": ("session_id", "TEXT"),
}


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def setup_db() -> None:
    with get_connection() as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)
        for table_name, (column_name, column_type) in SESSION_COLUMN_MIGRATIONS.items():
            _ensure_column(connection, table_name, column_name, column_type)


def _ensure_column(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_type: str,
) -> None:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    existing_columns = {row["name"] for row in rows}
    if column_name in existing_columns:
        return
    connection.execute(
        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
    )


def create_trial_session(session: TrialSession) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO trial_sessions (
                session_id,
                label,
                started_at,
                ended_at,
                status,
                notes
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session.session_id,
                session.label,
                session.started_at.isoformat(),
                session.ended_at.isoformat() if session.ended_at else None,
                session.status.value,
                session.notes,
            ),
        )


def get_current_trial_session() -> TrialSession | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                session_id,
                label,
                started_at,
                ended_at,
                status,
                notes
            FROM trial_sessions
            WHERE status = ?
            ORDER BY started_at DESC
            LIMIT 1
            """,
            (TrialSessionStatus.ACTIVE.value,),
        ).fetchone()
    if row is None:
        return None
    return _row_to_trial_session(dict(row))


def end_trial_session(session_id: str, ended_at: datetime, notes: str | None) -> TrialSession | None:
    existing = get_trial_session(session_id)
    if existing is None:
        return None
    merged_notes = notes if notes is not None else existing.notes
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE trial_sessions
            SET ended_at = ?, status = ?, notes = ?
            WHERE session_id = ?
            """,
            (
                ended_at.isoformat(),
                TrialSessionStatus.ENDED.value,
                merged_notes,
                session_id,
            ),
        )
    return get_trial_session(session_id)


def get_trial_session(session_id: str) -> TrialSession | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                session_id,
                label,
                started_at,
                ended_at,
                status,
                notes
            FROM trial_sessions
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()
    if row is None:
        return None
    return _row_to_trial_session(dict(row))


def list_trial_sessions() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                session_id,
                label,
                started_at,
                ended_at,
                status,
                notes
            FROM trial_sessions
            ORDER BY started_at DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def _row_to_trial_session(row: dict) -> TrialSession:
    return TrialSession(
        session_id=row["session_id"],
        label=row["label"],
        started_at=datetime.fromisoformat(row["started_at"]),
        ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
        status=TrialSessionStatus(row["status"]),
        notes=row["notes"],
    )


def persist_sensor_event(event: SensorEvent) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO sensor_events (
                sensor_id,
                sensor_type,
                zone_id,
                value,
                confidence,
                timestamp
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event.sensor_id,
                event.sensor_type.value,
                event.zone_id,
                event.value,
                event.confidence,
                event.timestamp.isoformat(),
            ),
        )
        return int(cursor.lastrowid)


def persist_identity_evaluation(
    event_id: int,
    zone_id: str,
    identity: IdentityState,
    created_at: str,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO identity_evaluations (
                event_id,
                zone_id,
                occupant_id,
                identity_confidence,
                known_occupant,
                reasoning_json,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                zone_id,
                identity.occupant_id,
                identity.identity_confidence,
                int(identity.known_occupant),
                json.dumps(identity.reasoning),
                created_at,
            ),
        )


def persist_threat_evaluation(
    event_id: int,
    threat: ThreatState,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO threat_evaluations (
                event_id,
                zone_id,
                threat_score,
                classification,
                reasoning_json,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                threat.zone_id,
                threat.threat_score,
                threat.classification.value,
                json.dumps(threat.reasoning),
                threat.last_updated.isoformat(),
            ),
        )


def persist_escalation_evaluation(
    event_id: int,
    escalation: EscalationState,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO escalation_evaluations (
                event_id,
                zone_id,
                stage,
                recommended_action,
                reasoning_json,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                escalation.zone_id,
                escalation.stage.value,
                escalation.recommended_action,
                json.dumps(escalation.reasoning),
                escalation.last_updated.isoformat(),
            ),
        )


def upsert_incident(incident: Incident, session_id: str | None = None) -> None:
    existing = get_incident(incident.incident_id)
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO incidents (
                incident_id,
                session_id,
                zone_id,
                severity,
                status,
                created_at,
                updated_at,
                related_event_count,
                related_escalation_count,
                reasoning_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(incident_id) DO UPDATE SET
                session_id = excluded.session_id,
                severity = excluded.severity,
                status = excluded.status,
                updated_at = excluded.updated_at,
                related_event_count = excluded.related_event_count,
                related_escalation_count = excluded.related_escalation_count,
                reasoning_summary = excluded.reasoning_summary
            """,
            (
                incident.incident_id,
                session_id,
                incident.zone_id,
                incident.severity.value,
                incident.status.value,
                incident.created_at.isoformat(),
                incident.updated_at.isoformat(),
                incident.related_event_count,
                incident.related_escalation_count,
                incident.reasoning_summary,
            ),
        )
        if existing is None:
            connection.execute(
                """
                INSERT INTO incident_status_history (
                    incident_id,
                    status,
                    created_at
                ) VALUES (?, ?, ?)
                """,
                (
                    incident.incident_id,
                    incident.status.value,
                    incident.created_at.isoformat(),
                ),
            )
        elif existing["status"] != incident.status.value:
            connection.execute(
                """
                INSERT INTO incident_status_history (
                    incident_id,
                    status,
                    created_at
                ) VALUES (?, ?, ?)
                """,
                (
                    incident.incident_id,
                    incident.status.value,
                    incident.updated_at.isoformat(),
                ),
            )


def update_incident_status(
    incident_id: str,
    status: IncidentStatus,
    updated_at: datetime,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE incidents
            SET status = ?, updated_at = ?
            WHERE incident_id = ?
            """,
            (
                status.value,
                updated_at.isoformat(),
                incident_id,
            ),
        )
        connection.execute(
            """
            INSERT INTO incident_status_history (
                incident_id,
                status,
                created_at
            ) VALUES (?, ?, ?)
            """,
            (
                incident_id,
                status.value,
                updated_at.isoformat(),
            ),
        )


def create_incident_note(
    incident_id: str,
    note: str,
) -> dict:
    created_at = datetime.now(UTC)
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO incident_notes (
                incident_id,
                note,
                created_at
            ) VALUES (?, ?, ?)
            """,
            (
                incident_id,
                note,
                created_at.isoformat(),
            ),
        )
        connection.execute(
            """
            UPDATE incidents
            SET updated_at = ?
            WHERE incident_id = ?
            """,
            (
                created_at.isoformat(),
                incident_id,
            ),
        )

    return {
        "id": int(cursor.lastrowid),
        "incident_id": incident_id,
        "note": note,
        "created_at": created_at.isoformat(),
    }


def persist_correlated_signal(
    event_id: int,
    incident_id: str | None,
    signal: CorrelatedSignal,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO correlated_signals (
                event_id,
                incident_id,
                zone_id,
                pattern_type,
                modifier,
                reasoning,
                contributing_event_ids_json,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                incident_id,
                signal.zone_id,
                signal.pattern_type,
                signal.modifier,
                signal.reasoning,
                json.dumps(signal.contributing_event_ids),
                signal.created_at.isoformat(),
            ),
        )


def persist_response_assessment(response: ResponseAssessment, session_id: str | None = None) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO response_assessments (
                event_id,
                incident_id,
                session_id,
                zone_id,
                response_confidence,
                urgency,
                response_state,
                occupant_safety_state,
                operator_recommendation,
                reasoning_json,
                cooldown_applied,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                response.event_id,
                response.incident_id,
                session_id,
                response.zone_id,
                response.response_confidence,
                response.urgency.value,
                response.response_state.value,
                response.occupant_safety_state.value,
                response.operator_recommendation,
                json.dumps(response.reasoning),
                int(response.cooldown_applied),
                response.created_at.isoformat(),
            ),
        )

    return int(cursor.lastrowid)


def persist_operational_narrative(
    narrative: OperationalNarrative,
    session_id: str | None = None,
) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO operational_narratives (
                event_id,
                incident_id,
                session_id,
                zone_id,
                summary,
                household_interpretation,
                progression_summary,
                confidence,
                reasoning_json,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                narrative.event_id,
                narrative.incident_id,
                session_id,
                narrative.zone_id,
                narrative.summary,
                narrative.household_interpretation,
                narrative.progression_summary,
                narrative.confidence.value,
                json.dumps(narrative.reasoning),
                narrative.created_at.isoformat(),
            ),
        )

    return int(cursor.lastrowid)


def create_operator_feedback(feedback: OperatorFeedback, session_id: str | None = None) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO operator_feedback (
                incident_id,
                narrative_id,
                session_id,
                feedback_type,
                note,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                feedback.incident_id,
                feedback.narrative_id,
                session_id,
                feedback.feedback_type.value,
                feedback.note,
                feedback.created_at.isoformat(),
            ),
        )

    return int(cursor.lastrowid)


def create_pilot_session_note(note: PilotSessionNote) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO pilot_session_notes (
                session_id,
                note_type,
                content,
                created_at
            ) VALUES (?, ?, ?, ?)
            """,
            (
                note.session_id,
                note.note_type.value,
                note.content,
                note.created_at.isoformat(),
            ),
        )

    return int(cursor.lastrowid)


def persist_trial_metric_snapshot(
    snapshot: TrialMetricSnapshot,
    session_id: str | None = None,
) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO trial_metric_snapshots (
                session_id,
                total_incidents,
                critical_incidents,
                suppressed_incidents,
                response_escalations,
                narrative_generations,
                trusted_presence_suppressions,
                active_response_recommendations,
                false_positive_candidate_count,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                snapshot.total_incidents,
                snapshot.critical_incidents,
                snapshot.suppressed_incidents,
                snapshot.response_escalations,
                snapshot.narrative_generations,
                snapshot.trusted_presence_suppressions,
                snapshot.active_response_recommendations,
                snapshot.false_positive_candidate_count,
                snapshot.created_at.isoformat(),
            ),
        )

    return int(cursor.lastrowid)


def list_incident_notes(incident_id: str) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                incident_id,
                note,
                created_at
            FROM incident_notes
            WHERE incident_id = ?
            ORDER BY id ASC
            """,
            (incident_id,),
        ).fetchall()

    return [dict(row) for row in rows]


def list_incident_status_history(incident_id: str) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                incident_id,
                status,
                created_at
            FROM incident_status_history
            WHERE incident_id = ?
            ORDER BY id ASC
            """,
            (incident_id,),
        ).fetchall()

    return [dict(row) for row in rows]


def list_recent_correlated_signals(limit: int = 20) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                event_id,
                incident_id,
                zone_id,
                pattern_type,
                modifier,
                reasoning,
                contributing_event_ids_json,
                created_at
            FROM correlated_signals
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [_decode_contributing_events(dict(row)) for row in rows]


def list_response_history(session_id: str | None = None) -> list[dict]:
    with get_connection() as connection:
        if session_id is None:
            rows = connection.execute(
                """
                SELECT
                    id,
                    event_id,
                    incident_id,
                    session_id,
                    zone_id,
                    response_confidence,
                    urgency,
                    response_state,
                    occupant_safety_state,
                    operator_recommendation,
                    reasoning_json,
                    cooldown_applied,
                    created_at
                FROM response_assessments
                ORDER BY id ASC
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT
                    id,
                    event_id,
                    incident_id,
                    session_id,
                    zone_id,
                    response_confidence,
                    urgency,
                    response_state,
                    occupant_safety_state,
                    operator_recommendation,
                    reasoning_json,
                    cooldown_applied,
                    created_at
                FROM response_assessments
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()

    history = [_decode_reasoning_row(dict(row)) for row in rows]
    for record in history:
        record["cooldown_applied"] = bool(record["cooldown_applied"])
    return history


def list_narrative_history(session_id: str | None = None) -> list[dict]:
    with get_connection() as connection:
        if session_id is None:
            rows = connection.execute(
                """
                SELECT
                    id,
                    event_id,
                    incident_id,
                    session_id,
                    zone_id,
                    summary,
                    household_interpretation,
                    progression_summary,
                    confidence,
                    reasoning_json,
                    created_at
                FROM operational_narratives
                ORDER BY id ASC
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT
                    id,
                    event_id,
                    incident_id,
                    session_id,
                    zone_id,
                    summary,
                    household_interpretation,
                    progression_summary,
                    confidence,
                    reasoning_json,
                    created_at
                FROM operational_narratives
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()

    return [_decode_reasoning_row(dict(row)) for row in rows]


def list_operator_feedback(session_id: str | None = None) -> list[dict]:
    with get_connection() as connection:
        if session_id is None:
            rows = connection.execute(
                """
                SELECT
                    id,
                    incident_id,
                    narrative_id,
                    session_id,
                    feedback_type,
                    note,
                    created_at
                FROM operator_feedback
                ORDER BY id ASC
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT
                    id,
                    incident_id,
                    narrative_id,
                    session_id,
                    feedback_type,
                    note,
                    created_at
                FROM operator_feedback
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()

    return [dict(row) for row in rows]


def list_pilot_session_notes(session_id: str | None) -> list[dict]:
    if session_id is None:
        return []

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                session_id,
                note_type,
                content,
                created_at
            FROM pilot_session_notes
            WHERE session_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (session_id,),
        ).fetchall()

    return [dict(row) for row in rows]


def list_trial_metric_snapshots(session_id: str | None = None) -> list[dict]:
    with get_connection() as connection:
        if session_id is None:
            rows = connection.execute(
                """
                SELECT
                    id,
                    session_id,
                    total_incidents,
                    critical_incidents,
                    suppressed_incidents,
                    response_escalations,
                    narrative_generations,
                    trusted_presence_suppressions,
                    active_response_recommendations,
                    false_positive_candidate_count,
                    created_at
                FROM trial_metric_snapshots
                ORDER BY id ASC
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT
                    id,
                    session_id,
                    total_incidents,
                    critical_incidents,
                    suppressed_incidents,
                    response_escalations,
                    narrative_generations,
                    trusted_presence_suppressions,
                    active_response_recommendations,
                    false_positive_candidate_count,
                    created_at
                FROM trial_metric_snapshots
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()

    return [dict(row) for row in rows]


def list_event_history() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                sensor_id,
                sensor_type,
                zone_id,
                value,
                confidence,
                timestamp
            FROM sensor_events
            ORDER BY id ASC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def list_identity_history() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                event_id,
                zone_id,
                occupant_id,
                identity_confidence,
                known_occupant,
                reasoning_json,
                created_at
            FROM identity_evaluations
            ORDER BY id ASC
            """
        ).fetchall()

    history = []
    for row in rows:
        record = _decode_reasoning_row(dict(row))
        record["known_occupant"] = bool(record["known_occupant"])
        history.append(record)

    return history


def list_threat_history() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                event_id,
                zone_id,
                threat_score,
                classification,
                reasoning_json,
                created_at
            FROM threat_evaluations
            ORDER BY id ASC
            """
        ).fetchall()

    return [_decode_reasoning_row(dict(row)) for row in rows]


def list_escalation_history() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                event_id,
                zone_id,
                stage,
                recommended_action,
                reasoning_json,
                created_at
            FROM escalation_evaluations
            ORDER BY id ASC
            """
        ).fetchall()

    return [_decode_reasoning_row(dict(row)) for row in rows]


def list_incident_history() -> list[dict]:
    return list_incidents()


def list_incidents(
    statuses: set[IncidentStatus] | None = None,
    session_id: str | None = None,
) -> list[dict]:
    query = """
        SELECT
            incident_id,
            session_id,
            zone_id,
            severity,
            status,
            created_at,
            updated_at,
            related_event_count,
            related_escalation_count,
            reasoning_summary
        FROM incidents
    """
    parameters: list[str] = []
    conditions: list[str] = []
    if session_id is not None:
        conditions.append("session_id = ?")
        parameters.append(session_id)
    if statuses:
        placeholders = ", ".join("?" for _ in statuses)
        conditions.append(f"status IN ({placeholders})")
        parameters.extend(status.value for status in statuses)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY updated_at DESC, incident_id DESC"

    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()

    return [dict(row) for row in rows]


def get_incident(incident_id: str) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                incident_id,
                session_id,
                zone_id,
                severity,
                status,
                created_at,
                updated_at,
                related_event_count,
                related_escalation_count,
                reasoning_summary
            FROM incidents
            WHERE incident_id = ?
            """,
            (incident_id,),
        ).fetchone()

    if row is None:
        return None

    return dict(row)


def get_incident_model(incident_id: str) -> Incident | None:
    incident = get_incident(incident_id)
    if incident is None:
        return None

    return Incident(
        incident_id=incident["incident_id"],
        zone_id=incident["zone_id"],
        severity=incident["severity"],
        status=incident["status"],
        created_at=datetime.fromisoformat(incident["created_at"]),
        updated_at=datetime.fromisoformat(incident["updated_at"]),
        related_event_count=incident["related_event_count"],
        related_escalation_count=incident["related_escalation_count"],
        reasoning_summary=incident["reasoning_summary"],
    )


def get_recent_active_incident(
    zone_id: str,
    window_start: datetime,
    session_id: str | None = None,
) -> Incident | None:
    with get_connection() as connection:
        if session_id is None:
            row = connection.execute(
                """
                SELECT
                    incident_id,
                    session_id,
                    zone_id,
                    severity,
                    status,
                    created_at,
                    updated_at,
                    related_event_count,
                    related_escalation_count,
                    reasoning_summary
                FROM incidents
                WHERE zone_id = ?
                  AND status IN (?, ?)
                  AND updated_at >= ?
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (
                    zone_id,
                    IncidentStatus.OPEN.value,
                    IncidentStatus.MONITORING.value,
                    window_start.isoformat(),
                ),
            ).fetchone()
        else:
            row = connection.execute(
                """
                SELECT
                    incident_id,
                    session_id,
                    zone_id,
                    severity,
                    status,
                    created_at,
                    updated_at,
                    related_event_count,
                    related_escalation_count,
                    reasoning_summary
                FROM incidents
                WHERE zone_id = ?
                  AND session_id = ?
                  AND status IN (?, ?)
                  AND updated_at >= ?
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (
                    zone_id,
                    session_id,
                    IncidentStatus.OPEN.value,
                    IncidentStatus.MONITORING.value,
                    window_start.isoformat(),
                ),
            ).fetchone()

    if row is None:
        return None

    return _row_to_incident(row)


def list_incident_correlated_signals(incident_id: str) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                event_id,
                incident_id,
                zone_id,
                pattern_type,
                modifier,
                reasoning,
                contributing_event_ids_json,
                created_at
            FROM correlated_signals
            WHERE incident_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (incident_id,),
        ).fetchall()

    return [_decode_contributing_events(dict(row)) for row in rows]


def list_incident_response_assessments(incident_id: str) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                event_id,
                incident_id,
                zone_id,
                response_confidence,
                urgency,
                response_state,
                occupant_safety_state,
                operator_recommendation,
                reasoning_json,
                cooldown_applied,
                created_at
            FROM response_assessments
            WHERE incident_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (incident_id,),
        ).fetchall()

    responses = [_decode_reasoning_row(dict(row)) for row in rows]
    for record in responses:
        record["cooldown_applied"] = bool(record["cooldown_applied"])
    return responses


def list_incident_narratives(incident_id: str) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                event_id,
                incident_id,
                zone_id,
                summary,
                household_interpretation,
                progression_summary,
                confidence,
                reasoning_json,
                created_at
            FROM operational_narratives
            WHERE incident_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (incident_id,),
        ).fetchall()

    return [_decode_reasoning_row(dict(row)) for row in rows]


def list_incident_related_activity(
    zone_id: str,
    window_start: datetime,
    window_end: datetime,
) -> dict[str, list[dict]]:
    query_params = (
        zone_id,
        window_start.isoformat(),
        window_end.isoformat(),
    )
    with get_connection() as connection:
        events = connection.execute(
            """
            SELECT
                id,
                sensor_id,
                sensor_type,
                zone_id,
                value,
                confidence,
                timestamp
            FROM sensor_events
            WHERE zone_id = ?
              AND timestamp >= ?
              AND timestamp <= ?
            ORDER BY timestamp ASC, id ASC
            """,
            query_params,
        ).fetchall()

        identity = connection.execute(
            """
            SELECT
                identity_evaluations.id,
                identity_evaluations.event_id,
                identity_evaluations.zone_id,
                identity_evaluations.occupant_id,
                identity_evaluations.identity_confidence,
                identity_evaluations.known_occupant,
                identity_evaluations.reasoning_json,
                identity_evaluations.created_at
            FROM identity_evaluations
            WHERE zone_id = ?
              AND created_at >= ?
              AND created_at <= ?
            ORDER BY created_at ASC, id ASC
            """,
            query_params,
        ).fetchall()

        threats = connection.execute(
            """
            SELECT
                id,
                event_id,
                zone_id,
                threat_score,
                classification,
                reasoning_json,
                created_at
            FROM threat_evaluations
            WHERE zone_id = ?
              AND created_at >= ?
              AND created_at <= ?
            ORDER BY created_at ASC, id ASC
            """,
            query_params,
        ).fetchall()

        escalations = connection.execute(
            """
            SELECT
                id,
                event_id,
                zone_id,
                stage,
                recommended_action,
                reasoning_json,
                created_at
            FROM escalation_evaluations
            WHERE zone_id = ?
              AND created_at >= ?
              AND created_at <= ?
            ORDER BY created_at ASC, id ASC
            """,
            query_params,
        ).fetchall()

        responses = connection.execute(
            """
            SELECT
                id,
                event_id,
                incident_id,
                zone_id,
                response_confidence,
                urgency,
                response_state,
                occupant_safety_state,
                operator_recommendation,
                reasoning_json,
                cooldown_applied,
                created_at
            FROM response_assessments
            WHERE zone_id = ?
              AND created_at >= ?
              AND created_at <= ?
            ORDER BY created_at ASC, id ASC
            """,
            query_params,
        ).fetchall()

    identity_rows = []
    for row in identity:
        record = _decode_reasoning_row(dict(row))
        record["known_occupant"] = bool(record["known_occupant"])
        identity_rows.append(record)

    return {
        "events": [dict(row) for row in events],
        "identity": identity_rows,
        "threats": [_decode_reasoning_row(dict(row)) for row in threats],
        "escalations": [_decode_reasoning_row(dict(row)) for row in escalations],
        "responses": [
            {
                **record,
                "cooldown_applied": bool(record["cooldown_applied"]),
            }
            for record in [_decode_reasoning_row(dict(row)) for row in responses]
        ],
    }


def reset_db() -> None:
    setup_db()
    with get_connection() as connection:
        connection.executescript(
            """
            DELETE FROM escalation_evaluations;
            DELETE FROM threat_evaluations;
            DELETE FROM identity_evaluations;
            DELETE FROM sensor_events;
            DELETE FROM incidents;
            DELETE FROM incident_notes;
            DELETE FROM incident_status_history;
            DELETE FROM correlated_signals;
            DELETE FROM response_assessments;
            DELETE FROM operational_narratives;
            DELETE FROM operator_feedback;
            DELETE FROM trial_metric_snapshots;
            DELETE FROM pilot_session_notes;
            DELETE FROM trial_sessions;
            DELETE FROM sqlite_sequence
            WHERE name IN (
                'sensor_events',
                'identity_evaluations',
                'threat_evaluations',
                'escalation_evaluations',
                'incident_notes',
                'incident_status_history',
                'correlated_signals',
                'response_assessments',
                'operational_narratives',
                'operator_feedback',
                'trial_metric_snapshots',
                'pilot_session_notes',
                'trial_sessions'
            );
            """
        )


def _decode_reasoning_row(row: dict) -> dict:
    row["reasoning"] = json.loads(row.pop("reasoning_json"))
    return row


def _decode_contributing_events(row: dict) -> dict:
    row["contributing_event_ids"] = json.loads(row.pop("contributing_event_ids_json"))
    return row


def _row_to_incident(row: sqlite3.Row | dict) -> Incident:
    return Incident(
        incident_id=row["incident_id"],
        zone_id=row["zone_id"],
        severity=row["severity"],
        status=row["status"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
        related_event_count=row["related_event_count"],
        related_escalation_count=row["related_escalation_count"],
        reasoning_summary=row["reasoning_summary"],
    )
