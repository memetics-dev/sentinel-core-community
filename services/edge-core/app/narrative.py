from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class NarrativeConfidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class OperationalNarrative(BaseModel):
    id: int | None = None
    event_id: int | None = None
    incident_id: str | None = None
    zone_id: str | None = None
    summary: str
    household_interpretation: str
    progression_summary: str
    confidence: NarrativeConfidence
    reasoning: list[str] = Field(default_factory=list)
    created_at: datetime
