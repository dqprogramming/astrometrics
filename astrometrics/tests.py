"""
Tests for project-level views (e.g. /health/).
"""

import json
from unittest import mock

from django.test import TestCase, override_settings

from astrometrics import __version__


class HealthEndpointTests(TestCase):
    """Tests for the /health/ JSON endpoint."""

    def test_health_returns_json_200(self):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"), "application/json"
        )

    def test_health_payload_includes_version(self):
        response = self.client.get("/health/")
        payload = json.loads(response.content)
        self.assertEqual(payload["version"], __version__)

    def test_health_payload_includes_debug_flag(self):
        response = self.client.get("/health/")
        payload = json.loads(response.content)
        self.assertIn("debug", payload)
        self.assertIsInstance(payload["debug"], bool)

    def test_health_payload_reports_database_connected(self):
        response = self.client.get("/health/")
        payload = json.loads(response.content)
        self.assertTrue(payload["database"]["connected"])
        self.assertIsNone(payload["database"]["error"])

    def test_health_payload_reports_redis_not_configured_under_locmem(self):
        # test_settings pins CACHES to LocMemCache, so Redis is reported
        # as not configured rather than as connected.
        response = self.client.get("/health/")
        payload = json.loads(response.content)
        self.assertFalse(payload["redis"]["configured"])
        self.assertFalse(payload["redis"]["connected"])

    def test_health_status_ok_when_all_healthy(self):
        response = self.client.get("/health/")
        payload = json.loads(response.content)
        self.assertEqual(payload["status"], "ok")

    def test_health_status_degraded_when_database_unreachable(self):
        with mock.patch(
            "astrometrics.health.connection.ensure_connection",
            side_effect=Exception("db down"),
        ):
            response = self.client.get("/health/")
        self.assertEqual(response.status_code, 503)
        payload = json.loads(response.content)
        self.assertEqual(payload["status"], "degraded")
        self.assertFalse(payload["database"]["connected"])
        self.assertIn("db down", payload["database"]["error"])

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": "redis://example.invalid:6379/0",
            }
        }
    )
    def test_health_reports_redis_connected_when_ping_succeeds(self):
        fake_conn = mock.MagicMock()
        fake_conn.ping.return_value = True
        with mock.patch(
            "astrometrics.health.get_redis_connection",
            return_value=fake_conn,
        ):
            response = self.client.get("/health/")
        payload = json.loads(response.content)
        self.assertTrue(payload["redis"]["configured"])
        self.assertTrue(payload["redis"]["connected"])
        self.assertIsNone(payload["redis"]["error"])

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": "redis://example.invalid:6379/0",
            }
        }
    )
    def test_health_status_degraded_when_redis_unreachable(self):
        with mock.patch(
            "astrometrics.health.get_redis_connection",
            side_effect=Exception("connection refused"),
        ):
            response = self.client.get("/health/")
        self.assertEqual(response.status_code, 503)
        payload = json.loads(response.content)
        self.assertEqual(payload["status"], "degraded")
        self.assertTrue(payload["redis"]["configured"])
        self.assertFalse(payload["redis"]["connected"])
        self.assertIn("connection refused", payload["redis"]["error"])
