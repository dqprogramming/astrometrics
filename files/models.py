"""MediaFile model: arbitrary uploads with UUID storage and slug-based public URLs.

Storage path is `files/<uuid>.<ext>` so the on-disk name cannot be guessed.
Public URL is `files/<slug>.<ext>` — slug is editor-controlled and may be
renamed without rewriting storage.
"""

import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse


def media_file_upload_path(instance, filename):
    """Return the storage path for a MediaFile blob.

    Always `files/<uuid>.<ext>` — independent of slug or original filename.
    The slug is for public URLs only; the on-disk name uses the UUID so it
    cannot be guessed and is unaffected by slug renames.
    """
    ext = (instance.extension or "").lstrip(".").lower()
    return f"files/{instance.id.hex}.{ext}"


class MediaFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=200)
    extension = models.CharField(max_length=16)
    file = models.FileField(upload_to=media_file_upload_path)
    original_filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=128, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["slug", "extension"],
                name="files_unique_slug_extension",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.display_name

    @property
    def public_url(self) -> str:
        """The user-facing URL: /files/<slug>.<ext>."""
        return reverse(
            "files:serve",
            kwargs={"slug": self.slug, "ext": self.extension},
        )
