# Inference API incident runbook

## Trigger

Use this runbook when readiness fails, the five-minute error rate is sustained above 0.5%, or p95 prediction latency exceeds 250 ms under the documented local profile.

## Diagnose

1. Open the Claims Intelligence Grafana dashboard and identify whether the problem is availability, errors, or latency.
2. Run `docker compose ps` and confirm `inference-api` is healthy.
3. Run `docker compose logs --tail=200 inference-api`; never copy request payloads or credentials into an incident record.
4. Call `curl http://localhost:8010/health/ready` and confirm the returned model version.
5. Confirm `artifacts/model/model.joblib` exists and was not partially replaced.

## Recover

1. If the current container is unhealthy but the artifact is intact, run `docker compose restart inference-api`.
2. If a new artifact caused the failure, restore the last reviewed artifact from the recorded release rather than retraining during the incident.
3. Verify readiness, send a synthetic smoke prediction, and watch errors and p95 latency for five minutes.

## Escalation and evidence

This local project has one operator. Record detection time, suspected cause, commands used, recovery time, model version, and follow-up action under `docs/incidents/`. Model drift is not a service outage and follows the monitoring investigation workflow instead.
