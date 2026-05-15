from datetime import UTC, datetime

from pydantic import BaseModel

from app.trial_feedback import FeedbackCategory
from app.trial_metrics import (
    ESCALATED_RESPONSE_STATES,
    SUPPRESSED_RESPONSE_STATES,
)
from app.trial_session import TrialSession


class TrialReport(BaseModel):
    report_id: str
    generated_at: datetime
    session: TrialSession | None = None
    household_id: str
    household_label: str
    trial_metrics_summary: dict
    incident_summary: dict
    response_summary: dict
    narrative_summary: dict
    feedback_summary: dict
    pilot_notes: list[dict]
    session_conclusions: list[str]
    false_positive_candidates: list[dict]
    recommended_review_points: list[str]


def build_trial_report(
    *,
    household_id: str,
    household_label: str,
    incidents: list[dict],
    responses: list[dict],
    narratives: list[dict],
    feedback: list[dict],
    pilot_notes: list[dict],
    session_conclusions: list[str],
    metrics,
    evaluation,
    session: TrialSession | None = None,
    generated_at: datetime | None = None,
) -> TrialReport:
    timestamp = (generated_at or datetime.now(UTC)).astimezone(UTC)
    false_positive_candidates = _build_false_positive_candidates(
        incidents=incidents,
        responses=responses,
        feedback=feedback,
    )

    critical_incidents = [
        incident for incident in incidents if incident["severity"] == "critical"
    ]
    open_incidents = [
        incident
        for incident in incidents
        if incident["status"] in {"open", "monitoring"}
    ]
    active_responses = [
        response
        for response in responses
        if response["response_state"] in ESCALATED_RESPONSE_STATES
    ]
    suppressed_responses = [
        response
        for response in responses
        if response["response_state"] in SUPPRESSED_RESPONSE_STATES
    ]

    return TrialReport(
        report_id=(
            f"trial-report-{household_id}-"
            f"{timestamp.strftime('%Y%m%dT%H%M%SZ')}"
        ),
        generated_at=timestamp,
        session=session,
        household_id=household_id,
        household_label=household_label,
        trial_metrics_summary={
            "total_incidents": metrics.total_incidents,
            "critical_incidents": metrics.critical_incidents,
            "suppressed_incidents": metrics.suppressed_incidents,
            "response_escalations": metrics.response_escalations,
            "narrative_generations": metrics.narrative_generations,
            "trusted_presence_suppressions": metrics.trusted_presence_suppressions,
            "active_response_recommendations": metrics.active_response_recommendations,
            "false_positive_candidate_count": metrics.false_positive_candidate_count,
            "generated_from_snapshot_at": metrics.created_at,
        },
        incident_summary={
            "total_incidents": len(incidents),
            "open_incidents": len(open_incidents),
            "critical_incidents": len(critical_incidents),
            "zones": sorted({incident["zone_id"] for incident in incidents}),
            "recent_incidents": incidents[:5],
        },
        response_summary={
            "total_responses": len(responses),
            "active_security_responses": len(active_responses),
            "suppressed_or_silent_responses": len(suppressed_responses),
            "latest_responses": responses[-5:],
        },
        narrative_summary={
            "total_narratives": len(narratives),
            "recent_narratives": narratives[-5:],
            "high_confidence_narratives": sum(
                1 for narrative in narratives if narrative["confidence"] == "high"
            ),
        },
        feedback_summary={
            "total_feedback_entries": len(feedback),
            "correct_detection_count": evaluation.correct_detection_count,
            "false_positive_count": evaluation.false_positive_count,
            "uncertain_count": evaluation.uncertain_count,
            "narrative_helpful_count": evaluation.narrative_helpful_count,
            "narrative_confusing_count": evaluation.narrative_confusing_count,
            "recent_feedback": feedback[-5:],
        },
        pilot_notes=pilot_notes[:10],
        session_conclusions=session_conclusions,
        false_positive_candidates=false_positive_candidates,
        recommended_review_points=_build_recommended_review_points(
            evaluation_recommendations=evaluation.recommended_actions,
            critical_incident_count=len(critical_incidents),
            false_positive_candidate_count=len(false_positive_candidates),
            narrative_confusing_count=evaluation.narrative_confusing_count,
            active_response_count=len(active_responses),
        ),
    )


def _build_false_positive_candidates(
    *,
    incidents: list[dict],
    responses: list[dict],
    feedback: list[dict],
) -> list[dict]:
    latest_response_by_incident: dict[str, dict] = {}
    for response in responses:
        incident_id = response.get("incident_id")
        if incident_id:
            latest_response_by_incident[incident_id] = response

    false_positive_feedback_ids = {
        entry["incident_id"]
        for entry in feedback
        if entry["feedback_type"] == FeedbackCategory.FALSE_POSITIVE.value
        and entry.get("incident_id")
    }

    candidates: list[dict] = []
    for incident in incidents:
        reasons: list[str] = []
        response = latest_response_by_incident.get(incident["incident_id"])
        if response and response["response_state"] in SUPPRESSED_RESPONSE_STATES:
            reasons.append("Suppressed or silent response posture detected.")
        if incident["incident_id"] in false_positive_feedback_ids:
            reasons.append("Operator marked this incident as a false positive.")
        if reasons:
            candidates.append(
                {
                    "incident_id": incident["incident_id"],
                    "zone_id": incident["zone_id"],
                    "severity": incident["severity"],
                    "status": incident["status"],
                    "reasoning_summary": incident["reasoning_summary"],
                    "candidate_reasons": reasons,
                }
            )

    return candidates


def _build_recommended_review_points(
    *,
    evaluation_recommendations: list[str],
    critical_incident_count: int,
    false_positive_candidate_count: int,
    narrative_confusing_count: int,
    active_response_count: int,
) -> list[str]:
    review_points = list(evaluation_recommendations)

    if critical_incident_count > 0:
        review_points.append(
            "Review critical incident replay and response posture before closing the trial session."
        )
    if false_positive_candidate_count > 0:
        review_points.append(
            "Compare false-positive candidates with trusted-presence and suppression reasoning."
        )
    if narrative_confusing_count > 0:
        review_points.append(
            "Check whether operational narratives remained clear during escalation transitions."
        )
    if active_response_count > 0:
        review_points.append(
            "Validate that active response recommendations matched the observed incident severity."
        )

    if not review_points:
        review_points.append(
            "No immediate review points detected. Continue gathering controlled household observations."
        )

    # Preserve stable order while removing duplicates.
    return list(dict.fromkeys(review_points))
