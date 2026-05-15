from datetime import UTC, datetime

from pydantic import BaseModel

from app.response_engine import list_active_response_assessments
from app.response import ResponseState
from app.trial_feedback import FeedbackCategory
from app.trial_session import TrialSession

SUPPRESSED_RESPONSE_STATES = {
    ResponseState.MONITOR_ONLY.value,
    ResponseState.SILENT_OPERATOR_REVIEW.value,
    ResponseState.OCCUPANT_VERIFICATION.value,
}
ESCALATED_RESPONSE_STATES = {
    ResponseState.ACTIVE_SECURITY_RESPONSE.value,
    ResponseState.EMERGENCY_RESPONSE.value,
}
TRUSTED_SUPPRESSION_MARKERS = {
    "Possible occupant movement continuity detected.",
    "Trusted occupant activity was recently observed in the household.",
}


class TrialMetricSnapshot(BaseModel):
    id: int | None = None
    total_incidents: int
    critical_incidents: int
    suppressed_incidents: int
    response_escalations: int
    narrative_generations: int
    trusted_presence_suppressions: int
    active_response_recommendations: int
    false_positive_candidate_count: int
    created_at: datetime


class EvaluationSummary(BaseModel):
    metrics: TrialMetricSnapshot
    total_feedback_entries: int
    correct_detection_count: int
    false_positive_count: int
    uncertain_count: int
    narrative_helpful_count: int
    narrative_confusing_count: int
    recommended_actions: list[str]


def build_trial_metric_snapshot(
    *,
    incidents: list[dict],
    responses: list[dict],
    narratives: list[dict],
    feedback: list[dict],
    created_at: datetime | None = None,
) -> TrialMetricSnapshot:
    latest_incident_responses = _latest_responses_by_incident(responses)
    suppressed_incident_ids = {
        incident_id
        for incident_id, response in latest_incident_responses.items()
        if response["response_state"] in SUPPRESSED_RESPONSE_STATES
    }
    explicit_false_positive_ids = {
        feedback_entry["incident_id"]
        for feedback_entry in feedback
        if feedback_entry["feedback_type"] == FeedbackCategory.FALSE_POSITIVE.value
        and feedback_entry.get("incident_id")
    }
    false_positive_candidate_ids = suppressed_incident_ids | explicit_false_positive_ids
    active_responses = list_active_response_assessments(responses, incidents)

    return TrialMetricSnapshot(
        total_incidents=len(incidents),
        critical_incidents=sum(
            1 for incident in incidents if incident["severity"] == "critical"
        ),
        suppressed_incidents=len(suppressed_incident_ids),
        response_escalations=sum(
            1
            for response in responses
            if response["response_state"] in ESCALATED_RESPONSE_STATES
        ),
        narrative_generations=len(narratives),
        trusted_presence_suppressions=sum(
            1
            for response in responses
            if response["response_state"] in SUPPRESSED_RESPONSE_STATES
            and any(marker in response["reasoning"] for marker in TRUSTED_SUPPRESSION_MARKERS)
        ),
        active_response_recommendations=len(active_responses),
        false_positive_candidate_count=len(false_positive_candidate_ids),
        created_at=(created_at or datetime.now(UTC)).astimezone(UTC),
    )


def build_evaluation_summary(
    *,
    metrics: TrialMetricSnapshot,
    feedback: list[dict],
) -> EvaluationSummary:
    feedback_counts = {
        category.value: sum(
            1 for item in feedback if item["feedback_type"] == category.value
        )
        for category in FeedbackCategory
    }
    recommended_actions: list[str] = []
    if feedback_counts[FeedbackCategory.FALSE_POSITIVE.value] > 0:
        recommended_actions.append(
            "Review false-positive candidate incidents and compare them with trusted-presence suppressions."
        )
    if feedback_counts[FeedbackCategory.NARRATIVE_CONFUSING.value] > 0:
        recommended_actions.append(
            "Review operational narrative phrasing for confusing trial situations."
        )
    if metrics.active_response_recommendations > 0:
        recommended_actions.append(
            "Review active response recommendations together with incident replay before closing trial observations."
        )
    if not recommended_actions:
        recommended_actions.append(
            "No immediate evaluation concerns detected. Continue collecting controlled household trial observations."
        )

    return EvaluationSummary(
        metrics=metrics,
        total_feedback_entries=len(feedback),
        correct_detection_count=feedback_counts[FeedbackCategory.CORRECT_DETECTION.value],
        false_positive_count=feedback_counts[FeedbackCategory.FALSE_POSITIVE.value],
        uncertain_count=feedback_counts[FeedbackCategory.UNCERTAIN.value],
        narrative_helpful_count=feedback_counts[FeedbackCategory.NARRATIVE_HELPFUL.value],
        narrative_confusing_count=feedback_counts[FeedbackCategory.NARRATIVE_CONFUSING.value],
        recommended_actions=recommended_actions,
    )


def build_trial_export(
    *,
    incidents: list[dict],
    responses: list[dict],
    narratives: list[dict],
    feedback: list[dict],
    metrics: TrialMetricSnapshot,
    evaluation: EvaluationSummary,
    session: TrialSession | None = None,
    pilot_notes: list[dict] | None = None,
    session_conclusions: list[str] | None = None,
) -> dict:
    return {
        "exported_at": datetime.now(UTC),
        "session": session,
        "incidents": incidents,
        "responses": responses,
        "narratives": narratives,
        "feedback": feedback,
        "pilot_notes": pilot_notes or [],
        "session_conclusions": session_conclusions or [],
        "summary_metrics": metrics,
        "evaluation_summary": evaluation,
    }


def _latest_responses_by_incident(responses: list[dict]) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for response in responses:
        incident_id = response.get("incident_id")
        if not incident_id:
            continue
        latest[incident_id] = response
    return latest
