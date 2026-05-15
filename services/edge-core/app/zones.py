from pydantic import BaseModel


class Zone(BaseModel):
    id: str
    label: str
    sensitivity: str
    night_access_expected: bool
    connected_zones: list[str]
