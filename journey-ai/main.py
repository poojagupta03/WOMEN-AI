from fastapi import FastAPI
from pydantic import BaseModel

from services.anomaly_model import check_anomaly
from services.assistant import build_advice
from services.risk_engine import JourneySignals, calculate_risk

app = FastAPI(title="Journey AI")


class RiskRequest(BaseModel):
    route_deviation_m: float = 0.0
    stop_duration_min: float = 0.0
    is_night: bool = False
    speed_kmh: float = 0.0


def level_from_score(score: int) -> str:
    if score >= 60:
        return "high"
    if score >= 30:
        return "medium"
    return "low"
def level_from_score(score: int) -> str:
    if score >= 60:
        return "high"
    if score >= 30:
        return "medium"
    return "low"


def compute_confidence(rule_score: float, anomaly_score: float, signals_triggered: int) -> dict:
    agreement = 1 - abs(rule_score - anomaly_score) / 100
    evidence = min(signals_triggered / 3, 1)
    confidence = round((0.7 * agreement + 0.3 * evidence) * 100)

    if confidence >= 75:
        label = "high"
    elif confidence >= 50:
        label = "medium"
    else:
        label = "low"

    return {"confidence": confidence, "confidence_level": label} 
def compute_risk(req: RiskRequest):
    signals = JourneySignals(
        route_deviation_m=req.route_deviation_m,
        stop_duration_min=req.stop_duration_min,
        is_night=req.is_night,
        speed_kmh=req.speed_kmh,
    )
    rules = calculate_risk(signals)
    anomaly = check_anomaly(
        req.route_deviation_m, req.stop_duration_min, req.is_night, req.speed_kmh
    )

    final_score = round(0.6 * rules["risk_score"] + 0.4 * anomaly["anomaly_score"])
    reasons = list(rules["reasons"])
    if anomaly["is_anomaly"]:
        reasons.append("Journey pattern is unusual compared to normal journeys")
    breakdown = [
        {
            "factor": item["factor"],
            "reason": item["reason"],
            "contribution": round(0.6 * item["points"], 1),
        }
        for item in rules["breakdown"]
    ]
    breakdown.append(
        {
            "factor": "anomaly_model",
            "reason": "Journey pattern is unusual compared to normal journeys"
            if anomaly["is_anomaly"]
            else "Journey pattern looks normal",
            "contribution": round(0.4 * anomaly["anomaly_score"], 1),
        }
    )
    confidence = compute_confidence(
        rules["risk_score"], anomaly["anomaly_score"], len(rules["breakdown"])
    ) 
    risk = {
        "risk_score": final_score,
        "risk_level": level_from_score(final_score),
        "rule_score": rules["risk_score"],
        "anomaly_score": anomaly["anomaly_score"],
        "is_anomaly": anomaly["is_anomaly"],
        "reasons": reasons,
        "breakdown": breakdown,
                **confidence,

    }
    
    return signals, risk


@app.get("/health")
def health():
    return {"status": "ok", "service": "journey-ai"}


@app.post("/risk/score")
def risk_score(req: RiskRequest):
    _, risk = compute_risk(req)
    return risk


@app.post("/assistant/advice")
def assistant_advice(req: RiskRequest):
    signals, risk = compute_risk(req)
    return {"risk": risk, "advice": build_advice(signals, risk)}
