# Baseline success metrics

These are initial acceptance criteria. Actual values must be measured and recorded; a target is not a result.

## Local vertical slice

- A fixed seed reproduces identical source data.
- Reprocessing the same source does not duplicate claim identifiers.
- Invalid records are rejected before Gold features are created.
- Leakage tests prove that future claims and not-yet-closed payments cannot influence a training row.
- A chronological train/validation/test split evaluates a median baseline and at least one tree-based candidate.
- The selected artifact records MAE, RMSE, high-severity precision, and high-severity recall.
- The prediction contract rejects missing, extra, and out-of-range fields.
- The response identifies the model version and a valid review priority.
- All automated tests, lint checks, and formatting checks pass.

## Later measured targets

- API p95 latency below 250 ms under the documented load profile, excluding cold start.
- At least 99.5% successful valid requests during the staged load test.
- Drift, delayed-performance, cost, SLO, recovery, and cloud measurements are added only after their corresponding release exists.
