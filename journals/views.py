"""
Advanced journal search views with PostgreSQL full-text search capabilities.
Clean ORM implementation for simplicity and maintainability.
"""

from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count, Avg, Min, Max
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.views.generic import ListView
from decimal import Decimal

from journals.models import Journal, Publisher, Subject, Language, PackageBand


class JournalSearchView(ListView):
    """
    Advanced journal search view with filtering and PostgreSQL full-text search.
    Clean ORM implementation for simplicity and maintainability.
    """
    model = Journal
    template_name = 'journals/search.html'
    context_object_name = 'journals'
    paginate_by = 25
    
    def get_queryset(self):
        """Build filtered and searched queryset with optimizations."""
        # Start with optimized base query
        queryset = Journal.objects.select_related(
            'publisher', 
            'package_band'
        ).prefetch_related(
            'languages',
            'subjects'
        )
        
        # Get search parameters
        search_query = self.request.GET.get('q', '').strip()
        search_fields = self.request.GET.getlist('search_fields')
        
        # Apply filters FIRST (before search) for better performance
        queryset = self._apply_filters(queryset)
        
        # Apply search if query provided (on already filtered set)
        if search_query:
            queryset = self._apply_search(queryset, search_query, search_fields)
        else:
            # Apply ordering only when not searching (search has its own ranking)
            queryset = self._apply_ordering(queryset)
        
        return queryset
    
    def _apply_search(self, queryset, search_query, search_fields):
        """
        Apply PostgreSQL full-text search or trigram similarity search.
        """
        use_fuzzy = self.request.GET.get('fuzzy', 'off') == 'on'
        
        if use_fuzzy:
            # Trigram fuzzy search on title only
            return queryset.annotate(
                similarity=TrigramSimilarity('title', search_query)
            ).filter(
                similarity__gt=0.2
            ).order_by('-similarity')
        
        # Default to searching main fields if none specified
        if not search_fields:
            search_fields = ['title', 'description']
        
        # Build search vector based on selected fields
        search_vectors = []
        
        if 'title' in search_fields:
            search_vectors.append(SearchVector('title', weight='A', config='english'))
        
        if 'description' in search_fields:
            search_vectors.append(SearchVector('description', weight='B', config='english'))
        
        if 'publisher' in search_fields:
            search_vectors.append(SearchVector('publisher__name', weight='C', config='english'))
        
        if 'subjects' in search_fields:
            search_vectors.append(SearchVector('subjects__name', weight='D', config='english'))
        
        if 'issn' in search_fields:
            search_vectors.append(SearchVector('issn', weight='A', config='english'))
        
        if 'journal_owner' in search_fields:
            search_vectors.append(SearchVector('journal_owner', weight='C', config='english'))
        
        # Combine search vectors
        if not search_vectors:
            return queryset
        
        combined_vector = search_vectors[0]
        for vector in search_vectors[1:]:
            combined_vector = combined_vector + vector
        
        # Create search query with websearch syntax
        search_query_obj = SearchQuery(search_query, search_type='websearch', config='english')
        
        # Annotate with rank and filter
        return queryset.annotate(
            rank=SearchRank(combined_vector, search_query_obj)
        ).filter(
            rank__gt=0
        ).order_by('-rank')
    
    def _apply_filters(self, queryset):
        """
        Apply various filters based on GET parameters.
        Optimized to use indexes and avoid unnecessary queries.
        """
        
        # Publisher filter (indexed FK)
        publisher_ids = self.request.GET.getlist('publisher')
        if publisher_ids:
            # Convert to integers to use index properly
            publisher_ids = [int(pid) for pid in publisher_ids if pid.isdigit()]
            queryset = queryset.filter(publisher_id__in=publisher_ids)
        
        # Package band filter (indexed FK)
        package_band_ids = self.request.GET.getlist('package_band')
        if package_band_ids:
            package_band_ids = [int(pid) for pid in package_band_ids if pid.isdigit()]
            queryset = queryset.filter(package_band_id__in=package_band_ids)
        
        # Subject filter (M2M - can't fully optimize without denormalization)
        subject_ids = self.request.GET.getlist('subject')
        if subject_ids:
            subject_ids = [int(sid) for sid in subject_ids if sid.isdigit()]
            queryset = queryset.filter(subjects__id__in=subject_ids)
        
        # Language filter (M2M)
        language_ids = self.request.GET.getlist('language')
        if language_ids:
            language_ids = [int(lid) for lid in language_ids if lid.isdigit()]
            queryset = queryset.filter(languages__id__in=language_ids)
        
        # Boolean filters (uses composite index)
        in_doaj = self.request.GET.get('in_doaj')
        if in_doaj == 'yes':
            queryset = queryset.filter(in_doaj=True)
        elif in_doaj == 'no':
            queryset = queryset.filter(in_doaj=False)
        
        in_scopus = self.request.GET.get('in_scopus')
        if in_scopus == 'yes':
            queryset = queryset.filter(in_scopus=True)
        elif in_scopus == 'no':
            queryset = queryset.filter(in_scopus=False)
        
        # Has impact factor (uses index)
        has_impact_factor = self.request.GET.get('has_impact_factor')
        if has_impact_factor == 'yes':
            queryset = queryset.filter(wos_impact_factor__isnull=False)
        elif has_impact_factor == 'no':
            queryset = queryset.filter(wos_impact_factor__isnull=True)
        
        # Cost range filter (uses index on cost_gbp)
        cost_min = self.request.GET.get('cost_min')
        cost_max = self.request.GET.get('cost_max')
        if cost_min or cost_max:
            try:
                if cost_min:
                    queryset = queryset.filter(cost_gbp__gte=Decimal(cost_min))
                if cost_max:
                    queryset = queryset.filter(cost_gbp__lte=Decimal(cost_max))
            except (ValueError, TypeError):
                pass
        
        # Article count range (uses index)
        articles_min = self.request.GET.get('articles_min')
        articles_max = self.request.GET.get('articles_max')
        if articles_min or articles_max:
            try:
                if articles_min:
                    queryset = queryset.filter(normalized_articles__gte=Decimal(articles_min))
                if articles_max:
                    queryset = queryset.filter(normalized_articles__lte=Decimal(articles_max))
            except (ValueError, TypeError):
                pass
        
        # Impact factor range (uses index)
        impact_min = self.request.GET.get('impact_min')
        impact_max = self.request.GET.get('impact_max')
        if impact_min or impact_max:
            try:
                if impact_min:
                    queryset = queryset.filter(wos_impact_factor__gte=Decimal(impact_min))
                if impact_max:
                    queryset = queryset.filter(wos_impact_factor__lte=Decimal(impact_max))
            except (ValueError, TypeError):
                pass
        
        # License filter (B-tree index via choices)
        license_type = self.request.GET.get('license')
        if license_type:
            queryset = queryset.filter(licensing=license_type)
        
        # Archive years filter
        archive_years_min = self.request.GET.get('archive_years_min')
        if archive_years_min:
            try:
                queryset = queryset.filter(archive_years__gte=int(archive_years_min))
            except (ValueError, TypeError):
                pass
        
        # Year established range (string comparison, not ideal but acceptable)
        year_min = self.request.GET.get('year_min')
        year_max = self.request.GET.get('year_max')
        if year_min:
            queryset = queryset.filter(year_established__gte=year_min)
        if year_max:
            queryset = queryset.filter(year_established__lte=year_max)
        
        # Apply distinct only if M2M filters were used
        if subject_ids or language_ids:
            queryset = queryset.distinct()
        
        return queryset
    
    def _apply_ordering(self, queryset):
        """Apply ordering based on GET parameter."""
        order_by = self.request.GET.get('order_by', 'title')
        order_dir = self.request.GET.get('order_dir', 'asc')
        
        valid_fields = {
            'title': 'title',
            'cost': 'cost_gbp',
            'articles': 'normalized_articles',
            'impact': 'wos_impact_factor',
            'publisher': 'publisher__name',
            'package_band': 'package_band__code',
            'created': 'created_at',
        }
        
        order_field = valid_fields.get(order_by, 'title')
        
        if order_dir == 'desc':
            order_field = f'-{order_field}'
        
        # Don't re-order if already ordered by search rank
        if 'rank' not in [f.name for f in queryset.query.annotations]:
            queryset = queryset.order_by(order_field)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add filter options and statistics to context."""
        context = super().get_context_data(**kwargs)
        
        # Add filter options
        context['publishers'] = Publisher.objects.all().order_by('name')
        context['package_bands'] = PackageBand.objects.all().order_by('code')
        context['subjects'] = Subject.objects.all().order_by('name')
        context['languages'] = Language.objects.all().order_by('name')
        context['license_choices'] = Journal.LICENSE_CHOICES
        
        # Add current filter values for form persistence
        context['current_filters'] = {
            'q': self.request.GET.get('q', ''),
            'search_fields': self.request.GET.getlist('search_fields'),
            'publisher': self.request.GET.getlist('publisher'),
            'package_band': self.request.GET.getlist('package_band'),
            'subject': self.request.GET.getlist('subject'),
            'language': self.request.GET.getlist('language'),
            'in_doaj': self.request.GET.get('in_doaj', ''),
            'in_scopus': self.request.GET.get('in_scopus', ''),
            'has_impact_factor': self.request.GET.get('has_impact_factor', ''),
            'cost_min': self.request.GET.get('cost_min', ''),
            'cost_max': self.request.GET.get('cost_max', ''),
            'articles_min': self.request.GET.get('articles_min', ''),
            'articles_max': self.request.GET.get('articles_max', ''),
            'impact_min': self.request.GET.get('impact_min', ''),
            'impact_max': self.request.GET.get('impact_max', ''),
            'license': self.request.GET.get('license', ''),
            'archive_years_min': self.request.GET.get('archive_years_min', ''),
            'year_min': self.request.GET.get('year_min', ''),
            'year_max': self.request.GET.get('year_max', ''),
            'order_by': self.request.GET.get('order_by', 'title'),
            'order_dir': self.request.GET.get('order_dir', 'asc'),
            'fuzzy': self.request.GET.get('fuzzy', 'off'),
        }
        
        # Add statistics for filtered results
        # Using single aggregate query for efficiency
        base_queryset = self.get_queryset()
        
        stats = base_queryset.aggregate(
            total_count=Count('id'),
            avg_cost=Avg('cost_gbp'),
            min_cost=Min('cost_gbp'),
            max_cost=Max('cost_gbp'),
            avg_articles=Avg('normalized_articles'),
            doaj_count=Count('id', filter=Q(in_doaj=True)),
            scopus_count=Count('id', filter=Q(in_scopus=True)),
        )
        
        context['statistics'] = stats
        
        # Build query string for pagination links (exclude page param)
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')
        context['query_string'] = query_params.urlencode()
        
        return context


def journal_detail_view(request, pk):
    """Detailed view of a single journal."""
    journal = get_object_or_404(
        Journal.objects.select_related('publisher', 'package_band')
        .prefetch_related('languages', 'subjects'),
        pk=pk
    )
    
    # Get related journals (same publisher or subjects)
    related_journals = Journal.objects.filter(
        Q(publisher=journal.publisher) | Q(subjects__in=journal.subjects.all())
    ).exclude(pk=journal.pk).distinct()[:5]
    
    context = {
        'journal': journal,
        'related_journals': related_journals,
    }
    
    return render(request, 'journals/detail.html', context)


def journal_stats_view(request):
    """Dashboard view with statistics and charts data."""
    from django.db.models import Count, Sum
    
    # Overall statistics
    total_journals = Journal.objects.count()
    total_cost = Journal.objects.aggregate(Sum('cost_gbp'))['cost_gbp__sum'] or 0
    avg_cost = Journal.objects.aggregate(Avg('cost_gbp'))['cost_gbp__avg'] or 0
    avg_articles = Journal.objects.aggregate(Avg('normalized_articles'))['normalized_articles__avg'] or 0
    
    # By publisher
    by_publisher = Publisher.objects.annotate(
        journal_count=Count('journals'),
        total_cost=Sum('journals__cost_gbp'),
        avg_cost=Avg('journals__cost_gbp')
    ).order_by('-journal_count')[:10]
    
    # By package band
    by_package_band = PackageBand.objects.annotate(
        journal_count=Count('journals'),
        total_cost=Sum('journals__cost_gbp'),
        avg_cost=Avg('journals__cost_gbp')
    ).order_by('code')
    
    # By subject
    by_subject = Subject.objects.annotate(
        journal_count=Count('journals')
    ).order_by('-journal_count')[:15]
    
    # DOAJ and Scopus coverage
    doaj_count = Journal.objects.filter(in_doaj=True).count()
    scopus_count = Journal.objects.filter(in_scopus=True).count()
    impact_factor_count = Journal.objects.filter(wos_impact_factor__isnull=False).count()
    
    # License distribution
    license_distribution = Journal.objects.values('licensing').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_journals': total_journals,
        'total_cost': total_cost,
        'avg_cost': avg_cost,
        'avg_articles': avg_articles,
        'by_publisher': by_publisher,
        'by_package_band': by_package_band,
        'by_subject': by_subject,
        'doaj_count': doaj_count,
        'doaj_percentage': (doaj_count / total_journals * 100) if total_journals else 0,
        'scopus_count': scopus_count,
        'scopus_percentage': (scopus_count / total_journals * 100) if total_journals else 0,
        'impact_factor_count': impact_factor_count,
        'license_distribution': license_distribution,
    }
    
    return render(request, 'journals/stats.html', context)
