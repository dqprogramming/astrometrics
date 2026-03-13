from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("manager/", include("manager.urls")),
    path("manager/cms/", include("cms.manager_urls")),
    path("manager/catalogue/", include("journals.manager_urls")),
    path("", include("journals.urls")),
]
