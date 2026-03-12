"""
Public-facing journal search views.
Simplified interface for browsing the journal catalogue.
"""

from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from journals.models import Journal, Language, Publisher, Subject


class PublicJournalSearchView(ListView):
    """Simplified public-facing journal search view.

    Less complex than the admin version, focusing on
    basic search and filtering.
    """

    model = Journal
    template_name = "public/public_search.html"
    context_object_name = "journals"
    paginate_by = 20

    def get_queryset(self):
        """Build filtered and searched queryset."""
        # Start with optimized base query
        queryset = Journal.objects.select_related(
            "publisher"
        ).prefetch_related("languages", "subjects")

        # Get search parameters
        search_query = self.request.GET.get("q", "").strip()

        # Apply filters
        queryset = self._apply_filters(queryset)

        # Apply search if query provided
        if search_query:
            queryset = self._apply_search(queryset, search_query)
        else:
            # Default ordering by title
            queryset = queryset.order_by("title")

        return queryset

    def _apply_search(self, queryset, search_query):
        """Apply full-text search across main fields."""
        # Build search vector for title, description, publisher, and subjects
        search_vector = (
            SearchVector("title", weight="A", config="english")
            + SearchVector("description", weight="B", config="english")
            + SearchVector("publisher__name", weight="C", config="english")
            + SearchVector("subjects__name", weight="B", config="english")
        )

        # Create search query with websearch syntax
        search_query_obj = SearchQuery(
            search_query, search_type="websearch", config="english"
        )

        # Annotate with rank and filter
        # Use distinct() because subjects is a M2M relationship
        return (
            queryset.annotate(rank=SearchRank(search_vector, search_query_obj))
            .filter(rank__gt=0)
            .distinct()
            .order_by("-rank")
        )

    def _apply_filters(self, queryset):
        """
        Apply simplified filters based on GET parameters.
        """
        # Subject filter (single select)
        subject_id = self.request.GET.get("subject")
        if subject_id:
            try:
                queryset = queryset.filter(
                    subjects__id=int(subject_id)
                ).distinct()
            except (ValueError, TypeError):
                pass

        # Publisher filter (single select)
        publisher_id = self.request.GET.get("publisher")
        if publisher_id:
            try:
                queryset = queryset.filter(publisher_id=int(publisher_id))
            except (ValueError, TypeError):
                pass

        # Language filter (single select)
        language_id = self.request.GET.get("language")
        if language_id:
            try:
                queryset = queryset.filter(
                    languages__id=int(language_id)
                ).distinct()
            except (ValueError, TypeError):
                pass

        # DOAJ filter
        in_doaj = self.request.GET.get("in_doaj")
        if in_doaj == "yes":
            queryset = queryset.filter(in_doaj=True)

        return queryset

    def get_context_data(self, **kwargs):
        """Add filter options and statistics to context."""
        context = super().get_context_data(**kwargs)

        # Add filter options (limit to most common for public view)
        context["publishers"] = (
            Publisher.objects.annotate(journal_count=Count("journals"))
            .filter(journal_count__gt=0)
            .order_by("name")[:50]
        )

        context["subjects"] = (
            Subject.objects.annotate(journal_count=Count("journals"))
            .filter(journal_count__gt=0)
            .order_by("name")[:30]
        )

        context["languages"] = (
            Language.objects.annotate(journal_count=Count("journals"))
            .filter(journal_count__gt=0)
            .order_by("name")[:20]
        )

        # Add current filter values for form persistence
        context["current_filters"] = {
            "q": self.request.GET.get("q", ""),
            "subject": self.request.GET.get("subject", ""),
            "publisher": self.request.GET.get("publisher", ""),
            "language": self.request.GET.get("language", ""),
            "in_doaj": self.request.GET.get("in_doaj", ""),
        }

        # Add statistics for filtered results
        base_queryset = self.get_queryset()

        stats = base_queryset.aggregate(
            total_count=Count("id"),
            doaj_count=Count("id", filter=Q(in_doaj=True)),
            scopus_count=Count("id", filter=Q(in_scopus=True)),
        )

        context["statistics"] = stats

        # Build query string for pagination links (exclude page param)
        query_params = self.request.GET.copy()
        if "page" in query_params:
            query_params.pop("page")
        context["query_string"] = query_params.urlencode()

        return context


def public_journal_detail_view(request, pk):
    """Public detailed view of a single journal."""
    journal = get_object_or_404(
        Journal.objects.select_related(
            "publisher", "package_band"
        ).prefetch_related("languages", "subjects"),
        pk=pk,
    )

    # Get related journals (same publisher or subjects)
    related_journals = (
        Journal.objects.filter(
            Q(publisher=journal.publisher)
            | Q(subjects__in=journal.subjects.all())
        )
        .exclude(pk=journal.pk)
        .distinct()[:6]
    )

    context = {
        "journal": journal,
        "related_journals": related_journals,
    }

    return render(request, "public/public_detail.html", context)
