from claims_intelligence.data.features import build_training_rows
from claims_intelligence.data.synthetic import generate_synthetic_data
from claims_intelligence.monitoring.drift import calculate_drift
from claims_intelligence.training.train import train_model


def test_drift_report_flags_material_numeric_shift(tmp_path) -> None:
    data = generate_synthetic_data(240, 100, seed=24)
    rows = build_training_rows(data.policies, data.claims)
    bundle = train_model(rows, tmp_path / "model.joblib", str(tmp_path / "mlflow.db"), seed=24)

    shifted = rows.copy()
    shifted["initial_estimate"] = shifted["initial_estimate"] * 4
    report = calculate_drift(bundle, shifted)

    assert report["status"] == "investigate"
    assert "initial_estimate" in report["drifted_features"]
