"""Write human-readable and machine-readable evidence for a training run."""

from __future__ import annotations

import json
from pathlib import Path

from claims_intelligence.training.artifact import ModelBundle


def write_training_evidence(bundle: ModelBundle, output_dir: Path) -> None:
    """Persist metrics and a concise model card beside the deployable artifact."""
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence = {
        "model_name": bundle.model_name,
        "model_version": bundle.model_version,
        "trained_at": bundle.trained_at,
        "thresholds": {
            "elevated": bundle.high_threshold,
            "urgent": bundle.urgent_threshold,
        },
        "metrics": bundle.metrics,
        "candidate_validation_mae": bundle.candidate_validation_mae,
        "features": bundle.feature_columns,
        "top_factors": bundle.top_factors,
    }
    (output_dir / "training-metrics.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    metric_lines = "\n".join(
        f"| `{name}` | {value:.2f} |" for name, value in sorted(bundle.metrics.items())
    )
    candidate_lines = "\n".join(
        f"| `{name}` | {value:.2f} |"
        for name, value in sorted(bundle.candidate_validation_mae.items())
    )
    card = f"""# Model card: {bundle.model_name}

## Intended use

This model estimates the eventual paid amount for a synthetic personal motor claim at first
report. Its priority band is an advisory recommendation for a human reviewer; it must not
automatically reject a claim or customer.

## Version

- Model version: `{bundle.model_version}`
- Trained at: `{bundle.trained_at}`
- Elevated threshold: `{bundle.high_threshold:.2f}`
- Urgent threshold: `{bundle.urgent_threshold:.2f}`

## Held-out results

| Metric | Value |
| --- | ---: |
{metric_lines}

## Candidate comparison

Lower validation MAE is better. The saved model is the candidate with the smallest value.

| Candidate | Validation MAE |
| --- | ---: |
{candidate_lines}

## Important limitations

- All training data is synthetic, so results do not establish real-world insurance performance.
- The reported factors are global feature importance hints, not causal explanations.
- Thresholds come from the training distribution and require review before any real use.
- A reviewer remains responsible for decisions; the prediction is stored as evidence, not truth.
"""
    (output_dir / "MODEL_CARD.md").write_text(card, encoding="utf-8")
