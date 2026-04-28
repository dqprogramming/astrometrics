from django.urls import path

from . import manager_views as views

app_name = "files_manager"

urlpatterns = [
    path("", views.MediaFileListView.as_view(), name="file_list"),
    path("upload/", views.MediaFileUploadView.as_view(), name="file_upload"),
    path(
        "<uuid:pk>/edit/",
        views.MediaFileUpdateView.as_view(),
        name="file_edit",
    ),
    path(
        "<uuid:pk>/delete/",
        views.MediaFileDeleteView.as_view(),
        name="file_delete",
    ),
    path(
        "<uuid:pk>/copy-url/",
        views.media_file_copy_url,
        name="file_copy_url",
    ),
]
