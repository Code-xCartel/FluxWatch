"""
Unit tests for Pydantic request/response models.

Validates field constraints, custom validators, and default values
with no external dependencies.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from flux_watch_api.models.account import AccountCreate, Email, Password
from flux_watch_api.models.events import (
    EntityType,
    EventActor,
    EventContext,
    EventCreate,
    EventEntity,
)


class TestEmail:
    def test_valid_email_is_accepted(self):
        m = Email(email="user@example.com")
        assert m.email == "user@example.com"

    def test_email_is_lowercased(self):
        m = Email(email="User@EXAMPLE.COM")
        assert m.email == "user@example.com"

    def test_email_is_stripped(self):
        m = Email(email="  user@example.com  ")
        assert m.email == "user@example.com"

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError, match="Invalid email address"):
            Email(email="not-an-email")

    def test_missing_tld_raises(self):
        with pytest.raises(ValidationError):
            Email(email="user@domain")

    def test_missing_at_sign_raises(self):
        with pytest.raises(ValidationError):
            Email(email="userexample.com")


class TestPassword:
    def test_valid_password_accepted(self):
        m = Password(password="ValidPass1!")
        assert m.password == "ValidPass1!"

    def test_too_short_raises(self):
        with pytest.raises(ValidationError):
            Password(password="short")

    def test_min_length_boundary_accepted(self):
        m = Password(password="12345678")
        assert m.password == "12345678"

    def test_too_long_raises(self):
        with pytest.raises(ValidationError):
            Password(password="a" * 65)

    def test_max_length_boundary_accepted(self):
        m = Password(password="a" * 64)
        assert len(m.password) == 64


class TestAccountCreate:
    def test_valid_payload_accepted(self):
        m = AccountCreate(name="Alice", email="alice@example.com", password="securepass")
        assert m.name == "Alice"
        assert m.email == "alice@example.com"

    def test_invalid_email_in_create_raises(self):
        with pytest.raises(ValidationError):
            AccountCreate(name="Alice", email="bad-email", password="securepass")

    def test_short_password_in_create_raises(self):
        with pytest.raises(ValidationError):
            AccountCreate(name="Alice", email="alice@example.com", password="short")


class TestEventContext:
    def test_all_fields_default_to_none(self):
        ctx = EventContext()
        assert ctx.trace_id is None
        assert ctx.session_id is None
        assert ctx.source is None

    def test_partial_construction_allowed(self):
        ctx = EventContext(source="web")
        assert ctx.source == "web"
        assert ctx.trace_id is None
        assert ctx.session_id is None

    def test_full_construction(self):
        ctx = EventContext(trace_id="t1", session_id="s1", source="mobile")
        assert ctx.trace_id == "t1"
        assert ctx.session_id == "s1"
        assert ctx.source == "mobile"


class TestEventCreate:
    @staticmethod
    def _make_event(entity_type: EntityType = "user", event_type="user.login", **kwargs):
        return EventCreate(
            entity=EventEntity(type=entity_type, id="entity-1"),
            event_type=event_type,
            producer="test-service",
            occurred_at=datetime.now(timezone.utc),
            **kwargs,
        )

    def test_valid_event_accepted(self):
        event = self._make_event()
        assert event.event_type == "user.login"
        assert event.producer == "test-service"

    def test_payload_defaults_to_empty_dict(self):
        event = self._make_event()
        assert event.payload == {}

    def test_actor_defaults_to_none(self):
        event = self._make_event()
        assert event.actor is None

    def test_context_defaults_to_none(self):
        event = self._make_event()
        assert event.context is None

    def test_invalid_event_type_for_entity_raises(self):
        with pytest.raises(ValidationError, match="Invalid event_type"):
            self._make_event(entity_type="user", event_type="order.created")

    def test_invalid_entity_type_raises(self):
        with pytest.raises(ValidationError):
            self._make_event(entity_type="unknown_entity")

    def test_all_valid_user_event_types_accepted(self):
        for et in ["user.login", "user.logout"]:
            event = self._make_event(entity_type="user", event_type=et)
            assert event.event_type == et

    def test_event_with_actor(self):
        event = self._make_event(actor=EventActor(type="admin", id="admin-1"))
        assert event.actor is not None
        assert event.actor.type == "admin"

    def test_event_with_context(self):
        event = self._make_event(context=EventContext(source="web"))
        assert event.context.source == "web"

    def test_order_event_types(self):
        for et in ["order.created", "order.completed", "order.cancelled"]:
            event = self._make_event(entity_type="order", event_type=et)
            assert event.event_type == et
