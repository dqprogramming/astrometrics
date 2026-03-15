"""
CMS models for translatable rich-text content pages and snippets.
"""

import bleach
from django.core.cache import cache
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


class LandingPageSettings(models.Model):
    """Singleton model for configurable landing page content.

    Only one row should exist — use LandingPageSettings.load() to
    fetch-or-create it.
    """

    # Hero section
    hero_heading = models.TextField(
        help_text="Main hero heading (translatable)",
    )
    hero_subheading = models.TextField(
        blank=True,
        help_text="Hero subheading text (translatable)",
    )
    hero_button_text = models.CharField(
        max_length=100,
        default="JOIN THE MOVEMENT",
        help_text="Hero call-to-action button label (translatable)",
    )
    hero_button_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Hero button link (URL or mailto:)",
    )

    # Feature card 1
    feature_1_title = models.CharField(
        max_length=255,
        help_text="Feature card 1 title (translatable)",
    )
    feature_1_text = models.TextField(
        blank=True,
        help_text="Feature card 1 description (translatable)",
    )
    feature_1_button_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Feature card 1 button label (translatable)",
    )
    feature_1_button_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Feature card 1 button link",
    )

    # Feature card 2
    feature_2_title = models.CharField(
        max_length=255,
        help_text="Feature card 2 title (translatable)",
    )
    feature_2_text = models.TextField(
        blank=True,
        help_text="Feature card 2 description (translatable)",
    )
    feature_2_button_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Feature card 2 button label (translatable)",
    )
    feature_2_button_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Feature card 2 button link",
    )

    # Feature card 3
    feature_3_title = models.CharField(
        max_length=255,
        help_text="Feature card 3 title (translatable)",
    )
    feature_3_text = models.TextField(
        blank=True,
        help_text="Feature card 3 description (translatable)",
    )
    feature_3_button_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Feature card 3 button label (translatable)",
    )
    feature_3_button_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Feature card 3 button link",
    )

    # Stats section
    stats_fundraising_target = models.PositiveIntegerField(
        default=0,
        help_text="Fundraising target in GBP (whole pounds)",
    )
    stats_amount_raised = models.PositiveIntegerField(
        default=0,
        help_text="Amount raised so far in GBP (whole pounds)",
    )
    stats_description = models.TextField(
        blank=True,
        help_text="Stats section description text (translatable)",
    )
    stats_button_1_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Stats section first button label (translatable)",
    )
    stats_button_1_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Stats section first button link",
    )
    stats_button_2_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Stats section second button label (translatable)",
    )
    stats_button_2_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Stats section second button link",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Landing Page Settings")
        verbose_name_plural = _("Landing Page Settings")

    def __str__(self):
        return "Landing Page Settings"

    CACHE_KEY = "landing_page_settings"
    CACHE_TTL = 60 * 60  # 1 hour

    @classmethod
    def load(cls):
        """Return the singleton instance, serving from cache when possible."""
        obj = cache.get(cls.CACHE_KEY)
        if obj is None:
            obj, _created = cls.objects.get_or_create(pk=1)
            cache.set(cls.CACHE_KEY, obj, cls.CACHE_TTL)
        return obj

    @property
    def stats_percentage(self):
        """Percentage of target raised, as an integer (no decimals)."""
        if not self.stats_fundraising_target:
            return 0
        return int(
            (self.stats_amount_raised / self.stats_fundraising_target) * 100
        )

    @property
    def stats_amount_raised_display(self):
        """Amount raised formatted as GBP currency: £11,500."""
        return f"£{self.stats_amount_raised:,}"

    @property
    def stats_fundraising_target_display(self):
        """Fundraising target formatted as GBP currency: £14,000."""
        return f"£{self.stats_fundraising_target:,}"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(self.CACHE_KEY)

    def delete(self, *args, **kwargs):
        pass


class FooterSettings(models.Model):
    """Singleton model for configurable footer content.

    Only one row should exist — use FooterSettings.load() to
    fetch-or-create it.
    """

    tagline_1 = models.CharField(
        max_length=255,
        default="For Academics.",
        help_text="First tagline (translatable)",
    )
    tagline_2 = models.CharField(
        max_length=255,
        default="For Libraries.",
        help_text="Second tagline (translatable)",
    )
    tagline_3 = models.CharField(
        max_length=255,
        default="For Publishers.",
        help_text="Third tagline (translatable)",
    )
    column_1_heading = models.CharField(
        max_length=255,
        default="About OJC",
        help_text="Column 1 heading (translatable)",
    )
    column_2_heading = models.CharField(
        max_length=255,
        default="Contact us",
        help_text="Column 2 heading (translatable)",
    )
    legal_text = models.TextField(
        blank=True,
        help_text="Legal text (rich text, translatable)",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Footer Settings")
        verbose_name_plural = _("Footer Settings")

    def __str__(self):
        return "Footer Settings"

    CACHE_KEY = "footer_settings"
    CACHE_TTL = 60 * 60  # 1 hour

    @classmethod
    def load(cls):
        """Return the singleton instance, serving from cache when possible."""
        obj = cache.get(cls.CACHE_KEY)
        if obj is None:
            obj, _created = cls.objects.get_or_create(pk=1)
            links = list(obj.links.all())
            obj._prefetched_links = links
            cache.set(cls.CACHE_KEY, obj, cls.CACHE_TTL)
        return obj

    def get_column_1_links(self):
        if hasattr(self, "_prefetched_links"):
            return [lnk for lnk in self._prefetched_links if lnk.column == 1]
        return self.links.filter(column=1)

    def get_column_2_links(self):
        if hasattr(self, "_prefetched_links"):
            return [lnk for lnk in self._prefetched_links if lnk.column == 2]
        return self.links.filter(column=2)

    def save(self, *args, **kwargs):
        self.pk = 1
        self.legal_text = sanitize_html(self.legal_text)
        super().save(*args, **kwargs)
        cache.delete(self.CACHE_KEY)

    def delete(self, *args, **kwargs):
        pass


class FooterLink(models.Model):
    """A link in one of the footer's two columns."""

    COLUMN_CHOICES = [(1, "Column 1"), (2, "Column 2")]

    footer = models.ForeignKey(
        FooterSettings,
        related_name="links",
        on_delete=models.CASCADE,
    )
    column = models.PositiveIntegerField(choices=COLUMN_CHOICES)
    label = models.CharField(
        max_length=255, help_text="Link label (translatable)"
    )
    url = models.CharField(max_length=500, blank=True, help_text="Link URL")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.label

    @property
    def is_disabled(self):
        return not self.url or self.url == "#"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(FooterSettings.CACHE_KEY)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete(FooterSettings.CACHE_KEY)


class HeaderSettings(models.Model):
    """Singleton model for configurable header content.

    Only one row should exist — use HeaderSettings.load() to
    fetch-or-create it.
    """

    logo_line_1 = models.CharField(
        max_length=100,
        default="Open",
        help_text="Logo text line 1 (translatable)",
    )
    logo_line_2 = models.CharField(
        max_length=100,
        default="Journals",
        help_text="Logo text line 2 (translatable)",
    )
    logo_line_3 = models.CharField(
        max_length=100,
        default="Collective",
        help_text="Logo text line 3 (translatable)",
    )
    cta_label = models.CharField(
        max_length=100,
        default="GET INVOLVED",
        help_text="CTA button label (translatable)",
    )
    cta_url = models.CharField(
        max_length=500,
        default="mailto:info@openjournalscollective.org?subject=Open Journals Collective",
        help_text="CTA button URL",
    )
    show_mobile_sub_items = models.BooleanField(
        default=True,
        help_text="Show sub-menu items in the mobile navigation",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Header Settings")
        verbose_name_plural = _("Header Settings")

    def __str__(self):
        return "Header Settings"

    CACHE_KEY = "header_settings"
    CACHE_TTL = 60 * 60  # 1 hour

    @classmethod
    def load(cls):
        """Return the singleton instance, serving from cache when possible."""
        obj = cache.get(cls.CACHE_KEY)
        if obj is None:
            obj, _created = cls.objects.get_or_create(pk=1)
            items = list(
                obj.menu_items.filter(parent__isnull=True)
                .prefetch_related("children")
                .order_by("sort_order")
            )
            obj._prefetched_menu_items = items
            cache.set(cls.CACHE_KEY, obj, cls.CACHE_TTL)
        return obj

    def get_menu_items(self):
        if hasattr(self, "_prefetched_menu_items"):
            return self._prefetched_menu_items
        return list(
            self.menu_items.filter(parent__isnull=True)
            .prefetch_related("children")
            .order_by("sort_order")
        )

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(self.CACHE_KEY)

    def delete(self, *args, **kwargs):
        pass


class MenuItem(models.Model):
    """A navigation item in the header menu, supporting one level of nesting."""

    header = models.ForeignKey(
        HeaderSettings,
        related_name="menu_items",
        on_delete=models.CASCADE,
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )
    label = models.CharField(
        max_length=255, help_text="Menu item label (translatable)"
    )
    url = models.CharField(
        max_length=500, blank=True, help_text="Menu item URL"
    )
    sort_order = models.PositiveIntegerField(default=0)
    show_cta_in_dropdown = models.BooleanField(
        default=False,
        help_text="Show call-to-action button in this item's dropdown (top-level only)",
    )
    cta_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Call-to-action button text (falls back to global if empty, translatable)",
    )
    cta_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Call-to-action button URL (falls back to global if empty)",
    )

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.label

    @property
    def is_disabled(self):
        return not self.url or self.url == "#"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(HeaderSettings.CACHE_KEY)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete(HeaderSettings.CACHE_KEY)


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
