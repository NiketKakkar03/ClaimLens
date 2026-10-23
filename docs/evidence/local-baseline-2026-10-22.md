# Local baseline evidence — 2026-10-22

## What was run

The reproducible local pipeline generated 1,000 synthetic claims linked to 500 policies, built point-in-time features, used a chronological 70/15/15 percent train/validation/test split, compared two candidates, and saved the strongest candidate. The random seed was `42`.

Command:

```bash
uv run claims-intelligence build-local --claims 1000 --policies 500
```

## Candidate selection

Mean absolute error (MAE) is the average absolute distance between the predicted and actual synthetic payment. Lower is better.

| Candidate | Validation MAE |
| --- | ---: |
| Median baseline | 4,126.74 |
| Random forest | 1,837.17 |

The random forest was selected because its validation MAE was 2,289.57 lower than the median baseline.

## Unseen test-period results

| Metric | Result |
| --- | ---: |
| MAE | 2,075.94 |
| RMSE | 3,410.44 |
| High-severity recall | 83.33% |
| High-severity precision | 78.12% |

The trained thresholds were 14,274.48 for elevated priority and 22,734.62 for urgent priority. These are experimental thresholds derived from synthetic training data, not production business rules.

## Verification

- Four automated tests passed: synthetic-data reproducibility, point-in-time feature correctness, unclosed-claim leakage protection, and training-to-API integration.
- Ruff formatting and lint checks passed.
- Docker Compose configuration validation passed.
- The API integration test accepted a valid claim and rejected a negative initial estimate with HTTP 422.
- The one-command Docker demonstration returned a standard-priority prediction of 9,489.33, exposed its exact model version, and incremented the Prometheus success counter.

## Interpretation and limitations

These measurements show that the local workflow functions and that the candidate learns the deliberately embedded synthetic signal better than a constant baseline. They do **not** demonstrate performance on real insurance claims. The generated model and complete machine-readable metrics remain under the ignored `artifacts/` directory and can be recreated with the command above.
