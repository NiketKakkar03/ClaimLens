"""Generate reproducible synthetic motor policies and claims."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from claims_intelligence.domain import ClaimType, ReportingChannel


@dataclass(frozen=True)
class GeneratedData:
    policies: pd.DataFrame
    claims: pd.DataFrame


def generate_synthetic_data(
    claim_count: int = 5_000,
    policy_count: int = 2_000,
    seed: int = 42,
) -> GeneratedData:
    """Return linked policies and claims with delayed, learnable outcomes."""
    if claim_count < 100 or policy_count < 50:
        raise ValueError("Generate at least 100 claims and 50 policies for meaningful splits")

    rng = np.random.default_rng(seed)
    policy_ids = np.array([f"pol_{i:06d}" for i in range(policy_count)])
    start = pd.Timestamp("2018-01-01")
    policy_start = start + pd.to_timedelta(rng.integers(0, 1_800, policy_count), unit="D")
    policies = pd.DataFrame(
        {
            "policy_id": policy_ids,
            "policy_start_date": policy_start,
            "coverage_type": rng.choice(
                ["basic", "standard", "comprehensive"], policy_count, p=[0.2, 0.5, 0.3]
            ),
            "deductible_band": rng.choice(
                ["low", "medium", "high"], policy_count, p=[0.25, 0.55, 0.2]
            ),
            "region_code": rng.choice(
                ["ON_METRO", "ON_URBAN", "ON_RURAL", "QC_METRO", "BC_METRO"], policy_count
            ),
            "asset_age_years": rng.integers(0, 19, policy_count),
            "annual_usage_band": rng.choice(
                ["low", "medium", "high"], policy_count, p=[0.25, 0.55, 0.2]
            ),
        }
    )

    chosen_policy = rng.choice(policy_ids, claim_count, replace=True)
    policy_lookup = policies.set_index("policy_id")
    earliest = pd.to_datetime(policy_lookup.loc[chosen_policy, "policy_start_date"].to_numpy())
    incident_offset = rng.integers(30, 2_200, claim_count)
    incident = earliest + pd.to_timedelta(incident_offset, unit="D")
    delay_hours = np.maximum(0.25, rng.lognormal(mean=2.1, sigma=0.9, size=claim_count))
    reported = incident + pd.to_timedelta(delay_hours, unit="h")
    claim_type = rng.choice(
        [item.value for item in ClaimType], claim_count, p=[0.45, 0.1, 0.15, 0.18, 0.12]
    )
    channel = rng.choice(
        [item.value for item in ReportingChannel], claim_count, p=[0.36, 0.28, 0.25, 0.11]
    )
    damage_count = np.clip(rng.poisson(2.2, claim_count), 0, 10)
    asset_age = policy_lookup.loc[chosen_policy, "asset_age_years"].to_numpy()
    type_multiplier = (
        pd.Series(claim_type)
        .map({"collision": 1.25, "theft": 1.65, "weather": 1.1, "glass": 0.32, "liability": 1.9})
        .to_numpy()
    )
    latent_cost = (
        900
        + damage_count * 1_750
        + asset_age * 115
        + delay_hours * 18
        + rng.lognormal(mean=7.3, sigma=0.7, size=claim_count)
    ) * type_multiplier
    final_paid = np.maximum(200, latent_cost * rng.lognormal(mean=0, sigma=0.28, size=claim_count))
    initial_estimate = np.maximum(
        100, final_paid * rng.lognormal(mean=-0.08, sigma=0.35, size=claim_count)
    )
    closure_days = np.clip(rng.gamma(shape=2.2, scale=22, size=claim_count), 2, 240)
    closed_at = reported + pd.to_timedelta(closure_days, unit="D")

    claims = pd.DataFrame(
        {
            "claim_id": [f"clm_{i:07d}" for i in range(claim_count)],
            "policy_id": chosen_policy,
            "incident_timestamp": incident,
            "reported_timestamp": reported,
            "claim_type": claim_type,
            "channel": channel,
            "initial_estimate": initial_estimate.round(2),
            "damage_indicator_count": damage_count,
            "weather_category": rng.choice(
                ["clear", "rain", "snow", "wind"], claim_count, p=[0.55, 0.22, 0.14, 0.09]
            ),
            "final_paid_amount": final_paid.round(2),
            "closed_timestamp": closed_at,
        }
    ).sort_values("reported_timestamp", ignore_index=True)
    return GeneratedData(policies=policies, claims=claims)


def write_synthetic_data(data: GeneratedData, output_dir: Path) -> None:
    """Write source records as CSV files with stable timestamp formatting."""
    output_dir.mkdir(parents=True, exist_ok=True)
    data.policies.to_csv(output_dir / "policies.csv", index=False)
    data.claims.to_csv(output_dir / "claims.csv", index=False)
