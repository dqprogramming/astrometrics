from django.urls import path

from . import manager_views as views

app_name = "cms_manager"

urlpatterns = [
    # TinyMCE image upload
    path("image-upload/", views.image_upload, name="image_upload"),
    # Header
    path("header/", views.HeaderSettingsUpdateView.as_view(), name="header"),
    # Footer
    path("footer/", views.FooterSettingsUpdateView.as_view(), name="footer"),
    # Landing Page
    path(
        "landing-page/",
        views.LandingPageSettingsUpdateView.as_view(),
        name="landing_page",
    ),
    # Our Model
    path(
        "our-model/",
        views.OurModelPageSettingsUpdateView.as_view(),
        name="our_model",
    ),
    # Pages
    path("pages/", views.PageListView.as_view(), name="page_list"),
    path("pages/new/", views.PageCreateView.as_view(), name="page_create"),
    path(
        "pages/<int:pk>/edit/",
        views.PageUpdateView.as_view(),
        name="page_edit",
    ),
    path(
        "pages/<int:pk>/delete/",
        views.PageDeleteView.as_view(),
        name="page_delete",
    ),
    # Posts
    path("posts/", views.PostListView.as_view(), name="post_list"),
    path("posts/new/", views.PostCreateView.as_view(), name="post_create"),
    path(
        "posts/<int:pk>/edit/",
        views.PostUpdateView.as_view(),
        name="post_edit",
    ),
    path(
        "posts/<int:pk>/delete/",
        views.PostDeleteView.as_view(),
        name="post_delete",
    ),
    # Snippets
    path("snippets/", views.SnippetListView.as_view(), name="snippet_list"),
    path(
        "snippets/new/",
        views.SnippetCreateView.as_view(),
        name="snippet_create",
    ),
    path(
        "snippets/<int:pk>/edit/",
        views.SnippetUpdateView.as_view(),
        name="snippet_edit",
    ),
    path(
        "snippets/<int:pk>/delete/",
        views.SnippetDeleteView.as_view(),
        name="snippet_delete",
    ),
]
