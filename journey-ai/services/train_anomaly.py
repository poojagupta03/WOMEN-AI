import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

FEATURES = ["route_deviation_m", "stop_duration_min", "is_night", "speed_kmh"]

df = pd.read_csv("data/journeys.csv")
X = df[FEATURES]
y = df["is_anomaly"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = IsolationForest(n_estimators=200, contamination=0.05, random_state=42)
model.fit(X_train)

pred = (model.predict(X_test) == -1).astype(int)
print(classification_report(y_test, pred, target_names=["normal", "anomaly"]))

joblib.dump({"model": model, "features": FEATURES}, "models/anomaly_model.joblib")
print("Saved models/anomaly_model.joblib")
