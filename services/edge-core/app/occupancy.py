from datetime import datetime

from pydantic import BaseModel


class OccupancyState(BaseModel):
    zone_id: str
    occupied: bool
    occupancy_confidence: int
    movement_state: str
    last_updated: datetime
