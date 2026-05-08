"""
Test settings: PostgreSQL when DATABASE_URL is set (CI), SQLite otherwise.

Usage:
    python manage.py test --settings=astrometrics.test_settings
"""

import os

import dj_database_url

from astrometrics.settings import *  # noqa: F401, F403

DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
    # Remove PostgreSQL-specific app since SQLite doesn't support it
    INSTALLED_APPS = [
        app
        for app in INSTALLED_APPS  # noqa: F405
        if app != "django.contrib.postgres"
    ]

# Pin tests to LocMemCache so a developer with REDIS_URL exported in their
# shell doesn't accidentally have tests reach a real Redis instance.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "astrometrics-tests",
    }
}
