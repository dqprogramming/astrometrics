"""
Project-level health check endpoint.

Exposes a JSON document at /health/ describing the runtime version,
DEBUG flag, and the reachability of the database and (when configured)
the Redis cache. Returns HTTP 200 when healthy, HTTP 503 when any
required dependency is unreachable.
"""

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django_redis import get_redis_connection

from astrometrics import __version__


def _check_database():
    try:
        connection.ensure_connection()
    except Exception as exc:
        return {"connected": False, "error": str(exc)}
    return {"connected": True, "error": None}


def _check_redis():
    backend = settings.CACHES.get("default", {}).get("BACKEND", "")
    if "RedisCache" not in backend:
        return {"configured": False, "connected": False, "error": None}
    try:
        get_redis_connection("default").ping()
    except Exception as exc:
        return {"configured": True, "connected": False, "error": str(exc)}
    return {"configured": True, "connected": True, "error": None}


def health_view(request):
    database = _check_database()
    redis = _check_redis()

    redis_ok = (not redis["configured"]) or redis["connected"]
    healthy = database["connected"] and redis_ok

    payload = {
        "version": __version__,
        "debug": bool(settings.DEBUG),
        "status": "ok" if healthy else "degraded",
        "database": database,
        "redis": redis,
    }
    return JsonResponse(payload, status=200 if healthy else 503)
