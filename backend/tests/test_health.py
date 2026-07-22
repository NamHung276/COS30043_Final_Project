"""
tests/test_health.py — Basic tests for the health endpoint.

Run with:
    cd backend
    pytest tests/ -v

These tests use FastAPI's TestClient (via httpx) so no real server is needed.
"""

import pytest
from fastapi.testclient import TestClient

# The TestClient import will trigger app startup, which is fine for unit tests.
# If Firebase Admin SDK fails to init (no service account), it logs a warning and continues.
import sys
import os

# Ensure the backend root is on the path when running pytest from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /api/health"""

    def test_health_returns_200(self):
        """Health endpoint must return HTTP 200."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_response_shape(self):
        """Health response must have required fields."""
        response = client.get("/api/health")
        data = response.json()

        assert "status" in data
        assert "version" in data
        assert "uptime_seconds" in data
        assert "environment" in data
        assert "cache_stats" in data

    def test_health_status_is_ok(self):
        """Status field must be 'ok'."""
        response = client.get("/api/health")
        assert response.json()["status"] == "ok"

    def test_health_uptime_is_positive(self):
        """Uptime must be a positive number."""
        response = client.get("/api/health")
        uptime = response.json()["uptime_seconds"]
        assert isinstance(uptime, (int, float))
        assert uptime >= 0

    def test_cache_stats_present(self):
        """Cache stats must include known fields."""
        response = client.get("/api/health")
        stats = response.json()["cache_stats"]
        assert "total_entries" in stats
        assert "live_entries" in stats
        assert "expired_entries" in stats
        assert "firebase_admin_ready" in stats


class TestRootRedirect:
    """Tests for GET / (root redirect to /docs)"""

    def test_root_redirects(self):
        """Root path should redirect to /docs."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code in (301, 302, 307, 308)


class TestCorsHeaders:
    """Tests that CORS headers are present."""

    def test_cors_preflight(self):
        """OPTIONS request from allowed origin should return CORS headers."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        # Should not be blocked
        assert response.status_code in (200, 204)
