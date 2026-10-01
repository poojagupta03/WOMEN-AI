from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "anomaly_model.joblib"

_bundle = joblib.load(MODEL_PATH)
_model = _bundle["model"]
_features = _bundle["features"]


def check_anomaly(route_deviation_m, stop_duration_min, is_night, speed_kmh) -> dict:
    row = pd.DataFrame(
        [[route_deviation_m, stop_duration_min, int(is_night), speed_kmh]],
        columns=_features,
    )
    raw = float(_model.decision_function(row)[0])
    is_anomaly = bool(_model.predict(row)[0] == -1)
    anomaly_score = round(min(max((0.1 - raw) / 0.3, 0.0), 1.0) * 100, 1)
    return {"is_anomaly": is_anomaly, "anomaly_score": anomaly_score}
