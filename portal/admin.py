from django.contrib import admin

from .models import AuditLog, PublisherUser


@admin.register(PublisherUser)
class PublisherUserAdmin(admin.ModelAdmin):
    list_display = ["user", "publisher", "created_at"]
    list_select_related = ["user", "publisher"]
    search_fields = ["user__username", "user__email", "publisher__name"]
    raw_id_fields = ["user"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "user", "object_repr", "action", "field"]
    list_filter = ["action", "content_type"]
    search_fields = ["user__username", "object_repr", "field"]
    readonly_fields = [
        "user",
        "content_type",
        "object_id",
        "object_repr",
        "action",
        "field",
        "old_value",
        "new_value",
        "timestamp",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
