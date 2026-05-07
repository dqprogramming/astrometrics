"""Import a content export produced by ``export_content`` into this database.

Usage::

    python manage.py import_content /path/to/export.zip
    python manage.py import_content /path/to/export.zip --default-user admin

By default the cms, portal, and files tables on the target are emptied before
the load. This is necessary because migrations may seed singleton rows
(HeaderSettings, FooterSettings, etc.) that would collide with explicit-PK
inserts. Pass ``--no-truncate`` to skip the wipe (only safe on a target whose
in-scope tables are guaranteed empty).

Data is loaded with explicit PKs so internal foreign keys remain intact.

External FKs are resolved against the live target database:

* ``auth.User`` references look up by ``username``. If no match is found and
  ``--default-user`` is given, that user is used; otherwise, nullable FKs are
  set to NULL and rows whose user FK is required (e.g. PublisherUser) are
  skipped with a warning.
* ``journals.Publisher`` references look up by ``name``. If no match is
  found, dependent rows are skipped.
* ``ContentType`` references resolve by ``(app_label, model)``. Rows whose
  content type does not exist on the target are skipped.

Auto-increment PK sequences for the loaded apps are reset at the end so
subsequent inserts do not collide with imported rows.
"""

from __future__ import annotations

import json
import zipfile

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection, transaction

from portal.management.commands._content_io import (
    EXPORT_FORMAT_VERSION,
    IN_SCOPE_APPS,
    get_model,
    get_model_order,
    model_filename,
    plan_fields,
)

User = get_user_model()


class SkipRow(Exception):
    """Raised when a row cannot be imported (missing required FK)."""


class Command(BaseCommand):
    help = "Import a content export zip produced by export_content."

    def add_arguments(self, parser):
        parser.add_argument(
            "archive",
            help="Path to the export .zip file to load.",
        )
        parser.add_argument(
            "--default-user",
            default=None,
            help=(
                "Username to use as a fallback when an external User FK "
                "cannot be resolved on this database."
            ),
        )
        parser.add_argument(
            "--no-truncate",
            dest="truncate",
            action="store_false",
            default=True,
            help=(
                "Skip wiping cms/portal/files tables before loading. "
                "Only safe when the target tables are already empty."
            ),
        )

    def handle(self, *args, **options):
        archive_path = options["archive"]
        default_user_username = options["default_user"]

        default_user = None
        if default_user_username:
            try:
                default_user = User.objects.get(username=default_user_username)
            except User.DoesNotExist as exc:
                raise CommandError(
                    f"--default-user {default_user_username!r} does not exist "
                    f"on this database."
                ) from exc

        with zipfile.ZipFile(archive_path, "r") as archive:
            self._validate_manifest(archive)
            self._restore_media(archive)
            with transaction.atomic():
                if options["truncate"]:
                    self._truncate_in_scope()
                loaded_models = self._load_data(archive, default_user)
                self._reset_sequences(loaded_models)

        self.stdout.write(self.style.SUCCESS("Import complete."))

    def _truncate_in_scope(self):
        """Empty every in-scope model in reverse dependency order."""
        for app_label, model_name in reversed(get_model_order()):
            model_cls = get_model(app_label, model_name)
            model_cls.objects.all().delete()
        self.stdout.write("Truncated existing rows in cms, portal, and files.")

    def _validate_manifest(self, archive):
        try:
            raw = archive.read("manifest.json")
        except KeyError as exc:
            raise CommandError("Archive is missing manifest.json") from exc
        manifest = json.loads(raw)
        version = manifest.get("format_version")
        if version != EXPORT_FORMAT_VERSION:
            raise CommandError(
                f"Unsupported export format version: {version!r} "
                f"(expected {EXPORT_FORMAT_VERSION})"
            )
        self.stdout.write(
            f"Loading export from {manifest.get('exported_at', 'unknown')} "
            f"(apps: {', '.join(manifest.get('apps', []))})"
        )

    def _restore_media(self, archive):
        """Copy media/* entries from the archive into default_storage."""
        count = 0
        for name in archive.namelist():
            if not name.startswith("media/") or name.endswith("/"):
                continue
            relative = name[len("media/") :]
            data = archive.read(name)
            if default_storage.exists(relative):
                default_storage.delete(relative)
            default_storage.save(relative, ContentFile(data))
            count += 1
        if count:
            self.stdout.write(f"Restored {count} media file(s).")

    def _load_data(self, archive, default_user):
        loaded_models = []
        for app_label, model_name in get_model_order():
            model_cls = get_model(app_label, model_name)
            filename = model_filename(app_label, model_name)
            try:
                payload = json.loads(archive.read(filename))
            except KeyError:
                continue
            self._load_model(model_cls, payload["rows"], default_user)
            loaded_models.append(model_cls)
        return loaded_models

    def _load_model(self, model_cls, rows, default_user):
        if not rows:
            return

        plans = plan_fields(model_cls)

        # Identify self-referencing FK fields so we can defer them to a second
        # pass — explicit-PK inserts cannot reference a row that does not yet
        # exist in the same table.
        self_fk_fields = {
            plan.name
            for plan in plans
            if plan.kind == "fk_internal"
            and plan.target_model
            == (model_cls._meta.app_label, model_cls._meta.model_name)
        }

        m2m_fields = [plan for plan in plans if plan.kind == "m2m_internal"]
        non_m2m_plans = [plan for plan in plans if plan.kind != "m2m_internal"]

        deferred_self_refs = []  # (pk, {field_name: original_value})
        m2m_assignments = []  # (instance, {field_name: [pks]})
        skipped = 0

        for row in rows:
            try:
                instance, deferred_refs, m2m_data = self._build_instance(
                    model_cls,
                    row,
                    non_m2m_plans,
                    m2m_fields,
                    self_fk_fields,
                    default_user,
                )
            except SkipRow as exc:
                skipped += 1
                self.stderr.write(
                    self.style.WARNING(
                        f"Skipped {model_cls.__name__} pk={row.get('pk')}: "
                        f"{exc}"
                    )
                )
                continue

            instance.save()
            if deferred_refs:
                deferred_self_refs.append((instance.pk, deferred_refs))
            if m2m_data:
                m2m_assignments.append((instance, m2m_data))

        # Second pass: set self-referencing FKs now that all rows exist.
        for pk, refs in deferred_self_refs:
            model_cls.objects.filter(pk=pk).update(
                **{f"{name}_id": value for name, value in refs.items()}
            )

        # M2M assignments — runs after all rows are present, but the target
        # models are already loaded in earlier passes since order is fixed.
        for instance, m2m_data in m2m_assignments:
            for field_name, pks in m2m_data.items():
                getattr(instance, field_name).set(pks)

        loaded = len(rows) - skipped
        self.stdout.write(f"  {model_cls.__name__}: loaded {loaded} rows")
        if skipped:
            self.stdout.write(f"    (skipped {skipped})")

    def _build_instance(
        self,
        model_cls,
        row,
        plans,
        m2m_fields,
        self_fk_fields,
        default_user,
    ):
        kwargs = {"pk": row["pk"]}
        deferred_refs = {}
        m2m_data = {}

        for plan in plans:
            raw_value = row["fields"].get(plan.name)
            if plan.name in self_fk_fields:
                if raw_value is not None:
                    deferred_refs[plan.name] = raw_value
                kwargs[f"{plan.name}_id"] = None
                continue
            kwargs.update(
                self._materialize(plan, raw_value, model_cls, default_user)
            )

        for plan in m2m_fields:
            raw_value = row["fields"].get(plan.name) or []
            if raw_value:
                m2m_data[plan.name] = raw_value

        instance = model_cls(**kwargs)
        return instance, deferred_refs, m2m_data

    def _materialize(self, plan, raw_value, model_cls, default_user):
        """Translate a serialised field value into kwargs for model.__init__."""
        if plan.kind == "scalar":
            return {plan.name: raw_value}

        if plan.kind == "file":
            return {plan.name: raw_value or ""}

        if plan.kind == "fk_internal":
            return {f"{plan.name}_id": raw_value}

        if plan.kind == "fk_external":
            if raw_value is None:
                return {f"{plan.name}_id": None}
            target_field = plan.natural_key
            value = (
                raw_value.get(target_field)
                if isinstance(raw_value, dict)
                else None
            )
            related = self._resolve_external(
                model_cls, plan, target_field, value, default_user
            )
            if related is None:
                model = model_cls._meta.get_field(plan.name).related_model
                if (
                    model is User
                    and not model_cls._meta.get_field(plan.name).null
                ):
                    raise SkipRow(
                        f"required user {value!r} not found "
                        f"and no default-user usable"
                    )
                if not model_cls._meta.get_field(plan.name).null:
                    raise SkipRow(f"required {plan.name} {value!r} not found")
                return {f"{plan.name}_id": None}
            return {f"{plan.name}_id": related.pk}

        if plan.kind == "fk_contenttype":
            if raw_value is None:
                return {f"{plan.name}_id": None}
            try:
                ct = ContentType.objects.get(
                    app_label=raw_value["app_label"],
                    model=raw_value["model"],
                )
            except ContentType.DoesNotExist as exc:
                raise SkipRow(
                    f"content type "
                    f"{raw_value['app_label']}.{raw_value['model']} "
                    f"not found on target"
                ) from exc
            return {f"{plan.name}_id": ct.pk}

        raise ValueError(f"unknown plan kind {plan.kind!r}")

    def _resolve_external(
        self, model_cls, plan, target_field, value, default_user
    ):
        if value is None:
            return None
        related_model = model_cls._meta.get_field(plan.name).related_model
        try:
            return related_model.objects.get(**{target_field: value})
        except related_model.DoesNotExist:
            if related_model is User and default_user is not None:
                self.stderr.write(
                    self.style.WARNING(
                        f"User {value!r} not found, using --default-user "
                        f"for {model_cls.__name__}.{plan.name}"
                    )
                )
                return default_user
            return None

    def _reset_sequences(self, models):
        """Reset Postgres sequences for in-scope tables after explicit-PK inserts."""
        if not models:
            return
        sql_statements = connection.ops.sequence_reset_sql(no_style(), models)
        if not sql_statements:
            return
        with connection.cursor() as cursor:
            for sql in sql_statements:
                cursor.execute(sql)
        self.stdout.write(
            f"Reset {len(sql_statements)} PK sequence(s) for "
            f"{', '.join(IN_SCOPE_APPS)}."
        )
