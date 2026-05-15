from enum import Enum
from pydantic import BaseModel


class OperatingMode(str, Enum):
    OBSERVE = "observe"
    HOME_ACTIVE = "home_active"
    NIGHT_LOCK = "night_lock"
    AWAY_GUARD = "away_guard"
    ELEVATED_ALERT = "elevated_alert"
    THREAT_ACTIVE = "threat_active"
    EMERGENCY_RESPONSE = "emergency_response"


class SystemModeState(BaseModel):
    mode: OperatingMode
    description: str
