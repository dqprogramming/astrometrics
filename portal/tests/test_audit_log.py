"""
Tests for the staff audit log view.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from journals.models import Journal, Publisher, Subject
from portal.models import AuditLog, PublisherUser

User = get_user_model()


class AuditLogViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="pass", is_staff=True, is_active=True
        )
        self.publisher = Publisher.objects.create(name="Pub")
        self.portal_user = User.objects.create_user(
            username="portaluser", password="pass"
        )
        PublisherUser.objects.create(
            user=self.portal_user, publisher=self.publisher
        )
        self.journal = Journal.objects.create(
            title="Test Journal", publisher=self.publisher
        )

    def _make_log(self, obj, action=AuditLog.ACTION_UPDATE, field="title"):
        from django.contrib.contenttypes.models import ContentType

        return AuditLog.objects.create(
            user=self.portal_user,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.pk,
            object_repr=str(obj),
            action=action,
            field=field,
            old_value="old",
            new_value="new",
        )

    def test_requires_staff(self):
        User.objects.create_user(username="nostaff", password="pass")
        self.client.login(username="nostaff", password="pass")
        response = self.client.get(reverse("portal_manager:audit_log"))
        # Authenticated non-staff → PermissionDenied (403)
        self.assertEqual(response.status_code, 403)

    def test_staff_can_view_audit_log(self):
        self._make_log(self.journal)
        self.client.login(username="staff", password="pass")
        response = self.client.get(reverse("portal_manager:audit_log"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Journal")

    def test_filter_by_user(self):
        self._make_log(self.journal)
        self.client.login(username="staff", password="pass")
        url = reverse("portal_manager:audit_log")
        response = self.client.get(url, {"user": self.portal_user.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Journal")

    def test_filter_by_publisher(self):
        self._make_log(self.journal)
        self.client.login(username="staff", password="pass")
        url = reverse("portal_manager:audit_log")
        response = self.client.get(url, {"publisher": self.publisher.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Journal")

    def test_audit_log_shows_action_labels(self):
        self._make_log(
            self.journal, action=AuditLog.ACTION_M2M_ADD, field="subjects"
        )
        self.client.login(username="staff", password="pass")
        response = self.client.get(reverse("portal_manager:audit_log"))
        self.assertContains(response, "Item added")

    def test_search_filters_by_object_repr(self):
        self._make_log(self.journal)
        self.client.login(username="staff", password="pass")
        response = self.client.get(
            reverse("portal_manager:audit_log"), {"q": "Test Journal"}
        )
        self.assertContains(response, "Test Journal")

    def test_search_excludes_non_matching(self):
        self._make_log(self.journal)
        self.client.login(username="staff", password="pass")
        response = self.client.get(
            reverse("portal_manager:audit_log"), {"q": "zzznomatch"}
        )
        self.assertNotContains(response, "Test Journal")


class RevertAuditLogTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="pass", is_staff=True, is_active=True
        )
        self.publisher = Publisher.objects.create(
            name="Original Name", website="https://example.com"
        )
        self.portal_user = User.objects.create_user(
            username="portaluser", password="pass"
        )
        PublisherUser.objects.create(
            user=self.portal_user, publisher=self.publisher
        )
        self.journal = Journal.objects.create(
            title="Test Journal", publisher=self.publisher
        )
        self.subject = Subject.objects.create(name="Biology")

    def _make_log(self, obj, action, field, old_value="", new_value=""):
        from django.contrib.contenttypes.models import ContentType

        return AuditLog.objects.create(
            user=self.portal_user,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.pk,
            object_repr=str(obj),
            action=action,
            field=field,
            old_value=old_value,
            new_value=new_value,
        )

    def test_revert_field_update(self):
        self.publisher.name = "New Name"
        self.publisher.save()
        entry = self._make_log(
            self.publisher,
            AuditLog.ACTION_UPDATE,
            "name",
            old_value="Original Name",
            new_value="New Name",
        )
        self.client.login(username="staff", password="pass")
        self.client.post(
            reverse("portal_manager:audit_log_revert", kwargs={"pk": entry.pk})
        )
        self.publisher.refresh_from_db()
        self.assertEqual(self.publisher.name, "Original Name")

    def test_revert_field_creates_new_log_entry(self):
        entry = self._make_log(
            self.publisher,
            AuditLog.ACTION_UPDATE,
            "name",
            old_value="Original Name",
            new_value="New Name",
        )
        self.client.login(username="staff", password="pass")
        self.client.post(
            reverse("portal_manager:audit_log_revert", kwargs={"pk": entry.pk})
        )
        # A new log entry should record the revert
        self.assertEqual(AuditLog.objects.count(), 2)
        revert_entry = AuditLog.objects.order_by("-timestamp").first()
        self.assertEqual(revert_entry.user, self.staff)
        self.assertEqual(revert_entry.new_value, "Original Name")

    def test_revert_m2m_add(self):
        self.journal.subjects.add(self.subject)
        entry = self._make_log(
            self.journal,
            AuditLog.ACTION_M2M_ADD,
            "subjects",
            new_value="Biology",
        )
        self.client.login(username="staff", password="pass")
        self.client.post(
            reverse("portal_manager:audit_log_revert", kwargs={"pk": entry.pk})
        )
        self.assertNotIn(self.subject, self.journal.subjects.all())

    def test_revert_m2m_remove(self):
        entry = self._make_log(
            self.journal,
            AuditLog.ACTION_M2M_REMOVE,
            "subjects",
            old_value="Biology",
        )
        self.client.login(username="staff", password="pass")
        self.client.post(
            reverse("portal_manager:audit_log_revert", kwargs={"pk": entry.pk})
        )
        self.assertIn(self.subject, self.journal.subjects.all())

    def test_revert_deleted_object_shows_error(self):
        entry = self._make_log(
            self.publisher,
            AuditLog.ACTION_UPDATE,
            "name",
            old_value="Old",
            new_value="New",
        )
        self.journal.delete()
        self.publisher.delete()
        self.client.login(username="staff", password="pass")
        response = self.client.post(
            reverse(
                "portal_manager:audit_log_revert", kwargs={"pk": entry.pk}
            ),
            follow=True,
        )
        self.assertContains(response, "no longer exists")
