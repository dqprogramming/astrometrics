"""
URL configuration for CMS pages.
"""

from django.urls import path

from cms.views import (
    board_view,
    index_view,
    news_detail_view,
    news_index_view,
    partial_view,
)

app_name = "cms"

urlpatterns = [
    path("", index_view, name="index"),
    path("board/", board_view, name="board"),
    path(
        "partial/<str:filename>",
        partial_view,
        name="partial",
    ),
    path("news/", news_index_view, name="news-index"),
    path("news/<slug:slug>/", news_detail_view, name="news-detail"),
]
