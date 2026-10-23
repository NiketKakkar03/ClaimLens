"""Train chronological baseline and candidate severity models."""

from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
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
        "hist_gradient_boosting": HistGradientBoostingRegressor(
            max_iter=150, max_leaf_nodes=31, learning_rate=0.08, random_state=seed
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
    reference_statistics = {
        feature: {
            "mean": float(train[feature].mean()),
            "std": float(train[feature].std()),
            "quantiles": [
                float(value) for value in train[feature].quantile([0, 0.25, 0.5, 0.75, 1])
            ],
        }
        for feature in FEATURE_COLUMNS
        if feature not in CATEGORICAL_FEATURES
    }
    reference_statistics.update(
        {
            feature: {
                "frequencies": {
                    str(key): float(value)
                    for key, value in train[feature].value_counts(normalize=True).items()
                }
            }
            for feature in CATEGORICAL_FEATURES
        }
    )
    dataset_version = hashlib.sha256(
        pd.util.hash_pandas_object(rows, index=True).values.tobytes()
    ).hexdigest()[:16]
    code_version = os.getenv("GITHUB_SHA", "local-working-tree")
    with mlflow.start_run(run_name="selected-model-registration"):
        mlflow.log_params(
            {
                "selected_candidate": name,
                "dataset_version": dataset_version,
                "code_version": code_version,
                "seed": seed,
            }
        )
        mlflow.log_metrics({f"test_{key}": value for key, value in test_metrics.items()})
        model_info = mlflow.sklearn.log_model(
            sk_model=selected,
            name="model",
            registered_model_name="claims-severity",
            serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE,
        )
    registry_version = str(model_info.registered_model_version)
    mlflow.MlflowClient().set_registered_model_alias(
        "claims-severity", "local-approved", registry_version
    )
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
        reference_statistics=reference_statistics,
        dataset_version=dataset_version,
        code_version=code_version,
        registry_version=registry_version,
    )
    bundle.save(output_path)
    return bundle
