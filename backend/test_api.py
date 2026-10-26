"""Call the running local Flask service with a generated safe sample."""
from __future__ import annotations

import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
payload = json.loads((ROOT / "backend" / "test_payload.json").read_text(encoding="utf-8"))
with requests.Session() as session:
    session.trust_env = False
    health = session.get("http://127.0.0.1:5000/health", timeout=5)
    health.raise_for_status()
    response = session.post("http://127.0.0.1:5000/predict", json=payload, timeout=30)
    response.raise_for_status()
    result = response.json()
print("Health:", health.json())
print("Prediction:", result["prediction"])
print("Top predictions:", result["probabilities"][:3])
print("PASS: Flask API")