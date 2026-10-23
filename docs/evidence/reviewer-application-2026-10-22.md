# Reviewer application evidence — 2026-10-22

## Implemented workflow

The first reviewer-facing release runs locally as three containers: an Nginx-served React/TypeScript interface, a FastAPI workflow API, and PostgreSQL. The already trained model artifact is mounted read-only into the API.

The verified browser-facing path was:

1. create synthetic claim `clm_stack_demo`;
2. request a prediction;
3. receive a severity estimate of 9,489.33 and standard recommendation from model version `20261023021811`;
4. record an elevated human-review priority with a reason;
5. retrieve the claim with both the unchanged prediction history and the separate human judgment.

The web server and its `/api` proxy both returned HTTP 200. PostgreSQL and the reviewer API passed their container health checks before the frontend started.

## Access-control evidence

An integration test proves that reviewer actions are attributed in the audit trail and that the audit-reader role receives HTTP 403 when it attempts to create a claim. Backend enforcement is important: hiding a button in React would not prevent a direct API request.

This milestone deliberately uses clearly named `X-Demo-User` and `X-Demo-Role` headers in `CLAIMS_AUTH_MODE=demo`. This is suitable only for local learning. It is **not authentication**, must never be enabled for an exposed environment, and will be replaced by the planned Keycloak/OIDC milestone.

## Automated checks

- Five Python tests pass, including the complete reviewer workflow and read-only denial.
- Python formatting and lint checks pass.
- Frontend ESLint and TypeScript production build pass.
- The production frontend bundle is approximately 192 KB JavaScript before gzip and 61 KB after gzip.
- Docker Compose configuration and live PostgreSQL/API/frontend startup pass.

## Local data note

The Compose password is an intentionally obvious local-only development value. It is not reused elsewhere and is not an example for cloud deployment. A later secrets milestone replaces inline development credentials before any cloud validation.
