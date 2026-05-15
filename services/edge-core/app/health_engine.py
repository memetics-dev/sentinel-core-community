from collections.abc import Iterable

import app.state as runtime_state
from app.behaviour_engine import build_household_rhythm_profile, list_behavioural_anomalies
from app.config_loader import CONFIG_PATH
from app.correlation_engine import evaluate_correlated_signals
from app.db import get_connection
from app.incident_engine import build_incident_from_event
from app.operations_feed import build_ops_snapshot, sse_event_stream
from app.state import occupants, system_mode, trusted_devices, zones

REQUIRED_TABLES = {
    "sensor_events",
    "identity_evaluations",
    "threat_evaluations",
    "escalation_evaluations",
    "incidents",
    "incident_notes",
    "incident_status_history",
    "correlated_signals",
    "response_assessments",
    "operational_narratives",
    "operator_feedback",
    "trial_metric_snapshots",
    "trial_sessions",
    "pilot_session_notes",
}

REQUIRED_HISTORY_PATHS = {
    "/history/events",
    "/history/identity",
    "/history/threats",
    "/history/escalations",
    "/history/incidents",
}

REQUIRED_OPS_PATHS = {
    "/ops/feed",
    "/ops/snapshot",
}


def get_health_report() -> dict:
    return {
        "service_status": "running",
        "database_reachable": is_database_reachable(),
        "config_loaded": runtime_state.household_config is not None,
        "zones_count": len(zones),
        "occupants_count": len(occupants),
        "trusted_devices_count": len(trusted_devices),
        "current_mode": system_mode,
    }


def get_trial_readiness_report(route_paths: Iterable[str]) -> dict:
    available_paths = set(route_paths)
    checks = [
        _build_check(
            name="household_config_exists",
            passed=CONFIG_PATH.exists() and runtime_state.household_config is not None,
            detail="Household configuration file is available and loaded.",
            remediation="Add or restore config/household.json and reload the service.",
        ),
        _build_check(
            name="occupants_configured",
            passed=len(occupants) >= 1,
            detail=f"{len(occupants)} occupant(s) configured.",
            remediation="Configure at least one occupant for trial verification.",
        ),
        _build_check(
            name="trusted_devices_configured",
            passed=len(trusted_devices) >= 1,
            detail=f"{len(trusted_devices)} trusted device(s) configured.",
            remediation="Add at least one trusted BLE or resident device.",
        ),
        _build_check(
            name="zones_configured",
            passed=len(zones) >= 3,
            detail=f"{len(zones)} zone(s) configured.",
            remediation="Configure at least three household zones for trial coverage.",
        ),
        _build_check(
            name="database_initialized",
            passed=is_database_initialized(),
            detail="SQLite persistence is reachable and core tables are present.",
            remediation="Initialize the local SQLite database before trials.",
        ),
        _build_check(
            name="history_endpoints_available",
            passed=REQUIRED_HISTORY_PATHS.issubset(available_paths),
            detail="History endpoints are registered in the API.",
            remediation="Restore the history endpoints before trial use.",
        ),
        _build_check(
            name="operations_feed_available",
            passed=REQUIRED_OPS_PATHS.issubset(available_paths)
            and callable(build_ops_snapshot)
            and callable(sse_event_stream),
            detail="Operational snapshot and SSE feed are available.",
            remediation="Restore the local operations feed endpoints.",
        ),
        _build_check(
            name="incident_engine_available",
            passed=callable(build_incident_from_event),
            detail="Incident engine is available for automatic grouping.",
            remediation="Restore incident evaluation support before trials.",
        ),
        _build_check(
            name="behaviour_engine_available",
            passed=callable(build_household_rhythm_profile)
            and callable(list_behavioural_anomalies),
            detail="Behavioural baseline logic is available.",
            remediation="Restore behavioural baseline support before trials.",
        ),
        _build_check(
            name="correlation_engine_available",
            passed=callable(evaluate_correlated_signals),
            detail="Correlation intelligence is available.",
            remediation="Restore multi-signal correlation support before trials.",
        ),
    ]

    failed_checks = [check for check in checks if check["status"] == "fail"]
    warning_checks = [check for check in checks if check["status"] == "warning"]

    if failed_checks:
        readiness_status = "not_ready"
    elif warning_checks:
        readiness_status = "warning"
    else:
        readiness_status = "ready"

    missing_or_weak_items = [check["name"] for check in checks if check["status"] != "pass"]
    recommended_next_actions = [
        check["remediation"] for check in checks if check["status"] != "pass"
    ]
    if not recommended_next_actions:
        recommended_next_actions.append(
            "No immediate action required. Edge Core instance is ready for controlled trials."
        )

    return {
        "readiness_status": readiness_status,
        "checks": checks,
        "missing_or_weak_items": missing_or_weak_items,
        "recommended_next_actions": recommended_next_actions,
    }


def is_database_reachable() -> bool:
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1").fetchone()
    except Exception:
        return False

    return True


def is_database_initialized() -> bool:
    if not is_database_reachable():
        return False

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()

    table_names = {row["name"] for row in rows}
    return REQUIRED_TABLES.issubset(table_names)


def _build_check(
    *,
    name: str,
    passed: bool,
    detail: str,
    remediation: str,
) -> dict:
    return {
        "name": name,
        "status": "pass" if passed else "fail",
        "detail": detail,
        "remediation": remediation,
    }
