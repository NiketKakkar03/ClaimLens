# Synthetic data specification

The generator creates personal motor-insurance policies and linked claim records. Every identifier is generated for this project; no source record describes a real person, vehicle, policy, or loss.

## Generation principles

- A fixed seed reproduces identical records.
- Claims always reference an existing policy.
- Policy start precedes incident and report timestamps.
- Final paid amount is generated from a learnable combination of damage indicators, claim type, asset age, reporting delay, and random noise.
- Initial estimate is correlated with final paid amount but remains imperfect.
- Claim closure occurs after reporting, which lets tests verify that paid-history features exclude outcomes unknown at the prediction moment.
- Categorical distributions and monetary formulas are modeling assumptions, not statements about real insurance populations.

## Label and time semantics

`final_paid_amount` is the total synthetic payment known after closure. It is a valid label for a closed claim. The initial model prediction occurs at claim reporting. Any feature derived from another claim must have been observable by that time. A claim may count as a prior report before closure, but its final paid amount cannot contribute to historical paid totals until closure.

## Limitations

Synthetic patterns can make models appear cleaner than real claims data. Results cannot establish production accuracy, fairness, loss reserves, customer outcomes, or business value. The generator exists to exercise engineering, evaluation, drift, and governance workflows safely.
