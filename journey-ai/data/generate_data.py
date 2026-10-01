import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

n_normal = 950
n_anomaly = 50

normal = pd.DataFrame({
    "route_deviation_m": np.abs(rng.normal(50, 40, n_normal)),
    "stop_duration_min": np.abs(rng.normal(2, 1.5, n_normal)),
    "is_night": (rng.random(n_normal) < 0.2).astype(int),
    "speed_kmh": np.clip(rng.normal(35, 12, n_normal), 0, None),
    "is_anomaly": 0,
})

fast = rng.random(n_anomaly) < 0.5
anomaly = pd.DataFrame({
    "route_deviation_m": rng.uniform(400, 1500, n_anomaly),
    "stop_duration_min": rng.uniform(10, 40, n_anomaly),
    "is_night": (rng.random(n_anomaly) < 0.7).astype(int),
    "speed_kmh": np.where(fast, rng.uniform(90, 140, n_anomaly), rng.uniform(0, 3, n_anomaly)),
    "is_anomaly": 1,
})

df = pd.concat([normal, anomaly]).sample(frac=1, random_state=42).reset_index(drop=True)
df = df.round(1)
df.to_csv("data/journeys.csv", index=False)
print(f"Saved data/journeys.csv: {len(df)} rows, {int(df['is_anomaly'].sum())} anomalies")
