from fastapi.testclient import TestClient

from claims_intelligence.application.api import create_reviewer_app
from claims_intelligence.application.db import create_session_factory
from claims_intelligence.data.features import build_training_rows
from claims_intelligence.data.synthetic import generate_synthetic_data
from claims_intelligence.training.train import train_model


def test_reviewer_workflow_and_read_only_role(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("CLAIMS_AUTH_MODE", "test")
    generated = generate_synthetic_data(240, 100, seed=12)
    rows = build_training_rows(generated.policies, generated.claims)
    bundle = train_model(
        rows,
        tmp_path / "model.joblib",
        tracking_uri=str(tmp_path / "mlflow.db"),
        seed=12,
    )
    sessions = create_session_factory(f"sqlite:///{tmp_path / 'application.db'}")
    payload = {
        "claim_id": "clm_reviewer_demo",
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

    with TestClient(create_reviewer_app(sessions, bundle)) as client:
        created = client.post("/api/claims", json=payload)
        assert created.status_code == 201

        predicted = client.post(f"/api/claims/{payload['claim_id']}/predictions")
        assert predicted.status_code == 201
        assert predicted.json()["model_version"] == bundle.model_version

        decision = client.put(
            f"/api/claims/{payload['claim_id']}/decision",
            json={"priority": "elevated", "reason": "Manual inspection needs specialist review"},
        )
        assert decision.status_code == 200
        assert decision.json()["selected_priority"] == "elevated"
        assert len(decision.json()["predictions"]) == 1

        audit = client.get(f"/api/claims/{payload['claim_id']}/audit")
        assert [event["action"] for event in audit.json()] == [
            "claim.created",
            "prediction.requested",
            "review.decision-recorded",
        ]

        denied = client.post(
            "/api/claims",
            json={**payload, "claim_id": "clm_forbidden"},
            headers={"X-Test-Role": "audit-reader", "X-Test-User": "local-auditor"},
        )
        assert denied.status_code == 403
