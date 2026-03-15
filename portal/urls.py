from django.urls import path

from . import views

app_name = "portal"

urlpatterns = [
    path("login/", views.PortalLoginView.as_view(), name="login"),
    path("logout/", views.PortalLogoutView.as_view(), name="logout"),
    path("", views.PortalDashboardView.as_view(), name="dashboard"),
    path(
        "publisher/", views.PublisherEditView.as_view(), name="publisher_edit"
    ),
    path(
        "journals/<int:pk>/",
        views.JournalEditView.as_view(),
        name="journal_edit",
    ),
    path(
        "journals/<int:pk>/subjects/search/",
        views.PortalSubjectSearchView.as_view(),
        name="subject_search",
    ),
    path(
        "journals/<int:pk>/subjects/add/",
        views.PortalSubjectAddView.as_view(),
        name="subject_add",
    ),
    path(
        "journals/<int:pk>/subjects/<int:item_pk>/remove/",
        views.PortalSubjectRemoveView.as_view(),
        name="subject_remove",
    ),
]
