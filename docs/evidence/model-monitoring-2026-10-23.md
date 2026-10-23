# Model lifecycle and monitoring evidence — 2026-10-23

## Candidate and registry result

The reproducible 1,000-claim run compared three candidates on a chronological validation window.

| Candidate | Validation MAE |
| --- | ---: |
| Median baseline | 4,126.74 |
| Histogram gradient boosting | 1,964.46 |
| Random forest | 1,837.17 |

Random forest remained the selected candidate. MLflow registered it as `claims-severity` version `1`, status `READY`, with alias `local-approved`. The evidence records dataset fingerprint `7e546ca031690273`, parameters, evaluation metrics, and training-reference statistics. A normal committed CI run supplies its Git commit through `GITHUB_SHA`; this local uncommitted verification correctly says `local-working-tree`.

MLflow uses Cloudpickle for the registered pipeline because the selected estimator can differ between runs and histogram gradient boosting contains a type that the safer Skops default refuses. Therefore only artifacts produced by this trusted pipeline may be loaded. Artifact provenance and immutable storage controls remain required before cloud use.

## Drift result

The monitoring job evaluated 1,000 current rows against the saved training reference. No feature crossed its threshold, so status was `within-threshold`. Numeric features use standardized mean shift and categorical features use total-variation distance. A test multiplies `initial_estimate` by four and verifies that the report changes to `investigate`.

Drift is not correctness and does not trigger automatic retraining. The weekly GitHub workflow creates a fresh synthetic run, generates JSON and Markdown reports, and retains them as workflow artifacts for 14 days.

## Dashboard verification

Prometheus reported the `claims-inference` scrape target as `up`. Grafana reported a healthy database and provisioned the `Claims Intelligence Overview` dashboard. It displays prediction request rate, p95 latency, successful and unavailable totals, and scrape-target status.

- Grafana: <http://localhost:3001> (`admin` / `local-only-admin`, local use only)
- Prometheus: <http://localhost:9091>
- Runbook: `docs/runbooks/inference-api.md`
