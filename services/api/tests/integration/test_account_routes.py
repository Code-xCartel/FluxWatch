"""
Integration tests for account and API key routes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from flux_watch_api.models.account import ApiKey
from flux_watch_api.repository.account.account import AccountRepository
from flux_watch_api.repository.auth.api_keys import ApiKeysRepository


class TestGetSelf:
    def test_returns_own_account(self, authed_client, app, mock_account, mock_account_repo):
        mock_account_repo.get_self.return_value = mock_account
        app.dependency_overrides[AccountRepository] = lambda: mock_account_repo

        response = authed_client.get("/api/v1/account/self")

        assert response.status_code == 200
        body = response.json()
        assert body["principal"] == "test@example.com"
        assert body["name"] == "Test User"

    def test_response_contains_resource_fields(
        self, authed_client, app, mock_account, mock_account_repo
    ):
        mock_account_repo.get_self.return_value = mock_account
        app.dependency_overrides[AccountRepository] = lambda: mock_account_repo

        response = authed_client.get("/api/v1/account/self")
        body = response.json()

        assert "id" in body
        assert "createdAt" in body
        assert "updatedAt" in body

    def test_unauthenticated_request_returns_401(self, client):
        response = client.get("/api/v1/account/self")
        assert response.status_code == 401


class TestGenerateApiKey:
    def test_generates_and_returns_raw_key(self, authed_client, app, mock_api_keys_repo):
        mock_api_keys_repo.generate_new_key.return_value = "rawkey_abc123"
        app.dependency_overrides[ApiKeysRepository] = lambda: mock_api_keys_repo

        response = authed_client.get("/api/v1/keys/generate")

        assert response.status_code == 200
        assert response.json()["key"] == "rawkey_abc123"
        mock_api_keys_repo.generate_new_key.assert_called_once()

    def test_unauthenticated_request_returns_401(self, client):
        response = client.get("/api/v1/keys/generate")
        assert response.status_code == 401


class TestGetApiKey:
    def test_returns_key_record_when_exists(self, authed_client, app, mock_api_keys_repo):
        key = ApiKey(
            id=uuid4(),
            is_active=True,
            last_used_at=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_api_keys_repo.get_key.return_value = key
        app.dependency_overrides[ApiKeysRepository] = lambda: mock_api_keys_repo

        response = authed_client.get("/api/v1/keys")

        assert response.status_code == 200
        body = response.json()
        assert body["isActive"] is True
        assert body["lastUsedAt"] is None

    def test_returns_null_when_no_key_exists(self, authed_client, app, mock_api_keys_repo):
        mock_api_keys_repo.get_key.return_value = None
        app.dependency_overrides[ApiKeysRepository] = lambda: mock_api_keys_repo

        response = authed_client.get("/api/v1/keys")

        assert response.status_code == 200
        assert response.json() is None

    def test_unauthenticated_request_returns_401(self, client):
        response = client.get("/api/v1/keys")
        assert response.status_code == 401
