"""
Tests for PeopleListBlock and PeopleListPerson models.
"""

from django.test import TestCase, override_settings

from cms.block_registry import (
    get_block_class,
    get_color_defaults,
    get_form_class,
    get_formset_class,
    get_label,
    get_manager_template,
    get_public_template,
)
from cms.models import PeopleListBlock, PeopleListPerson

CACHE_OVERRIDE = {
    "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
}


@override_settings(CACHES=CACHE_OVERRIDE)
class PeopleListBlockTests(TestCase):
    def test_defaults(self):
        block = PeopleListBlock.objects.create()
        self.assertEqual(block.name, "Board Members.")
        self.assertEqual(block.bg_color, "#ffffff")
        self.assertEqual(block.text_color, "#212129")
        self.assertEqual(block.card_bg_color, "#71f7f2")

    def test_str(self):
        block = PeopleListBlock.objects.create()
        self.assertEqual(str(block), f"PeopleListBlock #{block.pk}")

    def test_color_defaults_dict(self):
        self.assertEqual(
            PeopleListBlock.COLOR_DEFAULTS,
            {
                "bg_color": "#ffffff",
                "text_color": "#212129",
                "card_bg_color": "#71f7f2",
            },
        )

    def test_get_public_context_returns_people(self):
        block = PeopleListBlock.objects.create()
        PeopleListPerson.objects.create(
            block=block, name="Alice", sort_order=0
        )
        ctx = block.get_public_context()
        self.assertIn("people", ctx)
        self.assertEqual(ctx["people"].count(), 1)

    def test_create_children_from_config(self):
        block = PeopleListBlock.objects.create()
        children = [
            {
                "name": "Alice",
                "description": "CEO",
                "linkedin_url": "https://linkedin.com/in/alice",
                "sort_order": 0,
            },
            {
                "name": "Bob",
                "description": "CTO",
                "linkedin_url": "",
                "sort_order": 1,
            },
        ]
        block.create_children_from_config(children)
        self.assertEqual(block.people.count(), 2)
        self.assertEqual(block.people.first().name, "Alice")
        self.assertEqual(block.people.last().name, "Bob")


@override_settings(CACHES=CACHE_OVERRIDE)
class PeopleListPersonTests(TestCase):
    def test_creation(self):
        block = PeopleListBlock.objects.create()
        person = PeopleListPerson.objects.create(
            block=block,
            name="Test Person",
            description="A description",
            linkedin_url="https://linkedin.com/in/test",
            sort_order=0,
        )
        self.assertEqual(person.name, "Test Person")
        self.assertEqual(person.description, "A description")
        self.assertEqual(person.linkedin_url, "https://linkedin.com/in/test")

    def test_str(self):
        block = PeopleListBlock.objects.create()
        person = PeopleListPerson.objects.create(
            block=block, name="Jane Doe", sort_order=0
        )
        self.assertEqual(str(person), "Jane Doe")

    def test_ordering(self):
        block = PeopleListBlock.objects.create()
        PeopleListPerson.objects.create(block=block, name="Zara", sort_order=2)
        PeopleListPerson.objects.create(
            block=block, name="Alice", sort_order=0
        )
        PeopleListPerson.objects.create(block=block, name="Mid", sort_order=1)
        names = list(block.people.values_list("name", flat=True))
        self.assertEqual(names, ["Alice", "Mid", "Zara"])

    def test_description_sanitized_on_save(self):
        block = PeopleListBlock.objects.create()
        person = PeopleListPerson.objects.create(
            block=block,
            name="Test",
            description="<p>OK</p><script>bad</script>",
            sort_order=0,
        )
        person.refresh_from_db()
        self.assertNotIn("<script>", person.description)
        self.assertIn("<p>OK</p>", person.description)

    def test_cascade_delete(self):
        block = PeopleListBlock.objects.create()
        PeopleListPerson.objects.create(
            block=block, name="Deleted", sort_order=0
        )
        block.delete()
        self.assertEqual(PeopleListPerson.objects.count(), 0)


@override_settings(CACHES=CACHE_OVERRIDE)
class PeopleListRegistryTests(TestCase):
    def test_registered_block_type(self):
        cls = get_block_class("people_list")
        self.assertEqual(cls, PeopleListBlock)

    def test_label(self):
        self.assertEqual(get_label("people_list"), "People List")

    def test_manager_template(self):
        self.assertEqual(
            get_manager_template("people_list"),
            "cms/manager/blocks/_people_list.html",
        )

    def test_public_template(self):
        self.assertEqual(
            get_public_template("people_list"),
            "includes/blocks/_people_list.html",
        )

    def test_form_class(self):
        form_cls = get_form_class("people_list")
        self.assertEqual(form_cls.__name__, "PeopleListBlockForm")

    def test_formset_class(self):
        formset_cls = get_formset_class("people_list")
        self.assertEqual(formset_cls.__name__, "PeopleListPersonFormSet")

    def test_color_defaults(self):
        defaults = get_color_defaults("people_list")
        self.assertEqual(defaults["bg_color"], "#ffffff")
        self.assertEqual(defaults["card_bg_color"], "#71f7f2")
