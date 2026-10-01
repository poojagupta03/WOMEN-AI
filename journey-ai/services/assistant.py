from services.risk_engine import JourneySignals


def build_advice(signals: JourneySignals, risk: dict) -> dict:
    level = risk["risk_level"]
    recommendations = []
    insights = []

    if level == "high":
        summary = "High risk detected. Please act on the steps below now."
        recommendations.append("Share your live location with a trusted contact right now.")
        recommendations.append("Move to a well-lit, busy place if you can do so safely.")
        recommendations.append("If you feel unsafe, call 112 (emergency) or 1091 (women helpline).")
    elif level == "medium":
        summary = "Some unusual signals on this journey. Stay alert."
        recommendations.append("Let a trusted contact know about your journey status.")
        recommendations.append("Keep your phone charged and your location sharing on.")
    else:
        summary = "Your journey looks normal."
        recommendations.append("No action needed. Keep location sharing on for safety.")

    if signals.route_deviation_m > 200:
        recommendations.append("You are off the planned route. Check the map and confirm the new route is expected.")
    if signals.stop_duration_min > 5:
        recommendations.append("The vehicle has stopped for a while. Confirm that you are safe.")
    if signals.is_night:
        recommendations.append("It is night time. Prefer well-lit main roads where possible.")
    if signals.speed_kmh > 80:
        recommendations.append("Speed is very high. Ask the driver to slow down.")

    insights.append(
        f"Overall risk is {risk['risk_score']}/100 ({level}). "
        f"Rules gave {risk['rule_score']}, the anomaly model gave {risk['anomaly_score']}."
    )
    if risk["is_anomaly"]:
        insights.append("This journey looks different from typical safe journeys.")
    if risk["reasons"]:
        insights.append("Main reasons: " + "; ".join(risk["reasons"]) + ".")

    return {
        "summary": summary,
        "recommendations": recommendations,
        "insights": insights,
        "source": "rules",
    }
