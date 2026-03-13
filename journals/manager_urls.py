from django.urls import path

from . import manager_views as views

app_name = "journals_manager"

urlpatterns = [
    # Journals
    path("journals/", views.JournalListView.as_view(), name="journal_list"),
    path(
        "journals/new/",
        views.JournalCreateView.as_view(),
        name="journal_create",
    ),
    path(
        "journals/<int:pk>/edit/",
        views.JournalUpdateView.as_view(),
        name="journal_edit",
    ),
    path(
        "journals/<int:pk>/delete/",
        views.JournalDeleteView.as_view(),
        name="journal_delete",
    ),
    path(
        "journals/<int:pk>/tags/<str:field>/search/",
        views.JournalTagSearchView.as_view(),
        name="journal_tag_search",
    ),
    path(
        "journals/<int:pk>/tags/<str:field>/add/",
        views.JournalTagAddView.as_view(),
        name="journal_tag_add",
    ),
    path(
        "journals/<int:pk>/tags/<str:field>/<int:item_pk>/remove/",
        views.JournalTagRemoveView.as_view(),
        name="journal_tag_remove",
    ),
    # Archiving Services
    path(
        "archiving-services/",
        views.ArchivingServiceListView.as_view(),
        name="archivingservice_list",
    ),
    path(
        "archiving-services/new/",
        views.ArchivingServiceCreateView.as_view(),
        name="archivingservice_create",
    ),
    path(
        "archiving-services/<int:pk>/edit/",
        views.ArchivingServiceUpdateView.as_view(),
        name="archivingservice_edit",
    ),
    path(
        "archiving-services/<int:pk>/delete/",
        views.ArchivingServiceDeleteView.as_view(),
        name="archivingservice_delete",
    ),
    # Publishers
    path(
        "publishers/", views.PublisherListView.as_view(), name="publisher_list"
    ),
    path(
        "publishers/new/",
        views.PublisherCreateView.as_view(),
        name="publisher_create",
    ),
    path(
        "publishers/<int:pk>/edit/",
        views.PublisherUpdateView.as_view(),
        name="publisher_edit",
    ),
    path(
        "publishers/<int:pk>/delete/",
        views.PublisherDeleteView.as_view(),
        name="publisher_delete",
    ),
    # Subjects
    path("subjects/", views.SubjectListView.as_view(), name="subject_list"),
    path(
        "subjects/new/",
        views.SubjectCreateView.as_view(),
        name="subject_create",
    ),
    path(
        "subjects/<int:pk>/edit/",
        views.SubjectUpdateView.as_view(),
        name="subject_edit",
    ),
    path(
        "subjects/<int:pk>/delete/",
        views.SubjectDeleteView.as_view(),
        name="subject_delete",
    ),
    # Languages
    path("languages/", views.LanguageListView.as_view(), name="language_list"),
    path(
        "languages/new/",
        views.LanguageCreateView.as_view(),
        name="language_create",
    ),
    path(
        "languages/<int:pk>/edit/",
        views.LanguageUpdateView.as_view(),
        name="language_edit",
    ),
    path(
        "languages/<int:pk>/delete/",
        views.LanguageDeleteView.as_view(),
        name="language_delete",
    ),
    # Package Bands
    path(
        "package-bands/",
        views.PackageBandListView.as_view(),
        name="packageband_list",
    ),
    path(
        "package-bands/new/",
        views.PackageBandCreateView.as_view(),
        name="packageband_create",
    ),
    path(
        "package-bands/<int:pk>/edit/",
        views.PackageBandUpdateView.as_view(),
        name="packageband_edit",
    ),
    path(
        "package-bands/<int:pk>/delete/",
        views.PackageBandDeleteView.as_view(),
        name="packageband_delete",
    ),
    # Import / Export
    path("import/", views.ImportView.as_view(), name="import"),
    path(
        "import/logs/",
        views.ImportLogListView.as_view(),
        name="import_log_list",
    ),
    path(
        "import/logs/<int:pk>/",
        views.ImportLogDetailView.as_view(),
        name="import_log_detail",
    ),
    path("export/", views.ExportView.as_view(), name="export"),
]
