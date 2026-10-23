"""Deterministic feature-drift report using model-bundled reference statistics."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from claims_intelligence.data.features import CATEGORICAL_FEATURES
from claims_intelligence.training.artifact import ModelBundle


def _numeric_shift(series: pd.Series, reference: dict) -> float:
    reference_std = max(float(reference["std"]), 1e-9)
    return abs(float(series.mean()) - float(reference["mean"])) / reference_std


def _categorical_shift(series: pd.Series, reference: dict) -> float:
    observed = series.astype(str).value_counts(normalize=True).to_dict()
    expected = reference["frequencies"]
    categories = set(observed) | set(expected)
    return 0.5 * sum(abs(observed.get(key, 0.0) - expected.get(key, 0.0)) for key in categories)


def calculate_drift(bundle: ModelBundle, rows: pd.DataFrame) -> dict:
    """Compare a current feature window with training reference statistics."""
    feature_results: dict[str, dict[str, float | str | bool]] = {}
    for feature, reference in bundle.reference_statistics.items():
        if feature in CATEGORICAL_FEATURES:
            score = _categorical_shift(rows[feature], reference)
            threshold = 0.20
            method = "total_variation_distance"
        else:
            score = _numeric_shift(rows[feature], reference)
            threshold = 0.50
            method = "standardized_mean_shift"
        feature_results[feature] = {
            "method": method,
            "score": float(score),
            "threshold": threshold,
            "drifted": bool(score >= threshold),
        }
    drifted = sorted(name for name, result in feature_results.items() if result["drifted"])
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "model_version": bundle.model_version,
        "rows_evaluated": len(rows),
        "status": "investigate" if drifted else "within-threshold",
        "drifted_features": drifted,
        "features": feature_results,
    }


def write_drift_report(report: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "drift-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    rows = "\n".join(
        f"| `{name}` | {result['method']} | {result['score']:.3f} | "
        f"{result['threshold']:.2f} | {'yes' if result['drifted'] else 'no'} |"
        for name, result in sorted(report["features"].items())
    )
    markdown = f"""# Drift report

- Generated: `{report["generated_at"]}`
- Model version: `{report["model_version"]}`
- Rows evaluated: {report["rows_evaluated"]}
- Status: **{report["status"]}**

Drift is an investigation signal. It does not automatically retrain or promote a model.

| Feature | Method | Score | Threshold | Drifted |
| --- | --- | ---: | ---: | --- |
{rows}
"""
    (output_dir / "DRIFT_REPORT.md").write_text(markdown, encoding="utf-8")
