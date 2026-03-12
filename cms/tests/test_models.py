"""
Tests for CMS model behaviour.
"""

from django.test import TestCase
from django.utils import timezone

from cms.models import Page, Post, Snippet


class PageModelTests(TestCase):
    def test_str(self):
        page = Page.objects.create(title="About", slug="about")
        self.assertEqual(str(page), "About")

    def test_auto_slug_from_title(self):
        page = Page.objects.create(title="Contact Us")
        self.assertEqual(page.slug, "contact-us")

    def test_explicit_slug_not_overwritten(self):
        page = Page.objects.create(title="About", slug="custom-slug")
        self.assertEqual(page.slug, "custom-slug")

    def test_body_sanitized_on_save(self):
        page = Page.objects.create(
            title="Safe",
            slug="safe",
            body='<p>OK</p><script>alert("x")</script>',
        )
        self.assertNotIn("<script>", page.body)
        self.assertIn("<p>OK</p>", page.body)

    def test_body_allows_valid_html(self):
        html = "<h2>Hello</h2><p>World</p>"
        page = Page.objects.create(title="Valid", slug="valid", body=html)
        self.assertEqual(page.body, html)

    def test_default_not_published(self):
        page = Page.objects.create(title="Draft", slug="draft")
        self.assertFalse(page.is_published)

    def test_default_sort_order(self):
        page = Page.objects.create(title="Page", slug="page")
        self.assertEqual(page.sort_order, 0)

    def test_ordering(self):
        Page.objects.create(title="B Page", slug="b-page", sort_order=2)
        Page.objects.create(title="A Page", slug="a-page", sort_order=1)
        pages = list(Page.objects.values_list("slug", flat=True))
        self.assertEqual(pages, ["a-page", "b-page"])

    def test_meta_description_blank_by_default(self):
        page = Page.objects.create(title="Page", slug="page")
        self.assertEqual(page.meta_description, "")

    def test_slug_unique(self):
        Page.objects.create(title="P1", slug="same")
        with self.assertRaises(Exception):
            Page.objects.create(title="P2", slug="same")


class PostModelTests(TestCase):
    def test_str(self):
        post = Post.objects.create(title="First Post", slug="first")
        self.assertEqual(str(post), "First Post")

    def test_auto_slug_from_title(self):
        post = Post.objects.create(title="My Great Post")
        self.assertEqual(post.slug, "my-great-post")

    def test_explicit_slug_not_overwritten(self):
        post = Post.objects.create(title="Post", slug="custom-post-slug")
        self.assertEqual(post.slug, "custom-post-slug")

    def test_body_sanitized_on_save(self):
        post = Post.objects.create(
            title="Safe Post",
            slug="safe-post",
            body='<p>OK</p><script>alert("x")</script>',
        )
        self.assertNotIn("<script>", post.body)
        self.assertIn("<p>OK</p>", post.body)

    def test_summary_sanitized_on_save(self):
        post = Post.objects.create(
            title="Sum Post",
            slug="sum-post",
            summary="<p>Brief</p><script>bad()</script>",
        )
        self.assertNotIn("<script>", post.summary)
        self.assertIn("<p>Brief</p>", post.summary)

    def test_body_allows_valid_html(self):
        html = "<h2>Heading</h2><p>Body text</p>"
        post = Post.objects.create(
            title="Valid Post", slug="valid-post", body=html
        )
        self.assertEqual(post.body, html)

    def test_default_not_published(self):
        post = Post.objects.create(title="Draft", slug="draft-post")
        self.assertFalse(post.is_published)

    def test_published_at_nullable(self):
        post = Post.objects.create(title="No Date", slug="no-date")
        self.assertIsNone(post.published_at)

    def test_published_at_can_be_set(self):
        now = timezone.now()
        post = Post.objects.create(
            title="Dated",
            slug="dated",
            published_at=now,
        )
        self.assertEqual(post.published_at, now)

    def test_ordering_newest_first(self):
        now = timezone.now()
        old = now - timezone.timedelta(days=7)
        Post.objects.create(title="Old", slug="old", published_at=old)
        Post.objects.create(title="New", slug="new", published_at=now)
        slugs = list(Post.objects.values_list("slug", flat=True))
        self.assertEqual(slugs, ["new", "old"])

    def test_slug_unique(self):
        Post.objects.create(title="P1", slug="same-post")
        with self.assertRaises(Exception):
            Post.objects.create(title="P2", slug="same-post")

    def test_meta_description_blank_by_default(self):
        post = Post.objects.create(title="Post", slug="meta-post")
        self.assertEqual(post.meta_description, "")

    def test_summary_blank_by_default(self):
        post = Post.objects.create(title="Post", slug="sum-blank")
        self.assertEqual(post.summary, "")


class SnippetModelTests(TestCase):
    def test_str(self):
        snippet = Snippet.objects.create(name="Footer", key="footer")
        self.assertEqual(str(snippet), "Footer")

    def test_body_sanitized_on_save(self):
        snippet = Snippet.objects.create(
            name="Malicious",
            key="malicious",
            body="<p>Hi</p><script>bad()</script>",
        )
        self.assertNotIn("<script>", snippet.body)
        self.assertIn("<p>Hi</p>", snippet.body)

    def test_key_unique(self):
        Snippet.objects.create(name="S1", key="same-key")
        with self.assertRaises(Exception):
            Snippet.objects.create(name="S2", key="same-key")

    def test_body_allows_valid_html(self):
        html = "<ul><li>item</li></ul>"
        snippet = Snippet.objects.create(name="List", key="list", body=html)
        self.assertEqual(snippet.body, html)

    def test_ordering(self):
        Snippet.objects.create(name="Zeta", key="zeta")
        Snippet.objects.create(name="Alpha", key="alpha")
        names = list(Snippet.objects.values_list("name", flat=True))
        self.assertEqual(names, ["Alpha", "Zeta"])
