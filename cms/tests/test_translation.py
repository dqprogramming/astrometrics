"""
Tests for modeltranslation integration on CMS models.
"""

from django.test import TestCase, override_settings
from django.utils.translation import activate

from cms.models import Page, Post, Snippet


@override_settings(LANGUAGE_CODE="en")
class PageTranslationTests(TestCase):
    def test_translated_title_fields_exist(self):
        page = Page.objects.create(title="English Title", slug="t1")
        self.assertTrue(hasattr(page, "title_en"))
        self.assertTrue(hasattr(page, "title_fr"))
        self.assertTrue(hasattr(page, "title_de"))
        self.assertTrue(hasattr(page, "title_es"))

    def test_translated_body_fields_exist(self):
        page = Page.objects.create(title="Body Test", slug="t2")
        self.assertTrue(hasattr(page, "body_en"))
        self.assertTrue(hasattr(page, "body_fr"))
        self.assertTrue(hasattr(page, "body_de"))
        self.assertTrue(hasattr(page, "body_es"))

    def test_translated_meta_description_fields_exist(self):
        page = Page.objects.create(title="Meta Test", slug="t3")
        self.assertTrue(hasattr(page, "meta_description_en"))
        self.assertTrue(hasattr(page, "meta_description_fr"))
        self.assertTrue(hasattr(page, "meta_description_de"))
        self.assertTrue(hasattr(page, "meta_description_es"))

    def test_default_language_value(self):
        activate("en")
        page = Page.objects.create(title="Hello", slug="hello")
        self.assertEqual(page.title_en, "Hello")

    def test_set_translation_directly(self):
        page = Page.objects.create(title="Hello", slug="trans")
        page.title_fr = "Bonjour"
        page.save()
        page.refresh_from_db()
        self.assertEqual(page.title_fr, "Bonjour")

    def test_activate_language_returns_translation(self):
        page = Page.objects.create(title="Hello", slug="lang-switch")
        page.title_fr = "Bonjour"
        page.save()

        activate("fr")
        page.refresh_from_db()
        self.assertEqual(page.title, "Bonjour")
        activate("en")


@override_settings(LANGUAGE_CODE="en")
class PostTranslationTests(TestCase):
    def test_translated_title_fields_exist(self):
        post = Post.objects.create(title="News", slug="news")
        self.assertTrue(hasattr(post, "title_en"))
        self.assertTrue(hasattr(post, "title_fr"))
        self.assertTrue(hasattr(post, "title_de"))
        self.assertTrue(hasattr(post, "title_es"))

    def test_translated_summary_fields_exist(self):
        post = Post.objects.create(title="Sum", slug="sum")
        self.assertTrue(hasattr(post, "summary_en"))
        self.assertTrue(hasattr(post, "summary_fr"))
        self.assertTrue(hasattr(post, "summary_de"))
        self.assertTrue(hasattr(post, "summary_es"))

    def test_translated_body_fields_exist(self):
        post = Post.objects.create(title="Body", slug="body")
        self.assertTrue(hasattr(post, "body_en"))
        self.assertTrue(hasattr(post, "body_fr"))
        self.assertTrue(hasattr(post, "body_de"))
        self.assertTrue(hasattr(post, "body_es"))

    def test_translated_meta_description_fields_exist(self):
        post = Post.objects.create(title="Meta", slug="meta")
        self.assertTrue(hasattr(post, "meta_description_en"))
        self.assertTrue(hasattr(post, "meta_description_fr"))
        self.assertTrue(hasattr(post, "meta_description_de"))
        self.assertTrue(hasattr(post, "meta_description_es"))

    def test_default_language_value(self):
        activate("en")
        post = Post.objects.create(title="Hello", slug="hello-post")
        self.assertEqual(post.title_en, "Hello")

    def test_set_translation_directly(self):
        post = Post.objects.create(title="Hello", slug="trans-post")
        post.title_fr = "Bonjour"
        post.summary_fr = "Résumé"
        post.save()
        post.refresh_from_db()
        self.assertEqual(post.title_fr, "Bonjour")
        self.assertEqual(post.summary_fr, "Résumé")

    def test_activate_language_returns_translation(self):
        post = Post.objects.create(title="Hello", slug="lang-post")
        post.title_es = "Hola"
        post.save()

        activate("es")
        post.refresh_from_db()
        self.assertEqual(post.title, "Hola")
        activate("en")


@override_settings(LANGUAGE_CODE="en")
class SnippetTranslationTests(TestCase):
    def test_translated_name_fields_exist(self):
        snippet = Snippet.objects.create(name="Footer", key="footer")
        self.assertTrue(hasattr(snippet, "name_en"))
        self.assertTrue(hasattr(snippet, "name_fr"))
        self.assertTrue(hasattr(snippet, "name_de"))
        self.assertTrue(hasattr(snippet, "name_es"))

    def test_translated_body_fields_exist(self):
        snippet = Snippet.objects.create(name="Body", key="body")
        self.assertTrue(hasattr(snippet, "body_en"))
        self.assertTrue(hasattr(snippet, "body_fr"))
        self.assertTrue(hasattr(snippet, "body_de"))
        self.assertTrue(hasattr(snippet, "body_es"))

    def test_set_and_read_translation(self):
        snippet = Snippet.objects.create(name="Footer", key="footer-t")
        snippet.name_es = "Pie de página"
        snippet.save()
        snippet.refresh_from_db()
        self.assertEqual(snippet.name_es, "Pie de página")
