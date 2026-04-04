"""
Integration tests for GET /api/v1/health.

The health endpoint probes both Postgres and Redis and returns:
  - 200 {"status": "ok"}    when all dependencies are healthy
  - 503 {"status": "degraded", "checks": {...}} when any dependency fails

The endpoint must be publicly accessible (no auth required).
"""

from __future__ import annotations

from sqlalchemy.exc import OperationalError

HEALTH_URL = "/api/v1/health"


class TestHealthEndpoint:
    def test_returns_200_when_all_deps_healthy(self, client, mock_db, mock_redis):
        # Both DB and Redis respond normally (MagicMock returns truthy by default)
        mock_db.engine.connect.side_effect = None
        mock_redis.client.ping.side_effect = None
        mock_redis.client.ping.return_value = True

        response = client.get(HEALTH_URL)

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["checks"]["database"] == "ok"
        assert body["checks"]["redis"] == "ok"

    def test_returns_503_when_database_unavailable(self, client, mock_db, mock_redis):
        mock_db.engine.connect.side_effect = OperationalError("", {}, None)
        mock_redis.client.ping.side_effect = None
        mock_redis.client.ping.return_value = True

        response = client.get(HEALTH_URL)

        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "degraded"
        assert body["checks"]["database"] == "unavailable"
        assert body["checks"]["redis"] == "ok"

        # Reset so subsequent tests are not affected
        mock_db.engine.connect.side_effect = None

    def test_returns_503_when_redis_unavailable(self, client, mock_db, mock_redis):
        mock_db.engine.connect.side_effect = None
        mock_redis.client.ping.side_effect = ConnectionError("Redis unreachable")

        response = client.get(HEALTH_URL)

        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "degraded"
        assert body["checks"]["redis"] == "unavailable"
        assert body["checks"]["database"] == "ok"

        mock_redis.client.ping.side_effect = None

    def test_returns_503_when_both_deps_unavailable(self, client, mock_db, mock_redis):
        mock_db.engine.connect.side_effect = OperationalError("", {}, None)
        mock_redis.client.ping.side_effect = ConnectionError("Redis unreachable")

        response = client.get(HEALTH_URL)

        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "degraded"
        assert body["checks"]["database"] == "unavailable"
        assert body["checks"]["redis"] == "unavailable"

        mock_db.engine.connect.side_effect = None
        mock_redis.client.ping.side_effect = None

    def test_does_not_require_auth(self, client):
        """Health check must be reachable without an Authorization header."""
        response = client.get(HEALTH_URL)
        assert response.status_code != 401

    def test_response_includes_checks_object(self, client, mock_db, mock_redis):
        mock_db.engine.connect.side_effect = None
        mock_redis.client.ping.return_value = True

        response = client.get(HEALTH_URL)
        body = response.json()

        assert "checks" in body
        assert "database" in body["checks"]
        assert "redis" in body["checks"]
