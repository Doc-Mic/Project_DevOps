"""Create the API smoke-test payload from the generated one-row sample CSV."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "backend" / "models" / "model_bundle.joblib"
SAMPLE = ROOT / "data" / "sample_inputs.csv"
OUT = ROOT / "backend" / "test_payload.json"


def main() -> None:
    import joblib

    bundle = joblib.load(BUNDLE)
    frame = pd.read_csv(SAMPLE, nrows=1)
    missing = [name for name in bundle["features"] if name not in frame.columns]
    if missing:
        raise ValueError(f"Sample CSV is missing required fields: {missing}")
    row = frame.loc[0, bundle["features"]]
    payload = {name: None if pd.isna(value) else value.item() if hasattr(value, "item") else value for name, value in row.items()}
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Created {OUT} with {len(payload)} fields")


if __name__ == "__main__":
    main()