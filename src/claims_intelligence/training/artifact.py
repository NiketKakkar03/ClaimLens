"""Stable model bundle shared by training and serving."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from claims_intelligence.domain import ReviewPriority


@dataclass
class Prediction:
    predicted_severity: float
    priority: ReviewPriority
    top_factors: list[str]


@dataclass
class ModelBundle:
    pipeline: Any
    model_name: str
    model_version: str
    trained_at: str
    feature_columns: list[str]
    high_threshold: float
    urgent_threshold: float
    metrics: dict[str, float]
    top_factors: list[str]
    candidate_validation_mae: dict[str, float]

    def predict(self, features: dict[str, Any]) -> Prediction:
        missing = sorted(set(self.feature_columns).difference(features))
        if missing:
            raise ValueError(f"Missing model features: {missing}")
        frame = pd.DataFrame([{name: features[name] for name in self.feature_columns}])
        predicted = float(np.expm1(self.pipeline.predict(frame)[0]))
        predicted = max(0.0, predicted)
        if predicted >= self.urgent_threshold:
            priority = ReviewPriority.URGENT
        elif predicted >= self.high_threshold:
            priority = ReviewPriority.ELEVATED
        else:
            priority = ReviewPriority.STANDARD
        return Prediction(predicted, priority, self.top_factors[:3])

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: Path) -> ModelBundle:
        bundle = joblib.load(path)
        if not isinstance(bundle, cls):
            raise TypeError(f"Artifact at {path} is not a ModelBundle")
        return bundle
