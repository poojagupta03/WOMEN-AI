from dataclasses import dataclass


@dataclass
class JourneySignals:
    route_deviation_m: float = 0.0
    stop_duration_min: float = 0.0
    is_night: bool = False
    speed_kmh: float = 0.0


def calculate_risk(signals: JourneySignals) -> dict:
    score = 0
    breakdown = []

    def add(factor: str, points: int, reason: str):
        nonlocal score
        score += points
        breakdown.append({"factor": factor, "points": points, "reason": reason})

    if signals.route_deviation_m > 500:
        add("route_deviation", 35, "Far off the planned route (more than 500 m)")
    elif signals.route_deviation_m > 200:
        add("route_deviation", 20, "Off the planned route (more than 200 m)")

    if signals.stop_duration_min > 10:
        add("long_stop", 25, "Unexpected long stop (more than 10 minutes)")
    elif signals.stop_duration_min > 5:
        add("long_stop", 10, "Unexpected stop (more than 5 minutes)")

    if signals.is_night:
        add("night_travel", 15, "Travelling at night")

    if signals.speed_kmh > 80:
        add("high_speed", 15, "Unusually high speed")

    score = min(score, 100)

    if score >= 60:
        level = "high"
    elif score >= 30:
        level = "medium"
    else:
        level = "low"

    reasons = [item["reason"] for item in breakdown]
    return {
        "risk_score": score,
        "risk_level": level,
        "reasons": reasons,
        "breakdown": breakdown,
    }