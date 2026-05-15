from datetime import timedelta

from app.db import (
    get_incident_model,
    list_incident_correlated_signals,
    list_incident_narratives,
    list_incident_notes,
    list_incident_response_assessments,
    list_incident_related_activity,
    list_incident_status_history,
)
from app.incident_engine import INCIDENT_GROUPING_WINDOW
from app.incidents import IncidentReplay, IncidentStatus, IncidentTimelineEntry
from app.narrative_engine import (
    build_narrative_timeline_entries,
    build_operator_narrative_interpretation,
    latest_narrative_for_incident,
)


def build_incident_timeline(incident_id: str) -> list[IncidentTimelineEntry] | None:
    incident = get_incident_model(incident_id)
    if incident is None:
        return None

    window_end = max(incident.updated_at, incident.created_at + INCIDENT_GROUPING_WINDOW)
    activity = list_incident_related_activity(
        zone_id=incident.zone_id,
        window_start=incident.created_at - timedelta(seconds=1),
        window_end=window_end,
    )

    entries: list[IncidentTimelineEntry] = []

    for event in activity["events"]:
        entries.append(
            IncidentTimelineEntry(
                entry_type="sensor_event",
                timestamp=event["timestamp"],
                details=event,
            )
        )

    for identity in activity["identity"]:
        entries.append(
            IncidentTimelineEntry(
                entry_type="identity_evaluation",
                timestamp=identity["created_at"],
                details=identity,
            )
        )

    for threat in activity["threats"]:
        entries.append(
            IncidentTimelineEntry(
                entry_type="threat_evaluation",
                timestamp=threat["created_at"],
                details=threat,
            )
        )

    for escalation in activity["escalations"]:
        entries.append(
            IncidentTimelineEntry(
                entry_type="escalation_evaluation",
                timestamp=escalation["created_at"],
                details=escalation,
            )
        )

    for response in activity["responses"]:
        entries.append(
            IncidentTimelineEntry(
                entry_type="response_assessment",
                timestamp=response["created_at"],
                details=response,
            )
        )

    for correlation in list_incident_correlated_signals(incident_id):
        entries.append(
            IncidentTimelineEntry(
                entry_type="correlated_signal",
                timestamp=correlation["created_at"],
                details=correlation,
            )
        )

    incident_narratives = list_incident_narratives(incident_id)
    entries.extend(build_narrative_timeline_entries(incident_narratives))

    for note in list_incident_notes(incident_id):
        entries.append(
            IncidentTimelineEntry(
                entry_type="note",
                timestamp=note["created_at"],
                details=note,
            )
        )

    for status_change in list_incident_status_history(incident_id):
        entries.append(
            IncidentTimelineEntry(
                entry_type="status_change",
                timestamp=status_change["created_at"],
                details=status_change,
            )
        )

    entries.sort(key=lambda entry: (entry.timestamp, entry.entry_type))
    return entries


def build_incident_replay(incident_id: str) -> IncidentReplay | None:
    incident = get_incident_model(incident_id)
    if incident is None:
        return None

    timeline = build_incident_timeline(incident_id)
    if timeline is None:
        return None

    narratives = list_incident_narratives(incident_id)
    latest_narrative = latest_narrative_for_incident(incident_id, narratives)

    return IncidentReplay(
        incident=incident,
        timeline=timeline,
        final_status=incident.status,
        severity=incident.severity,
        reasoning_summary=incident.reasoning_summary,
        latest_response_assessment=_latest_response_assessment(incident_id),
        latest_narrative=latest_narrative,
        recommended_operator_interpretation=build_operator_narrative_interpretation(
            incident,
            latest_narrative,
        ),
    )


def _latest_response_assessment(incident_id: str) -> dict | None:
    responses = list_incident_response_assessments(incident_id)
    if not responses:
        return None
    return responses[-1]
