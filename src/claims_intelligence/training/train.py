"""Train chronological baseline and candidate severity models."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from claims_intelligence.data.features import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
)
from claims_intelligence.training.artifact import ModelBundle


def _sqlite_tracking_uri(value: str) -> str:
    """Return a supported local MLflow URI, upgrading bare paths to SQLite."""
    if "://" in value:
        if value.startswith("sqlite:///"):
            database_path = Path(value.removeprefix("sqlite:///"))
            database_path.parent.mkdir(parents=True, exist_ok=True)
        return value
    database_path = Path(value)
    if database_path.suffix != ".db":
        database_path = database_path / "mlflow.db"
    database_path = database_path.resolve()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{database_path}"


def _source_feature_name(transformed_name: str) -> str:
    for feature in CATEGORICAL_FEATURES:
        if transformed_name.startswith(f"{feature}_"):
            return feature
    return transformed_name


def _metrics(
    y_true: np.ndarray, predicted_log: np.ndarray, high_threshold: float
) -> dict[str, float]:
    predicted = np.maximum(0, np.expm1(predicted_log))
    actual_high = y_true >= high_threshold
    predicted_high = predicted >= high_threshold
    true_positive = int(np.logical_and(actual_high, predicted_high).sum())
    recall = true_positive / max(1, int(actual_high.sum()))
    precision = true_positive / max(1, int(predicted_high.sum()))
    return {
        "mae": float(mean_absolute_error(y_true, predicted)),
        "rmse": float(mean_squared_error(y_true, predicted) ** 0.5),
        "high_severity_recall": float(recall),
        "high_severity_precision": float(precision),
    }


def train_model(
    rows: pd.DataFrame, output_path: Path, tracking_uri: str = "mlruns", seed: int = 42
) -> ModelBundle:
    """Train, compare, log, and save the strongest candidate on chronological data."""
    if len(rows) < 100:
        raise ValueError("Training requires at least 100 rows")
    rows = rows.sort_values("reported_timestamp", ignore_index=True)
    train_end = int(len(rows) * 0.70)
    validation_end = int(len(rows) * 0.85)
    train = rows.iloc[:train_end]
    validation = rows.iloc[train_end:validation_end]
    test = rows.iloc[validation_end:]
    high_threshold = float(train["final_paid_amount"].quantile(0.80))
    urgent_threshold = float(train["final_paid_amount"].quantile(0.95))

    def make_preprocessor() -> ColumnTransformer:
        return ColumnTransformer(
            [
                (
                    "categorical",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    CATEGORICAL_FEATURES,
                )
            ],
            remainder="passthrough",
            verbose_feature_names_out=False,
        )

    candidates = {
        "median_baseline": DummyRegressor(strategy="median"),
        "random_forest": RandomForestRegressor(
            n_estimators=120, min_samples_leaf=3, random_state=seed, n_jobs=-1
        ),
    }
    mlflow.set_tracking_uri(_sqlite_tracking_uri(tracking_uri))
    mlflow.set_experiment("claims-severity-local")
    evaluated: list[tuple[str, Pipeline, dict[str, float]]] = []
    for name, estimator in candidates.items():
        pipeline = Pipeline([("preprocess", make_preprocessor()), ("model", estimator)])
        with mlflow.start_run(run_name=name):
            pipeline.fit(train[FEATURE_COLUMNS], np.log1p(train["final_paid_amount"]))
            metrics = _metrics(
                validation["final_paid_amount"].to_numpy(),
                pipeline.predict(validation[FEATURE_COLUMNS]),
                high_threshold,
            )
            mlflow.log_params({"candidate": name, "seed": seed, "training_rows": len(train)})
            mlflow.log_metrics({f"validation_{key}": value for key, value in metrics.items()})
            evaluated.append((name, pipeline, metrics))

    name, selected, validation_metrics = min(evaluated, key=lambda item: item[2]["mae"])
    candidate_validation_mae = {
        candidate_name: candidate_metrics["mae"]
        for candidate_name, _, candidate_metrics in evaluated
    }
    test_metrics = _metrics(
        test["final_paid_amount"].to_numpy(),
        selected.predict(test[FEATURE_COLUMNS]),
        high_threshold,
    )
    transformed_names = selected.named_steps["preprocess"].get_feature_names_out()
    model = selected.named_steps["model"]
    if hasattr(model, "feature_importances_"):
        importance_order = np.argsort(model.feature_importances_)[::-1]
        top_factors = [
            _source_feature_name(str(transformed_names[index])) for index in importance_order[:10]
        ]
    else:
        top_factors = ["initial_estimate", "damage_indicator_count", "claim_type"]
    top_factors = list(dict.fromkeys(top_factors))
    version = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    bundle = ModelBundle(
        pipeline=selected,
        model_name=f"claims-severity-{name}",
        model_version=version,
        trained_at=datetime.now(UTC).isoformat(),
        feature_columns=FEATURE_COLUMNS,
        high_threshold=high_threshold,
        urgent_threshold=urgent_threshold,
        metrics={
            **{f"validation_{k}": v for k, v in validation_metrics.items()},
            **{f"test_{k}": v for k, v in test_metrics.items()},
        },
        top_factors=top_factors,
        candidate_validation_mae=candidate_validation_mae,
    )
    bundle.save(output_path)
    return bundle
