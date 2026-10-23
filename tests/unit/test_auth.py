from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

from claims_intelligence.application.auth import ApplicationRole, OIDCAuthenticator, OIDCSettings

ISSUER = "http://identity.test/realms/claims"
AUDIENCE = "claims-reviewer"


@pytest.fixture
def oidc_material():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_jwk = jwt.algorithms.RSAAlgorithm.to_jwk(private_key.public_key(), as_dict=True)
    public_jwk.update({"kid": "test-key", "use": "sig", "alg": "RS256"})
    authenticator = OIDCAuthenticator(
        OIDCSettings(ISSUER, AUDIENCE, "http://unused.test/certs"),
        {"keys": [public_jwk]},
    )
    return private_key, authenticator


def token(private_key, role: str, **overrides) -> str:
    now = datetime.now(UTC)
    claims = {
        "sub": "user-123",
        "preferred_username": "local-user",
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=5),
        "realm_access": {"roles": [role]},
        **overrides,
    }
    return jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": "test-key"})


@pytest.mark.parametrize(
    ("role", "expected"),
    [
        ("reviewer", ApplicationRole.REVIEWER),
        ("supervisor", ApplicationRole.SUPERVISOR),
        ("audit-reader", ApplicationRole.AUDIT_READER),
    ],
)
def test_valid_application_roles(oidc_material, role, expected) -> None:
    private_key, authenticator = oidc_material
    assert authenticator.authenticate(token(private_key, role)).role is expected


def test_expired_token_is_rejected(oidc_material) -> None:
    private_key, authenticator = oidc_material
    with pytest.raises(HTTPException) as error:
        authenticator.authenticate(
            token(private_key, "reviewer", exp=datetime.now(UTC) - timedelta(seconds=1))
        )
    assert error.value.status_code == 401


def test_forged_role_is_rejected(oidc_material) -> None:
    _, authenticator = oidc_material
    attacker_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with pytest.raises(HTTPException) as error:
        authenticator.authenticate(token(attacker_key, "supervisor"))
    assert error.value.status_code == 401


def test_unknown_or_multiple_application_roles_are_rejected(oidc_material) -> None:
    private_key, authenticator = oidc_material
    with pytest.raises(HTTPException) as error:
        authenticator.authenticate(token(private_key, "realm-admin"))
    assert error.value.status_code == 403


def test_wrong_audience_is_rejected(oidc_material) -> None:
    private_key, authenticator = oidc_material
    with pytest.raises(HTTPException) as error:
        authenticator.authenticate(token(private_key, "reviewer", aud="another-client"))
    assert error.value.status_code == 401
