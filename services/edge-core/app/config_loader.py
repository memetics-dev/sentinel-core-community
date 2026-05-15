import json
from pathlib import Path

from app.models import HouseholdConfig

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "household.json"


def load_household_config() -> HouseholdConfig:
    with CONFIG_PATH.open() as config_file:
        payload = json.load(config_file)

    return HouseholdConfig.model_validate(payload)
