"""
URL configuration for CMS pages.
"""

from django.urls import path

from cms.views import (
    about_us_view,
    board_view,
    index_view,
    news_detail_view,
    news_index_view,
    our_team_view,
    page_preview_view,
    partial_view,
    post_preview_view,
    slug_page_view,
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
    path("about-us/", about_us_view, name="about-us"),
    path("our-team/", our_team_view, name="our-team"),
    path("news/", news_index_view, name="news-index"),
    path("news/<slug:slug>/", news_detail_view, name="news-detail"),
    path("preview/post/<uuid:token>/", post_preview_view, name="post-preview"),
    path("preview/page/<uuid:token>/", page_preview_view, name="page-preview"),
    # Slug catch-all — tries block page first, then Our Manifesto / Our Model
    path("<slug:slug>/", slug_page_view, name="slug-page"),
]
