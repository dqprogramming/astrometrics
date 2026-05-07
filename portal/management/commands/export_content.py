"""Export cms, portal, and files content into a single zip archive.

Usage::

    python manage.py export_content /path/to/export.zip

The archive contains a manifest, per-model JSON dumps in dependency order,
and any uploaded media referenced by FileField/ImageField columns.

Foreign keys to journals.Publisher and auth.User are written as natural keys
(name / username) so they can be resolved on a target deployment whose user
and publisher PKs differ from the source. ContentType references are written
as ``{app_label, model}`` for the same reason.

Use ``import_content`` on the target deployment to load the archive.
"""

from __future__ import annotations

import datetime
import json
import os
import zipfile

from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from portal.management.commands._content_io import (
    EXPORT_FORMAT_VERSION,
    IN_SCOPE_APPS,
    ContentJSONEncoder,
    get_model,
    get_model_order,
    model_filename,
    plan_fields,
)


class Command(BaseCommand):
    help = (
        "Export cms, portal, and files content (excluding journals) to a "
        "single zip archive."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "output",
            help="Path to the .zip file to write.",
        )

    def handle(self, *args, **options):
        output_path = options["output"]
        if os.path.isdir(output_path):
            raise CommandError(f"{output_path!r} is a directory.")

        manifest = {
            "format_version": EXPORT_FORMAT_VERSION,
            "exported_at": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
            "apps": list(IN_SCOPE_APPS),
            "models": [],
        }

        with zipfile.ZipFile(
            output_path, "w", zipfile.ZIP_DEFLATED
        ) as archive:
            written_files: set[str] = set()

            for app_label, model_name in get_model_order():
                model_cls = get_model(app_label, model_name)
                rows = self._dump_model(model_cls, archive, written_files)
                manifest["models"].append(
                    {
                        "app": app_label,
                        "model": model_name,
                        "count": len(rows["rows"]),
                    }
                )
                archive.writestr(
                    model_filename(app_label, model_name),
                    json.dumps(rows, indent=2, cls=ContentJSONEncoder),
                )

            archive.writestr(
                "manifest.json",
                json.dumps(manifest, indent=2, cls=ContentJSONEncoder),
            )

        total_rows = sum(m["count"] for m in manifest["models"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Wrote {total_rows} rows across {len(manifest['models'])} "
                f"models to {output_path}"
            )
        )

    def _dump_model(self, model_cls, archive, written_files):
        plans = plan_fields(model_cls)
        rows = []

        queryset = model_cls.objects.all()
        if model_cls.__name__ == "AuditLog":
            queryset = queryset.filter(
                content_type__app_label__in=IN_SCOPE_APPS,
            )
        elif model_cls.__name__ == "PageBlock":
            queryset = queryset.filter(
                content_type__app_label__in=IN_SCOPE_APPS,
            )

        for instance in queryset:
            row = {"pk": instance.pk, "fields": {}}
            for plan in plans:
                row["fields"][plan.name] = self._serialize_field(
                    instance, plan, archive, written_files
                )
            rows.append(row)

        return {
            "model": f"{model_cls._meta.app_label}.{model_cls._meta.model_name}",
            "rows": rows,
        }

    def _serialize_field(self, instance, plan, archive, written_files):
        if plan.kind == "scalar":
            return getattr(instance, plan.name)

        if plan.kind == "file":
            field_value = getattr(instance, plan.name)
            if not field_value or not field_value.name:
                return None
            self._copy_media_into_archive(
                field_value.name, archive, written_files
            )
            return field_value.name

        if plan.kind == "fk_internal":
            return getattr(instance, plan.name + "_id")

        if plan.kind == "fk_external":
            related = getattr(instance, plan.name)
            if related is None:
                return None
            return {plan.natural_key: getattr(related, plan.natural_key)}

        if plan.kind == "fk_contenttype":
            ct_id = getattr(instance, plan.name + "_id")
            if ct_id is None:
                return None
            ct = ContentType.objects.get(pk=ct_id)
            return {"app_label": ct.app_label, "model": ct.model}

        if plan.kind == "m2m_internal":
            return list(
                getattr(instance, plan.name).values_list("pk", flat=True)
            )

        raise ValueError(f"unknown field kind {plan.kind!r}")

    def _copy_media_into_archive(self, name, archive, written_files):
        """Read a media file from default_storage and add it under media/."""
        archive_path = f"media/{name}"
        if archive_path in written_files:
            return
        try:
            with default_storage.open(name, "rb") as src:
                archive.writestr(archive_path, src.read())
        except FileNotFoundError:
            self.stderr.write(
                self.style.WARNING(
                    f"Missing media file on disk, skipping: {name}"
                )
            )
            return
        written_files.add(archive_path)
