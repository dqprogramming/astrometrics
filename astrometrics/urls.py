from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import (
    include,
    path,
)

from astrometrics.health import health_view

urlpatterns = [
    path("health/", health_view, name="health"),
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    path("manager/", include("manager.urls")),
    path("manager/cms/", include("cms.manager_urls")),
    path("manager/catalogue/", include("journals.manager_urls")),
    path("manager/portal/", include("portal.manager_urls")),
    path("manager/files/", include("files.manager_urls")),
    path("portal/", include("portal.urls")),
    path("catalogue/", include("journals.urls")),
    # Public file serving — must precede the cms catch-all `<slug>` route
    path("files/", include("files.urls")),
    path("", include("cms.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    if "debug_toolbar" in settings.INSTALLED_APPS:
        urlpatterns = [
            path("__debug__/", include("debug_toolbar.urls")),
        ] + urlpatterns
