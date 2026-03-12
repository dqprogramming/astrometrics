"""
Django admin configuration for journal management.
"""

from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import ImportLog, Journal, Language, Publisher, Subject


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ["name", "journal_count", "website_link", "created_at"]
    search_fields = ["name"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at", "updated_at"]

    def journal_count(self, obj):
        return obj.journals.count()

    journal_count.short_description = "Number of Journals"

    def website_link(self, obj):
        if obj.website:
            return format_html(
                '<a href="{}" target="_blank">Visit</a>', obj.website
            )
        return "-"

    website_link.short_description = "Website"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(journals_count=Count("journals"))


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["name", "journal_count", "created_at"]
    search_fields = ["name"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at", "updated_at"]

    def journal_count(self, obj):
        return obj.journals.count()

    journal_count.short_description = "Number of Journals"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(journals_count=Count("journals"))


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "journal_count", "created_at"]
    search_fields = ["name", "code"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at", "updated_at"]

    def journal_count(self, obj):
        return obj.journals.count()

    journal_count.short_description = "Number of Journals"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(journals_count=Count("journals"))


class SubjectInline(admin.TabularInline):
    model = Journal.subjects.through
    extra = 1
    verbose_name = "Subject"
    verbose_name_plural = "Subjects"


class LanguageInline(admin.TabularInline):
    model = Journal.languages.through
    extra = 1
    verbose_name = "Language"
    verbose_name_plural = "Languages"


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "publisher",
        "package_band",
        "cost_gbp",
        "normalized_articles",
        "cost_per_article_display",
        "in_doaj",
        "in_scopus",
        "created_at",
    ]

    list_filter = [
        "publisher",
        "package_band",
        "in_doaj",
        "in_scopus",
        "licensing",
        "created_at",
    ]

    search_fields = ["title", "description", "issn", "publisher__name"]

    readonly_fields = ["created_at", "updated_at", "cost_per_article_display"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "year_established",
                    "publisher",
                    "journal_owner",
                    "description",
                )
            },
        ),
        (
            "URLs & Identifiers",
            {"fields": ("journal_url", "publisher_url", "issn")},
        ),
        (
            "Cost & Package",
            {
                "fields": (
                    "package_band",
                    "cost_gbp",
                    "normalized_articles",
                    "cost_per_article_display",
                )
            },
        ),
        (
            "Indexing & Impact",
            {"fields": ("in_doaj", "in_scopus", "wos_impact_factor")},
        ),
        (
            "Archive Information",
            {
                "fields": (
                    "archive_available_diamond_oa",
                    "archive_years",
                    "archiving_services",
                )
            },
        ),
        ("Licensing & Other", {"fields": ("licensing", "usps")}),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    filter_horizontal = ["languages", "subjects"]

    # Inlines can be used instead of filter_horizontal if preferred
    # inlines = [LanguageInline, SubjectInline]

    def cost_per_article_display(self, obj):
        """Display calculated cost per article."""
        cost = obj.cost_per_article
        if cost:
            return f"£{cost:.2f}"
        return "-"

    cost_per_article_display.short_description = "Cost per Article"

    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        qs = super().get_queryset(request)
        return qs.select_related("publisher").prefetch_related(
            "languages", "subjects"
        )

    actions = ["export_to_csv", "mark_in_doaj", "mark_not_in_doaj"]

    def mark_in_doaj(self, request, queryset):
        """Mark selected journals as listed in DOAJ."""
        count = queryset.update(in_doaj=True)
        self.message_user(request, f"{count} journal(s) marked as in DOAJ.")

    mark_in_doaj.short_description = "Mark selected journals as in DOAJ"

    def mark_not_in_doaj(self, request, queryset):
        """Mark selected journals as not listed in DOAJ."""
        count = queryset.update(in_doaj=False)
        self.message_user(
            request, f"{count} journal(s) marked as not in DOAJ."
        )

    mark_not_in_doaj.short_description = (
        "Mark selected journals as not in DOAJ"
    )

    def export_to_csv(self, request, queryset):
        """Export selected journals to CSV."""
        import csv
        from datetime import datetime

        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"journals_export_{timestamp}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "Title",
                "Publisher",
                "Package Band",
                "Cost (GBP)",
                "Normalized Articles",
                "Cost per Article",
                "ISSN",
                "In DOAJ",
                "In Scopus",
                "WOS Impact Factor",
                "Languages",
                "Subjects",
                "License",
            ]
        )

        for journal in queryset:
            languages = ", ".join(
                lang.name for lang in journal.languages.all()
            )
            subjects = ", ".join(subj.name for subj in journal.subjects.all())
            cost_per_article = journal.cost_per_article or ""

            writer.writerow(
                [
                    journal.title,
                    journal.publisher.name,
                    journal.package_band,
                    journal.cost_gbp or "",
                    journal.normalized_articles or "",
                    f"{cost_per_article:.2f}" if cost_per_article else "",
                    journal.issn,
                    "Yes" if journal.in_doaj else "No",
                    "Yes" if journal.in_scopus else "No",
                    journal.wos_impact_factor or "",
                    languages,
                    subjects,
                    journal.licensing,
                ]
            )

        return response

    export_to_csv.short_description = "Export selected journals to CSV"


@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = [
        "filename",
        "status",
        "records_processed",
        "records_created",
        "records_updated",
        "records_failed",
        "started_at",
        "completed_at",
    ]

    list_filter = ["status", "started_at"]
    search_fields = ["filename", "error_log"]
    readonly_fields = [
        "filename",
        "status",
        "records_processed",
        "records_created",
        "records_updated",
        "records_failed",
        "error_log",
        "started_at",
        "completed_at",
    ]

    fieldsets = (
        (
            "Import Information",
            {"fields": ("filename", "status", "started_at", "completed_at")},
        ),
        (
            "Statistics",
            {
                "fields": (
                    "records_processed",
                    "records_created",
                    "records_updated",
                    "records_failed",
                )
            },
        ),
        ("Error Log", {"fields": ("error_log",), "classes": ("collapse",)}),
    )

    def has_add_permission(self, request):
        """Prevent manual creation of import logs."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion of old import logs."""
        return True
