import json
from pathlib import Path

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

from claims_intelligence.data.features import build_training_rows
from claims_intelligence.data.synthetic import generate_synthetic_data
from claims_intelligence.serving.api import create_app
from claims_intelligence.training.artifact import ModelBundle
from claims_intelligence.training.evidence import write_training_evidence
from claims_intelligence.training.train import train_model


def test_trained_artifact_serves_prediction(tmp_path) -> None:
    data = generate_synthetic_data(240, 100, seed=9)
    rows = build_training_rows(data.policies, data.claims)
    artifact = tmp_path / "model.joblib"
    bundle = train_model(rows, artifact, tracking_uri=str(tmp_path / "mlflow.db"), seed=9)
    loaded = ModelBundle.load(artifact)
    write_training_evidence(loaded, tmp_path)
    assert (tmp_path / "training-metrics.json").exists()
    assert (tmp_path / "MODEL_CARD.md").exists()
    assert set(loaded.candidate_validation_mae) == {"median_baseline", "random_forest"}
    payload = {
        "claim_id": "clm_demo_1042",
        "policy_tenure_days": 842,
        "claim_type": "collision",
        "reporting_delay_hours": 4.5,
        "initial_estimate": 7200,
        "prior_claim_count_365d": 1,
        "prior_paid_amount_730d": 1500,
        "damage_indicator_count": 3,
        "region_code": "ON_METRO",
        "channel": "mobile",
        "asset_age_years": 5,
        "coverage_type": "standard",
        "deductible_band": "medium",
    }
    request_contract = json.loads(Path("contracts/prediction_request.schema.json").read_text())
    Draft202012Validator(request_contract).validate(payload)
    with TestClient(create_app(loaded)) as client:
        response = client.post("/v1/predictions/claim-severity", json=payload)
        assert response.status_code == 200
        body = response.json()
        response_contract = json.loads(
            Path("contracts/prediction_response.schema.json").read_text()
        )
        Draft202012Validator(response_contract).validate(body)
        assert body["claim_id"] == payload["claim_id"]
        assert body["predicted_severity"] >= 0
        assert body["priority_band"] in {"standard", "elevated", "urgent"}
        assert body["model_version"] == bundle.model_version

        invalid = client.post(
            "/v1/predictions/claim-severity", json={**payload, "initial_estimate": -1}
        )
        assert invalid.status_code == 422
