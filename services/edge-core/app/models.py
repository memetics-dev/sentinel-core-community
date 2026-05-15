from datetime import UTC, datetime
from enum import Enum
from pydantic import BaseModel, Field

from app.zones import Zone


class SensorType(str, Enum):
    MMWAVE = "mmwave"
    BLE = "ble"
    CONTACT = "contact"
    VIBRATION = "vibration"


class SensorEvent(BaseModel):
    sensor_id: str
    sensor_type: SensorType
    zone_id: str
    value: str
    confidence: int = Field(ge=0, le=100)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Occupant(BaseModel):
    id: str
    label: str
    role: str


class TrustedDevice(BaseModel):
    id: str
    label: str
    occupant_id: str
    sensor_type: SensorType
    sensor_id: str


class HouseholdConfig(BaseModel):
    household_id: str
    household_label: str
    occupants: list[Occupant]
    trusted_devices: list[TrustedDevice]
    zones: list[Zone]


class ActivityWindow(BaseModel):
    start_hour: int
    end_hour: int
    event_count: int


class ZoneActivityBaseline(BaseModel):
    zone_id: str
    active_hours: list[int]
    normal_movement_windows: list[ActivityWindow]
    movement_frequency: float
    recent_continuity: int


class HouseholdRhythmProfile(BaseModel):
    generated_at: datetime
    total_events: int
    common_active_hours: list[int]
    zone_baselines: dict[str, ZoneActivityBaseline]


class CorrelatedSignal(BaseModel):
    pattern_type: str
    zone_id: str
    modifier: int
    reasoning: str
    contributing_event_ids: list[int]
    created_at: datetime


class OccupantPresenceState(BaseModel):
    occupant_id: str
    occupant_label: str
    likely_home: bool
    recently_active: bool
    last_seen_at: datetime | None
    recent_zone_id: str | None
    reasoning: list[str]


class HouseholdActivityState(BaseModel):
    state: str
    recent_movement_count: int
    settled: bool
    reasoning: list[str]


class HouseholdPresenceState(BaseModel):
    summary: str
    all_occupants_likely_home: bool
    no_trusted_occupants_detected: bool
    partial_occupancy: bool
    trusted_occupant_recently_active: bool
    unknown_presence_detected: bool
    household_activity: HouseholdActivityState
    occupants: list[OccupantPresenceState]
    reasoning: list[str]
    generated_at: datetime
