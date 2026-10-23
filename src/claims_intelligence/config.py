"""Central configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path(os.getenv("CLAIMS_DATA_DIR", "data/generated"))
    artifact_dir: Path = Path(os.getenv("CLAIMS_ARTIFACT_DIR", "artifacts/model"))
    mlflow_tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///artifacts/mlflow.db")
    random_seed: int = int(os.getenv("CLAIMS_RANDOM_SEED", "42"))


settings = Settings()
