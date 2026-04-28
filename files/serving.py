"""Storage-agnostic serving of MediaFile blobs.

This is the single place that knows about storage backends so a future
move from FileSystemStorage to S3 (or any django-storages backend) is
localised here.
"""

import mimetypes

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, HttpResponseRedirect


def is_filesystem_storage(storage) -> bool:
    """True if the storage is local-disk-backed."""
    return isinstance(storage, FileSystemStorage)


def _try_signed_url(storage, name, ttl):
    """Return a signed URL if the backend supports `expire`, else None."""
    try:
        return storage.url(name, expire=ttl)
    except TypeError:
        return None


def _stream_through_django(media):
    """Open via the storage backend and stream the bytes."""
    fh = media.file.storage.open(media.file.name, "rb")
    content_type = media.mime_type or (
        mimetypes.guess_type(media.original_filename)[0]
        or "application/octet-stream"
    )
    response = FileResponse(
        fh,
        as_attachment=False,
        filename=media.original_filename,
        content_type=content_type,
    )
    if media.is_public:
        response["Cache-Control"] = "public, max-age=3600"
    else:
        response["Cache-Control"] = "private, no-store"
    return response


def serve_or_redirect(media, request):
    """Return an HTTP response that serves a MediaFile.

    - FileSystemStorage: stream via FileResponse
    - Public + remote storage: 302 to the storage public URL
    - Private + signed-URL-capable remote: 302 to a short-lived signed URL
    - Private + remote without signing: stream through Django
    """
    storage = media.file.storage

    if is_filesystem_storage(storage):
        return _stream_through_django(media)

    if media.is_public:
        return HttpResponseRedirect(storage.url(media.file.name))

    # Private + remote — try a short-lived signed URL first.
    ttl = getattr(settings, "FILES_SIGNED_URL_TTL", 300)
    signed = _try_signed_url(storage, media.file.name, ttl)
    if signed is not None:
        return HttpResponseRedirect(signed)
    return _stream_through_django(media)
