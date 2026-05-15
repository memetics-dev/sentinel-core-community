from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class PilotNoteType(str, Enum):
    OPERATOR_OBSERVATION = "operator_observation"
    SYSTEM_STRENGTH = "system_strength"
    SYSTEM_CONFUSION = "system_confusion"
    FALSE_POSITIVE_OBSERVATION = "false_positive_observation"
    NARRATIVE_QUALITY = "narrative_quality"
    RESPONSE_QUALITY = "response_quality"
    HOUSEHOLD_CONTEXT = "household_context"


class PilotSessionNoteCreate(BaseModel):
    note_type: PilotNoteType
    content: str = Field(min_length=1, max_length=1000)


class PilotSessionNote(BaseModel):
    id: int | None = None
    session_id: str
    note_type: PilotNoteType
    content: str
    created_at: datetime


def build_session_conclusions(notes: list[dict]) -> list[str]:
    if not notes:
        return []

    grouped_notes: dict[str, list[str]] = {}
    for note in notes:
        grouped_notes.setdefault(note["note_type"], []).append(note["content"])

    conclusions: list[str] = []
    if PilotNoteType.SYSTEM_STRENGTH.value in grouped_notes:
        conclusions.append(
            "Operator noted clear system strengths during this session."
        )
    if PilotNoteType.SYSTEM_CONFUSION.value in grouped_notes:
        conclusions.append(
            "Operator observed points of system confusion that should be reviewed before broader pilot use."
        )
    if PilotNoteType.FALSE_POSITIVE_OBSERVATION.value in grouped_notes:
        conclusions.append(
            "False-positive observations were recorded and should be compared with suppression and trusted-presence reasoning."
        )
    if PilotNoteType.NARRATIVE_QUALITY.value in grouped_notes:
        conclusions.append(
            "Narrative quality observations were recorded for later phrasing review."
        )
    if PilotNoteType.RESPONSE_QUALITY.value in grouped_notes:
        conclusions.append(
            "Response quality observations were recorded against the session evidence."
        )
    if PilotNoteType.HOUSEHOLD_CONTEXT.value in grouped_notes:
        conclusions.append(
            "Additional household context was recorded for interpreting this session."
        )
    if PilotNoteType.OPERATOR_OBSERVATION.value in grouped_notes:
        conclusions.append(
            "Operator observations were captured alongside the session evidence."
        )

    if not conclusions:
        conclusions.append(
            "No session conclusions were derived from the recorded pilot notes."
        )

    return conclusions


def new_pilot_session_note(
    *,
    session_id: str,
    note_type: PilotNoteType,
    content: str,
) -> PilotSessionNote:
    return PilotSessionNote(
        session_id=session_id,
        note_type=note_type,
        content=content.strip(),
        created_at=datetime.now(UTC),
    )
