"""Local Flask API for the GTD research classifier."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from flask import Flask, jsonify, request

MODEL_PATH = Path(__file__).resolve().parent / "models" / "model_bundle.joblib"
DISCLAIMER = (
    "Research and teaching prototype using historical GTD records. Predictions are uncertain, "
    "retrospective classifications and must not be used for operational, legal, or security decisions."
)


def load_bundle() -> dict[str, Any] | None:
    if not MODEL_PATH.is_file():
        return None
    return joblib.load(MODEL_PATH)


def create_app(bundle: dict[str, Any] | None = None, *, load_local: bool = True) -> Flask:
    app = Flask(__name__)
    loaded = load_bundle() if bundle is None and load_local else bundle

    @app.get("/health")
    def health():
        return jsonify(
            status="ok" if loaded else "model_unavailable",
            model_loaded=loaded is not None,
            features=len(loaded["features"]) if loaded else 0,
            task=loaded["task"] if loaded else "multiclass_classification",
            model_version=loaded["model_version"] if loaded else None,
        ), (200 if loaded else 503)

    @app.post("/predict")
    def predict():
        if loaded is None:
            return jsonify(error="Model bundle is not available", detail="Run python backend/train_model.py first."), 503
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error="Expected a JSON object"), 400
        features = loaded["features"]
        missing = [name for name in features if name not in data]
        extra = [name for name in data if name not in features]
        if missing or extra:
            return jsonify(error="Input schema mismatch", missing=missing, extra=extra), 400

        categories = loaded.get("allowed_categories", {})
        bounds = loaded.get("numeric_bounds", {})
        values: dict[str, float] = {}
        for name in features:
            value = data[name]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                return jsonify(error="Invalid input", detail=f"{name} must be a finite number"), 400
            numeric = float(value)
            if name in categories:
                if not numeric.is_integer() or int(numeric) not in categories[name]:
                    return jsonify(error="Invalid input", detail=f"{name} must be one of the listed GTD codes"), 400
                values[name] = int(numeric)
            else:
                rule = bounds.get(name, {})
                if rule and (numeric < rule["min"] or numeric > rule["max"]):
                    return jsonify(error="Invalid input", detail=f"{name} is outside the trained data range"), 400
                values[name] = numeric

        try:
            frame = pd.DataFrame([[values[name] for name in features]], columns=features)
            model = loaded["pipeline"]
            prediction = str(model.predict(frame)[0])
            probabilities = []
            if hasattr(model, "predict_proba"):
                scores = model.predict_proba(frame)[0]
                classes = model.named_steps["model"].classes_ if hasattr(model, "named_steps") else model.classes_
                order = sorted(range(len(scores)), key=lambda i: float(scores[i]), reverse=True)[:5]
                probabilities = [
                    {"group": str(classes[i]), "probability": round(float(scores[i]), 6)} for i in order
                ]
            return jsonify(
                prediction=prediction,
                task=loaded["task"],
                probabilities=probabilities,
                disclaimer=DISCLAIMER,
            )
        except (ValueError, TypeError) as exc:
            return jsonify(error="Invalid input", detail=str(exc)), 400
        except Exception:
            app.logger.exception("Prediction failed")
            return jsonify(error="Prediction processing failed"), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)