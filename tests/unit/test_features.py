import pandas as pd

from claims_intelligence.data.features import build_training_rows


def test_prior_claim_features_exclude_current_and_future_claims() -> None:
    policies = pd.DataFrame(
        [
            {
                "policy_id": "pol_1",
                "policy_start_date": "2020-01-01",
                "region_code": "ON_METRO",
                "asset_age_years": 4,
                "coverage_type": "standard",
                "deductible_band": "medium",
            }
        ]
    )
    claims = pd.DataFrame(
        [
            {
                "claim_id": "clm_1",
                "policy_id": "pol_1",
                "incident_timestamp": "2024-01-01",
                "reported_timestamp": "2024-01-02",
                "claim_type": "collision",
                "channel": "web",
                "initial_estimate": 1000,
                "damage_indicator_count": 1,
                "final_paid_amount": 1200,
                "closed_timestamp": "2024-01-20",
            },
            {
                "claim_id": "clm_2",
                "policy_id": "pol_1",
                "incident_timestamp": "2024-02-01",
                "reported_timestamp": "2024-02-02",
                "claim_type": "collision",
                "channel": "web",
                "initial_estimate": 2000,
                "damage_indicator_count": 2,
                "final_paid_amount": 2400,
                "closed_timestamp": "2024-03-10",
            },
        ]
    )
    rows = build_training_rows(policies, claims)
    assert rows.loc[0, "prior_claim_count_365d"] == 0
    assert rows.loc[0, "prior_paid_amount_730d"] == 0
    assert rows.loc[1, "prior_claim_count_365d"] == 1
    assert rows.loc[1, "prior_paid_amount_730d"] == 1200


def test_prior_paid_amount_excludes_claim_not_closed_at_prediction_time() -> None:
    policies = pd.DataFrame(
        [
            {
                "policy_id": "pol_1",
                "policy_start_date": "2020-01-01",
                "region_code": "ON_METRO",
                "asset_age_years": 4,
                "coverage_type": "standard",
                "deductible_band": "medium",
            }
        ]
    )
    claims = pd.DataFrame(
        [
            {
                "claim_id": "clm_1",
                "policy_id": "pol_1",
                "incident_timestamp": "2024-01-01",
                "reported_timestamp": "2024-01-02",
                "claim_type": "collision",
                "channel": "web",
                "initial_estimate": 1000,
                "damage_indicator_count": 1,
                "final_paid_amount": 1200,
                "closed_timestamp": "2024-04-01",
            },
            {
                "claim_id": "clm_2",
                "policy_id": "pol_1",
                "incident_timestamp": "2024-02-01",
                "reported_timestamp": "2024-02-02",
                "claim_type": "collision",
                "channel": "web",
                "initial_estimate": 2000,
                "damage_indicator_count": 2,
                "final_paid_amount": 2400,
                "closed_timestamp": "2024-05-01",
            },
        ]
    )
    rows = build_training_rows(policies, claims)
    assert rows.loc[1, "prior_claim_count_365d"] == 1
    assert rows.loc[1, "prior_paid_amount_730d"] == 0
