"""
Tests for HeaderSettings and MenuItem models, forms, views, context processor,
and template rendering.
"""

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from cms.forms import HeaderSettingsForm, MenuItemForm
from cms.models import HeaderSettings, MenuItem


class HeaderSettingsModelTests(TestCase):
    def setUp(self):
        cache.clear()
        MenuItem.objects.all().delete()

    def test_str(self):
        settings = HeaderSettings.load()
        self.assertEqual(str(settings), "Header Settings")

    def test_load_creates_singleton(self):
        settings = HeaderSettings.load()
        self.assertEqual(settings.pk, 1)
        self.assertEqual(HeaderSettings.objects.count(), 1)

    def test_load_returns_same_instance(self):
        s1 = HeaderSettings.load()
        s2 = HeaderSettings.load()
        self.assertEqual(s1.pk, s2.pk)
        self.assertEqual(HeaderSettings.objects.count(), 1)

    def test_save_forces_pk_1(self):
        settings = HeaderSettings(pk=99, logo_line_1="Test")
        settings.save()
        self.assertEqual(settings.pk, 1)
        self.assertEqual(HeaderSettings.objects.count(), 1)

    def test_delete_is_noop(self):
        settings = HeaderSettings.load()
        settings.delete()
        self.assertEqual(HeaderSettings.objects.count(), 1)

    def test_save_invalidates_cache(self):
        settings = HeaderSettings.load()
        self.assertIsNotNone(cache.get(HeaderSettings.CACHE_KEY))
        settings.logo_line_1 = "Changed"
        settings.save()
        self.assertIsNone(cache.get(HeaderSettings.CACHE_KEY))

    def test_load_caches_result(self):
        HeaderSettings.load()
        self.assertIsNotNone(cache.get(HeaderSettings.CACHE_KEY))

    def test_logo_fields_default(self):
        settings = HeaderSettings.load()
        self.assertEqual(settings.logo_line_1, "Open")
        self.assertEqual(settings.logo_line_2, "Journals")
        self.assertEqual(settings.logo_line_3, "Collective")

    def test_cta_fields_default(self):
        settings = HeaderSettings.load()
        self.assertEqual(settings.cta_label, "GET INVOLVED")
        self.assertIn("mailto:", settings.cta_url)

    def test_show_mobile_sub_items_default_true(self):
        settings = HeaderSettings.load()
        self.assertTrue(settings.show_mobile_sub_items)

    def test_load_prefetches_menu_items(self):
        settings = HeaderSettings.load()
        MenuItem.objects.create(
            header=settings, label="About", url="/about", sort_order=0
        )
        cache.clear()
        settings = HeaderSettings.load()
        self.assertTrue(hasattr(settings, "_prefetched_menu_items"))

    def test_get_menu_items_returns_top_level_only(self):
        settings = HeaderSettings.load()
        parent = MenuItem.objects.create(
            header=settings, label="About", url="/about", sort_order=0
        )
        MenuItem.objects.create(
            header=settings,
            parent=parent,
            label="Sub",
            url="/sub",
            sort_order=0,
        )
        cache.clear()
        settings = HeaderSettings.load()
        items = settings.get_menu_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].label, "About")

    def test_get_menu_items_without_cache(self):
        """Test menu items method when no prefetched items exist."""
        settings = HeaderSettings.load()
        MenuItem.objects.create(
            header=settings, label="About", url="/about", sort_order=0
        )
        fresh = HeaderSettings.objects.get(pk=1)
        items = list(fresh.get_menu_items())
        self.assertEqual(len(items), 1)


class MenuItemModelTests(TestCase):
    def setUp(self):
        cache.clear()
        MenuItem.objects.all().delete()
        self.header = HeaderSettings.load()

    def test_str(self):
        item = MenuItem.objects.create(
            header=self.header, label="Test", url="/test"
        )
        self.assertEqual(str(item), "Test")

    def test_is_disabled_empty_url(self):
        item = MenuItem(header=self.header, label="Test", url="")
        self.assertTrue(item.is_disabled)

    def test_is_disabled_hash_url(self):
        item = MenuItem(header=self.header, label="Test", url="#")
        self.assertTrue(item.is_disabled)

    def test_is_not_disabled_with_url(self):
        item = MenuItem(
            header=self.header,
            label="Test",
            url="https://example.com",
        )
        self.assertFalse(item.is_disabled)

    def test_ordering_by_sort_order(self):
        MenuItem.objects.create(
            header=self.header,
            label="Second",
            url="/b",
            sort_order=2,
        )
        MenuItem.objects.create(
            header=self.header, label="First", url="/a", sort_order=1
        )
        labels = list(MenuItem.objects.values_list("label", flat=True))
        self.assertEqual(labels, ["First", "Second"])

    def test_save_invalidates_header_cache(self):
        HeaderSettings.load()
        self.assertIsNotNone(cache.get(HeaderSettings.CACHE_KEY))
        MenuItem.objects.create(header=self.header, label="New", url="/new")
        self.assertIsNone(cache.get(HeaderSettings.CACHE_KEY))

    def test_delete_invalidates_header_cache(self):
        item = MenuItem.objects.create(
            header=self.header, label="Del", url="/del"
        )
        HeaderSettings.load()
        self.assertIsNotNone(cache.get(HeaderSettings.CACHE_KEY))
        item.delete()
        self.assertIsNone(cache.get(HeaderSettings.CACHE_KEY))

    def test_parent_child_relationship(self):
        parent = MenuItem.objects.create(
            header=self.header, label="Parent", url="/parent", sort_order=0
        )
        child = MenuItem.objects.create(
            header=self.header,
            parent=parent,
            label="Child",
            url="/child",
            sort_order=0,
        )
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())

    def test_show_cta_in_dropdown_default_false(self):
        item = MenuItem.objects.create(
            header=self.header, label="Test", url="/test"
        )
        self.assertFalse(item.show_cta_in_dropdown)

    def test_show_cta_in_dropdown_true(self):
        item = MenuItem.objects.create(
            header=self.header,
            label="Test",
            url="/test",
            show_cta_in_dropdown=True,
        )
        self.assertTrue(item.show_cta_in_dropdown)

    def test_cta_text_default_empty(self):
        item = MenuItem.objects.create(
            header=self.header, label="Test", url="/test"
        )
        self.assertEqual(item.cta_text, "")

    def test_cta_url_default_empty(self):
        item = MenuItem.objects.create(
            header=self.header, label="Test", url="/test"
        )
        self.assertEqual(item.cta_url, "")

    def test_cta_text_and_url_stored(self):
        item = MenuItem.objects.create(
            header=self.header,
            label="Test",
            url="/test",
            show_cta_in_dropdown=True,
            cta_text="Join Now",
            cta_url="https://example.com/join",
        )
        item.refresh_from_db()
        self.assertEqual(item.cta_text, "Join Now")
        self.assertEqual(item.cta_url, "https://example.com/join")

    def test_cascade_delete_children(self):
        parent = MenuItem.objects.create(
            header=self.header, label="Parent", url="/parent", sort_order=0
        )
        MenuItem.objects.create(
            header=self.header,
            parent=parent,
            label="Child",
            url="/child",
            sort_order=0,
        )
        parent.delete()
        self.assertEqual(MenuItem.objects.count(), 0)


class HeaderSettingsFormTests(TestCase):
    def _valid_data(self, **overrides):
        data = {
            "logo_line_1": "Open",
            "logo_line_2": "Journals",
            "logo_line_3": "Collective",
            "cta_label": "GET INVOLVED",
            "cta_url": "mailto:info@example.org",
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        form = HeaderSettingsForm(data=self._valid_data())
        self.assertTrue(form.is_valid())

    def test_logo_line_1_required(self):
        form = HeaderSettingsForm(data=self._valid_data(logo_line_1=""))
        self.assertFalse(form.is_valid())
        self.assertIn("logo_line_1", form.errors)

    def test_cta_label_required(self):
        form = HeaderSettingsForm(data=self._valid_data(cta_label=""))
        self.assertFalse(form.is_valid())
        self.assertIn("cta_label", form.errors)

    def test_cta_url_required(self):
        form = HeaderSettingsForm(data=self._valid_data(cta_url=""))
        self.assertFalse(form.is_valid())
        self.assertIn("cta_url", form.errors)


class MenuItemFormTests(TestCase):
    def test_valid_form(self):
        form = MenuItemForm(
            data={
                "label": "Test Item",
                "url": "https://example.com",
                "sort_order": 0,
                "parent": "",
                "show_cta_in_dropdown": False,
                "cta_text": "",
                "cta_url": "",
            }
        )
        self.assertTrue(form.is_valid())

    def test_label_required(self):
        form = MenuItemForm(
            data={
                "label": "",
                "url": "https://example.com",
                "sort_order": 0,
                "parent": "",
                "show_cta_in_dropdown": False,
                "cta_text": "",
                "cta_url": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("label", form.errors)

    def test_url_optional(self):
        form = MenuItemForm(
            data={
                "label": "Test",
                "url": "",
                "sort_order": 0,
                "parent": "",
                "show_cta_in_dropdown": False,
                "cta_text": "",
                "cta_url": "",
            }
        )
        self.assertTrue(form.is_valid())

    def test_parent_field_optional(self):
        form = MenuItemForm(
            data={
                "label": "Test",
                "url": "/test",
                "sort_order": 0,
                "parent": "",
                "show_cta_in_dropdown": False,
                "cta_text": "",
                "cta_url": "",
            }
        )
        self.assertTrue(form.is_valid())

    def test_cta_text_optional(self):
        form = MenuItemForm(
            data={
                "label": "Test",
                "url": "/test",
                "sort_order": 0,
                "parent": "",
                "show_cta_in_dropdown": True,
                "cta_text": "",
                "cta_url": "",
            }
        )
        self.assertTrue(form.is_valid())

    def test_cta_fields_accepted(self):
        form = MenuItemForm(
            data={
                "label": "Test",
                "url": "/test",
                "sort_order": 0,
                "parent": "",
                "show_cta_in_dropdown": True,
                "cta_text": "Get Involved",
                "cta_url": "https://example.com",
            }
        )
        self.assertTrue(form.is_valid())


class ContextProcessorTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_header_settings_in_context(self):
        from django.test import RequestFactory

        from cms.context_processors import header_settings

        request = RequestFactory().get("/")
        result = header_settings(request)
        self.assertIn("header", result)
        self.assertIsInstance(result["header"], HeaderSettings)


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class HeaderManagerViewTests(TestCase):
    def setUp(self):
        cache.clear()
        MenuItem.objects.all().delete()
        self.staff_user = User.objects.create_user(
            username="staff",
            password="testpass123",
            is_staff=True,
        )
        self.url = reverse("cms_manager:header")

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_staff_can_access(self):
        self.client.login(username="staff", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def _base_post_data(self, **extra):
        data = {
            "logo_line_1": "Open",
            "logo_line_2": "Journals",
            "logo_line_3": "Collective",
            "cta_label": "GET INVOLVED",
            "cta_url": "mailto:info@example.org",
            "menu_items-TOTAL_FORMS": "0",
            "menu_items-INITIAL_FORMS": "0",
            "menu_items-MIN_NUM_FORMS": "0",
            "menu_items-MAX_NUM_FORMS": "1000",
        }
        data.update(extra)
        return data

    def test_post_saves_settings(self):
        self.client.login(username="staff", password="testpass123")
        data = self._base_post_data(
            logo_line_1="New Open",
            logo_line_2="New Journals",
        )
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        settings = HeaderSettings.load()
        self.assertEqual(settings.logo_line_1, "New Open")
        self.assertEqual(settings.logo_line_2, "New Journals")

    def test_post_creates_top_level_items(self):
        self.client.login(username="staff", password="testpass123")
        data = self._base_post_data(
            **{
                "menu_items-TOTAL_FORMS": "1",
                "menu_items-0-label": "About",
                "menu_items-0-url": "/about",
                "menu_items-0-sort_order": "0",
                "menu_items-0-parent": "",
                "menu_items-0-show_cta_in_dropdown": "",
                "menu_items-0-cta_text": "",
                "menu_items-0-cta_url": "",
                "menu_items-0-id": "",
            }
        )
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        items = MenuItem.objects.filter(parent__isnull=True)
        self.assertEqual(items.count(), 1)
        self.assertEqual(items.first().label, "About")

    def test_post_creates_sub_items(self):
        self.client.login(username="staff", password="testpass123")
        header = HeaderSettings.load()
        parent = MenuItem.objects.create(
            header=header, label="About", url="/about", sort_order=0
        )
        data = self._base_post_data(
            **{
                "menu_items-TOTAL_FORMS": "2",
                "menu_items-INITIAL_FORMS": "1",
                "menu_items-0-label": "About",
                "menu_items-0-url": "/about",
                "menu_items-0-sort_order": "0",
                "menu_items-0-parent": "",
                "menu_items-0-show_cta_in_dropdown": "",
                "menu_items-0-cta_text": "",
                "menu_items-0-cta_url": "",
                "menu_items-0-id": str(parent.pk),
                "menu_items-1-label": "Sub Item",
                "menu_items-1-url": "/sub",
                "menu_items-1-sort_order": "0",
                "menu_items-1-parent": str(parent.pk),
                "menu_items-1-show_cta_in_dropdown": "",
                "menu_items-1-cta_text": "",
                "menu_items-1-cta_url": "",
                "menu_items-1-id": "",
            }
        )
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        sub_items = MenuItem.objects.filter(parent=parent)
        self.assertEqual(sub_items.count(), 1)
        self.assertEqual(sub_items.first().label, "Sub Item")

    def test_post_saves_per_item_cta_fields(self):
        self.client.login(username="staff", password="testpass123")
        data = self._base_post_data(
            **{
                "menu_items-TOTAL_FORMS": "1",
                "menu_items-0-label": "About",
                "menu_items-0-url": "/about",
                "menu_items-0-sort_order": "0",
                "menu_items-0-parent": "",
                "menu_items-0-show_cta_in_dropdown": "on",
                "menu_items-0-cta_text": "Join Now",
                "menu_items-0-cta_url": "https://example.com/join",
                "menu_items-0-id": "",
            }
        )
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        item = MenuItem.objects.get(label="About")
        self.assertTrue(item.show_cta_in_dropdown)
        self.assertEqual(item.cta_text, "Join Now")
        self.assertEqual(item.cta_url, "https://example.com/join")

    def test_post_deletes_items(self):
        self.client.login(username="staff", password="testpass123")
        header = HeaderSettings.load()
        item = MenuItem.objects.create(
            header=header,
            label="Delete Me",
            url="/del",
            sort_order=0,
        )
        data = self._base_post_data(
            **{
                "menu_items-TOTAL_FORMS": "1",
                "menu_items-INITIAL_FORMS": "1",
                "menu_items-0-label": "Delete Me",
                "menu_items-0-url": "/del",
                "menu_items-0-sort_order": "0",
                "menu_items-0-parent": "",
                "menu_items-0-show_cta_in_dropdown": "",
                "menu_items-0-cta_text": "",
                "menu_items-0-cta_url": "",
                "menu_items-0-id": str(item.pk),
                "menu_items-0-DELETE": "on",
            }
        )
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MenuItem.objects.count(), 0)

    def test_sort_order_respected(self):
        self.client.login(username="staff", password="testpass123")
        data = self._base_post_data(
            **{
                "menu_items-TOTAL_FORMS": "2",
                "menu_items-0-label": "Second",
                "menu_items-0-url": "/b",
                "menu_items-0-sort_order": "2",
                "menu_items-0-parent": "",
                "menu_items-0-show_cta_in_dropdown": "",
                "menu_items-0-cta_text": "",
                "menu_items-0-cta_url": "",
                "menu_items-0-id": "",
                "menu_items-1-label": "First",
                "menu_items-1-url": "/a",
                "menu_items-1-sort_order": "1",
                "menu_items-1-parent": "",
                "menu_items-1-show_cta_in_dropdown": "",
                "menu_items-1-cta_text": "",
                "menu_items-1-cta_url": "",
                "menu_items-1-id": "",
            }
        )
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        labels = list(
            MenuItem.objects.filter(parent__isnull=True).values_list(
                "label", flat=True
            )
        )
        self.assertEqual(labels, ["First", "Second"])


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class HeaderTemplateTests(TestCase):
    def setUp(self):
        cache.clear()
        MenuItem.objects.all().delete()
        self.header = HeaderSettings.load()
        self.header.logo_line_1 = "Test Open"
        self.header.logo_line_2 = "Test Journals"
        self.header.logo_line_3 = "Test Collective"
        self.header.cta_label = "JOIN US"
        self.header.cta_url = "mailto:test@example.com"
        self.header.save()

    def test_header_renders_logo_text(self):
        response = self.client.get(reverse("cms:index"))
        self.assertContains(response, "Test Open")
        self.assertContains(response, "Test Journals")
        self.assertContains(response, "Test Collective")

    def test_header_renders_cta(self):
        response = self.client.get(reverse("cms:index"))
        self.assertContains(response, "JOIN US")
        self.assertContains(response, "mailto:test@example.com")

    def test_header_renders_nav_items(self):
        MenuItem.objects.create(
            header=self.header,
            label="About",
            url="/about",
            sort_order=0,
        )
        cache.clear()
        response = self.client.get(reverse("cms:index"))
        self.assertContains(response, "About")
        self.assertContains(response, "/about")

    def test_header_renders_dropdown(self):
        parent = MenuItem.objects.create(
            header=self.header,
            label="About OJC",
            url="/#who-we-are",
            sort_order=0,
        )
        MenuItem.objects.create(
            header=self.header,
            parent=parent,
            label="Our team",
            url="/#team",
            sort_order=0,
        )
        cache.clear()
        response = self.client.get(reverse("cms:index"))
        self.assertContains(response, "About OJC")
        self.assertContains(response, "Our team")
        self.assertContains(response, "landing-nav-dropdown")

    def test_header_renders_cta_in_dropdown(self):
        parent = MenuItem.objects.create(
            header=self.header,
            label="About OJC",
            url="/#who-we-are",
            sort_order=0,
            show_cta_in_dropdown=True,
        )
        MenuItem.objects.create(
            header=self.header,
            parent=parent,
            label="Our team",
            url="/#team",
            sort_order=0,
        )
        cache.clear()
        response = self.client.get(reverse("cms:index"))
        self.assertContains(response, "landing-dropdown-cta")

    def test_header_renders_per_item_cta_text_and_url(self):
        parent = MenuItem.objects.create(
            header=self.header,
            label="About OJC",
            url="/#who-we-are",
            sort_order=0,
            show_cta_in_dropdown=True,
            cta_text="Custom CTA",
            cta_url="https://custom.example.com",
        )
        MenuItem.objects.create(
            header=self.header,
            parent=parent,
            label="Our team",
            url="/#team",
            sort_order=0,
        )
        cache.clear()
        response = self.client.get(reverse("cms:index"))
        self.assertContains(response, "Custom CTA")
        self.assertContains(response, "https://custom.example.com")

    def test_header_cta_falls_back_to_global_when_empty(self):
        parent = MenuItem.objects.create(
            header=self.header,
            label="About OJC",
            url="/#who-we-are",
            sort_order=0,
            show_cta_in_dropdown=True,
            cta_text="",
            cta_url="",
        )
        MenuItem.objects.create(
            header=self.header,
            parent=parent,
            label="Our team",
            url="/#team",
            sort_order=0,
        )
        cache.clear()
        response = self.client.get(reverse("cms:index"))
        self.assertContains(response, "JOIN US")
        self.assertContains(response, "mailto:test@example.com")

    def test_header_renders_mobile_nav(self):
        MenuItem.objects.create(
            header=self.header,
            label="About",
            url="/about",
            sort_order=0,
        )
        cache.clear()
        response = self.client.get(reverse("cms:index"))
        self.assertContains(response, "fullscreen-nav")
        self.assertContains(response, "About")

    def test_header_renders_mobile_sub_items_when_enabled(self):
        self.header.show_mobile_sub_items = True
        self.header.save()
        parent = MenuItem.objects.create(
            header=self.header,
            label="About OJC",
            url="/#who-we-are",
            sort_order=0,
        )
        MenuItem.objects.create(
            header=self.header,
            parent=parent,
            label="Our team",
            url="/#team",
            sort_order=0,
        )
        cache.clear()
        response = self.client.get(reverse("cms:index"))
        content = response.content.decode()
        self.assertIn("mobile-nav-submenu", content)
        self.assertIn("nav-sub-link", content)

    def test_header_hides_mobile_sub_items_when_disabled(self):
        self.header.show_mobile_sub_items = False
        self.header.save()
        parent = MenuItem.objects.create(
            header=self.header,
            label="About OJC",
            url="/#who-we-are",
            sort_order=0,
        )
        MenuItem.objects.create(
            header=self.header,
            parent=parent,
            label="Our team",
            url="/#team",
            sort_order=0,
        )
        cache.clear()
        response = self.client.get(reverse("cms:index"))
        content = response.content.decode()
        self.assertNotIn("mobile-nav-submenu", content)
        self.assertNotIn("nav-sub-link", content)
