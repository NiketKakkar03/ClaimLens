# Claims Intelligence ML Platform

A learning and portfolio project for ML engineering and ML platform operations, using synthetic personal motor-insurance claims to demonstrate severity predictions and human-review prioritization.

## Current status

Design interview in progress. This repository currently contains planning and design documentation; the application, models, pipelines, dashboards, and cloud deployment have not been implemented. Setup commands, application URLs, metrics access, and measured results will be added when they exist.

Build the complete data-to-prediction workflow locally first, then deliver the web application and platform capabilities in separate releases. The web application will use React, TypeScript, Vite, FastAPI, PostgreSQL, and locally hosted Keycloak for login. Its first release gives reviewers a shared synthetic claim queue; individual assignments follow later. Avoid personal spending and use real AWS only for reviewed, short-lived credit-funded validation where feasible.

The planned normal startup runs the application, database, prediction service, and local login service. Separate commands will start training, detailed monitoring, and Kubernetes exercises as needed. Startup commands are not available yet.

## Documentation

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

## Architecture decisions

- [Build locally before validating cloud deployment](docs/adr/0001-local-first-platform.md).
- [Preserve predictions as claim information changes](docs/adr/0002-preserve-advisory-prediction-history.md).
- [Store application records in PostgreSQL alongside the analytical lakehouse](docs/adr/0003-operational-records-in-postgresql.md).
- [Transfer application changes into the lakehouse in batches](docs/adr/0004-batch-application-changes-into-lakehouse.md).
- [Use self-hosted Keycloak for application login](docs/adr/0005-self-hosted-local-identity.md).

## Learning report and evidence

The final report will explain the project in simple language: how each component works, why it was chosen, how requests and data move through the system, what happens during failures, and what was actually demonstrated on AWS. Tests, performance measurements, model evaluations, operational experiments, and limitations will provide supporting evidence as development proceeds.
