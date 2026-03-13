"""
URL configuration for journal search and detail views.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from journals.views import JournalSearchView, journal_detail_view, journal_stats_view
from journals.public_views import PublicJournalSearchView, public_journal_detail_view

app_name = 'journals'

urlpatterns = [
    # Admin/Internal Routes
    path('manager/search/', JournalSearchView.as_view(), name='search'),
    path('manager/stats/', journal_stats_view, name='stats'),
    path('manager/<int:pk>/', journal_detail_view, name='detail'),

    # Public Routes
    path('', PublicJournalSearchView.as_view(), name='public_search'),
    path('journal/<int:pk>/', public_journal_detail_view, name='public_detail'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
