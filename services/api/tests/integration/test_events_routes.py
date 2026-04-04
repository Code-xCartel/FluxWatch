"""
Integration tests for event routes.

All EventsRepository calls are mocked so no real DB or Redis writes occur.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from flux_watch_api.errors.rest_errors import NotFoundError
from flux_watch_api.models.events import Event, EventEntity
from flux_watch_api.models.response_schema import ListResponse, Meta
from flux_watch_api.repository.events.events import EventsRepository

BASE = "/api/v1/events"


def _make_event(**overrides) -> Event:
    defaults = dict(
        id=uuid4(),
        entity=EventEntity(type="user", id="user-1"),
        event_type="user.login",
        producer="test-service",
        occurred_at=datetime.now(timezone.utc),
        actor=None,
        context=None,
        payload={},
        event_version=1,
        parent="test@example.com",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return Event(**defaults)


class TestIngestEvent:
    def test_valid_event_returns_201(self, authed_client, app, mock_events_repo):
        event = _make_event()
        mock_events_repo.ingest_event.return_value = event
        app.dependency_overrides[EventsRepository] = lambda: mock_events_repo

        response = authed_client.post(
            f"{BASE}/ingest",
            json={
                "entity": {"type": "user", "id": "user-1"},
                "eventType": "user.login",
                "producer": "test-service",
                "occurredAt": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 201
        mock_events_repo.ingest_event.assert_called_once()

    def test_invalid_event_type_for_entity_returns_422(self, authed_client):
        # Validation is handled by Pydantic before the repo is called
        response = authed_client.post(
            f"{BASE}/ingest",
            json={
                "entity": {"type": "user", "id": "user-1"},
                "eventType": "order.created",  # invalid for user entity
                "producer": "test-service",
                "occurredAt": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert response.status_code == 422

    def test_unknown_entity_type_returns_422(self, authed_client):
        response = authed_client.post(
            f"{BASE}/ingest",
            json={
                "entity": {"type": "unknown", "id": "x"},
                "eventType": "user.login",
                "producer": "svc",
                "occurredAt": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert response.status_code == 422

    def test_missing_required_fields_returns_422(self, authed_client):
        response = authed_client.post(f"{BASE}/ingest", json={"entity": {"type": "user"}})
        assert response.status_code == 422

    def test_unauthenticated_request_returns_401(self, client, app, mock_events_repo):
        app.dependency_overrides[EventsRepository] = lambda: mock_events_repo

        response = client.post(
            f"{BASE}/ingest",
            json={
                "entity": {"type": "user", "id": "u1"},
                "eventType": "user.login",
                "producer": "svc",
                "occurredAt": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert response.status_code == 401


class TestGetEventById:
    def test_existing_event_returns_200(self, authed_client, app, mock_events_repo):
        event = _make_event()
        mock_events_repo.get_event_by_id.return_value = event
        app.dependency_overrides[EventsRepository] = lambda: mock_events_repo

        response = authed_client.get(f"{BASE}/{event.id}")

        assert response.status_code == 200
        mock_events_repo.get_event_by_id.assert_called_once_with(str(event.id))

    def test_nonexistent_event_returns_404(self, authed_client, app, mock_events_repo):
        mock_events_repo.get_event_by_id.side_effect = NotFoundError()
        app.dependency_overrides[EventsRepository] = lambda: mock_events_repo

        response = authed_client.get(f"{BASE}/{uuid4()}")

        assert response.status_code == 404

    def test_response_contains_event_type(self, authed_client, app, mock_events_repo):
        event = _make_event(event_type="user.logout")
        mock_events_repo.get_event_by_id.return_value = event
        app.dependency_overrides[EventsRepository] = lambda: mock_events_repo

        response = authed_client.get(f"{BASE}/{event.id}")
        body = response.json()

        assert body["eventType"] == "user.logout"


class TestListEvents:
    def test_returns_paginated_list(self, authed_client, app, mock_events_repo):
        events = [_make_event(), _make_event()]
        mock_events_repo.get_all_events.return_value = ListResponse(
            meta=Meta(total_count=2, returned_count=2),
            results=events,
        )
        app.dependency_overrides[EventsRepository] = lambda: mock_events_repo

        response = authed_client.get(BASE)

        assert response.status_code == 200
        body = response.json()
        assert body["meta"]["totalCount"] == 2
        assert body["meta"]["returnedCount"] == 2
        assert len(body["results"]) == 2

    def test_returns_empty_list_when_no_events(self, authed_client, app, mock_events_repo):
        mock_events_repo.get_all_events.return_value = ListResponse(
            meta=Meta(total_count=0, returned_count=0),
            results=[],
        )
        app.dependency_overrides[EventsRepository] = lambda: mock_events_repo

        response = authed_client.get(BASE)

        assert response.status_code == 200
        assert response.json()["results"] == []

    def test_passes_query_params_to_repo(self, authed_client, app, mock_events_repo):
        mock_events_repo.get_all_events.return_value = ListResponse(
            meta=Meta(total_count=0, returned_count=0),
            results=[],
        )
        app.dependency_overrides[EventsRepository] = lambda: mock_events_repo

        authed_client.get(f"{BASE}?pageSize=20&page=2")

        call_kwargs = mock_events_repo.get_all_events.call_args[0][0]
        assert call_kwargs["page_size"] == 20
        assert call_kwargs["page"] == 2
