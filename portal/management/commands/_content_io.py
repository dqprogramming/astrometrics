"""Shared configuration and helpers for content export/import.

The export and import commands move cms, portal, and files data between
deployments while leaving the journals app untouched.

Internal foreign keys preserve PKs verbatim. External foreign keys (auth.User,
journals.Publisher) and ContentType references are serialised as natural keys
and resolved against the target database on import.
"""

from __future__ import annotations

import datetime
import decimal
import json
import uuid
from dataclasses import dataclass

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

EXPORT_FORMAT_VERSION = 1

IN_SCOPE_APPS = ("cms", "portal", "files")


def _block_models():
    """Return concrete block model classes registered in cms.block_registry."""
    from cms.block_registry import _registry

    return list(_registry.values())


def get_model_order():
    """Return the ordered list of (app_label, model_name) tuples to dump.

    Order matters: parents come before children so explicit-PK inserts on the
    target side never violate a FK constraint. Block subclasses are pulled
    from the registry so adding a block doesn't require touching this file.
    """
    order = [
        ("files", "MediaFile"),
        ("cms", "Category"),
        ("cms", "Page"),
        ("cms", "Post"),
        ("cms", "FooterSettings"),
        ("cms", "FooterLink"),
        ("cms", "HeaderSettings"),
        ("cms", "MenuItem"),
        ("cms", "Snippet"),
        ("cms", "BlockPageTemplate"),
        ("cms", "BlockPage"),
    ]
    for cls in _block_models():
        order.append((cls._meta.app_label, cls.__name__))
    order += [
        ("cms", "PersonCarouselQuote"),
        ("cms", "PeopleListPerson"),
        ("cms", "InstitutionEntry"),
        ("cms", "RevenueTableColumn"),
        ("cms", "RevenuePackageTable"),
        ("cms", "RevenuePackageRow"),
        ("cms", "RevenuePackageCell"),
        ("cms", "OrgCarouselQuote"),
        ("cms", "ContactFormRecipient"),
        ("cms", "PageBlock"),
        ("portal", "PublisherUser"),
        ("portal", "AuditLog"),
    ]
    return order


# Foreign keys that point outside the in-scope apps. Values are the natural-key
# field on the target model used to resolve the reference at import time.
EXTERNAL_FK_NATURAL_KEYS = {
    # (app_label, model_name, field_name): natural_key_field_on_target
    ("files", "mediafile", "created_by"): "username",
    ("portal", "publisheruser", "user"): "username",
    ("portal", "publisheruser", "publisher"): "name",
    ("portal", "auditlog", "user"): "username",
}


def model_key(model_cls):
    return (model_cls._meta.app_label, model_cls._meta.model_name)


def model_filename(app_label, model_name):
    """Filename inside the export zip for a given model's data."""
    return f"data/{app_label}__{model_name.lower()}.json"


def get_model(app_label, model_name):
    return apps.get_model(app_label, model_name)


@dataclass
class FieldPlan:
    """Describes how to serialise/deserialise a single model field."""

    name: str
    kind: str  # "scalar", "fk_internal", "fk_external", "fk_contenttype",
    #          "file", "m2m_internal"
    natural_key: str | None = None  # for fk_external
    target_model: tuple | None = None  # for fk_internal / m2m_internal


def plan_fields(model_cls):
    """Build a list of FieldPlan describing each persistable field on a model.

    Skips reverse relations, GenericForeignKey (handled via its underlying
    content_type + object_id fields), and auto fields like the implicit pk
    (the pk is dumped separately).
    """
    plans: list[FieldPlan] = []
    app_label, model_name = model_key(model_cls)

    for field in model_cls._meta.get_fields():
        if isinstance(field, GenericForeignKey):
            continue
        if field.auto_created and not field.concrete:
            continue
        if not getattr(field, "concrete", False):
            continue
        if field.primary_key:
            continue
        if field.many_to_many:
            related = field.related_model
            if model_key(related)[0] in IN_SCOPE_APPS:
                plans.append(
                    FieldPlan(
                        name=field.name,
                        kind="m2m_internal",
                        target_model=model_key(related),
                    )
                )
            # M2M to out-of-scope models: skip silently.
            continue
        if isinstance(field, (models.FileField,)):
            plans.append(FieldPlan(name=field.name, kind="file"))
            continue
        if field.is_relation:
            related = field.related_model
            if related is ContentType:
                plans.append(FieldPlan(name=field.name, kind="fk_contenttype"))
                continue
            external_key = EXTERNAL_FK_NATURAL_KEYS.get(
                (app_label, model_name, field.name)
            )
            if external_key:
                plans.append(
                    FieldPlan(
                        name=field.name,
                        kind="fk_external",
                        natural_key=external_key,
                    )
                )
                continue
            plans.append(
                FieldPlan(
                    name=field.name,
                    kind="fk_internal",
                    target_model=model_key(related),
                )
            )
            continue
        plans.append(FieldPlan(name=field.name, kind="scalar"))

    return plans


class ContentJSONEncoder(json.JSONEncoder):
    """JSON encoder that handles types Django models commonly produce."""

    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        if isinstance(obj, datetime.timedelta):
            return obj.total_seconds()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)
