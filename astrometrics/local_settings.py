"""
Local development settings for Docker Compose environment.

Usage: DJANGO_SETTINGS_MODULE=astrometrics.local_settings
"""

import dj_database_url

from astrometrics.settings import *  # noqa: F401, F403

DATABASES = {
    "default": dj_database_url.config(
        default="postgres://astrometrics:astrometrics@db:5432/astrometrics",
        conn_max_age=600,
    )
}

ALLOWED_HOSTS = ["*"]
