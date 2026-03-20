"""
Tests for OJC Boards page: models, public view, manager views, image upload,
and seed migration.
"""

import io
import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from cms.models import BoardMember, BoardSection


def _dummy_cache():
    return {
        "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
    }


def _create_staff_user(username="staff", password="pass"):
    return User.objects.create_user(
        username=username, password=password, is_staff=True
    )


def _create_section(name="Test Section", sort_order=0):
    return BoardSection.objects.create(name=name, sort_order=sort_order)


def _create_member(section, name="Test Member", sort_order=0, **kwargs):
    return BoardMember.objects.create(
        section=section, name=name, sort_order=sort_order, **kwargs
    )


def _make_upload_image(width=800, height=600, fmt="JPEG"):
    img = Image.new("RGB", (width, height), color="red")
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    buf.name = "test.jpg"
    return buf


# -- Model tests -------------------------------------------------------------


@override_settings(CACHES=_dummy_cache())
class BoardSectionModelTests(TestCase):
    def setUp(self):
        BoardSection.objects.all().delete()

    def test_str(self):
        section = _create_section(name="Publishers")
        self.assertEqual(str(section), "Publishers")

    def test_ordering_by_sort_order(self):
        s2 = _create_section(name="Library", sort_order=2)
        s0 = _create_section(name="Publishers", sort_order=0)
        s1 = _create_section(name="Advisory", sort_order=1)
        sections = list(BoardSection.objects.all())
        self.assertEqual(sections, [s0, s1, s2])


@override_settings(CACHES=_dummy_cache())
class BoardMemberModelTests(TestCase):
    def setUp(self):
        BoardSection.objects.all().delete()

    def test_str(self):
        section = _create_section()
        member = _create_member(section, name="Alice")
        self.assertEqual(str(member), "Alice")

    def test_fk_to_section(self):
        section = _create_section()
        member = _create_member(section)
        self.assertEqual(member.section, section)

    def test_ordering_by_sort_order(self):
        section = _create_section()
        m2 = _create_member(section, name="C", sort_order=2)
        m0 = _create_member(section, name="A", sort_order=0)
        m1 = _create_member(section, name="B", sort_order=1)
        members = list(BoardMember.objects.all())
        self.assertEqual(members, [m0, m1, m2])

    def test_description_sanitized_on_save(self):
        section = _create_section()
        member = _create_member(
            section,
            description='<p>Hello</p><script>alert("xss")</script>',
        )
        self.assertNotIn("<script>", member.description)
        self.assertIn("<p>Hello</p>", member.description)

    def test_cascade_delete(self):
        section = _create_section()
        _create_member(section, name="A")
        _create_member(section, name="B")
        section.delete()
        self.assertEqual(BoardMember.objects.count(), 0)


# -- Public view tests -------------------------------------------------------


@override_settings(CACHES=_dummy_cache())
class BoardPagePublicViewTests(TestCase):
    def setUp(self):
        BoardSection.objects.all().delete()

    def test_returns_200(self):
        response = self.client.get(reverse("cms:board"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("cms:board"))
        self.assertTemplateUsed(response, "board.html")

    def test_sections_and_members_from_db(self):
        s = _create_section(name="Publishers")
        _create_member(s, name="Alice")
        response = self.client.get(reverse("cms:board"))
        content = response.content.decode()
        self.assertIn("Publishers", content)
        self.assertIn("Alice", content)

    def test_ordering_respected(self):
        s0 = _create_section(name="First", sort_order=0)
        s1 = _create_section(name="Second", sort_order=1)
        _create_member(s0, name="A-member")
        _create_member(s1, name="B-member")
        response = self.client.get(reverse("cms:board"))
        content = response.content.decode()
        pos_first = content.index("First")
        pos_second = content.index("Second")
        self.assertLess(pos_first, pos_second)

    def test_empty_state(self):
        response = self.client.get(reverse("cms:board"))
        self.assertEqual(response.status_code, 200)

    def test_no_contact_form(self):
        response = self.client.get(reverse("cms:board"))
        content = response.content.decode()
        self.assertNotIn('name="email"', content)
        self.assertNotIn('name="message"', content)

    def test_context_has_sections(self):
        _create_section(name="Ctx Section")
        response = self.client.get(reverse("cms:board"))
        self.assertIn("sections", response.context)


# -- Manager view tests ------------------------------------------------------


def _build_board_formset_data(sections_with_members):
    """Build POST data for all sections and their member formsets."""
    data = {}
    for section, members in sections_with_members:
        data[f"section_{section.pk}_name"] = section.name
        data[f"section_{section.pk}_sort_order"] = str(section.sort_order)
        prefix = f"members_{section.pk}"
        data[f"{prefix}-TOTAL_FORMS"] = str(len(members))
        data[f"{prefix}-INITIAL_FORMS"] = str(len(members))
        data[f"{prefix}-MIN_NUM_FORMS"] = "0"
        data[f"{prefix}-MAX_NUM_FORMS"] = "1000"
        for i, member in enumerate(members):
            data[f"{prefix}-{i}-id"] = str(member.pk)
            data[f"{prefix}-{i}-section"] = str(section.pk)
            data[f"{prefix}-{i}-name"] = member.name
            data[f"{prefix}-{i}-description"] = member.description
            data[f"{prefix}-{i}-linkedin_url"] = member.linkedin_url
            data[f"{prefix}-{i}-image"] = member.image
            data[f"{prefix}-{i}-sort_order"] = str(member.sort_order)
    return data


@override_settings(CACHES=_dummy_cache())
class BoardManagerViewTests(TestCase):
    def setUp(self):
        BoardSection.objects.all().delete()

    def test_login_required(self):
        response = self.client.get(reverse("cms_manager:board"))
        self.assertEqual(response.status_code, 302)

    def test_staff_get_200(self):
        _create_staff_user()
        self.client.login(username="staff", password="pass")
        response = self.client.get(reverse("cms_manager:board"))
        self.assertEqual(response.status_code, 200)

    def test_post_save_sections_and_members(self):
        _create_staff_user()
        self.client.login(username="staff", password="pass")
        section = _create_section(name="Publishers")
        member = _create_member(section, name="Alice")

        data = _build_board_formset_data([(section, [member])])
        data[f"section_{section.pk}_name"] = "Updated Publishers"
        data[f"members_{section.pk}-0-name"] = "Alice Updated"

        response = self.client.post(
            reverse("cms_manager:board"), data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        section.refresh_from_db()
        self.assertEqual(section.name, "Updated Publishers")
        member.refresh_from_db()
        self.assertEqual(member.name, "Alice Updated")

    def test_add_section(self):
        _create_staff_user()
        self.client.login(username="staff", password="pass")
        self.assertEqual(BoardSection.objects.count(), 0)
        response = self.client.post(
            reverse("cms_manager:board_section_add"), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BoardSection.objects.count(), 1)

    def test_delete_section(self):
        _create_staff_user()
        self.client.login(username="staff", password="pass")
        section = _create_section(name="ToDelete")
        self.assertEqual(BoardSection.objects.count(), 1)
        response = self.client.post(
            reverse(
                "cms_manager:board_section_delete",
                kwargs={"pk": section.pk},
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BoardSection.objects.count(), 0)

    def test_delete_member(self):
        _create_staff_user()
        self.client.login(username="staff", password="pass")
        section = _create_section()
        member = _create_member(section, name="Gone")
        self.assertEqual(BoardMember.objects.count(), 1)
        response = self.client.post(
            reverse(
                "cms_manager:board_member_delete",
                kwargs={"pk": member.pk},
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BoardMember.objects.count(), 0)


# -- Image upload tests ------------------------------------------------------


@override_settings(CACHES=_dummy_cache())
class BoardMemberImageUploadTests(TestCase):
    def test_staff_only(self):
        img = _make_upload_image()
        response = self.client.post(
            reverse("cms_manager:board_member_image_upload"),
            {"image": img},
        )
        self.assertEqual(response.status_code, 403)

    @patch("cms.manager_views.default_storage")
    def test_returns_json_with_url(self, mock_storage):
        mock_storage.save.return_value = "cms/board/test.jpg"
        mock_storage.url.return_value = "/media/cms/board/test.jpg"
        _create_staff_user()
        self.client.login(username="staff", password="pass")
        img = _make_upload_image()
        response = self.client.post(
            reverse("cms_manager:board_member_image_upload"),
            {"image": img},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("url", data)

    @patch("cms.manager_views.default_storage")
    def test_validates_content_type(self, mock_storage):
        _create_staff_user()
        self.client.login(username="staff", password="pass")
        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded = SimpleUploadedFile(
            "test.txt", b"not an image", content_type="text/plain"
        )
        response = self.client.post(
            reverse("cms_manager:board_member_image_upload"),
            {"image": uploaded},
        )
        self.assertEqual(response.status_code, 400)

    @patch("cms.manager_views.default_storage")
    def test_image_cropped_to_600x400(self, mock_storage):
        mock_storage.save.return_value = "cms/board/test.jpg"
        mock_storage.url.return_value = "/media/cms/board/test.jpg"
        _create_staff_user()
        self.client.login(username="staff", password="pass")
        img = _make_upload_image(width=1000, height=1000)

        saved_content = None

        def capture_save(path, content):
            nonlocal saved_content
            saved_content = content
            return path

        mock_storage.save.side_effect = capture_save

        response = self.client.post(
            reverse("cms_manager:board_member_image_upload"),
            {"image": img},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(saved_content)
        saved_content.seek(0)
        saved_img = Image.open(saved_content)
        self.assertEqual(saved_img.size, (600, 400))


# -- Seed migration tests ----------------------------------------------------


@override_settings(CACHES=_dummy_cache())
class BoardSeedMigrationTests(TestCase):
    """Verify the seed data migration created expected records.

    Since migrations run before tests, the seed data should exist.
    These tests do NOT clear seed data in setUp.
    """

    def test_two_sections_exist(self):
        self.assertEqual(BoardSection.objects.count(), 2)

    def test_publishers_board_has_16_members(self):
        section = BoardSection.objects.get(name="OJC Publishers' Board.")
        self.assertEqual(section.members.count(), 16)

    def test_library_board_has_20_members(self):
        section = BoardSection.objects.get(name="OJC Library Board.")
        self.assertEqual(section.members.count(), 20)

    def test_section_names(self):
        names = list(
            BoardSection.objects.order_by("sort_order").values_list(
                "name", flat=True
            )
        )
        self.assertEqual(
            names,
            ["OJC Publishers' Board.", "OJC Library Board."],
        )
