# Proposed application access control

Status: the first backend role boundary and attributed audit trail are implemented. Local demo headers stand in for identity only during development; they are not authentication. Login, seeded reviewer accounts, and self-hosted local Keycloak remain accepted next-stage work. Assignment-level boundaries remain a later proposal.

Interview update: the user provisionally accepted the three role names but needs a plain-language explanation before confirming their boundaries. Distinct model-governance identities remain undecided. There is one human operator; account permissions would be configured through the project's local setup. They do not require permission from an external organization.

Accepted starting scope: the first web application gives reviewers a shared synthetic claim queue. Individual assignments and their access restrictions follow in a later learning stage. The assignment-scoped role matrix below describes a proposed later stage, not the first web release.

## Terms and recommendation

Authentication establishes who a person is. Authorization decides what that person may do. OpenID Connect (OIDC) is a login protocol; RBAC, ABAC, and ReBAC are ways of deciding permissions. They solve different parts of access control.

Recommend a small set of roles mapped to explicit permissions, combined with checks against a claim's assignment and review state. RBAC alone answers whether someone is a reviewer, but cannot establish whether this particular claim is theirs to update. Avoid a separate policy server until the rules justify one.

## Proposed application roles

| Action | Claims reviewer | Claims supervisor | Audit reader |
| --- | --- | --- | --- |
| View claim information and prediction history | Assigned claims | Claims in their team | Explicitly granted audit scope |
| Create a synthetic claim | Yes, assigned to the creator | Yes, within their team | No |
| Add claim information or request a prediction | Assigned claims, subject to claim state | Claims in their team, subject to claim state | No |
| Record review priority and a reason | Assigned claims | Claims in their team | No |
| Reassign a claim | No | Within their team | No |
| Read audit history | Assigned claims | Claims in their team | Granted audit scope |
| Change user roles | No | No | No |
| Approve or deploy models | No | No | No |

Account provisioning and role assignment would use a restricted identity-administration interface or setup workflow. They are privileged operations and must be audited. Avoid an all-powerful application Admin role that automatically inherits unrelated claims and model-governance powers.

The role and assignment checks must filter collection searches and apply to details, updates, histories, exports, briefs, and prediction endpoints. A resource identifier or hidden frontend control does not establish permission. Historical entries retain the original actor; reassignment affects future access rather than rewriting past actions.

## Accepted identity service and proposed session design

Use self-hosted Keycloak through OIDC for the web release. Keycloak supports demonstration accounts and teaches integration with an identity provider. Its open-source distribution can run on the developer's computer without paying for an identity subscription or a hosted service. It still consumes local CPU, memory, and storage, and deploying it on rented cloud infrastructure can incur infrastructure costs. The trade-off is an additional service to configure and operate. Its development startup configuration is not a production deployment configuration.

Prefer the backend handling the login exchange and keeping provider tokens server-side. The browser would hold an opaque session cookie with HttpOnly and appropriate SameSite settings, plus Secure under HTTPS. Protect state-changing requests against CSRF, validate the OIDC exchange with a maintained integration, and enforce logout, expiration, disabled-account handling, and a bounded policy for changed permissions. Exact library, local transport, token validation, and session-storage choices remain open.

Frontend visibility reflects backend-granted capabilities, but FastAPI enforces authorization. Deny access without a matching permission and resource rule. Resolve the actor from authenticated identity rather than a user ID or role submitted in a form.

## Separate security boundaries

Application roles cover claim workflows. Model proposal, risk approval, and deployment require distinct permissions in their respective registry and CI/CD workflows. AWS IAM roles govern workloads' access to AWS resources; they do not replace application user permissions. A future shared identity provider may connect these tools, but a login or a README link alone does not grant access to Grafana, MLflow, Databricks, or AWS.

Model approval should distinguish the identity proposing a candidate from the identity approving it. In this solo learning project, separate demonstration accounts illustrate the control but are not evidence of independent human review. Machine identities for ingestion, training, monitoring, and deployment receive their own permissions rather than borrowing a reviewer's session.

## Verification evidence

Test allowed actions and rejected actions, including another reviewer's claim, direct API calls bypassing the UI, claim searches, role changes, revoked assignments, expired sessions, disabled accounts, and attempts to submit a different actor or role. Audit account/permission changes, claim changes, reviewer-selected priorities, and denied privileged actions without storing credentials or tokens in logs. A restricted application API is only one layer: internal tools and database/service credentials need their own access controls.

## Sources

- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html): least privilege, deny by default, per-request and per-object checks, RBAC limitations, and authorization tests.
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html): browser session handling, cookie settings, session lifecycle, and logout.
- [FastAPI OAuth2 scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/): permission names can integrate with API dependencies and documentation; the application still enforces them.
- [Keycloak Docker getting started](https://www.keycloak.org/getting-started/getting-started-docker): local startup, users, OIDC clients, and the additional requirements for production use.
- [Keycloak project](https://www.keycloak.org/) and [official Apache 2.0 license](https://github.com/keycloak/keycloak/blob/main/LICENSE.txt): open-source identity management and no-charge licensing, checked on 2026-10-22.
