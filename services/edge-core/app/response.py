from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ResponseUrgency(str, Enum):
    LOW = "low"
    ELEVATED = "elevated"
    URGENT = "urgent"
    CRITICAL = "critical"


class OccupantSafetyState(str, Enum):
    LIKELY_SAFE = "likely_safe"
    VERIFY_OCCUPANT = "verify_occupant"
    POSSIBLE_RISK = "possible_risk"
    HIGH_RISK = "high_risk"


class ResponseState(str, Enum):
    MONITOR_ONLY = "monitor_only"
    SILENT_OPERATOR_REVIEW = "silent_operator_review"
    OCCUPANT_VERIFICATION = "occupant_verification"
    ACTIVE_SECURITY_RESPONSE = "active_security_response"
    EMERGENCY_RESPONSE = "emergency_response"


class ResponseAssessment(BaseModel):
    id: int | None = None
    event_id: int
    incident_id: str | None = None
    zone_id: str
    response_confidence: int = Field(ge=0, le=100)
    urgency: ResponseUrgency
    response_state: ResponseState
    occupant_safety_state: OccupantSafetyState
    operator_recommendation: str
    reasoning: list[str]
    cooldown_applied: bool = False
    created_at: datetime
