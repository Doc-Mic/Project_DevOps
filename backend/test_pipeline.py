"""Run one direct local model prediction against the generated sample."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
bundle = joblib.load(ROOT / "backend" / "models" / "model_bundle.joblib")
payload = json.loads((ROOT / "backend" / "test_payload.json").read_text(encoding="utf-8"))
features = bundle["features"]
if set(payload) != set(features):
    raise AssertionError("Payload fields must exactly match the model schema")
frame = pd.DataFrame([[payload[name] for name in features]], columns=features)
model = bundle["pipeline"]
print("Predicted group:", model.predict(frame)[0])
if hasattr(model, "predict_proba"):
    print("Top class probability:", round(float(model.predict_proba(frame).max()), 4))
print("PASS: local inference")