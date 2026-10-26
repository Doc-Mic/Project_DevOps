from __future__ import annotations

from typing import Any

import pandas as pd
import pytest

from backend.app import DISCLAIMER, create_app

FEATURES = ["iyear", "attacktype1"]


class FakeModel:
    classes_ = ["Group A", "Group B"]

    def predict(self, frame: pd.DataFrame):
        assert list(frame.columns) == FEATURES
        return ["Group A"]

    def predict_proba(self, frame: pd.DataFrame):
        return [[0.75, 0.25]]


class FakePipeline:
    named_steps = {"model": FakeModel()}

    def predict(self, frame: pd.DataFrame):
        return self.named_steps["model"].predict(frame)

    def predict_proba(self, frame: pd.DataFrame):
        return self.named_steps["model"].predict_proba(frame)


@pytest.fixture()
def client():
    bundle: dict[str, Any] = {
        "pipeline": FakePipeline(), "features": FEATURES, "task": "multiclass_classification",
        "model_version": "test", "classes": ["Group A", "Group B"],
        "allowed_categories": {"attacktype1": [1, 2]},
        "numeric_bounds": {"iyear": {"min": 1970, "max": 2017}},
    }
    return create_app(bundle).test_client()


def test_health_reports_loaded_model(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["model_loaded"] is True
    assert response.json["features"] == 2


def test_valid_prediction_returns_top_probabilities(client):
    response = client.post("/predict", json={"iyear": 2001, "attacktype1": 1})
    assert response.status_code == 200
    assert response.json["prediction"] == "Group A"
    assert response.json["probabilities"][0] == {"group": "Group A", "probability": 0.75}
    assert "must not be used" in response.json["disclaimer"]


def test_schema_mismatch_is_rejected(client):
    response = client.post("/predict", json={"iyear": 2001})
    assert response.status_code == 400
    assert response.json["missing"] == ["attacktype1"]


def test_invalid_code_and_out_of_range_year_are_rejected(client):
    bad_code = client.post("/predict", json={"iyear": 2001, "attacktype1": 999})
    bad_year = client.post("/predict", json={"iyear": 2060, "attacktype1": 1})
    assert bad_code.status_code == 400
    assert bad_year.status_code == 400


def test_non_json_request_is_rejected(client):
    response = client.post("/predict", data="not json", content_type="text/plain")
    assert response.status_code == 400
    assert response.json["error"] == "Expected a JSON object"


def test_missing_model_returns_clear_service_error():
    client = create_app(load_local=False).test_client()
    assert client.get("/health").status_code == 503
    response = client.post("/predict", json={"iyear": 2001, "attacktype1": 1})
    assert response.status_code == 503
    assert "train_model.py" in response.json["detail"]