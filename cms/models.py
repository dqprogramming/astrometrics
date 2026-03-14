"""
CMS models for translatable rich-text content pages and snippets.
"""

import bleach
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

ALLOWED_TAGS = [
    "a",
    "abbr",
    "acronym",
    "b",
    "blockquote",
    "br",
    "code",
    "del",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "img",
    "li",
    "ol",
    "p",
    "pre",
    "s",
    "span",
    "strong",
    "sub",
    "sup",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "u",
    "ul",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel", "target"],
    "abbr": ["title"],
    "acronym": ["title"],
    "img": ["src", "alt", "width", "height", "class"],
    "td": ["colspan", "rowspan"],
    "th": ["colspan", "rowspan", "scope"],
    "span": ["class"],
}


def sanitize_html(value):
    """Sanitize HTML using Bleach with the project allow-list."""
    if not value:
        return value
    return bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )


class Page(models.Model):
    """A CMS content page with translatable rich-text body."""

    title = models.CharField(
        max_length=255,
        help_text="Page title (translatable)",
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="URL-friendly identifier",
    )
    body = models.TextField(
        blank=True,
        help_text="Rich-text HTML content (translatable)",
    )
    meta_description = models.CharField(
        max_length=320,
        blank=True,
        help_text="SEO meta description (translatable)",
    )
    is_published = models.BooleanField(
        default=False,
        help_text="Only published pages are visible on the site",
    )
    sort_order = models.IntegerField(
        default=0,
        help_text="Lower numbers appear first",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "title"]
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        indexes = [
            models.Index(fields=["is_published", "sort_order", "title"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.body = sanitize_html(self.body)
        super().save(*args, **kwargs)


class Post(models.Model):
    """A news or blog post, listed chronologically."""

    title = models.CharField(
        max_length=255,
        help_text="Post title (translatable)",
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="URL-friendly identifier",
    )
    summary = models.TextField(
        blank=True,
        help_text="Short summary shown in listings (translatable)",
    )
    body = models.TextField(
        blank=True,
        help_text="Rich-text HTML content (translatable)",
    )
    meta_description = models.CharField(
        max_length=320,
        blank=True,
        help_text="SEO meta description (translatable)",
    )
    is_published = models.BooleanField(
        default=False,
        help_text="Only published posts are visible on the site",
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Publication date; used for ordering in listings",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        indexes = [
            models.Index(fields=["is_published", "-published_at"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.body = sanitize_html(self.body)
        self.summary = sanitize_html(self.summary)
        super().save(*args, **kwargs)


class Snippet(models.Model):
    """A reusable translatable rich-text content block.

    Snippets are identified by a unique key so templates can
    look them up (e.g. ``Snippet.objects.get(key="footer")``).
    """

    name = models.CharField(
        max_length=255,
        help_text="Human-readable label (translatable)",
    )
    key = models.SlugField(
        max_length=100,
        unique=True,
        help_text="Unique lookup key used in templates",
    )
    body = models.TextField(
        blank=True,
        help_text="Rich-text HTML content (translatable)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Snippet")
        verbose_name_plural = _("Snippets")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.body = sanitize_html(self.body)
        super().save(*args, **kwargs)
