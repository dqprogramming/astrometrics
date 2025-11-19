"""
Migration to add PostgreSQL extensions and indexes for fast ORM-based search.
This is a simplified version that works well with Django's ORM.
"""

from django.contrib.postgres.operations import TrigramExtension
from django.contrib.postgres.indexes import GinIndex
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journals', '0001_initial'),
    ]

    operations = [
        # Enable PostgreSQL trigram extension for fuzzy search
        TrigramExtension(),

        # GIN trigram index on title for fuzzy search
        migrations.AddIndex(
            model_name='journal',
            index=GinIndex(
                fields=['title'],
                name='journal_title_trgm_idx',
                opclasses=['gin_trgm_ops'],
            ),
        ),

        # B-tree indexes for filters (these will speed up common queries)
        migrations.AddIndex(
            model_name='journal',
            index=models.Index(fields=['cost_gbp'], name='journal_cost_idx'),
        ),
        migrations.AddIndex(
            model_name='journal',
            index=models.Index(fields=['normalized_articles'], name='journal_articles_idx'),
        ),
        migrations.AddIndex(
            model_name='journal',
            index=models.Index(fields=['wos_impact_factor'], name='journal_impact_idx'),
        ),
        migrations.AddIndex(
            model_name='journal',
            index=models.Index(fields=['in_doaj', 'in_scopus'], name='journal_indexing_idx'),
        ),

        # Composite indexes for common filter combinations
        migrations.AddIndex(
            model_name='journal',
            index=models.Index(
                fields=['publisher', 'package_band'],
                name='journal_pub_band_idx'
            ),
        ),
    ]
