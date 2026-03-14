from django.contrib import admin
from django.urls import (
    include,
    path,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("manager/", include("manager.urls")),
    path("manager/cms/", include("cms.manager_urls")),
    path("manager/catalogue/", include("journals.manager_urls")),
    path("manager/portal/", include("portal.manager_urls")),
    path("portal/", include("portal.urls")),
    path("catalogue/", include("journals.urls")),
    path("", include("cms.urls")),
]
