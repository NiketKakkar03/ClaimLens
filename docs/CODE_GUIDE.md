# Code guide

This is the navigation map for implemented code. It will grow after every milestone; generated data and model artifacts are deliberately excluded because they can be rebuilt.

## Local severity slice

| File | What it does | Why it exists |
| --- | --- | --- |
| `src/claims_intelligence/config.py` | Reads local paths and the reproducible random seed from environment variables. | Keeps configuration out of business logic. |
| `src/claims_intelligence/domain.py` | Defines the shared review-priority vocabulary. | Prevents different layers from inventing conflicting labels. |
| `src/claims_intelligence/data/synthetic.py` | Generates linked, reproducible synthetic policy and claim records and writes CSV files. | Provides safe data with a known relationship between inputs and severity. |
| `src/claims_intelligence/data/features.py` | Builds model features using only information available at the claim's report time. | Prevents future information from leaking into training. |
| `src/claims_intelligence/data/lakehouse.py` | Uses local Spark and Delta Lake to write raw Bronze data, validated Silver and quarantine data, and point-in-time Gold features. | Teaches the same medallion and time-awareness ideas used by managed lakehouse platforms without requiring a paid account. |
| `src/claims_intelligence/training/train.py` | Uses chronological splits, compares a median baseline with a random forest, records MLflow runs, evaluates the winner, and saves it. | Makes model selection measurable and repeatable. |
| `src/claims_intelligence/training/artifact.py` | Packages preprocessing, model, thresholds, metadata, and one prediction interface in a versioned artifact. | Training and serving use the same transformations and decision rules. |
| `src/claims_intelligence/training/evidence.py` | Writes metrics as JSON and a readable model card. | Preserves results and limitations for later review. |
| `src/claims_intelligence/monitoring/drift.py` | Compares current features with reference statistics stored in the model bundle and writes JSON/Markdown reports. | Turns distribution changes into an investigation signal without automatic retraining. |
| `src/claims_intelligence/serving/schemas.py` | Validates the prediction request and response. | Rejects malformed inputs at the API boundary. |
| `src/claims_intelligence/serving/api.py` | Loads the model and exposes health, metrics, and prediction endpoints. | Turns the trained artifact into an observable service. |
| `src/claims_intelligence/cli.py` | Provides `generate`, `train`, and `build-local` commands. | Gives a learner a short, repeatable interface to the workflow. |
| `tests/unit/test_synthetic.py` | Checks synthetic data reproducibility and relationships. | Detects accidental generator changes. |
| `tests/unit/test_features.py` | Checks point-in-time history, including the rule that an unclosed claim has no known payment. | Guards against training leakage. |
| `tests/integration/test_training_and_api.py` | Trains a real artifact and sends a request through the API. | Proves the local path works end to end. |
| `Dockerfile` | Builds a non-root inference API image. | Creates a portable serving unit. |
| `Dockerfile.spark` | Builds a non-root Java/Python image for the local Spark/Delta job. | Lets a learner run the lakehouse path without installing Java on the host. |
| `docker/requirements-*.txt` | Separates runtime dependencies for inference and Spark container images. | Keeps training-only packages out of serving and makes code-only rebuilds fast. |
| `compose.yaml` | Runs the API with its locally trained artifact and a readiness check. | Makes container testing understandable and repeatable. |
| `Makefile` | Groups common install, validation, training, and serving commands. | Reduces command memorization. |
| `scripts/demo_local.sh` | Trains on 1,000 claims, starts the inference container, waits for readiness, requests a prediction, and prints metrics and access URLs. | Proves the local vertical slice through one learner-facing command. |
| `.github/workflows/ci.yml` | Runs formatting, linting, and tests on pushes and pull requests. | Supplies automated quality evidence. |
| `.github/workflows/drift-report.yml` | Runs the reproducible training and drift report every Monday or on demand, then uploads its evidence. | Demonstrates scheduled monitoring without a paid scheduler. |
| `monitoring/prometheus.yml` | Scrapes inference metrics every five seconds. | Collects the time series used by the dashboard. |
| `monitoring/grafana/dashboards/claims-overview.json` | Defines the version-controlled service dashboard. | Makes monitoring reproducible and accessible through one dashboard. |
| `docs/runbooks/inference-api.md` | Guides diagnosis, safe recovery, verification, and incident evidence. | Connects alerts and metrics to an operational response. |

## AWS infrastructure definition

| File | What it does | Why it exists |
| --- | --- | --- |
| `infra/terraform/versions.tf` | Pins Terraform and the AWS provider and applies ownership tags. | Makes provider behavior and cost attribution repeatable. |
| `infra/terraform/main.tf` | Defines protected S3, immutable ECR, retention, and an optional budget notification. | Supplies the persistent AWS foundation without creating it automatically. |
| `infra/terraform/eks.tf` | Defines optional networking, IAM roles, EKS, and a small Spot node group behind `create_eks`. | Teaches the Kubernetes infrastructure while preventing accidental control-plane charges. |
| `infra/terraform/variables.tf` | Declares region, environment, cost, version, CIDR, and EKS safety gates. | Forces risky or account-specific choices to be visible. |
| `infra/terraform/outputs.tf` | Exposes bucket, repository, and optional cluster identifiers. | Gives later deployment stages stable integration points. |

## Reviewer web application

| File | What it does | Why it exists |
| --- | --- | --- |
| `src/claims_intelligence/application/db.py` | Defines PostgreSQL/SQLite records for claims, immutable prediction history, and audit events. | Keeps workflow state durable and separate from analytical Delta tables. |
| `keycloak/claims-local-realm.json` | Imports the local realm, PKCE client, short token lifetime, roles, event auditing, and disposable users. | Makes the development identity service reproducible. |
| `src/claims_intelligence/application/auth.py` | Validates RS256 tokens against Keycloak's keys and enforces issuer, audience, expiry, required claims, and one application role. | Centralizes authentication and backend authorization; unsigned headers exist only in explicit test mode. |
| `src/claims_intelligence/application/schemas.py` | Defines validated create, decision, prediction, claim, and audit payloads. | Gives the frontend and backend a clear interface. |
| `src/claims_intelligence/application/api.py` | Exposes the shared queue, claim creation, prediction, human decision, and audit endpoints. | Implements the end-to-end reviewer workflow and preserves model/human disagreement. |
| `tests/integration/test_reviewer_application.py` | Exercises claim creation through prediction and decision, then checks audit attribution and a forbidden audit-reader write. | Demonstrates workflow integrity and backend RBAC. |
| `tests/unit/test_auth.py` | Signs controlled JWTs for role, expiry, audience, and forged-signature cases. | Proves token checks without trusting a live identity server. |
| `tests/integration/test_authentication_boundary.py` | Calls the API without a token. | Proves anonymous direct requests are rejected. |
| `frontend/src/auth.ts` | Configures Keycloak, refreshes access tokens, and supplies them to API requests. | Keeps browser login state in one module. |
| `frontend/src/App.tsx` | Renders the queue, claim evidence, prediction history, recommendation, and human decision form and calls the API. | Gives reviewers one coherent operational workspace. |
| `frontend/src/styles.css` | Supplies the responsive visual system and priority states. | Creates a proper, usable web interface without Streamlit. |
| `frontend/Dockerfile` | Builds static React assets and serves them from Nginx. | Produces a small deployable frontend image. |
| `frontend/nginx.conf` | Serves the single-page application and proxies `/api` to FastAPI. | Keeps browser requests same-origin and gives one user-facing URL. |
