"""FastAPI application factory for severity inference."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from claims_intelligence.serving.schemas import PredictionRequest, PredictionResponse
from claims_intelligence.training.artifact import ModelBundle

REQUESTS = Counter("claims_prediction_requests_total", "Prediction requests", ["status"])
LATENCY = Histogram("claims_prediction_duration_seconds", "Prediction request duration")


def create_app(bundle: ModelBundle | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if bundle is not None:
            app.state.bundle = bundle
        else:
            artifact_path = Path(os.getenv("CLAIMS_MODEL_PATH", "artifacts/model/model.joblib"))
            if artifact_path.exists():
                app.state.bundle = ModelBundle.load(artifact_path)
        yield

    app = FastAPI(title="Claims Intelligence Inference", version="1.0.0", lifespan=lifespan)

    @app.get("/health/live")
    def live() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/health/ready")
    def ready(request: Request) -> dict[str, str]:
        if not hasattr(request.app.state, "bundle"):
            raise HTTPException(status_code=503, detail="Model artifact is not loaded")
        return {"status": "ready", "model_version": request.app.state.bundle.model_version}

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.post("/v1/predictions/claim-severity", response_model=PredictionResponse)
    def predict(payload: PredictionRequest, request: Request) -> PredictionResponse:
        started = perf_counter()
        try:
            model: ModelBundle = request.app.state.bundle
            features = payload.model_dump(exclude={"claim_id"}, mode="json")
            result = model.predict(features)
            REQUESTS.labels(status="success").inc()
            return PredictionResponse(
                claim_id=payload.claim_id,
                predicted_severity=round(result.predicted_severity, 2),
                priority_band=result.priority,
                model_name=model.model_name,
                model_version=model.model_version,
                top_factors=result.top_factors,
                prediction_id=f"pred_{uuid4().hex}",
            )
        except AttributeError as error:
            REQUESTS.labels(status="unavailable").inc()
            raise HTTPException(status_code=503, detail="Model artifact is not loaded") from error
        finally:
            LATENCY.observe(perf_counter() - started)

    return app


app = create_app()
