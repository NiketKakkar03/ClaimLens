"""Versioned HTTP request and response contracts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from claims_intelligence.domain import ClaimType, ReportingChannel, ReviewPriority


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(pattern=r"^clm_[A-Za-z0-9_-]+$")
    policy_tenure_days: float = Field(ge=0)
    claim_type: ClaimType
    reporting_delay_hours: float = Field(ge=0, le=8_760)
    initial_estimate: float = Field(ge=0, le=10_000_000)
    prior_claim_count_365d: int = Field(ge=0, le=100)
    prior_paid_amount_730d: float = Field(default=0, ge=0, le=100_000_000)
    damage_indicator_count: int = Field(ge=0, le=100)
    region_code: str = Field(min_length=2, max_length=40)
    channel: ReportingChannel
    asset_age_years: int = Field(ge=0, le=100)
    coverage_type: str = Field(min_length=2, max_length=40)
    deductible_band: str = Field(min_length=2, max_length=40)


class PredictionResponse(BaseModel):
    claim_id: str
    predicted_severity: float
    priority_band: ReviewPriority
    model_name: str
    model_version: str
    model_alias: str = "local-approved"
    top_factors: list[str]
    prediction_id: str
