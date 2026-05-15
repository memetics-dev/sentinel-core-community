from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class FeedbackCategory(str, Enum):
    CORRECT_DETECTION = "correct_detection"
    FALSE_POSITIVE = "false_positive"
    UNCERTAIN = "uncertain"
    NARRATIVE_HELPFUL = "narrative_helpful"
    NARRATIVE_CONFUSING = "narrative_confusing"


class OperatorFeedbackCreate(BaseModel):
    incident_id: str | None = None
    narrative_id: int | None = None
    feedback_type: FeedbackCategory
    note: str | None = Field(default=None, max_length=500)


class OperatorFeedback(BaseModel):
    id: int | None = None
    incident_id: str | None = None
    narrative_id: int | None = None
    feedback_type: FeedbackCategory
    note: str | None = None
    created_at: datetime
