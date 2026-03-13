import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    uuid and cover columns already exist in the database (added outside of
    migrations). This migration brings Django's state in sync without running
    any DDL against the live schema.
    """

    dependencies = [
        ("journals", "0004_remove_journal_journal_title_trgm_idx_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="journal",
                    name="uuid",
                    field=models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        unique=True,
                        help_text="Stable public identifier",
                    ),
                ),
                migrations.AddField(
                    model_name="journal",
                    name="cover",
                    field=models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="journal_covers/",
                        help_text="Journal cover image",
                    ),
                ),
            ],
            database_operations=[],  # columns already exist in the DB
        ),
    ]
