"""Human-facing commands for the local vertical slice."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from claims_intelligence.config import settings
from claims_intelligence.data.features import build_training_rows
from claims_intelligence.data.synthetic import generate_synthetic_data, write_synthetic_data
from claims_intelligence.training.evidence import write_training_evidence
from claims_intelligence.training.train import train_model

app = typer.Typer(no_args_is_help=True)


@app.command()
def generate(claims: int = 5_000, policies: int = 2_000, output: Path = settings.data_dir) -> None:
    """Generate linked synthetic motor policy and claim records."""
    data = generate_synthetic_data(
        claim_count=claims, policy_count=policies, seed=settings.random_seed
    )
    write_synthetic_data(data, output)
    typer.echo(f"Generated {len(data.claims)} claims and {len(data.policies)} policies in {output}")


@app.command()
def train(
    data_dir: Path = settings.data_dir, artifact: Path = settings.artifact_dir / "model.joblib"
) -> None:
    """Build point-in-time features, compare models, and save the selected bundle."""
    policies = pd.read_csv(data_dir / "policies.csv")
    claims = pd.read_csv(data_dir / "claims.csv")
    rows = build_training_rows(policies, claims)
    bundle = train_model(
        rows, artifact, tracking_uri=settings.mlflow_tracking_uri, seed=settings.random_seed
    )
    write_training_evidence(bundle, artifact.parent)
    typer.echo(f"Saved {bundle.model_name} version {bundle.model_version} to {artifact}")
    typer.echo(f"Test MAE: {bundle.metrics['test_mae']:.2f}")


@app.command("build-local")
def build_local(claims: int = 5_000, policies: int = 2_000) -> None:
    """Generate data and train the local model in one repeatable command."""
    data = generate_synthetic_data(
        claim_count=claims, policy_count=policies, seed=settings.random_seed
    )
    write_synthetic_data(data, settings.data_dir)
    rows = build_training_rows(data.policies, data.claims)
    artifact = settings.artifact_dir / "model.joblib"
    bundle = train_model(
        rows, artifact, tracking_uri=settings.mlflow_tracking_uri, seed=settings.random_seed
    )
    write_training_evidence(bundle, artifact.parent)
    typer.echo(f"Local slice ready: {bundle.model_name} version {bundle.model_version}")
    typer.echo(f"Artifact: {artifact}; test MAE: {bundle.metrics['test_mae']:.2f}")
