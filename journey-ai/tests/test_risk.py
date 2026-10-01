from fastapi.testclient import TestClient

from main import app
from services.risk_engine import JourneySignals, calculate_risk

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_rule_engine_gives_reasons():
    result = calculate_risk(
        JourneySignals(route_deviation_m=600, stop_duration_min=12, is_night=True)
    )
    assert result["risk_score"] == 75
    assert result["risk_level"] == "high"
    assert len(result["reasons"]) == 3


def test_normal_journey_is_low_risk():
    res = client.post(
        "/risk/score",
        json={
            "route_deviation_m": 30,
            "stop_duration_min": 2,
            "is_night": False,
            "speed_kmh": 35,
        },
    )
    body = res.json()
    assert res.status_code == 200
    assert body["risk_level"] == "low"
    assert body["is_anomaly"] is False


def test_risky_journey_is_high_risk_and_anomaly():
    res = client.post(
        "/risk/score",
        json={
            "route_deviation_m": 600,
            "stop_duration_min": 12,
            "is_night": True,
            "speed_kmh": 40,
        },
    )
    body = res.json()
    assert res.status_code == 200
    assert body["risk_level"] == "high"
    assert body["is_anomaly"] is True
    assert any("unusual" in r for r in body["reasons"])
