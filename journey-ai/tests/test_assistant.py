from fastapi.testclient import TestClient

from main import app
from services.assistant import build_advice
from services.risk_engine import JourneySignals

client = TestClient(app)


def test_advice_endpoint_high_risk():
    res = client.post(
        "/assistant/advice",
        json={
            "route_deviation_m": 600,
            "stop_duration_min": 12,
            "is_night": True,
            "speed_kmh": 40,
        },
    )
    body = res.json()
    assert res.status_code == 200
    assert body["risk"]["risk_level"] == "high"
    assert any("112" in r for r in body["advice"]["recommendations"])
    assert len(body["advice"]["insights"]) >= 2


def test_advice_endpoint_normal_journey():
    res = client.post(
        "/assistant/advice",
        json={
            "route_deviation_m": 30,
            "stop_duration_min": 2,
            "is_night": False,
            "speed_kmh": 35,
        },
    )
    body = res.json()
    assert res.status_code == 200
    assert body["risk"]["risk_level"] == "low"
    assert body["advice"]["summary"] == "Your journey looks normal."


def test_build_advice_medium_risk():
    risk = {
        "risk_score": 40,
        "risk_level": "medium",
        "rule_score": 45,
        "anomaly_score": 30.0,
        "is_anomaly": False,
        "reasons": [],
    }
    advice = build_advice(JourneySignals(route_deviation_m=300), risk)
    assert advice["summary"].startswith("Some unusual")
    assert any("off the planned route" in r for r in advice["recommendations"])


def test_missing_fields_use_defaults():
    res = client.post("/assistant/advice", json={})
    assert res.status_code == 200
