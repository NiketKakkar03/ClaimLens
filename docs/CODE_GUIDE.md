# Code guide

This is the navigation map for implemented code. It will grow after every milestone; generated data and model artifacts are deliberately excluded because they can be rebuilt.

## Local severity slice

| File | What it does | Why it exists |
| --- | --- | --- |
| `src/claims_intelligence/config.py` | Reads local paths and the reproducible random seed from environment variables. | Keeps configuration out of business logic. |
| `src/claims_intelligence/domain.py` | Defines the shared review-priority vocabulary. | Prevents different layers from inventing conflicting labels. |
| `src/claims_intelligence/data/synthetic.py` | Generates linked, reproducible synthetic policy and claim records and writes CSV files. | Provides safe data with a known relationship between inputs and severity. |
| `src/claims_intelligence/data/features.py` | Builds model features using only information available at the claim's report time. | Prevents future information from leaking into training. |
| `src/claims_intelligence/training/train.py` | Uses chronological splits, compares a median baseline with a random forest, records MLflow runs, evaluates the winner, and saves it. | Makes model selection measurable and repeatable. |
| `src/claims_intelligence/training/artifact.py` | Packages preprocessing, model, thresholds, metadata, and one prediction interface in a versioned artifact. | Training and serving use the same transformations and decision rules. |
| `src/claims_intelligence/training/evidence.py` | Writes metrics as JSON and a readable model card. | Preserves results and limitations for later review. |
| `src/claims_intelligence/serving/schemas.py` | Validates the prediction request and response. | Rejects malformed inputs at the API boundary. |
| `src/claims_intelligence/serving/api.py` | Loads the model and exposes health, metrics, and prediction endpoints. | Turns the trained artifact into an observable service. |
| `src/claims_intelligence/cli.py` | Provides `generate`, `train`, and `build-local` commands. | Gives a learner a short, repeatable interface to the workflow. |
| `tests/unit/test_synthetic.py` | Checks synthetic data reproducibility and relationships. | Detects accidental generator changes. |
| `tests/unit/test_features.py` | Checks point-in-time history, including the rule that an unclosed claim has no known payment. | Guards against training leakage. |
| `tests/integration/test_training_and_api.py` | Trains a real artifact and sends a request through the API. | Proves the local path works end to end. |
| `Dockerfile` | Builds a non-root inference API image. | Creates a portable serving unit. |
| `compose.yaml` | Runs the API with its locally trained artifact and a readiness check. | Makes container testing understandable and repeatable. |
| `Makefile` | Groups common install, validation, training, and serving commands. | Reduces command memorization. |
| `.github/workflows/ci.yml` | Runs formatting, linting, and tests on pushes and pull requests. | Supplies automated quality evidence. |
