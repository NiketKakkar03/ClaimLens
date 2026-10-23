# Local Keycloak authentication evidence — 2026-10-23

## Implemented boundary

The local Compose application now runs Keycloak on host port 8180 and imports the reproducible `claims-local` realm. The React client uses OIDC Authorization Code with PKCE. FastAPI accepts bearer access tokens only in normal mode and validates the Keycloak signature, exact issuer, `claims-reviewer` audience, expiry, issued-at time, subject, and exactly one application role.

Three disposable local identities demonstrate reviewer, supervisor, and read-only audit access. Their obvious passwords are local fixtures, not real secrets and not suitable for deployment. Keycloak records login and administrator events in its local data volume.

## Automated security checks

The authentication tests cover:

- valid reviewer, supervisor, and audit-reader tokens;
- missing bearer tokens;
- expired access tokens;
- a wrong client audience;
- an unknown application role;
- a forged supervisor token signed by an attacker key;
- an audit reader attempting a direct claim-creation request.

Backend permission checks return HTTP 403 even if a request bypasses the React interface. The explicit `CLAIMS_AUTH_MODE=test` override uses `X-Test-*` headers only in automated tests; the Compose service uses `oidc`.

## Operational interpretation

Access tokens last five minutes. Logout terminates the browser's Keycloak session, and disabled users cannot log in or refresh. Offline JWT verification means a token issued just before an account disable or role change can remain valid until expiry; this bounded delay is documented rather than presented as immediate revocation.

## Verified results

- All 14 Python tests passed, including the new authentication and direct-API cases.
- Python format and lint checks passed.
- Frontend ESLint, TypeScript compilation, and the Vite production build passed; the JavaScript bundle measured 222.94 KB before gzip and 69.77 KB after gzip.
- Compose configuration validation passed, and the Keycloak, PostgreSQL, reviewer API, and reviewer web containers started successfully.
- The live reviewer access token returned the expected username and role from `/api/session`.
- The live API returned 401 without a token, 200 for an audit-reader list request, and 403 for a schema-valid audit-reader write.
- Chrome completed the Keycloak PKCE redirect, displayed the authenticated reviewer identity and queue, and returned to the Keycloak login page after logout.

This demonstrates the local development configuration only, not a production identity deployment.
