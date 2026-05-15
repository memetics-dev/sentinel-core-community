from pydantic import BaseModel


class IdentityState(BaseModel):
    occupant_id: str | None
    identity_confidence: int
    known_occupant: bool
    reasoning: list[str]
