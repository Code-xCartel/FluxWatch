"""
Integration-test fixtures.

Provides mock versions of every route-level dependency (repositories,
managers, email service) so integration tests never touch a real database
or external service.

Each fixture is function-scoped. An autouse fixture clears
app.dependency_overrides after every test so overrides don't bleed.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from flux_watch_api.managers.auth.auth_manager import AuthManager
from flux_watch_api.repository.account.account import AccountRepository
from flux_watch_api.repository.auth.api_keys import ApiKeysRepository
from flux_watch_api.repository.events.events import EventsRepository
from flux_watch_api.services.email_service import EmailService


@pytest.fixture(autouse=True)
def clear_dependency_overrides(app):
    """Ensure dependency overrides are cleaned up after each test."""
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_auth_manager() -> MagicMock:
    return MagicMock(spec=AuthManager)


@pytest.fixture
def mock_events_repo() -> MagicMock:
    return MagicMock(spec=EventsRepository)


@pytest.fixture
def mock_account_repo() -> MagicMock:
    return MagicMock(spec=AccountRepository)


@pytest.fixture
def mock_api_keys_repo() -> MagicMock:
    return MagicMock(spec=ApiKeysRepository)


@pytest.fixture
def mock_email_service() -> MagicMock:
    return MagicMock(spec=EmailService)
