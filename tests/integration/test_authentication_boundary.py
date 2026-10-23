from fastapi.testclient import TestClient

from claims_intelligence.application.api import create_reviewer_app
from claims_intelligence.application.db import create_session_factory


def test_missing_token_is_rejected(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("CLAIMS_AUTH_MODE", "oidc")
    sessions = create_session_factory(f"sqlite:///{tmp_path / 'auth-boundary.db'}")
    with TestClient(create_reviewer_app(sessions=sessions)) as client:
        response = client.get("/api/claims")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
