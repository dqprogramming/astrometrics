"""
Portal models: links users to publishers and records an audit trail of all
changes made through the portal.
"""

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from journals.models import Publisher

User = get_user_model()


class PublisherUser(models.Model):
    """Links a Django user account to a Publisher for portal access."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="publisher_user",
        help_text="The user account that has portal access",
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="portal_users",
        help_text="The publisher this user can manage",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__username"]
        verbose_name = _("Publisher User")
        verbose_name_plural = _("Publisher Users")

    def __str__(self):
        return f"{self.user.username} → {self.publisher.name}"


class AuditLog(models.Model):
    """Records every change made through the publisher portal."""

    ACTION_UPDATE = "update"
    ACTION_M2M_ADD = "m2m_add"
    ACTION_M2M_REMOVE = "m2m_remove"

    ACTION_CHOICES = [
        (ACTION_UPDATE, "Field updated"),
        (ACTION_M2M_ADD, "Item added"),
        (ACTION_M2M_REMOVE, "Item removed"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="portal_audit_logs",
        help_text="User who made the change",
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Model type of the changed object",
    )
    object_id = models.PositiveIntegerField(
        help_text="Primary key of the changed object",
    )
    content_object = GenericForeignKey("content_type", "object_id")
    object_repr = models.CharField(
        max_length=255,
        help_text="String representation of the object at time of change",
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text="Type of change",
    )
    field = models.CharField(
        max_length=100,
        help_text="Field or relation that was changed",
    )
    old_value = models.TextField(
        blank=True,
        help_text="Previous value (for field updates)",
    )
    new_value = models.TextField(
        blank=True,
        help_text="New value (for field updates) or item name (for M2M)",
    )
    is_reversion = models.BooleanField(
        default=False,
        help_text="True when this entry was created by reverting a previous change",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = _("Audit Log Entry")
        verbose_name_plural = _("Audit Log")
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["user", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} — {self.user} — {self.object_repr} — {self.field}"
