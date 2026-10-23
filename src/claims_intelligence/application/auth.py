"""OIDC authentication and application role authorization for the reviewer API."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
from typing import Annotated, Any

import jwt
from fastapi import Header, HTTPException
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError


class ApplicationRole(StrEnum):
    REVIEWER = "reviewer"
    SUPERVISOR = "supervisor"
    AUDIT_READER = "audit-reader"


@dataclass(frozen=True)
class Actor:
    subject: str
    username: str
    role: ApplicationRole


@dataclass(frozen=True)
class OIDCSettings:
    issuer: str
    audience: str
    jwks_url: str

    @classmethod
    def from_environment(cls) -> OIDCSettings:
        issuer = os.getenv("CLAIMS_OIDC_ISSUER", "").rstrip("/")
        audience = os.getenv("CLAIMS_OIDC_AUDIENCE", "")
        jwks_url = os.getenv("CLAIMS_OIDC_JWKS_URL", f"{issuer}/protocol/openid-connect/certs")
        if not issuer or not audience:
            raise RuntimeError("CLAIMS_OIDC_ISSUER and CLAIMS_OIDC_AUDIENCE are required")
        return cls(issuer=issuer, audience=audience, jwks_url=jwks_url)


class OIDCAuthenticator:
    """Validate signed access tokens and translate one realm role into an app actor."""

    def __init__(self, settings: OIDCSettings, jwks: dict[str, Any] | None = None) -> None:
        self.settings = settings
        self._jwks_client = PyJWKClient(settings.jwks_url) if jwks is None else None
        self._jwks = jwks

    def authenticate(self, token: str) -> Actor:
        try:
            if self._jwks is not None:
                signing_key = jwt.PyJWKSet.from_dict(self._jwks).keys[0].key
            else:
                assert self._jwks_client is not None
                signing_key = self._jwks_client.get_signing_key_from_jwt(token).key
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=self.settings.audience,
                issuer=self.settings.issuer,
                options={"require": ["exp", "iat", "sub", "iss", "aud"]},
            )
        except (InvalidTokenError, ValueError, IndexError) as error:
            raise HTTPException(
                status_code=401,
                detail="Access token is missing, expired, or invalid",
                headers={"WWW-Authenticate": "Bearer"},
            ) from error

        realm_roles = claims.get("realm_access", {}).get("roles", [])
        roles = [role for role in ApplicationRole if role.value in realm_roles]
        if len(roles) != 1:
            raise HTTPException(status_code=403, detail="Exactly one application role is required")
        return Actor(
            subject=str(claims["sub"]),
            username=str(claims.get("preferred_username", claims["sub"])),
            role=roles[0],
        )


@lru_cache(maxsize=1)
def _oidc_authenticator() -> OIDCAuthenticator:
    return OIDCAuthenticator(OIDCSettings.from_environment())


def current_actor(
    authorization: Annotated[str | None, Header()] = None,
    x_test_user: Annotated[str | None, Header()] = None,
    x_test_role: Annotated[str | None, Header()] = None,
) -> Actor:
    """Resolve a verified OIDC identity, or an explicit test-only override."""
    if os.getenv("CLAIMS_AUTH_MODE", "oidc") == "test":
        try:
            role = ApplicationRole(x_test_role or "reviewer")
        except ValueError as error:
            raise HTTPException(status_code=403, detail="Unknown application role") from error
        username = x_test_user or "automated-test-reviewer"
        return Actor(subject=f"test:{username}", username=username, role=role)

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="A bearer access token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _oidc_authenticator().authenticate(authorization.removeprefix("Bearer ").strip())


def require_writer(actor: Actor) -> None:
    if actor.role not in {ApplicationRole.REVIEWER, ApplicationRole.SUPERVISOR}:
        raise HTTPException(status_code=403, detail="This role has read-only access")
