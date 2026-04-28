"""Signals for the files app.

`pre_save` normalises the extension (lowercase, no leading dot) so the
storage path computed by `media_file_upload_path` matches what the URL
resolver expects.

`pre_delete` removes the underlying storage blob when a row is removed
so we don't leak orphan files.
"""

from django.core.files.storage import default_storage
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from .models import MediaFile


@receiver(pre_save, sender=MediaFile)
def normalise_extension(sender, instance, **kwargs):
    if instance.extension:
        instance.extension = instance.extension.lstrip(".").lower()


@receiver(pre_delete, sender=MediaFile)
def delete_storage_blob(sender, instance, **kwargs):
    name = instance.file.name if instance.file else ""
    if name and default_storage.exists(name):
        default_storage.delete(name)
