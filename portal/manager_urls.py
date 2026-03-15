from django.urls import path

from . import views

app_name = "portal_manager"

urlpatterns = [
    path(
        "users/search/",
        views.UserSearchView.as_view(),
        name="user_search",
    ),
    path(
        "audit-log/",
        views.AuditLogListView.as_view(),
        name="audit_log",
    ),
    path(
        "audit-log/<int:pk>/revert/",
        views.RevertAuditLogView.as_view(),
        name="audit_log_revert",
    ),
    path(
        "users/",
        views.PublisherUserListView.as_view(),
        name="publisher_user_list",
    ),
    path(
        "users/add/",
        views.PublisherUserCreateView.as_view(),
        name="publisher_user_create",
    ),
    path(
        "users/<int:pk>/delete/",
        views.PublisherUserDeleteView.as_view(),
        name="publisher_user_delete",
    ),
]
