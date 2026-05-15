from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class EscalationStage(str, Enum):
    SUPPRESS = "suppress"
    OCCUPANT_AWARENESS = "occupant_awareness"
    VERIFICATION = "verification"
    HUMAN_MONITORING_PREP = "human_monitoring_prep"
    ACTIVE_INTERVENTION = "active_intervention"
    EMERGENCY_RESPONSE = "emergency_response"


class EscalationState(BaseModel):
    zone_id: str
    stage: EscalationStage
    recommended_action: str
    reasoning: list[str]
    last_updated: datetime
