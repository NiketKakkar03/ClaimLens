"""Authentication identity and role checks for the reviewer API."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum

from fastapi import Header, HTTPException


class ApplicationRole(StrEnum):
    REVIEWER = "reviewer"
    SUPERVISOR = "supervisor"
    AUDIT_READER = "audit-reader"


@dataclass(frozen=True)
class Actor:
    subject: str
    role: ApplicationRole


def current_actor(
    x_demo_user: str = Header(default="local-reviewer"),
    x_demo_role: str = Header(default="reviewer"),
) -> Actor:
    """Resolve the local demo identity; production mode refuses unsigned headers."""
    if os.getenv("CLAIMS_AUTH_MODE", "demo") != "demo":
        raise HTTPException(status_code=503, detail="OIDC authentication is not configured")
    try:
        role = ApplicationRole(x_demo_role)
    except ValueError as error:
        raise HTTPException(status_code=403, detail="Unknown application role") from error
    return Actor(subject=x_demo_user, role=role)


def require_writer(actor: Actor) -> None:
    if actor.role not in {ApplicationRole.REVIEWER, ApplicationRole.SUPERVISOR}:
        raise HTTPException(status_code=403, detail="This role has read-only access")
