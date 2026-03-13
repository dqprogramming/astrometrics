from django.contrib import admin
from django.urls import (
    include,
    path,
)

urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "catalogue/",
        include("journals.urls"),
    ),
    path(
        "",
        include("cms.urls"),
    ),
]
