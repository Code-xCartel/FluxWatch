"""
Unit tests for AuthUtils.

All methods are pure functions (no I/O, no DB) so no mocking is needed.
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from flux_watch_api.utils.auth import AuthUtils


@pytest.fixture
def utils() -> AuthUtils:
    return AuthUtils()


class TestHashPassword:
    def test_returns_string(self, utils: AuthUtils):
        result = utils.hash_password("my_password")
        assert isinstance(result, str)

    def test_different_hash_each_call(self, utils: AuthUtils):
        # bcrypt salts are random — same input must never produce the same hash
        h1 = utils.hash_password("my_password")
        h2 = utils.hash_password("my_password")
        assert h1 != h2

    def test_hash_not_plaintext(self, utils: AuthUtils):
        result = utils.hash_password("my_password")
        assert "my_password" not in result


class TestValidatePassword:
    def test_correct_password_returns_true(self, utils: AuthUtils):
        hashed = utils.hash_password("correct_password")
        assert utils.validate_password("correct_password", hashed) is True

    def test_wrong_password_returns_false(self, utils: AuthUtils):
        hashed = utils.hash_password("correct_password")
        assert utils.validate_password("wrong_password", hashed) is False

    def test_empty_password_returns_false(self, utils: AuthUtils):
        hashed = utils.hash_password("correct_password")
        assert utils.validate_password("", hashed) is False


class TestMakeTtl:
    def test_returns_timezone_aware_datetime(self):
        result = AuthUtils.make_ttl(1)
        assert result.tzinfo is not None

    def test_default_is_approximately_one_day(self):
        result = AuthUtils.make_ttl(None)
        now = datetime.now(timezone.utc)
        delta = result - now
        # Within 1 second of exactly 24 hours
        assert abs(delta.total_seconds() - 86400) < 5

    def test_fractional_days(self):
        result = AuthUtils.make_ttl(0.1)  # ~2.4 hours (used for temp sessions)
        now = datetime.now(timezone.utc)
        delta = result - now
        assert abs(delta.total_seconds() - 8640) < 5

    def test_custom_days(self):
        result = AuthUtils.make_ttl(30)
        now = datetime.now(timezone.utc)
        delta = result - now
        assert abs(delta.days - 30) <= 1


class TestMakeToken:
    def test_token_is_valid_base64(self):
        account = MagicMock()
        account.principal = "user@example.com"
        session_id = uuid4()

        token = AuthUtils.make_token(session_id, account)
        # Must not raise
        decoded = base64.b64decode(token).decode()
        assert decoded == f"{session_id}:user@example.com"

    def test_token_is_string(self):
        account = MagicMock()
        account.principal = "user@example.com"
        result = AuthUtils.make_token(uuid4(), account)
        assert isinstance(result, str)

    def test_token_encodes_session_id_before_colon(self):
        account = MagicMock()
        account.principal = "user@example.com"
        session_id = uuid4()

        token = AuthUtils.make_token(session_id, account)
        raw = base64.b64decode(token).decode()
        encoded_id, _ = raw.split(":", 1)
        assert encoded_id == str(session_id)
