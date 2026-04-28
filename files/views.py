"""Public serve view for MediaFile.

Routed at /files/<slug>.<ext>. Resolves the slug, enforces visibility,
and delegates to serving.serve_or_redirect.
"""

from django.http import Http404
from django.views.decorators.http import require_GET

from .models import MediaFile
from .serving import serve_or_redirect


@require_GET
def serve_file(request, slug, ext):
    try:
        media = MediaFile.objects.get(slug=slug, extension=ext.lower())
    except MediaFile.DoesNotExist:
        raise Http404

    if not media.is_public:
        user = getattr(request, "user", None)
        if not (user and user.is_active and user.is_staff):
            # 404 not 403 — don't leak the existence of private files.
            raise Http404

    return serve_or_redirect(media, request)
