import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score

from services.anomaly_model import check_anomaly
from services.risk_engine import JourneySignals, calculate_risk

rng = np.random.default_rng(7)
n_normal, n_anomaly = 900, 100

normal = pd.DataFrame({
    "route_deviation_m": np.abs(rng.normal(120, 120, n_normal)),
    "stop_duration_min": np.abs(rng.normal(3, 3, n_normal)),
    "is_night": (rng.random(n_normal) < 0.35).astype(int),
    "speed_kmh": np.clip(rng.normal(38, 18, n_normal), 0, None),
    "is_anomaly": 0,
})
anomaly = pd.DataFrame({
    "route_deviation_m": rng.uniform(250, 1500, n_anomaly),
    "stop_duration_min": rng.uniform(6, 40, n_anomaly),
    "is_night": (rng.random(n_anomaly) < 0.7).astype(int),
    "speed_kmh": np.where(rng.random(n_anomaly) < 0.5,
                          rng.uniform(80, 140, n_anomaly), rng.uniform(0, 5, n_anomaly)),
    "is_anomaly": 1,
})
df = pd.concat([normal, anomaly]).reset_index(drop=True)

rule_flag, model_flag, combined_flag = [], [], []
for _, r in df.iterrows():
    vals = (r.route_deviation_m, r.stop_duration_min, bool(r.is_night), r.speed_kmh)
    rules = calculate_risk(JourneySignals(*vals))["risk_score"]
    anom = check_anomaly(*vals)
    final = round(0.6 * rules + 0.4 * anom["anomaly_score"])
    rule_flag.append(int(rules >= 30))
    model_flag.append(int(anom["is_anomaly"]))
    combined_flag.append(int(final >= 30))

y = df["is_anomaly"]
print("Harder test set: 900 normal + 100 risky journeys\n")
for name, pred in [("Rules only", rule_flag), ("Anomaly model only", model_flag),
                   ("Combined (final score >= 30)", combined_flag)]:
    tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
    print(f"{name}")
    print(f"  precision={precision_score(y, pred):.2f}  recall={recall_score(y, pred):.2f}  f1={f1_score(y, pred):.2f}")
    print(f"  caught risky: {tp}/100, missed: {fn}, false alarms: {fp}/900\n")
