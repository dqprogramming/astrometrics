"""Forms for the files manager dashboard."""

import os

from django import forms
from django.conf import settings
from django.utils.text import slugify

from .models import MediaFile


def _split_extension(filename: str) -> str:
    base, ext = os.path.splitext(filename)
    return ext.lstrip(".").lower()


class MediaFileUploadForm(forms.ModelForm):
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"class": "mgr-input"})
    )

    class Meta:
        model = MediaFile
        fields = ["display_name", "slug", "description", "is_public"]
        widgets = {
            "display_name": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "e.g. Quarterly statistics",
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "quarterly-statistics",
                }
            ),
            "description": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get("slug") or ""
        slug = slugify(slug)
        if not slug:
            raise forms.ValidationError("A URL slug is required.")
        return slug

    def clean(self):
        cleaned = super().clean()
        upload = cleaned.get("file")
        slug = cleaned.get("slug")

        if not upload:
            return cleaned

        ext = _split_extension(upload.name)
        if not ext:
            raise forms.ValidationError(
                "The uploaded file has no extension; please add one."
            )

        blocked = {
            e.lower().lstrip(".")
            for e in getattr(settings, "FILES_BLOCKED_EXTENSIONS", set())
        }
        if ext in blocked:
            raise forms.ValidationError(
                f"Files with the .{ext} extension are not permitted."
            )

        max_size = getattr(settings, "FILES_MAX_UPLOAD_SIZE", 50 * 1024 * 1024)
        if upload.size > max_size:
            raise forms.ValidationError(
                f"File is too large ({upload.size:,} bytes); "
                f"maximum is {max_size:,} bytes."
            )

        if (
            slug
            and MediaFile.objects.filter(slug=slug, extension=ext).exists()
        ):
            self.add_error(
                "slug",
                f"A file with slug '{slug}.{ext}' already exists. "
                f"Try '{slug}-2'.",
            )

        cleaned["_extension"] = ext
        return cleaned

    def save(self, commit=True, user=None):
        upload = self.cleaned_data["file"]
        ext = self.cleaned_data["_extension"]

        instance = super().save(commit=False)
        instance.extension = ext
        instance.original_filename = upload.name
        instance.mime_type = upload.content_type or ""
        instance.size = upload.size
        if user is not None and user.is_authenticated:
            instance.created_by = user
        # Assigning here lets Django's FileField pre_save write the blob
        # exactly once during instance.save(), via upload_to().
        instance.file = upload
        if commit:
            instance.save()
        return instance


class MediaFileEditForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ["display_name", "slug", "description", "is_public"]
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "mgr-input"}),
            "slug": forms.TextInput(attrs={"class": "mgr-input"}),
            "description": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
        }

    def clean_slug(self):
        slug = slugify(self.cleaned_data.get("slug") or "")
        if not slug:
            raise forms.ValidationError("A URL slug is required.")
        # Check uniqueness with current extension, excluding this row
        qs = MediaFile.objects.filter(
            slug=slug, extension=self.instance.extension
        )
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                f"A file with slug '{slug}.{self.instance.extension}' "
                f"already exists."
            )
        return slug
