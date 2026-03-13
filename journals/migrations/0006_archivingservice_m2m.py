"""
Convert archiving_services from a free-text TextField to a proper M2M
relationship with a new ArchivingService model.

Steps performed in a single migration:
  1. Create ArchivingService table
  2. Rename old TextField to archiving_services_raw
  3. Add new M2M archiving_services
  4. Data migration: parse existing text → ArchivingService objects → M2M links
  5. Drop archiving_services_raw
"""

import re

from django.db import migrations, models


def _parse_services(raw):
    """Split messy text into individual service names."""
    parts = re.split(r"[\n,]+", raw or "")
    return [p.strip() for p in parts if p.strip() and p.strip().lower() != "n/a"]


def populate_m2m(apps, schema_editor):
    Journal = apps.get_model("journals", "Journal")
    ArchivingService = apps.get_model("journals", "ArchivingService")
    for journal in Journal.objects.exclude(archiving_services_raw=""):
        for name in _parse_services(journal.archiving_services_raw):
            if len(name) > 100:  # skip free-text notes accidentally stored here
                continue
            svc, _ = ArchivingService.objects.get_or_create(name=name)
            journal.archiving_services.add(svc)


class Migration(migrations.Migration):
    dependencies = [
        ("journals", "0004_remove_journal_journal_title_trgm_idx_and_more"),
    ]

    operations = [
        # 1. Create ArchivingService
        migrations.CreateModel(
            name="ArchivingService",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("name", models.CharField(help_text="Archiving service name", max_length=255, unique=True)),
            ],
            options={
                "verbose_name": "Archiving Service",
                "verbose_name_plural": "Archiving Services",
                "ordering": ["name"],
            },
        ),
        # 2. Rename old TextField so we can reuse the field name
        migrations.RenameField(
            model_name="journal",
            old_name="archiving_services",
            new_name="archiving_services_raw",
        ),
        # 3. Add new M2M
        migrations.AddField(
            model_name="journal",
            name="archiving_services",
            field=models.ManyToManyField(
                blank=True,
                help_text="Archiving services (CLOCKSS, LOCKSS, PKP PN, etc.)",
                related_name="journals",
                to="journals.archivingservice",
            ),
        ),
        # 4. Populate M2M from old text
        migrations.RunPython(populate_m2m, migrations.RunPython.noop),
        # 5. Drop old field
        migrations.RemoveField(
            model_name="journal",
            name="archiving_services_raw",
        ),
    ]
