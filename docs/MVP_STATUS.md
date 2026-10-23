# MVP completion status

Status: **implemented and verified locally** on 2026-10-23.

This status applies to the minimum viable portfolio scope in `Project.md`. It does not claim that the later strong-final-version roadmap or a real AWS deployment is complete.

| MVP requirement | Implementation | Evidence |
| --- | --- | --- |
| Synthetic dataset | Reproducible linked policies and claims with delayed final-payment labels | `tests/unit/test_synthetic.py`, local baseline evidence |
| PySpark Bronze/Silver/Gold | Containerized Spark/Delta pipeline with strict schema, quarantine, and point-in-time Gold features | Local lakehouse evidence |
| MLflow tracking and registry | Candidate runs, selected-model registration, version, alias, dataset fingerprint, code field, parameters, metrics | Model lifecycle evidence |
| Tree model plus baseline | Median baseline, random forest, and histogram gradient boosting compared chronologically | Model card and model lifecycle evidence |
| Dockerized FastAPI | Non-root inference image with readiness, prediction, and metrics endpoints | `make demo`, integration test |
| Terraform S3/ECR/IAM/EKS | Validated cost-gated configuration; EKS defaults off | Terraform validation evidence and green CI |
| GitHub Actions CI | Python, frontend, contract, and Terraform validation jobs | GitHub Actions run `39988497675` |
| Prometheus/Grafana metrics | Live scrape target and provisioned single coherent dashboard | Model lifecycle evidence |
| Scheduled drift report | Weekly/on-demand workflow plus deterministic local report and shifted-data test | `.github/workflows/drift-report.yml`, drift test |
| Model card and runbook | Generated model card and version-controlled inference incident procedure | `artifacts/model/MODEL_CARD.md`, `docs/runbooks/inference-api.md` |

## Additional application capability

The MVP also includes a React/TypeScript reviewer application backed by FastAPI and PostgreSQL. It preserves prediction history, records a separate human priority and reason, emits attributed audit events, and denies writes from the audit-reader role. This exceeds the original platform-only MVP requirement but remains local-first.

## Honest boundaries

- AWS resources have not been created. Terraform was initialized, formatted, validated locally, and validated in CI. A credentialed plan and short-lived apply require a separate cost review.
- Demo identity headers are not real authentication. Keycloak/OIDC remains a post-MVP security milestone.
- Synthetic performance is evidence of pipeline behavior, not real insurance performance.
- The current drift job creates investigation evidence; it does not automatically retrain or promote models.
- Kubernetes deployment, HPA, rollback, GitOps, recovery drills, delayed-label monitoring, and GenAI remain post-MVP roadmap work.

## Primary commands

```bash
make install
make check
make test
make build-local
make docker-lakehouse
make demo
make app
make monitoring
make drift-report
```

See `README.md` for URLs and `docs/CODE_GUIDE.md` for a file-by-file explanation of the implementation.
