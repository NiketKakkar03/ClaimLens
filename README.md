# Claims Intelligence ML Platform

A learning and portfolio project for ML engineering and ML platform operations, using synthetic personal motor-insurance claims to demonstrate severity predictions and human-review prioritization.

## Current status

The project design, local severity slice, local Spark/Delta lakehouse, and first reviewer web application are implemented. The web release includes React/TypeScript, FastAPI, PostgreSQL, prediction history, human decisions, audit events, and backend role checks. Keycloak login, orchestration, monitoring dashboards, and cloud validation follow in later milestones.

Build the complete data-to-prediction workflow locally first, then deliver the web application and platform capabilities in separate releases. The web application will use React, TypeScript, Vite, FastAPI, PostgreSQL, and locally hosted Keycloak for login. Its first release gives reviewers a shared synthetic claim queue; individual assignments follow later. Avoid personal spending and use real AWS only for reviewed, short-lived credit-funded validation where feasible.

## Run the local severity slice

Requirements: Python 3.12, [uv](https://docs.astral.sh/uv/), and Docker Desktop for the optional container run. These commands do not call paid services.

```bash
make install
make check
make test
make build-local
make serve
```

Open the interactive API documentation at <http://localhost:8000/docs>, readiness at <http://localhost:8000/health/ready>, and Prometheus-format service metrics at <http://localhost:8000/metrics>. Training results are written to `artifacts/model/training-metrics.json` and `artifacts/model/MODEL_CARD.md`; MLflow uses the local database `artifacts/mlflow.db`.

After `make build-local`, the same API can run in a container with `docker compose up --build`. Its host URLs use port `8010` by default so they do not compete with common port-8000 development services; set `CLAIMS_API_PORT` to override it. The later application milestone will add the dashboard, database, and login service to this normal startup path.

To learn the medallion lakehouse flow without a paid Databricks account or a host Java installation, run `make docker-lakehouse` after `make build-local`. It creates local Delta tables under `data/lakehouse`: raw Bronze inputs, validated Silver claims, quarantined invalid claims, and point-in-time Gold features. The container downloads Delta's matching Java packages on its first run, so that first run requires internet access.

For the complete one-command training-to-prediction demonstration, run `make demo`. It trains a small reproducible model, starts the container, waits for model readiness, prints a real prediction and its Prometheus metrics, and leaves the API running for exploration. Stop it with `docker compose down`.

## Run the reviewer web application

Train the local artifact once with `make build-local`, then run `make app`. Open <http://localhost:5174> for the reviewer dashboard. The direct reviewer API and its interactive documentation are available at <http://localhost:8020/docs>. PostgreSQL is internal to the Compose network and is not published to the host.

The current interface uses one local reviewer identity so the workflow is easy to learn. The `CLAIMS_AUTH_MODE=demo` headers are not secure authentication and must not be used outside local development. The next security milestone connects Keycloak login and validated OIDC identity; the API role checks already form the authorization seam it will use.

## Run monitoring and drift checks

Run `make monitoring` to start Prometheus and Grafana alongside inference. Open Grafana at <http://localhost:3001> using the documented local-only credentials `admin` / `local-only-admin`; the provisioned Claims Intelligence Overview dashboard is ready without manual setup. Prometheus is available at <http://localhost:9091>. Run `make drift-report` to write JSON and Markdown results under `artifacts/monitoring/`. The inference incident procedure is in [the runbook](docs/runbooks/inference-api.md).

## Review the AWS plan without spending money

The Terraform foundation is under [`infra/terraform`](infra/terraform/README.md). It defines S3, ECR, IAM, and an optional small EKS environment, but `create_eks` defaults to `false`. Formatting and validation run locally and in CI without creating resources. Do not run `terraform apply` until the account's credits, plan, expected price, access CIDR, and same-day teardown have been reviewed. No AWS resources have been created by this project.

## Documentation

- [MVP completion status](docs/MVP_STATUS.md): requirement-by-requirement implementation evidence and honest post-MVP boundaries.
- [Original project proposal](Project.md): the initial architecture, technology scope, and roadmap. Read with the interview record because some details have changed during design.
- [Confirmed design direction](docs/design-session.md): decisions accepted in the interview and the remaining open questions.
- [Domain glossary](GLOSSARY.md): agreed meanings of claims, predictions, and review terminology.
- [Access-control exploration](docs/access-control-design.md): proposed roles, login options, and access checks, with explicit accepted and unresolved boundaries.
- [Guided demonstration scenarios](docs/demo-scenarios.md): accepted application workflows and the evidence each should produce.
- [Local language-model feasibility](docs/local-llm-feasibility.md): researched options and proposed measurements, explicitly deferred until after the local MVP; no model is selected yet.
- [Architecture](docs/architecture.md): current local data, training, and prediction paths.
- [Synthetic data specification](docs/synthetic-data-specification.md): generated entities, label semantics, and limitations.
- [Threat model](docs/threat-model.md): assets, initial threats, and planned controls.
- [Baseline success metrics](docs/baseline-success-metrics.md): acceptance criteria that later evidence must substantiate.
- [Code guide](docs/CODE_GUIDE.md): file-by-file explanation of implemented scripts and how their logic connects.
- [First local baseline evidence](docs/evidence/local-baseline-2026-10-22.md): recorded candidate comparison, held-out results, verification, and limitations.
- [Local Spark/Delta evidence](docs/evidence/local-lakehouse-2026-10-22.md): measured medallion row counts, issues found, and local container facts.
- [Reviewer application evidence](docs/evidence/reviewer-application-2026-10-22.md): verified UI/API/PostgreSQL workflow, RBAC denial, build results, and current login limitation.
- [Model lifecycle and monitoring evidence](docs/evidence/model-monitoring-2026-10-23.md): three-candidate comparison, MLflow registry verification, drift results, and live dashboard checks.
- [Terraform validation evidence](docs/evidence/terraform-validation-2026-10-23.md): defined AWS resources, local validation, cost gates, and the explicit no-apply boundary.

## Architecture decisions

- [Build locally before validating cloud deployment](docs/adr/0001-local-first-platform.md).
- [Preserve predictions as claim information changes](docs/adr/0002-preserve-advisory-prediction-history.md).
- [Store application records in PostgreSQL alongside the analytical lakehouse](docs/adr/0003-operational-records-in-postgresql.md).
- [Transfer application changes into the lakehouse in batches](docs/adr/0004-batch-application-changes-into-lakehouse.md).
- [Use self-hosted Keycloak for application login](docs/adr/0005-self-hosted-local-identity.md).

## Learning report and evidence

The final report will explain the project in simple language: how each component works, why it was chosen, how requests and data move through the system, what happens during failures, and what was actually demonstrated on AWS. Tests, performance measurements, model evaluations, operational experiments, and limitations will provide supporting evidence as development proceeds.
