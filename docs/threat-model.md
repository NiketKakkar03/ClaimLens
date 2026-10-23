# Threat model

## Assets

- Model artifacts and approval state
- Application sessions and demonstration accounts
- Claim records, prediction history, and audit history
- MLflow experiment metadata
- Infrastructure and deployment credentials introduced in later releases

## Initial threats and controls

| Threat | Initial control |
| --- | --- |
| Malformed or oversized prediction input | Strict Pydantic schema, range limits, unknown-field rejection, request-size limit at deployment |
| Caller selects an unapproved model | Server-controlled artifact path and explicit approval workflow |
| Sensitive request data appears in logs | Structured metadata only; never log full request bodies |
| Training uses future outcomes | Point-in-time feature tests and chronological splits |
| Tampered or incompatible artifact | Versioned immutable artifact, metadata checks, later digest/signature verification |
| Unauthorized claim access | Backend authorization on every request; role and assignment tests in the web release |
| Stolen browser session | OIDC integration, protected cookies, expiration, logout, HTTPS in deployed environments |
| Dependency or image compromise | Locked dependencies, CI scanning, SBOM, immutable image digest in later releases |
| Excessive local resource use | Bounded datasets, separate runtime profiles, capped load and failure experiments |

The project uses synthetic data, which reduces privacy impact but does not remove the need to demonstrate safe engineering. Cloud-specific threats will be expanded before any AWS deployment.
