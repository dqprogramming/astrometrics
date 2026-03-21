from django.urls import path

from . import manager_views as views

app_name = "cms_manager"

urlpatterns = [
    # TinyMCE image upload
    path("image-upload/", views.image_upload, name="image_upload"),
    # Featured image upload (generic — for new posts not yet saved)
    path(
        "post-image-upload/",
        views.post_featured_image_upload,
        name="post_featured_image_upload",
    ),
    # Featured image upload (post-specific — auto-saves immediately)
    path(
        "posts/<int:pk>/image-upload/",
        views.post_featured_image_upload,
        name="post_featured_image_upload_pk",
    ),
    # Post category tag widget
    path(
        "posts/<int:pk>/categories/search/",
        views.PostCategorySearchView.as_view(),
        name="post_category_search",
    ),
    path(
        "posts/<int:pk>/categories/add/",
        views.PostCategoryAddView.as_view(),
        name="post_category_add",
    ),
    path(
        "posts/<int:pk>/categories/<int:item_pk>/remove/",
        views.PostCategoryRemoveView.as_view(),
        name="post_category_remove",
    ),
    # Categories
    path(
        "categories/", views.CategoryListView.as_view(), name="category_list"
    ),
    path(
        "categories/new/",
        views.CategoryCreateView.as_view(),
        name="category_create",
    ),
    path(
        "categories/<int:pk>/edit/",
        views.CategoryUpdateView.as_view(),
        name="category_edit",
    ),
    path(
        "categories/<int:pk>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category_delete",
    ),
    # Contact Form Settings
    path(
        "contact-form/",
        views.ContactFormSettingsUpdateView.as_view(),
        name="contact_form",
    ),
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
    # Our Manifesto
    path(
        "our-manifesto/",
        views.ManifestoPageSettingsUpdateView.as_view(),
        name="manifesto",
    ),
    # Our Model
    path(
        "our-model/",
        views.OurModelPageSettingsUpdateView.as_view(),
        name="our_model",
    ),
    # Our Team
    path(
        "our-team/",
        views.OurTeamManagerView.as_view(),
        name="our_team",
    ),
    path(
        "our-team/section/add/",
        views.OurTeamSectionAddView.as_view(),
        name="our_team_section_add",
    ),
    path(
        "our-team/section/<int:pk>/delete/",
        views.OurTeamSectionDeleteView.as_view(),
        name="our_team_section_delete",
    ),
    path(
        "our-team/member/<int:pk>/delete/",
        views.OurTeamMemberDeleteView.as_view(),
        name="our_team_member_delete",
    ),
    path(
        "our-team/member-image-upload/",
        views.team_member_image_upload,
        name="team_member_image_upload",
    ),
    # OJC Boards
    path(
        "board/",
        views.BoardManagerView.as_view(),
        name="board",
    ),
    path(
        "board/section/add/",
        views.BoardSectionAddView.as_view(),
        name="board_section_add",
    ),
    path(
        "board/section/<int:pk>/delete/",
        views.BoardSectionDeleteView.as_view(),
        name="board_section_delete",
    ),
    path(
        "board/member/<int:pk>/delete/",
        views.BoardMemberDeleteView.as_view(),
        name="board_member_delete",
    ),
    path(
        "board/member-image-upload/",
        views.board_member_image_upload,
        name="board_member_image_upload",
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
