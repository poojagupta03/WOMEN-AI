from dataclasses import dataclass


@dataclass
class JourneySignals:
    route_deviation_m: float = 0.0
    stop_duration_min: float = 0.0
    is_night: bool = False
    speed_kmh: float = 0.0


def calculate_risk(signals: JourneySignals) -> dict:
    score = 0
    reasons = []

    if signals.route_deviation_m > 500:
        score += 35
        reasons.append("Far off the planned route (more than 500 m)")
    elif signals.route_deviation_m > 200:
        score += 20
        reasons.append("Off the planned route (more than 200 m)")

    if signals.stop_duration_min > 10:
        score += 25
        reasons.append("Unexpected long stop (more than 10 minutes)")
    elif signals.stop_duration_min > 5:
        score += 10
        reasons.append("Unexpected stop (more than 5 minutes)")

    if signals.is_night:
        score += 15
        reasons.append("Travelling at night")

    if signals.speed_kmh > 80:
        score += 15
        reasons.append("Unusually high speed")

    score = min(score, 100)

    if score >= 60:
        level = "high"
    elif score >= 30:
        level = "medium"
    else:
        level = "low"

    return {"risk_score": score, "risk_level": level, "reasons": reasons}
