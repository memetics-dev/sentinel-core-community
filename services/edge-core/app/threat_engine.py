from app.modes import OperatingMode
from app.models import SensorEvent
from app.threats import ThreatClassification
from app.zones import Zone

def classify_threat(score: int) -> ThreatClassification:
    if score <= 20:
        return ThreatClassification.BENIGN
    if score <= 40:
        return ThreatClassification.IRREGULAR
    if score <= 65:
        return ThreatClassification.SUSPICIOUS
    if score <= 85:
        return ThreatClassification.HIGH_THREAT

    return ThreatClassification.CRITICAL


def calculate_threat_score(
    event: SensorEvent,
    mode: OperatingMode,
    known_occupant: bool,
    zone: Zone | None,
) -> tuple[int, list[str]]:
    threat_score = 0
    reasoning = []

    if known_occupant:
        threat_score -= 35
        reasoning.append("Trusted occupant or device continuity lowers concern")
    else:
        threat_score += 25
        reasoning.append("No trusted occupant continuity detected")

    if mode == OperatingMode.NIGHT_LOCK:
        if zone and zone.night_access_expected:
            threat_score += 5
            reasoning.append(
                "Night Lock is active, but this zone can support limited expected night access"
            )
        else:
            threat_score += 20
            reasoning.append("Night Lock is active")

    if mode == OperatingMode.AWAY_GUARD:
        threat_score += 30
        reasoning.append("Away Guard is active")

    if event.sensor_type == "mmwave":
        threat_score += 20
        reasoning.append("Movement detected")

    if zone:
        if zone.sensitivity == "high":
            threat_score += 25
            reasoning.append(
                f"{zone.label} is a high-sensitivity zone"
            )

        elif zone.sensitivity == "medium":
            threat_score += 10
            reasoning.append(
                f"{zone.label} is a medium-sensitivity zone"
            )

        if (
            mode == OperatingMode.NIGHT_LOCK
            and not zone.night_access_expected
        ):
            threat_score += 15
            reasoning.append(
                f"{zone.label} is not normally accessed during Night Lock"
            )
        elif (
            mode == OperatingMode.NIGHT_LOCK
            and zone.night_access_expected
        ):
            threat_score -= 10
            reasoning.append(
                f"{zone.label} can support limited expected night access"
            )

    if event.confidence > 80:
        threat_score += 15
        reasoning.append("High-confidence sensor reading")

    return max(0, min(threat_score, 100)), reasoning
