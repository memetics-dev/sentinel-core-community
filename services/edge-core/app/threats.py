from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ThreatClassification(str, Enum):
    BENIGN = "benign"
    IRREGULAR = "irregular"
    SUSPICIOUS = "suspicious"
    HIGH_THREAT = "high_threat"
    CRITICAL = "critical"


class ThreatState(BaseModel):
    zone_id: str
    threat_score: int
    classification: ThreatClassification
    reasoning: list[str]
    last_updated: datetime
