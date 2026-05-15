from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TrialSessionStatus(str, Enum):
    ACTIVE = "active"
    ENDED = "ended"


class TrialSession(BaseModel):
    session_id: str
    label: str
    started_at: datetime
    ended_at: datetime | None = None
    status: TrialSessionStatus
    notes: str | None = None


class TrialSessionStart(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    notes: str | None = Field(default=None, max_length=500)


class TrialSessionEnd(BaseModel):
    notes: str | None = Field(default=None, max_length=500)
