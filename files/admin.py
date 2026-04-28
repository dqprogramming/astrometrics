from django.contrib import admin

from .models import MediaFile


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "slug",
        "extension",
        "is_public",
        "size",
        "created_at",
    )
    list_filter = ("is_public", "extension")
    search_fields = ("display_name", "slug", "original_filename")
    readonly_fields = (
        "id",
        "extension",
        "original_filename",
        "mime_type",
        "size",
        "created_at",
        "updated_at",
        "created_by",
    )
