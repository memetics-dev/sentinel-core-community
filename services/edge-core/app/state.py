from app.config_loader import load_household_config
from app.db import reset_db
from app.escalation import EscalationState
from app.identity import IdentityState
from app.models import HouseholdConfig, Occupant, SensorEvent, TrustedDevice
from app.modes import OperatingMode, SystemModeState
from app.occupancy import OccupancyState
from app.threats import ThreatState
from app.zones import Zone

sensor_events: list[SensorEvent] = []

occupancy_state: dict[str, OccupancyState] = {}

threat_state: dict[str, ThreatState] = {}

identity_state: dict[str, IdentityState] = {}

escalation_state: dict[str, EscalationState] = {}

system_mode = SystemModeState(
    mode=OperatingMode.HOME_ACTIVE,
    description="Normal protected household mode",
)

household_config: HouseholdConfig | None = None

occupants: dict[str, Occupant] = {}

trusted_devices: dict[str, TrustedDevice] = {}

zones: dict[str, Zone] = {}


def load_runtime_config() -> None:
    global household_config

    household_config = load_household_config()
    occupants.clear()
    trusted_devices.clear()
    zones.clear()

    occupants.update({occupant.id: occupant for occupant in household_config.occupants})
    trusted_devices.update(
        {device.sensor_id: device for device in household_config.trusted_devices}
    )
    zones.update({zone.id: zone for zone in household_config.zones})


def reset_runtime_state() -> None:
    from app.operations_feed import reset_ops_feed

    sensor_events.clear()
    occupancy_state.clear()
    threat_state.clear()
    identity_state.clear()
    escalation_state.clear()
    system_mode.mode = OperatingMode.HOME_ACTIVE
    system_mode.description = "Normal protected household mode"
    reset_db()
    reset_ops_feed()
    load_runtime_config()


load_runtime_config()
