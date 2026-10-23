# Guided application scenarios

These are accepted demonstration requirements, not completed tests or measured results. Add actual commands, screenshots, and evidence paths as the relevant releases are implemented.

## New claim

Open a preloaded synthetic claim or create one through the form. Save its information, request a prediction, and inspect estimated final cost, recommended review priority, influential inputs, and model version. Initial predictions are informational and support human review.

Capture the claim information version, prediction identifier, model version, timestamp, and displayed result.

## New evidence

Add a meaningful inspection finding to an existing claim and save it. Confirm the interface identifies the prior prediction as based on older information. Request an updated prediction and compare the old and new results with the information available at each moment.

Capture both predictions and the changed information. The direction or size of an estimate change must reflect evaluated model behavior rather than a hardcoded demonstration result.

## Reviewer disagreement

Record a review priority different from the system recommendation, with a reason. Request another prediction and confirm that the reviewer-selected priority and explanation remain available. The application should show any disagreement with the latest recommendation.

Capture the recommendation, the reviewer-selected priority, the reason, and the attributed action history. The reviewer's choice is not automatically a model-training label.

## Prediction service failure and retry

Use a documented, bounded local failure experiment to make prediction temporarily unavailable. Save claim information and attempt a prediction. Confirm that saved information and the last successful prediction remain available, the attempt is identified as failed, and a retry is offered. Restore the service and retry.

Capture the failed attempt, displayed error state, older prediction timestamp, service restoration, and successful retry. The experiment requires scoped prerequisites and cleanup so that the intended prediction failure does not accidentally disable the entire application.
