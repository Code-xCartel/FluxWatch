"""
Shared fixtures for the entire test suite.

Strategy
--------
- The registry is a process-wide singleton, so we pre-populate it with
  mock instances once per session before calling create_app().
- register_common_deps() is patched to a no-op so it never tries to
  open real database or Redis connections.
- auth_middleware is overridden per-test via the `authed_client` fixture
  so protected routes receive a synthetic session account.
"""

from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from starlette.requests import Request

from flux_watch_api.core.config import AppConfig
from flux_watch_api.core.registry import registry
from flux_watch_api.database.redis import Redis
from flux_watch_api.database.session import Database
from flux_watch_api.middlewares.auth import auth_middleware
from flux_watch_api.models.account import Account

# ---------------------------------------------------------------------------
# Infrastructure mocks (session-scoped — created once for the whole run)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def mock_db() -> MagicMock:
    db = MagicMock(spec=Database)
    db.engine = MagicMock()
    db.session_local = MagicMock()
    return db


@pytest.fixture(scope="session")
def mock_redis() -> MagicMock:
    r = MagicMock(spec=Redis)
    r.client = MagicMock()
    r._buffer = []
    r.flush = MagicMock()
    return r


# ---------------------------------------------------------------------------
# Application fixture
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def app(mock_db: MagicMock, mock_redis: MagicMock):
    # Pre-populate the singleton registry so registry.resolve() works
    # without running the real register_common_deps().
    registry._dependencies[AppConfig] = AppConfig()
    registry._dependencies[Database] = mock_db
    registry._dependencies[Redis] = mock_redis

    # Patch register_common_deps where it is *used* (create_app module)
    # so no real DB / Redis connections are attempted.
    with patch("flux_watch_api.create_app.register_common_deps"):
        from flux_watch_api.create_app import create_app

        return create_app()


# ---------------------------------------------------------------------------
# HTTP client fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client(app) -> Generator[TestClient]:
    """Unauthenticated test client."""
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def mock_account() -> Account:
    return Account(
        id=uuid4(),
        name="Test User",
        principal="test@example.com",
        is_active=True,
        is_locked=False,
        failed_login_attempts=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def authed_client(app, client: TestClient, mock_account: Account):
    """
    TestClient where auth middleware is bypassed.
    Sets request.state.session to mock_account so all repo methods
    that read session_account behave correctly.
    """

    def _bypass(request: Request):
        request.state.session = mock_account

    app.dependency_overrides[auth_middleware] = _bypass
    yield client
    app.dependency_overrides.pop(auth_middleware, None)
