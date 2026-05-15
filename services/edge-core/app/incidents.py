from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class IncidentStatus(str, Enum):
    OPEN = "open"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class IncidentSeverity(str, Enum):
    SUSPICIOUS = "suspicious"
    HIGH_THREAT = "high_threat"
    CRITICAL = "critical"


class Incident(BaseModel):
    incident_id: str
    zone_id: str
    severity: IncidentSeverity
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    related_event_count: int
    related_escalation_count: int
    reasoning_summary: str


class IncidentNoteCreate(BaseModel):
    note: str = Field(min_length=1)


class IncidentNote(BaseModel):
    id: int
    incident_id: str
    note: str
    created_at: datetime


class IncidentTimelineEntry(BaseModel):
    entry_type: str
    timestamp: datetime
    details: dict


class IncidentReplay(BaseModel):
    incident: Incident
    timeline: list[IncidentTimelineEntry]
    final_status: IncidentStatus
    severity: IncidentSeverity
    reasoning_summary: str
    latest_response_assessment: dict | None = None
    latest_narrative: dict | None = None
    recommended_operator_interpretation: str
