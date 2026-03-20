"""
URL configuration for CMS pages.
"""

from django.urls import path

from cms.views import (
    board_view,
    index_view,
    news_detail_view,
    news_index_view,
    our_model_view,
    our_team_view,
    page_preview_view,
    partial_view,
    post_preview_view,
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
    path("our-team/", our_team_view, name="our-team"),
    path("news/", news_index_view, name="news-index"),
    path("news/<slug:slug>/", news_detail_view, name="news-detail"),
    path("preview/post/<uuid:token>/", post_preview_view, name="post-preview"),
    path("preview/page/<uuid:token>/", page_preview_view, name="page-preview"),
    # Our Model — slug catch-all, placed last
    path("<slug:slug>/", our_model_view, name="our-model"),
]
