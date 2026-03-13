"""
URL configuration for CMS pages.
"""

from django.urls import path

from cms.views import board_view, index_view, partial_view

app_name = "cms"

urlpatterns = [
    path("", index_view, name="index"),
    path("board/", board_view, name="board"),
    path(
        "partial/<str:filename>",
        partial_view,
        name="partial",
    ),
]
