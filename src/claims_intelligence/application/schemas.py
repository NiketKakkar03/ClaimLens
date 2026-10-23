"""HTTP contracts for reviewer workflow resources."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from claims_intelligence.domain import ReviewPriority
from claims_intelligence.serving.schemas import PredictionRequest


class ClaimCreate(PredictionRequest):
    pass


class ReviewerDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    priority: ReviewPriority
    reason: str = Field(min_length=5, max_length=500)


class PredictionView(BaseModel):
    prediction_id: str
    predicted_severity: float
    priority_band: ReviewPriority
    model_name: str
    model_version: str
    top_factors: list[str]
    created_at: datetime


class ClaimView(BaseModel):
    claim_id: str
    status: str
    features: dict[str, object]
    selected_priority: ReviewPriority | None
    decision_reason: str | None
    created_at: datetime
    updated_at: datetime
    predictions: list[PredictionView]


class AuditView(BaseModel):
    event_id: str
    actor: str
    action: str
    details: dict[str, object]
    created_at: datetime
