"""Construct point-in-time-correct training and serving features."""

from __future__ import annotations

import pandas as pd

FEATURE_COLUMNS = [
    "policy_tenure_days",
    "claim_type",
    "reporting_delay_hours",
    "initial_estimate",
    "prior_claim_count_365d",
    "prior_paid_amount_730d",
    "damage_indicator_count",
    "region_code",
    "channel",
    "asset_age_years",
    "coverage_type",
    "deductible_band",
]

CATEGORICAL_FEATURES = ["claim_type", "region_code", "channel", "coverage_type", "deductible_band"]
NUMERIC_FEATURES = [name for name in FEATURE_COLUMNS if name not in CATEGORICAL_FEATURES]


def build_training_rows(policies: pd.DataFrame, claims: pd.DataFrame) -> pd.DataFrame:
    """Build one row per claim using only information available when it was reported."""
    required_policy = {
        "policy_id",
        "policy_start_date",
        "region_code",
        "asset_age_years",
        "coverage_type",
        "deductible_band",
    }
    required_claim = {
        "claim_id",
        "policy_id",
        "incident_timestamp",
        "reported_timestamp",
        "claim_type",
        "channel",
        "initial_estimate",
        "damage_indicator_count",
        "final_paid_amount",
        "closed_timestamp",
    }
    if missing := required_policy.difference(policies.columns):
        raise ValueError(f"Policies missing columns: {sorted(missing)}")
    if missing := required_claim.difference(claims.columns):
        raise ValueError(f"Claims missing columns: {sorted(missing)}")

    policies = policies.copy()
    claims = claims.copy()
    policies["policy_start_date"] = pd.to_datetime(policies["policy_start_date"], utc=True)
    for column in ("incident_timestamp", "reported_timestamp", "closed_timestamp"):
        claims[column] = pd.to_datetime(claims[column], utc=True)
    claims = claims.sort_values(["policy_id", "reported_timestamp", "claim_id"], ignore_index=True)

    history: dict[str, list[tuple[int, int, float]]] = {}
    prior_count: list[int] = []
    prior_paid: list[float] = []
    for row in claims.itertuples(index=False):
        prediction_time = pd.Timestamp(row.reported_timestamp).value
        one_year_ago = prediction_time - 365 * 86_400 * 1_000_000_000
        two_years_ago = prediction_time - 730 * 86_400 * 1_000_000_000
        prior = history.get(row.policy_id, [])
        prior_count.append(sum(1 for reported_at, _, _ in prior if reported_at >= one_year_ago))
        prior_paid.append(
            sum(
                amount
                for reported_at, closed_at, amount in prior
                if reported_at >= two_years_ago and closed_at <= prediction_time
            )
        )
        history.setdefault(row.policy_id, []).append(
            (
                prediction_time,
                pd.Timestamp(row.closed_timestamp).value,
                float(row.final_paid_amount),
            )
        )

    claims["prior_claim_count_365d"] = prior_count
    claims["prior_paid_amount_730d"] = prior_paid
    rows = claims.merge(policies, on="policy_id", how="left", validate="many_to_one")
    if rows["policy_start_date"].isna().any():
        raise ValueError("Every claim must reference an existing policy")
    rows["policy_tenure_days"] = (
        rows["reported_timestamp"] - rows["policy_start_date"]
    ).dt.total_seconds() / 86_400
    rows["reporting_delay_hours"] = (
        rows["reported_timestamp"] - rows["incident_timestamp"]
    ).dt.total_seconds() / 3_600
    if (rows["policy_tenure_days"] < 0).any() or (rows["reporting_delay_hours"] < 0).any():
        raise ValueError("Policy tenure and reporting delay must be non-negative")
    return rows[
        ["claim_id", "reported_timestamp", "final_paid_amount", *FEATURE_COLUMNS]
    ].sort_values("reported_timestamp", ignore_index=True)
