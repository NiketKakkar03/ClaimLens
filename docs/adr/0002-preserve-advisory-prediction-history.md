# Preserve predictions as claim information changes

The initial prediction for a synthetic personal motor claim is informational. A later required release produces updated predictions when meaningful new claim information arrives, preserving the earlier predictions together with the information and model version used. This supports an understandable history of why estimates changed at different points in the claim's lifecycle.

Review-priority changes remain recommendations for human review. The application does not accept or reject customers or decide coverage. Priority uses estimated final cost and transparent operational rules; retraining is considered when new labeled data or a meaningful evaluated performance problem warrants it, with testing and approval before replacement.

Reviewers save information and explicitly request an updated prediction. A newer model recommendation does not overwrite the reviewer's selected priority or explanation. A failed prediction preserves saved information and the last successful result, labels the failed attempt, and allows retry; the older prediction remains linked to its original information and date.

Preserving history requires more storage and lifecycle design than keeping only the latest score, but makes changes reviewable. PostgreSQL stores the operational history. Detailed update triggers and the remaining reviewer actions are still open design decisions.
