"""FastAPI reviewer workflow with persistence, prediction history, and RBAC."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from claims_intelligence.application.auth import Actor, current_actor, require_writer
from claims_intelligence.application.db import (
    AuditEvent,
    ClaimRecord,
    PredictionRecord,
    create_session_factory,
    utc_now,
)
from claims_intelligence.application.schemas import (
    AuditView,
    ClaimCreate,
    ClaimView,
    PredictionView,
    ReviewerDecision,
)
from claims_intelligence.training.artifact import ModelBundle

ActorDependency = Annotated[Actor, Depends(current_actor)]


def _claim_view(claim: ClaimRecord) -> ClaimView:
    return ClaimView(
        claim_id=claim.claim_id,
        status=claim.status,
        features=claim.features,
        selected_priority=claim.selected_priority,
        decision_reason=claim.decision_reason,
        created_at=claim.created_at,
        updated_at=claim.updated_at,
        predictions=[
            PredictionView(
                prediction_id=item.prediction_id,
                predicted_severity=item.predicted_severity,
                priority_band=item.priority_band,
                model_name=item.model_name,
                model_version=item.model_version,
                top_factors=item.top_factors,
                created_at=item.created_at,
            )
            for item in claim.predictions
        ],
    )


def create_reviewer_app(
    sessions: sessionmaker | None = None, bundle: ModelBundle | None = None
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.sessions = sessions or create_session_factory()
        artifact = Path("artifacts/model/model.joblib")
        app.state.bundle = bundle or (ModelBundle.load(artifact) if artifact.exists() else None)
        yield

    app = FastAPI(title="Claims Reviewer Application API", version="1.0.0", lifespan=lifespan)

    @app.get("/health/ready")
    def ready(request: Request) -> dict[str, str]:
        if request.app.state.bundle is None:
            raise HTTPException(status_code=503, detail="Model artifact is not loaded")
        return {"status": "ready", "model_version": request.app.state.bundle.model_version}

    @app.get("/api/claims", response_model=list[ClaimView])
    def list_claims(request: Request, actor: ActorDependency) -> list[ClaimView]:
        del actor
        with request.app.state.sessions() as session:
            claims = session.scalars(
                select(ClaimRecord).order_by(ClaimRecord.updated_at.desc())
            ).all()
            return [_claim_view(claim) for claim in claims]

    @app.get("/api/session")
    def session_identity(actor: ActorDependency) -> dict[str, str]:
        return {"subject": actor.subject, "username": actor.username, "role": actor.role.value}

    @app.post("/api/claims", response_model=ClaimView, status_code=201)
    def create_claim(payload: ClaimCreate, request: Request, actor: ActorDependency) -> ClaimView:
        require_writer(actor)
        now = utc_now()
        features = payload.model_dump(exclude={"claim_id"}, mode="json")
        with request.app.state.sessions() as session:
            if session.get(ClaimRecord, payload.claim_id):
                raise HTTPException(status_code=409, detail="Claim already exists")
            claim = ClaimRecord(
                claim_id=payload.claim_id,
                features=features,
                created_at=now,
                updated_at=now,
            )
            session.add(claim)
            session.add(
                AuditEvent(
                    event_id=f"evt_{uuid4().hex}",
                    claim_id=claim.claim_id,
                    actor=actor.subject,
                    action="claim.created",
                    details={},
                    created_at=now,
                )
            )
            session.commit()
            return _claim_view(claim)

    @app.post("/api/claims/{claim_id}/predictions", response_model=PredictionView, status_code=201)
    def predict_claim(claim_id: str, request: Request, actor: ActorDependency) -> PredictionView:
        require_writer(actor)
        with request.app.state.sessions() as session:
            claim = session.get(ClaimRecord, claim_id)
            if claim is None:
                raise HTTPException(status_code=404, detail="Claim not found")
            bundle: ModelBundle | None = request.app.state.bundle
            if bundle is None:
                raise HTTPException(status_code=503, detail="Prediction service is unavailable")
            result = bundle.predict(claim.features)
            now = utc_now()
            record = PredictionRecord(
                prediction_id=f"pred_{uuid4().hex}",
                claim_id=claim_id,
                predicted_severity=round(result.predicted_severity, 2),
                priority_band=result.priority.value,
                model_name=bundle.model_name,
                model_version=bundle.model_version,
                top_factors=result.top_factors,
                input_snapshot=claim.features,
                created_at=now,
            )
            claim.updated_at = now
            session.add(record)
            session.add(
                AuditEvent(
                    event_id=f"evt_{uuid4().hex}",
                    claim_id=claim_id,
                    actor=actor.subject,
                    action="prediction.requested",
                    details={"prediction_id": record.prediction_id},
                    created_at=now,
                )
            )
            session.commit()
            return PredictionView.model_validate(record, from_attributes=True)

    @app.put("/api/claims/{claim_id}/decision", response_model=ClaimView)
    def decide_claim(
        claim_id: str,
        payload: ReviewerDecision,
        request: Request,
        actor: ActorDependency,
    ) -> ClaimView:
        require_writer(actor)
        with request.app.state.sessions() as session:
            claim = session.get(ClaimRecord, claim_id)
            if claim is None:
                raise HTTPException(status_code=404, detail="Claim not found")
            now = utc_now()
            claim.selected_priority = payload.priority.value
            claim.decision_reason = payload.reason
            claim.updated_at = now
            session.add(
                AuditEvent(
                    event_id=f"evt_{uuid4().hex}",
                    claim_id=claim_id,
                    actor=actor.subject,
                    action="review.decision-recorded",
                    details={"priority": payload.priority.value, "reason": payload.reason},
                    created_at=now,
                )
            )
            session.commit()
            return _claim_view(claim)

    @app.get("/api/claims/{claim_id}/audit", response_model=list[AuditView])
    def claim_audit(claim_id: str, request: Request, actor: ActorDependency) -> list[AuditView]:
        del actor
        with request.app.state.sessions() as session:
            events = session.scalars(
                select(AuditEvent)
                .where(AuditEvent.claim_id == claim_id)
                .order_by(AuditEvent.created_at)
            ).all()
            return [AuditView.model_validate(event, from_attributes=True) for event in events]

    return app


app = create_reviewer_app()
