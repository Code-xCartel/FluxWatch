"""
Integration tests for authentication routes.

Routes under /api/v1/auth/ are tested with all downstream dependencies
(AuthManager, EmailService) replaced by mocks so no real DB or SMTP
calls are made.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from flux_watch_api.errors.rest_errors import AlreadyExistsError, UnauthorizedError
from flux_watch_api.managers.auth.auth_manager import AuthManager
from flux_watch_api.models.account import AccountSessionMinimal, Sessions
from flux_watch_api.services.email_service import EmailService

BASE = "/api/v1/auth"

_future_ttl = datetime.now(timezone.utc) + timedelta(days=7)


class TestSignUp:
    def test_valid_payload_returns_201(
        self, client, app, mock_auth_manager, mock_email_service, mock_account
    ):
        mock_auth_manager.create_new.return_value = "mock_activation_token"
        app.dependency_overrides[AuthManager] = lambda: mock_auth_manager
        app.dependency_overrides[EmailService] = lambda: mock_email_service

        response = client.post(
            f"{BASE}/sign-up",
            json={"name": "Alice", "email": "alice@example.com", "password": "securepass"},
        )

        assert response.status_code == 201
        assert response.json()["msg"] == "Account created successfully"
        mock_auth_manager.create_new.assert_called_once_with(
            name="Alice", email="alice@example.com", password="securepass"
        )

    def test_invalid_email_returns_422(self, client):
        response = client.post(
            f"{BASE}/sign-up",
            json={"name": "Alice", "email": "not-an-email", "password": "securepass"},
        )
        assert response.status_code == 422

    def test_short_password_returns_422(self, client):
        response = client.post(
            f"{BASE}/sign-up",
            json={"name": "Alice", "email": "alice@example.com", "password": "short"},
        )
        assert response.status_code == 422

    def test_duplicate_email_returns_409(self, client, app, mock_auth_manager, mock_email_service):
        mock_auth_manager.create_new.side_effect = AlreadyExistsError("Email already registered")
        app.dependency_overrides[AuthManager] = lambda: mock_auth_manager
        app.dependency_overrides[EmailService] = lambda: mock_email_service

        response = client.post(
            f"{BASE}/sign-up",
            json={"name": "Alice", "email": "alice@example.com", "password": "securepass"},
        )

        assert response.status_code == 409

    def test_missing_name_returns_422(self, client):
        response = client.post(
            f"{BASE}/sign-up",
            json={"email": "alice@example.com", "password": "securepass"},
        )
        assert response.status_code == 422


class TestSignIn:
    def test_valid_credentials_returns_200_with_token(self, client, app, mock_auth_manager):
        mock_auth_manager.authenticate_and_save.return_value = AccountSessionMinimal(
            access_token="test_token_abc",
            ttl=_future_ttl,
        )
        app.dependency_overrides[AuthManager] = lambda: mock_auth_manager

        response = client.post(
            f"{BASE}/sign-in",
            headers={"Authorization": "Resident dXNlckBleGFtcGxlLmNvbTpwYXNzd29yZA=="},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["accessToken"] == "test_token_abc"

    def test_invalid_credentials_returns_401(self, client, app, mock_auth_manager):
        mock_auth_manager.authenticate_and_save.side_effect = UnauthorizedError(
            "Invalid credentials"
        )
        app.dependency_overrides[AuthManager] = lambda: mock_auth_manager

        response = client.post(
            f"{BASE}/sign-in",
            headers={"Authorization": "Resident bad_creds"},
        )

        assert response.status_code == 401

    def test_missing_auth_header_returns_401(self, client, app, mock_auth_manager):
        mock_auth_manager.authenticate_and_save.side_effect = UnauthorizedError(
            "No auth header provided"
        )
        app.dependency_overrides[AuthManager] = lambda: mock_auth_manager

        response = client.post(f"{BASE}/sign-in")

        assert response.status_code == 401


class TestSignOut:
    def test_sign_out_current_session_returns_200(self, authed_client, app, mock_auth_manager):
        mock_auth_manager.delete_sessions.return_value = None
        app.dependency_overrides[AuthManager] = lambda: mock_auth_manager

        response = authed_client.delete(
            f"{BASE}/sign-out",
            params={"scope": "current"},
            headers={"Authorization": "Token mock_token"},
        )

        assert response.status_code == 200

    def test_sign_out_all_sessions_returns_200(self, authed_client, app, mock_auth_manager):
        mock_auth_manager.delete_sessions.return_value = None
        app.dependency_overrides[AuthManager] = lambda: mock_auth_manager

        response = authed_client.delete(
            f"{BASE}/sign-out",
            params={"scope": "all"},
            headers={"Authorization": "Token mock_token"},
        )

        assert response.status_code == 200

    def test_sign_out_without_scope_returns_422(self, authed_client, app, mock_auth_manager):
        app.dependency_overrides[AuthManager] = lambda: mock_auth_manager
        response = authed_client.delete(
            f"{BASE}/sign-out",
            headers={"Authorization": "Token mock_token"},
        )
        assert response.status_code == 422


class TestGetSessions:
    def test_returns_list_of_sessions(self, authed_client, app, mock_auth_manager):
        mock_session = MagicMock(spec=Sessions)
        mock_auth_manager.get_sessions.return_value = [mock_session]
        app.dependency_overrides[AuthManager] = lambda: mock_auth_manager

        response = authed_client.get(
            f"{BASE}/sessions",
            headers={"Authorization": "Token mock_token"},
        )

        assert response.status_code == 200
        assert "sessions" in response.json()

    def test_returns_empty_list_when_no_other_sessions(self, authed_client, app, mock_auth_manager):
        mock_auth_manager.get_sessions.return_value = []
        app.dependency_overrides[AuthManager] = lambda: mock_auth_manager

        response = authed_client.get(
            f"{BASE}/sessions",
            headers={"Authorization": "Token mock_token"},
        )

        assert response.status_code == 200
        assert response.json()["sessions"] == []


class TestActivateAccount:
    def test_valid_token_activates_account(self, client, app, mock_auth_manager):
        mock_auth_manager.activate_account.return_value = None
        app.dependency_overrides[AuthManager] = lambda: mock_auth_manager

        response = client.post(
            f"{BASE}/activate",
            headers={"Authorization": "Token mock_activation_token"},
        )

        assert response.status_code == 200
        assert response.json()["msg"] == "Account activated successfully"


class TestForgotPassword:
    def test_sends_reset_email_returns_200(
        self, client, app, mock_auth_manager, mock_email_service, mock_account
    ):
        mock_session = MagicMock()
        mock_session.account.principal = "alice@example.com"
        mock_session.account.name = "Alice"
        mock_session.access_token = "reset_token_xyz"
        mock_auth_manager.new_temp_session.return_value = mock_session
        app.dependency_overrides[AuthManager] = lambda: mock_auth_manager
        app.dependency_overrides[EmailService] = lambda: mock_email_service

        response = client.post(
            f"{BASE}/forgot-password",
            json={"email": "alice@example.com"},
        )

        assert response.status_code == 200
        assert "sent" in response.json()["msg"].lower()

    def test_invalid_email_body_returns_422(self, client):
        response = client.post(
            f"{BASE}/forgot-password",
            json={"email": "not-valid"},
        )
        assert response.status_code == 422
