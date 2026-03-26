"""
CMS models for translatable rich-text content pages and snippets.
"""

import uuid

import bleach
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from cms.block_registry import get_block_class, get_label, register

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


class Category(models.Model):
    """A category for grouping news posts."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


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
    HERO_BG_YELLOW = "yellow"
    HERO_BG_BLUE = "blue"
    HERO_BG_GREEN = "green"
    HERO_BG_PINK = "pink"
    HERO_BG_DARK = "dark"
    HERO_BG_WHITE = "white"
    HERO_BG_CHOICES = [
        (HERO_BG_YELLOW, "Yellow"),
        (HERO_BG_BLUE, "Blue"),
        (HERO_BG_GREEN, "Green"),
        (HERO_BG_PINK, "Pink"),
        (HERO_BG_DARK, "Dark"),
        (HERO_BG_WHITE, "White"),
    ]
    _HERO_BG_CSS = {
        HERO_BG_YELLOW: "#FFDE59",
        HERO_BG_BLUE: "#a5bfff",
        HERO_BG_GREEN: "#78f2c1",
        HERO_BG_PINK: "#ffd4f7",
        HERO_BG_DARK: "#212129",
        HERO_BG_WHITE: "#ffffff",
    }
    _HERO_TEXT_CSS = {
        HERO_BG_YELLOW: "#38383f",
        HERO_BG_BLUE: "#212129",
        HERO_BG_GREEN: "#212129",
        HERO_BG_PINK: "#212129",
        HERO_BG_DARK: "#ffffff",
        HERO_BG_WHITE: "#212129",
    }

    HERO_ARC_TOP_RIGHT = "top-right"
    HERO_ARC_TOP_LEFT = "top-left"
    HERO_ARC_BOTTOM_RIGHT = "bottom-right"
    HERO_ARC_BOTTOM_LEFT = "bottom-left"
    HERO_ARC_CENTER_RIGHT = "center-right"
    HERO_ARC_CENTER_LEFT = "center-left"
    HERO_ARC_NONE = "none"
    HERO_ARC_CHOICES = [
        (HERO_ARC_TOP_RIGHT, "Top right"),
        (HERO_ARC_TOP_LEFT, "Top left"),
        (HERO_ARC_CENTER_RIGHT, "Centre right"),
        (HERO_ARC_CENTER_LEFT, "Centre left"),
        (HERO_ARC_BOTTOM_RIGHT, "Bottom right"),
        (HERO_ARC_BOTTOM_LEFT, "Bottom left"),
        (HERO_ARC_NONE, "None"),
    ]

    hero_bg = models.CharField(
        max_length=10,
        choices=HERO_BG_CHOICES,
        default=HERO_BG_YELLOW,
        help_text="Hero section background colour",
    )
    hero_arc_position = models.CharField(
        max_length=14,
        choices=HERO_ARC_CHOICES,
        default=HERO_ARC_TOP_RIGHT,
        help_text="Position of the decorative arc in the hero section",
    )

    is_published = models.BooleanField(
        default=False,
        help_text="Only published pages are visible on the site",
    )
    preview_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Secret token for shareable preview URL",
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

    @property
    def hero_bg_colour(self):
        return self._HERO_BG_CSS.get(self.hero_bg, "#FFDE59")

    @property
    def hero_text_colour(self):
        return self._HERO_TEXT_CSS.get(self.hero_bg, "#38383f")

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
    byline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Author name displayed on the post. Defaults to the creating user's name.",
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
    preview_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Secret token for shareable preview URL",
    )
    featured_image = models.CharField(
        max_length=500,
        blank=True,
        help_text="Featured image URL — uploaded via the manager",
    )
    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name="posts",
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
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
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


class ContactFormSettings(models.Model):
    """Singleton model for contact form configuration.

    Only one row should exist — use ContactFormSettings.load() to
    fetch-or-create it.
    """

    from_email = models.EmailField(
        default="noreply@example.com",
        help_text="Sender address for contact form emails",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Contact Form Settings")
        verbose_name_plural = _("Contact Form Settings")

    def __str__(self):
        return "Contact Form Settings"

    CACHE_KEY = "contact_form_settings"
    CACHE_TTL = 60 * 60  # 1 hour

    @classmethod
    def load(cls):
        """Return the singleton instance, serving from cache when possible."""
        obj = cache.get(cls.CACHE_KEY)
        if obj is None:
            obj, _created = cls.objects.get_or_create(pk=1)
            obj._prefetched_recipients = list(
                obj.recipients.order_by("sort_order")
            )
            cache.set(cls.CACHE_KEY, obj, cls.CACHE_TTL)
        return obj

    def get_recipient_emails(self):
        if hasattr(self, "_prefetched_recipients"):
            return [r.email for r in self._prefetched_recipients]
        return list(
            self.recipients.order_by("sort_order").values_list(
                "email", flat=True
            )
        )

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(self.CACHE_KEY)

    def delete(self, *args, **kwargs):
        pass


class ContactRecipient(models.Model):
    """An email address that receives contact form submissions."""

    settings = models.ForeignKey(
        ContactFormSettings,
        related_name="recipients",
        on_delete=models.CASCADE,
    )
    email = models.EmailField()
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(ContactFormSettings.CACHE_KEY)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete(ContactFormSettings.CACHE_KEY)


class AboutUsPageSettings(models.Model):
    """Singleton model for the About Us page content.

    Only one row should exist — use AboutUsPageSettings.load() to
    fetch-or-create it.
    """

    # URL
    slug = models.SlugField(
        default="about-us",
        help_text="URL slug for the page",
    )

    # Hero section
    hero_heading = models.CharField(
        max_length=500,
        default="Our mission is lorem ipsum dolor sit amet, consectetur ips remit et.",
        help_text="Main hero heading",
    )
    hero_sub = models.TextField(
        blank=True,
        default="",
        help_text="Hero sub-heading text",
    )

    # Content section
    section_title = models.CharField(
        max_length=200,
        default="About us.",
        help_text="Content section title",
    )
    col_1_title = models.CharField(
        max_length=200,
        default="Our vision.",
        help_text="Left column title",
    )
    col_1_body = models.TextField(
        blank=True,
        help_text="Left column body — rich text, sanitized",
    )
    col_2_title = models.CharField(
        max_length=200,
        default="Our Mission.",
        help_text="Right column title",
    )
    col_2_body = models.TextField(
        blank=True,
        help_text="Right column body — rich text, sanitized",
    )

    # Stats
    stat_1_value = models.CharField(max_length=50, default="6")
    stat_1_text = models.TextField(blank=True)
    stat_2_value = models.CharField(max_length=50, default="60%")
    stat_2_text = models.TextField(blank=True)
    stat_3_value = models.CharField(max_length=50, default="3m")
    stat_3_text = models.TextField(blank=True)
    stat_4_value = models.CharField(max_length=50, default="300k")
    stat_4_text = models.TextField(blank=True)

    # Metadata
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("About Us Page Settings")
        verbose_name_plural = _("About Us Page Settings")

    def __str__(self):
        return "About Us Page Settings"

    CACHE_KEY = "about_us_page_settings"
    CACHE_TTL = 60 * 60  # 1 hour

    @classmethod
    def load(cls):
        """Return the singleton instance, serving from cache when possible."""
        obj = cache.get(cls.CACHE_KEY)
        if obj is None:
            obj, _created = cls.objects.get_or_create(pk=1)
            cache.set(cls.CACHE_KEY, obj, cls.CACHE_TTL)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1
        self.col_1_body = sanitize_html(self.col_1_body)
        self.col_2_body = sanitize_html(self.col_2_body)
        self.stat_1_text = sanitize_html(self.stat_1_text)
        self.stat_2_text = sanitize_html(self.stat_2_text)
        self.stat_3_text = sanitize_html(self.stat_3_text)
        self.stat_4_text = sanitize_html(self.stat_4_text)
        super().save(*args, **kwargs)
        cache.delete(self.CACHE_KEY)

    def delete(self, *args, **kwargs):
        pass


class AboutUsQuote(models.Model):
    """A quote displayed in the About Us page carousel."""

    page = models.ForeignKey(
        AboutUsPageSettings,
        on_delete=models.CASCADE,
        related_name="quotes",
    )
    logo = models.ImageField(
        upload_to="about_us/logos/",
        blank=True,
        help_text="Publisher logo image",
    )
    quote_text = models.TextField()
    author_name = models.CharField(max_length=255)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.author_name

    def save(self, *args, **kwargs):
        self.quote_text = sanitize_html(self.quote_text)
        super().save(*args, **kwargs)


LOREM_BODY = (
    "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
    "sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna "
    "aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud "
    "exerci tation ullamcorper suscipit.</p>"
)


class BlockPage(models.Model):
    """A dynamic block page with ordered content blocks."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    template_key = models.CharField(max_length=50, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    blocks = GenericRelation(
        "PageBlock",
        content_type_field="content_type",
        object_id_field="page_id",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class BlockPageTemplate(models.Model):
    """Stores predefined page templates (default block configurations)."""

    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    config = models.JSONField()

    def __str__(self):
        return self.name


# Keep DEFAULT_PAGE_CONFIG at module level for backward compatibility
# (old migrations and data seeding reference this).
DEFAULT_PAGE_CONFIG = [
    {
        "block_type": "members_header",
        "is_visible": True,
        "defaults": {"heading": "Our members."},
    },
    {
        "block_type": "who_we_are",
        "is_visible": True,
        "defaults": {
            "section_heading": "Who we are.",
            "circle_1_title": "We are Academics.",
            "circle_1_body": LOREM_BODY,
            "circle_2_title": "We are Librarians.",
            "circle_2_body": LOREM_BODY,
            "circle_3_title": "We are Publishers.",
            "circle_3_body": LOREM_BODY,
            "cta_text": "Join Us",
            "cta_url": "#",
            "show_cta": True,
        },
    },
    {
        "block_type": "person_carousel",
        "is_visible": True,
        "defaults": {
            "bg_color": "#a5bfff",
            "text_color": "#212129",
            "bullet_color": "#999999",
            "bullet_active_color": "#000000",
        },
        "children": [
            {
                "quote_text": (
                    "<p>Quote from a member that's already onboard. Lorem "
                    "ipsum dolor sit amet, consectetuer adipis cing elit, "
                    "sed diam nonummy nibh euismod tincidunt ut laoreet.</p>"
                ),
                "author_name": "Name Here, Company",
                "sort_order": 0,
            },
            {
                "quote_text": (
                    "<p>Another testimonial from a valued member of the "
                    "collective. Their experience highlights the benefits "
                    "of open access publishing.</p>"
                ),
                "author_name": "Jane Smith, University Press",
                "sort_order": 1,
            },
        ],
    },
    {
        "block_type": "members_institutions",
        "is_visible": True,
        "defaults": {
            "heading": "OJC Members.",
            "cta_text": "Join Us",
            "cta_url": "#",
            "show_cta": True,
        },
    },
    {
        "block_type": "person_carousel",
        "is_visible": True,
        "defaults": {
            "bg_color": "#212129",
            "text_color": "#ffffff",
            "bullet_color": "#ffffff",
            "bullet_active_color": "#999999",
        },
        "children": [
            {
                "quote_text": (
                    "<p>Quote from a member that's already onboard. Lorem "
                    "ipsum dolor sit amet, consectetuer adipis cing elit, "
                    "sed diam nonummy nibh euismod tincidunt ut laoreet.</p>"
                ),
                "author_name": "Name Here, Company",
                "sort_order": 0,
            },
            {
                "quote_text": (
                    "<p>Open access is the future of academic publishing "
                    "and the collective model ensures sustainability for "
                    "all participants.</p>"
                ),
                "author_name": "Dr. Sarah Williams, Oxford Press",
                "sort_order": 1,
            },
        ],
    },
]


# ── Block System ─────────────────────────────────────────────────────────────


class BaseBlock(models.Model):
    """Abstract base for all CMS blocks."""

    BLOCK_TYPE = ""
    LABEL = ""
    ICON = ""
    FORM_CLASS = ""
    MANAGER_TEMPLATE = ""
    PUBLIC_TEMPLATE = ""
    FORMSET_CLASS = ""
    COLOR_DEFAULTS = {}

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def get_public_context(self):
        return {}

    def create_children_from_config(self, children_config):
        pass


@register
class MembersHeaderBlock(BaseBlock):
    """Header block for the Our Members page."""

    BLOCK_TYPE = "members_header"
    LABEL = "Hero: Thin Band Style"
    ICON = "bi-type-h1"
    FORM_CLASS = "cms.forms.MembersHeaderBlockForm"
    MANAGER_TEMPLATE = "cms/manager/blocks/_members_header.html"
    PUBLIC_TEMPLATE = "includes/blocks/_members_header.html"
    COLOR_DEFAULTS = {
        "bg_color": "#71f7f2",
        "text_color": "#212129",
    }

    heading = models.CharField(
        max_length=500,
        default="Our members.",
        help_text="Main hero heading",
    )
    bg_color = models.CharField(max_length=7, default="#71f7f2")
    text_color = models.CharField(max_length=7, default="#212129")

    def __str__(self):
        return f"MembersHeaderBlock #{self.pk}"


@register
class WhoWeAreBlock(BaseBlock):
    """Who We Are block for the Our Members page."""

    BLOCK_TYPE = "who_we_are"
    LABEL = "Who We Are"
    ICON = "bi-people-fill"
    FORM_CLASS = "cms.forms.WhoWeAreBlockForm"
    MANAGER_TEMPLATE = "cms/manager/blocks/_who_we_are.html"
    PUBLIC_TEMPLATE = "includes/blocks/_who_we_are.html"
    COLOR_DEFAULTS = {
        "bg_color": "#ffffff",
        "text_color": "#212129",
    }

    section_heading = models.CharField(
        max_length=200,
        default="Who we are.",
        help_text="Content section heading",
    )
    circle_1_title = models.CharField(
        max_length=200, default="We are Academics."
    )
    circle_1_body = models.TextField(blank=True, default=LOREM_BODY)
    circle_2_title = models.CharField(
        max_length=200, default="We are Librarians."
    )
    circle_2_body = models.TextField(blank=True, default=LOREM_BODY)
    circle_3_title = models.CharField(
        max_length=200, default="We are Publishers."
    )
    circle_3_body = models.TextField(blank=True, default=LOREM_BODY)
    bg_color = models.CharField(max_length=7, default="#ffffff")
    text_color = models.CharField(max_length=7, default="#212129")
    show_cta = models.BooleanField(default=True)
    cta_text = models.CharField(max_length=200, default="Join Us")
    cta_url = models.CharField(max_length=500, default="#", blank=True)

    def __str__(self):
        return f"WhoWeAreBlock #{self.pk}"

    def save(self, *args, **kwargs):
        self.circle_1_body = sanitize_html(self.circle_1_body)
        self.circle_2_body = sanitize_html(self.circle_2_body)
        self.circle_3_body = sanitize_html(self.circle_3_body)
        super().save(*args, **kwargs)


@register
class PersonCarouselBlock(BaseBlock):
    """Person carousel block for the Our Members page."""

    BLOCK_TYPE = "person_carousel"
    LABEL = "Person Carousel"
    ICON = "bi-chat-quote"
    FORM_CLASS = "cms.forms.PersonCarouselBlockForm"
    FORMSET_CLASS = "cms.forms.PersonCarouselQuoteFormSet"
    MANAGER_TEMPLATE = "cms/manager/blocks/_person_carousel.html"
    PUBLIC_TEMPLATE = "includes/blocks/_person_carousel.html"
    COLOR_DEFAULTS = {
        "bg_color": "#a5bfff",
        "text_color": "#212129",
        "bullet_color": "#999999",
        "bullet_active_color": "#000000",
    }

    bg_color = models.CharField(max_length=7, default="#a5bfff")
    text_color = models.CharField(max_length=7, default="#212129")
    bullet_color = models.CharField(
        max_length=7,
        default="#999999",
        help_text="Carousel dot colour (unselected)",
    )
    bullet_active_color = models.CharField(
        max_length=7,
        default="#000000",
        help_text="Carousel dot colour (selected)",
    )

    def __str__(self):
        return f"PersonCarouselBlock #{self.pk}"

    def get_public_context(self):
        return {"quotes": self.quotes.all()}

    def create_children_from_config(self, children_config):
        for child in children_config:
            PersonCarouselQuote.objects.create(block=self, **child)


class PersonCarouselQuote(models.Model):
    """A quote in a person carousel block."""

    block = models.ForeignKey(
        PersonCarouselBlock,
        on_delete=models.CASCADE,
        related_name="quotes",
    )
    image = models.ImageField(
        upload_to="our_members/carousel/",
        blank=True,
        help_text="Quote image",
    )
    quote_text = models.TextField()
    author_name = models.CharField(max_length=255)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.author_name

    def save(self, *args, **kwargs):
        self.quote_text = sanitize_html(self.quote_text)
        super().save(*args, **kwargs)


@register
class PeopleListBlock(BaseBlock):
    """A list of people with photos, names, descriptions, and LinkedIn links."""

    BLOCK_TYPE = "people_list"
    LABEL = "People List"
    ICON = "bi-people"
    FORM_CLASS = "cms.forms.PeopleListBlockForm"
    FORMSET_CLASS = "cms.forms.PeopleListPersonFormSet"
    MANAGER_TEMPLATE = "cms/manager/blocks/_people_list.html"
    PUBLIC_TEMPLATE = "includes/blocks/_people_list.html"
    COLOR_DEFAULTS = {
        "bg_color": "#ffffff",
        "text_color": "#212129",
        "card_bg_color": "#71f7f2",
    }

    name = models.CharField(max_length=255, default="Board Members.")
    bg_color = models.CharField(max_length=7, default="#ffffff")
    text_color = models.CharField(max_length=7, default="#212129")
    card_bg_color = models.CharField(max_length=7, default="#71f7f2")

    def __str__(self):
        return f"PeopleListBlock #{self.pk}"

    def get_public_context(self):
        return {"people": self.people.all()}

    def create_children_from_config(self, children_config):
        import os

        from django.conf import settings as django_settings
        from django.core.files.base import ContentFile

        for child in children_config:
            static_image = child.pop("static_image", None)
            person = PeopleListPerson.objects.create(block=self, **child)
            if static_image:
                # Copy static file to media storage
                static_path = os.path.join(
                    django_settings.BASE_DIR, static_image.lstrip("/")
                )
                if os.path.isfile(static_path):
                    ext = os.path.splitext(static_path)[1]
                    dest_name = f"blocks/people_list/{person.pk}{ext}"
                    with open(static_path, "rb") as f:
                        person.image.save(
                            dest_name, ContentFile(f.read()), save=True
                        )


class PeopleListPerson(models.Model):
    """A person in a people list block."""

    block = models.ForeignKey(
        PeopleListBlock,
        on_delete=models.CASCADE,
        related_name="people",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    linkedin_url = models.CharField(max_length=500, blank=True)
    image = models.ImageField(
        upload_to="blocks/people_list/",
        blank=True,
        help_text="Person photo (will be cropped to 600x400)",
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.description = sanitize_html(self.description)
        super().save(*args, **kwargs)


@register
class ManifestoHeroBlock(BaseBlock):
    """Hero block for the Our Manifesto page."""

    BLOCK_TYPE = "manifesto_hero"
    LABEL = "Hero: Quarter Circle on Left with Image"
    ICON = "bi-type-h1"
    FORM_CLASS = "cms.forms.ManifestoHeroBlockForm"
    MANAGER_TEMPLATE = "cms/manager/blocks/_manifesto_hero.html"
    PUBLIC_TEMPLATE = "includes/blocks/_manifesto_hero.html"
    COLOR_DEFAULTS = {
        "bg_color": "#71f7f2",
        "text_color": "#212129",
    }

    heading = models.CharField(
        max_length=500,
        default="OJC is leading a growing academic movement.",
        help_text="Main hero heading",
    )
    sub_heading = models.TextField(
        blank=True,
        default=(
            "Our mission is to build a sustainable future for academic "
            "journals by challenging the profit-making models of global "
            "corporate publishing and data systems."
        ),
        help_text="Hero sub-heading text",
    )
    hero_image = models.ImageField(
        upload_to="blocks/hero/",
        blank=True,
        help_text="Hero image (550×526). Will be resized/cropped if needed.",
    )
    hero_image_alt = models.CharField(
        max_length=255,
        default="A person contemplating the future of academic publishing",
        help_text="Alt text for the hero image",
    )
    bg_color = models.CharField(max_length=7, default="#71f7f2")
    text_color = models.CharField(max_length=7, default="#212129")

    HERO_IMAGE_WIDTH = 550
    HERO_IMAGE_HEIGHT = 526

    def __str__(self):
        return f"ManifestoHeroBlock #{self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.hero_image:
            self._resize_hero_image()

    def _resize_hero_image(self):
        from io import BytesIO

        from django.core.files.base import ContentFile
        from PIL import Image

        try:
            img = Image.open(self.hero_image)
        except Exception:
            return

        w, h = img.size
        tw, th = self.HERO_IMAGE_WIDTH, self.HERO_IMAGE_HEIGHT

        if w == tw and h == th:
            return

        target_ratio = tw / th
        current_ratio = w / h

        if abs(current_ratio - target_ratio) < 0.01:
            # Close enough — just resize
            img = img.resize((tw, th), Image.LANCZOS)
        elif current_ratio > target_ratio:
            # Too wide — resize by height, crop width
            new_h = th
            new_w = int(w * (th / h))
            img = img.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - tw) // 2
            img = img.crop((left, 0, left + tw, th))
        else:
            # Too tall — resize by width, crop height
            new_w = tw
            new_h = int(h * (tw / w))
            img = img.resize((new_w, new_h), Image.LANCZOS)
            top = (new_h - th) // 3  # bias toward top third
            img = img.crop((0, top, tw, top + th))

        buf = BytesIO()
        fmt = (
            "PNG" if self.hero_image.name.lower().endswith(".png") else "JPEG"
        )
        save_kwargs = {"format": fmt}
        if fmt == "JPEG":
            save_kwargs["quality"] = 90
        img.save(buf, **save_kwargs)

        name = self.hero_image.name
        self.hero_image.save(name, ContentFile(buf.getvalue()), save=False)
        type(self).objects.filter(pk=self.pk).update(
            hero_image=self.hero_image
        )


@register
class ManifestoTextBlock(BaseBlock):
    """Text body block for the Our Manifesto page."""

    BLOCK_TYPE = "manifesto_text"
    LABEL = "Standalone Text Block"
    ICON = "bi-text-paragraph"
    FORM_CLASS = "cms.forms.ManifestoTextBlockForm"
    MANAGER_TEMPLATE = "cms/manager/blocks/_manifesto_text.html"
    PUBLIC_TEMPLATE = "includes/blocks/_manifesto_text.html"
    COLOR_DEFAULTS = {
        "bg_color": "#ffffff",
        "text_color": "#212129",
    }

    body = models.TextField(blank=True)
    bg_color = models.CharField(max_length=7, default="#ffffff")
    text_color = models.CharField(max_length=7, default="#212129")

    def __str__(self):
        return f"ManifestoTextBlock #{self.pk}"

    def save(self, *args, **kwargs):
        self.body = sanitize_html(self.body)
        super().save(*args, **kwargs)


@register
class ManifestoOrganiseBlock(BaseBlock):
    """Organise + achievable block for the Our Manifesto page."""

    BLOCK_TYPE = "manifesto_organise"
    LABEL = "Importance of Organisation"
    ICON = "bi-chat-square-text"
    FORM_CLASS = "cms.forms.ManifestoOrganiseBlockForm"
    MANAGER_TEMPLATE = "cms/manager/blocks/_manifesto_organise.html"
    PUBLIC_TEMPLATE = "includes/blocks/_manifesto_organise.html"
    COLOR_DEFAULTS = {
        "bg_color": "#a5bfff",
        "text_color": "#ffffff",
        "cta_bg_color": "#000000",
        "cta_text_color": "#ffffff",
        "cta_hover_bg_color": "#000000",
        "cta_hover_text_color": "#ffffff",
    }

    organise_heading = models.CharField(
        max_length=500,
        default="To do this, we must organise.",
    )
    organise_body = models.TextField(
        blank=True,
        default=(
            "<p>Responding to their own historical moment of capitalist "
            "crisis, Marx and Engels wrote in The Communist Manifesto: "
            "\u2018Workers of the world unite; you have nothing to lose "
            "but your chains\u2019. Breaking society up into two great "
            "hostile camps, into two great classes directly facing each "
            "other: bourgeoisie and proletariat.</p>"
            "<p>Almost 180 years after this manifesto was written, we "
            "find ourselves again at a significant moment of capitalist "
            "crisis in academic journals publishing. Our lives are "
            "closely drawn with two great classes: directly facing each "
            "other. Corporate middle-men publishers like Elsevier, RELX, "
            "Wiley, Springer Nature, Taylor &amp; Francis and others "
            "continue to extract monopoly profits for their shareholders. "
            "Directly facing them is the international academic labour of "
            "academics who give these publishers their research while "
            "their library colleagues have to find a way to bear the "
            "crippling costs of buying this research back.</p>"
            "<p>The crisis in journals publishing cannot go on any "
            "longer. The commodification of the higher education sector "
            "simply won\u2019t allow it.</p>"
        ),
    )
    achievable_heading = models.CharField(
        max_length=500,
        default="Our task is ambitious, yet achievable.",
    )
    achievable_body = models.TextField(
        blank=True,
        default=(
            "<p>We want a world where academic research is available to "
            "all, with no author fees and no paywalls. Working together "
            "with librarians, funders and policymakers, academics and "
            "researchers can co-design an exit ramp from this commercial "
            "stranglehold.</p>"
            "<p>This collaboration is what led to the launch of the Open "
            "Journals Collective. By building a strong collective "
            "network, we protect bibliodiversity and build resilience "
            "against a ravaging industry. If not now, perhaps never at "
            "all (just kidding).</p>"
        ),
    )
    show_cta = models.BooleanField(default=True)
    cta_text = models.CharField(max_length=100, default="It starts here")
    cta_url = models.CharField(max_length=500, default="/our-team/")
    cta_bg_color = models.CharField(max_length=7, default="#000000")
    cta_text_color = models.CharField(max_length=7, default="#ffffff")
    cta_hover_bg_color = models.CharField(max_length=7, default="#000000")
    cta_hover_text_color = models.CharField(max_length=7, default="#ffffff")
    bg_color = models.CharField(max_length=7, default="#a5bfff")
    text_color = models.CharField(max_length=7, default="#ffffff")

    def __str__(self):
        return f"ManifestoOrganiseBlock #{self.pk}"

    def save(self, *args, **kwargs):
        self.organise_body = sanitize_html(self.organise_body)
        self.achievable_body = sanitize_html(self.achievable_body)
        super().save(*args, **kwargs)


@register
class FreeAccessJournalsBlock(BaseBlock):
    """Free access to journals CTA block."""

    BLOCK_TYPE = "free_access_journals"
    LABEL = "Free Access To Leading Journals"
    ICON = "bi-megaphone"
    FORM_CLASS = "cms.forms.FreeAccessJournalsBlockForm"
    MANAGER_TEMPLATE = "cms/manager/blocks/_free_access_journals.html"
    PUBLIC_TEMPLATE = "includes/blocks/_free_access_journals.html"
    COLOR_DEFAULTS = {
        "bg_color": "#ffffff",
        "text_color": "#212129",
        "cta_bg_color": "#000000",
        "cta_text_color": "#ffffff",
        "cta_hover_bg_color": "#000000",
        "cta_hover_text_color": "#ffffff",
    }

    heading = models.CharField(
        max_length=500,
        default=(
            "Free access to hundreds of the world\u2019s leading "
            "academic journals."
        ),
    )
    image = models.ImageField(
        upload_to="blocks/free_access/",
        blank=True,
    )
    image_alt = models.CharField(
        max_length=255,
        default="A modern library representing free access to academic journals",
    )
    show_cta = models.BooleanField(default=True)
    cta_text = models.CharField(max_length=100, default="Speak to us")
    cta_url = models.CharField(max_length=500, default="/our-team/")
    cta_bg_color = models.CharField(max_length=7, default="#000000")
    cta_text_color = models.CharField(max_length=7, default="#ffffff")
    cta_hover_bg_color = models.CharField(max_length=7, default="#000000")
    cta_hover_text_color = models.CharField(max_length=7, default="#ffffff")
    bg_color = models.CharField(max_length=7, default="#ffffff")
    text_color = models.CharField(max_length=7, default="#212129")

    def __str__(self):
        return f"FreeAccessJournalsBlock #{self.pk}"


@register
class MembersInstitutionsBlock(BaseBlock):
    """Members institutions grid block for the Our Members page."""

    BLOCK_TYPE = "members_institutions"
    LABEL = "Supporting Institutions List"
    ICON = "bi-building"
    FORM_CLASS = "cms.forms.MembersInstitutionsBlockForm"
    FORMSET_CLASS = "cms.forms.InstitutionEntryFormSet"
    MANAGER_TEMPLATE = "cms/manager/blocks/_members_institutions.html"
    PUBLIC_TEMPLATE = "includes/blocks/_members_institutions.html"
    COLOR_DEFAULTS = {
        "bg_color": "#f0f0f1",
        "text_color": "#212129",
    }

    heading = models.CharField(
        max_length=200,
        default="OJC Members.",
        help_text="Members list section heading",
    )
    bg_color = models.CharField(max_length=7, default="#f0f0f1")
    text_color = models.CharField(max_length=7, default="#212129")
    show_cta = models.BooleanField(default=True)
    cta_text = models.CharField(max_length=200, default="Join Us")
    cta_url = models.CharField(max_length=500, default="#", blank=True)

    def __str__(self):
        return f"MembersInstitutionsBlock #{self.pk}"

    def get_public_context(self):
        return {"institutions": self.institutions.all()}

    def create_children_from_config(self, children_config):
        for child in children_config:
            InstitutionEntry.objects.create(block=self, **child)


class InstitutionEntry(models.Model):
    """An institution entry in a members institutions block."""

    block = models.ForeignKey(
        MembersInstitutionsBlock,
        on_delete=models.CASCADE,
        related_name="institutions",
    )
    name = models.CharField(max_length=255)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


@register
class OurModelHeroBlock(BaseBlock):
    """Hero block with full width image and concentric circles."""

    BLOCK_TYPE = "our_model_hero"
    LABEL = "Hero: Full Width Image and Concentric Circles"
    ICON = "bi-type-h1"
    FORM_CLASS = "cms.forms.OurModelHeroBlockForm"
    MANAGER_TEMPLATE = "cms/manager/blocks/_our_model_hero.html"
    PUBLIC_TEMPLATE = "includes/blocks/_our_model_hero.html"
    COLOR_DEFAULTS = {
        "circle_color": "#71f7f2",
        "bg_color": "#ffffff",
        "text_color": "#212129",
    }

    heading = models.TextField(
        default=(
            "By joining OJC, libraries support the long-term"
            " sustainability of non-profit, university-based"
            ' <span class="highlight">journals.</span>'
        ),
        help_text="Hero heading — may contain <span> for highlights",
    )
    hero_image = models.ImageField(
        upload_to="blocks/our_model_hero/",
        blank=True,
        help_text="Hero image (970x400). Will be resized/cropped if needed.",
    )
    hero_image_alt = models.CharField(
        max_length=255,
        default="A researcher browsing books in a library",
        help_text="Alt text for the hero image",
    )
    circle_color = models.CharField(max_length=7, default="#71f7f2")
    bg_color = models.CharField(max_length=7, default="#ffffff")
    text_color = models.CharField(max_length=7, default="#212129")

    HERO_IMAGE_WIDTH = 970
    HERO_IMAGE_HEIGHT = 400

    def __str__(self):
        return f"OurModelHeroBlock #{self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.hero_image:
            self._resize_hero_image()

    def _resize_hero_image(self):
        from io import BytesIO

        from django.core.files.base import ContentFile
        from PIL import Image

        try:
            img = Image.open(self.hero_image)
        except Exception:
            return

        w, h = img.size
        tw, th = self.HERO_IMAGE_WIDTH, self.HERO_IMAGE_HEIGHT

        if w == tw and h == th:
            return

        target_ratio = tw / th
        current_ratio = w / h

        if abs(current_ratio - target_ratio) < 0.01:
            img = img.resize((tw, th), Image.LANCZOS)
        elif current_ratio > target_ratio:
            new_h = th
            new_w = int(w * (th / h))
            img = img.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - tw) // 2
            img = img.crop((left, 0, left + tw, th))
        else:
            new_w = tw
            new_h = int(h * (tw / w))
            img = img.resize((new_w, new_h), Image.LANCZOS)
            top = (new_h - th) // 3
            img = img.crop((0, top, tw, top + th))

        buf = BytesIO()
        fmt = (
            "PNG" if self.hero_image.name.lower().endswith(".png") else "JPEG"
        )
        save_kwargs = {"format": fmt}
        if fmt == "JPEG":
            save_kwargs["quality"] = 90
        img.save(buf, **save_kwargs)

        name = self.hero_image.name
        self.hero_image.save(name, ContentFile(buf.getvalue()), save=False)
        type(self).objects.filter(pk=self.pk).update(
            hero_image=self.hero_image
        )


@register
class OJCModelBlock(BaseBlock):
    """OJC Model section block with collection cards."""

    BLOCK_TYPE = "ojc_model"
    LABEL = "OJC Model"
    ICON = "bi-diagram-3"
    FORM_CLASS = "cms.forms.OJCModelBlockForm"
    MANAGER_TEMPLATE = "cms/manager/blocks/_ojc_model.html"
    PUBLIC_TEMPLATE = "includes/blocks/_ojc_model.html"
    COLOR_DEFAULTS = {
        "circle_bg_color": "#71f7f2",
        "circle_text_color": "#212129",
        "bg_color": "#e8e8e8",
        "text_color": "#212129",
    }

    heading = models.CharField(max_length=255, default="The OJC Model.")
    body = models.TextField(blank=True)
    collections_label = models.TextField(blank=True)
    collection_1_number = models.CharField(max_length=10, default="01")
    collection_1_title = models.CharField(
        max_length=255, default="The Multidisciplinary Collection"
    )
    collection_1_link_text = models.CharField(
        max_length=100, default="BROWSE JOURNALS"
    )
    collection_1_link_url = models.CharField(max_length=500, blank=True)
    collection_2_number = models.CharField(max_length=10, default="02")
    collection_2_title = models.CharField(
        max_length=255,
        default="The Arts, Humanities & Social Sciences Collection.",
    )
    collection_2_link_text = models.CharField(
        max_length=100, default="BROWSE JOURNALS"
    )
    collection_2_link_url = models.CharField(max_length=500, blank=True)
    collection_3_number = models.CharField(max_length=10, default="03")
    collection_3_title = models.CharField(
        max_length=255,
        default="The Science, Engineering, Technology & Maths Collection.",
    )
    collection_3_link_text = models.CharField(
        max_length=100, default="BROWSE JOURNALS"
    )
    collection_3_link_url = models.CharField(max_length=500, blank=True)
    circle_bg_color = models.CharField(max_length=7, default="#71f7f2")
    circle_text_color = models.CharField(max_length=7, default="#212129")
    bg_color = models.CharField(max_length=7, default="#e8e8e8")
    text_color = models.CharField(max_length=7, default="#212129")

    def __str__(self):
        return f"OJCModelBlock #{self.pk}"

    def save(self, *args, **kwargs):
        self.body = sanitize_html(self.body)
        super().save(*args, **kwargs)


@register
class JournalFundingBlock(BaseBlock):
    """Journal Funding section block."""

    BLOCK_TYPE = "journal_funding"
    LABEL = "Journal Funding"
    ICON = "bi-currency-pound"
    FORM_CLASS = "cms.forms.JournalFundingBlockForm"
    MANAGER_TEMPLATE = "cms/manager/blocks/_journal_funding.html"
    PUBLIC_TEMPLATE = "includes/blocks/_journal_funding.html"
    COLOR_DEFAULTS = {
        "bg_color": "#ffffff",
        "text_color": "#212129",
    }

    heading = models.CharField(max_length=255, default="Journal Funding.")
    body = models.TextField(blank=True)
    upper_image = models.ImageField(
        upload_to="blocks/journal_funding/",
        blank=True,
    )
    upper_image_alt = models.CharField(
        max_length=255,
        default="Academic collaboration in a meeting room",
    )
    lower_image = models.ImageField(
        upload_to="blocks/journal_funding/",
        blank=True,
    )
    lower_image_alt = models.CharField(
        max_length=255,
        default="Open access academic journals supported by OJC",
    )
    bg_color = models.CharField(max_length=7, default="#ffffff")
    text_color = models.CharField(max_length=7, default="#212129")

    def __str__(self):
        return f"JournalFundingBlock #{self.pk}"

    def save(self, *args, **kwargs):
        self.body = sanitize_html(self.body)
        super().save(*args, **kwargs)


@register
class RevenueDistributionBlock(BaseBlock):
    """Revenue distribution section with dynamic tables."""

    BLOCK_TYPE = "revenue_distribution"
    LABEL = "Journal Funding and Revenue Distribution"
    ICON = "bi-table"
    FORM_CLASS = "cms.forms.RevenueDistributionBlockForm"
    MANAGER_TEMPLATE = "cms/manager/blocks/_revenue_distribution.html"
    PUBLIC_TEMPLATE = "includes/blocks/_revenue_distribution.html"
    FORMSET_CLASS = "cms.forms.RevenuePackageTableFormSet"
    COLOR_DEFAULTS = {
        "bg_color": "#e8e8e8",
        "text_color": "#212129",
    }

    heading = models.CharField(
        max_length=255,
        default="Journal Funding & \nRevenue Distribution.",
    )
    description = models.TextField(
        blank=True,
        default=(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit,"
            " sed do eiusmod tempor incididunt ut labore et dolore"
            " magna aliqua. Ut enim ad minim veniam, quis nostrud"
            " exercitation ullamco."
        ),
    )
    callout = models.TextField(
        blank=True,
        default=(
            "We will provide documentation, training events, and"
            " regular community meet-ups for OJC members."
        ),
    )
    bg_color = models.CharField(max_length=7, default="#e8e8e8")
    text_color = models.CharField(max_length=7, default="#212129")

    _DEFAULT_CHILDREN = {
        "columns": [
            "Package & Band",
            "Journal Size",
            "No. of articles p/year",
            "Annual Funding",
        ],
        "tables": [
            {
                "title": "Package A (full fat)",
                "description": "Full support for journals with no funding or income.",
                "colour_preset": "pink",
                "sort_order": 0,
                "rows": [
                    ["1", "Tiny", "10", "\u00a310,500"],
                    ["2", "Small", "25", ""],
                    ["3", "Medium", "50", "\u00a319,200"],
                    ["4", "Large", "100", "\u00a325,500"],
                    ["5", "Very Large", "500", ""],
                ],
            },
            {
                "title": "Package B (semi-skimmed)",
                "description": "Partial support for journals with minimal funding or income.",
                "colour_preset": "green",
                "sort_order": 1,
                "rows": [
                    ["1", "Tiny", "10", ""],
                    ["2", "Small", "25", "\u00a39,000"],
                    ["3", "Medium", "50", "\u00a317,700"],
                    ["4", "Large", "100", "\u00a324,000"],
                    ["5", "Very Large", "500", ""],
                ],
            },
            {
                "title": "Package C (skimmed)",
                "description": "Top-up support for journals with established funding or income.",
                "colour_preset": "blue",
                "sort_order": 2,
                "rows": [
                    ["1", "Tiny", "10", "\u00a35,000"],
                    ["2", "Small", "25", "\u00a37,000"],
                    ["3", "Medium", "50", "\u00a39,350"],
                    ["4", "Large", "100", "\u00a312,500"],
                    ["5", "Very Large", "500", "\u00a324,500"],
                ],
            },
        ],
    }

    def __str__(self):
        return f"RevenueDistributionBlock #{self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_public_context(self):
        columns = list(self.table_columns.order_by("sort_order"))
        tables = list(
            self.package_tables.prefetch_related("rows__cells").order_by(
                "sort_order"
            )
        )
        num_columns = len(columns)
        col_width_pct = (100 // num_columns) if num_columns else 25

        for table in tables:
            for row in table.rows.all():
                cells_by_col = {
                    cell.column_id: cell.value for cell in row.cells.all()
                }
                row.ordered_cells = [
                    cells_by_col.get(col.pk, "") for col in columns
                ]

        return {
            "columns": columns,
            "tables": tables,
            "num_columns": num_columns,
            "col_width_pct": col_width_pct,
        }

    def create_children_from_config(self, children_config):
        # Create columns
        column_headings = children_config.get("columns", [])
        columns = []
        for i, heading in enumerate(column_headings):
            col = RevenueTableColumn.objects.create(
                block=self, heading=heading, sort_order=i
            )
            columns.append(col)

        # Create tables with rows and cells
        for table_data in children_config.get("tables", []):
            rows_data = table_data.get("rows", [])
            table = RevenuePackageTable.objects.create(
                block=self,
                title=table_data.get("title", ""),
                description=table_data.get("description", ""),
                colour_preset=table_data.get("colour_preset", "pink"),
                sort_order=table_data.get("sort_order", 0),
            )
            for row_idx, row_values in enumerate(rows_data):
                row = RevenuePackageRow.objects.create(
                    table=table, sort_order=row_idx
                )
                for col_idx, cell_value in enumerate(row_values):
                    if col_idx < len(columns):
                        RevenuePackageCell.objects.create(
                            row=row,
                            column=columns[col_idx],
                            value=cell_value,
                        )


class RevenueTableColumn(models.Model):
    """Column header for revenue distribution tables."""

    block = models.ForeignKey(
        RevenueDistributionBlock,
        on_delete=models.CASCADE,
        related_name="table_columns",
    )
    heading = models.CharField(max_length=100)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.heading


class RevenuePackageTable(models.Model):
    """A colour-coded package table in a revenue distribution block."""

    COLOUR_PINK = "pink"
    COLOUR_GREEN = "green"
    COLOUR_BLUE = "blue"
    COLOUR_CUSTOM = "custom"
    COLOUR_CHOICES = [
        (COLOUR_PINK, "Pink"),
        (COLOUR_GREEN, "Green"),
        (COLOUR_BLUE, "Blue"),
        (COLOUR_CUSTOM, "Custom"),
    ]
    _COLOUR_MAP = {
        COLOUR_PINK: {"header": "#ffd8fd", "rows": "#ffecfe"},
        COLOUR_GREEN: {"header": "#8ee8c8", "rows": "#d4f5e8"},
        COLOUR_BLUE: {"header": "#a5bfff", "rows": "#dce6ff"},
    }

    block = models.ForeignKey(
        RevenueDistributionBlock,
        on_delete=models.CASCADE,
        related_name="package_tables",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    colour_preset = models.CharField(
        max_length=10, choices=COLOUR_CHOICES, default=COLOUR_PINK
    )
    custom_header_bg = models.CharField(max_length=7, blank=True)
    custom_row_bg = models.CharField(max_length=7, blank=True)
    custom_text_colour = models.CharField(max_length=7, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.title

    @property
    def header_bg_colour(self):
        if self.colour_preset == self.COLOUR_CUSTOM:
            return self.custom_header_bg
        return self._COLOUR_MAP.get(self.colour_preset, {}).get(
            "header", "#ffd8fd"
        )

    @property
    def row_bg_colour(self):
        if self.colour_preset == self.COLOUR_CUSTOM:
            return self.custom_row_bg
        return self._COLOUR_MAP.get(self.colour_preset, {}).get(
            "rows", "#ffecfe"
        )

    @property
    def text_colour(self):
        if self.colour_preset == self.COLOUR_CUSTOM:
            return self.custom_text_colour or "#212129"
        return "#212129"


class RevenuePackageRow(models.Model):
    """A row in a revenue distribution package table."""

    table = models.ForeignKey(
        RevenuePackageTable,
        on_delete=models.CASCADE,
        related_name="rows",
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"Row {self.sort_order} of {self.table}"

    def get_cells_by_column(self):
        """Return a dict of {column_id: cell_value}."""
        return {cell.column_id: cell.value for cell in self.cells.all()}


class RevenuePackageCell(models.Model):
    """A single cell in a revenue distribution table."""

    row = models.ForeignKey(
        RevenuePackageRow,
        on_delete=models.CASCADE,
        related_name="cells",
    )
    column = models.ForeignKey(
        RevenueTableColumn,
        on_delete=models.CASCADE,
    )
    value = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["row", "column"],
                name="unique_revenue_cell_per_row_column",
            )
        ]

    def __str__(self):
        return self.value


@register
class TextImageCTABlock(BaseBlock):
    """Text, image and call to action block."""

    BLOCK_TYPE = "text_image_cta"
    LABEL = "Text, Image and Call to Action"
    ICON = "bi-layout-text-window"
    FORM_CLASS = "cms.forms.TextImageCTABlockForm"
    MANAGER_TEMPLATE = "cms/manager/blocks/_text_image_cta.html"
    PUBLIC_TEMPLATE = "includes/blocks/_text_image_cta.html"
    COLOR_DEFAULTS = {
        "cta_bg_color": "#000000",
        "cta_text_color": "#ffffff",
        "cta_hover_bg_color": "#000000",
        "cta_hover_text_color": "#ffffff",
        "bg_color": "#ffffff",
        "text_color": "#212129",
    }

    heading = models.CharField(max_length=255, default="Title here.")
    body = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="blocks/text_image_cta/",
        blank=True,
    )
    image_alt = models.CharField(
        max_length=255,
        default="A collection of academic journal covers from OJC publishers",
    )
    show_cta = models.BooleanField(default=True)
    cta_text = models.CharField(max_length=100, default="Join the movement")
    cta_url = models.CharField(max_length=500, blank=True)
    cta_bg_color = models.CharField(max_length=7, default="#000000")
    cta_text_color = models.CharField(max_length=7, default="#ffffff")
    cta_hover_bg_color = models.CharField(max_length=7, default="#000000")
    cta_hover_text_color = models.CharField(max_length=7, default="#ffffff")
    bg_color = models.CharField(max_length=7, default="#ffffff")
    text_color = models.CharField(max_length=7, default="#212129")

    def __str__(self):
        return f"TextImageCTABlock #{self.pk}"

    def save(self, *args, **kwargs):
        self.body = sanitize_html(self.body)
        super().save(*args, **kwargs)


@register
class WideHeaderCirclesBlock(BaseBlock):
    """Wide header with large concentric circles block."""

    BLOCK_TYPE = "wide_header_circles"
    LABEL = "Wide Header With Large Concentric Circles"
    ICON = "bi-type-h1"
    FORM_CLASS = "cms.forms.WideHeaderCirclesBlockForm"
    MANAGER_TEMPLATE = "cms/manager/blocks/_wide_header_circles.html"
    PUBLIC_TEMPLATE = "includes/blocks/_wide_header_circles.html"
    COLOR_DEFAULTS = {
        "bg_color": "#71f7f2",
        "text_color": "#212129",
        "circle_color": "#ffffff",
    }

    heading = models.CharField(
        max_length=500,
        default=(
            "Our mission is lorem ipsum dolor sit amet,"
            " consectetur ips remit et."
        ),
        help_text="Main hero heading",
    )
    sub_heading = models.TextField(
        blank=True,
        default="",
        help_text="Hero sub-heading text",
    )
    bg_color = models.CharField(max_length=7, default="#71f7f2")
    text_color = models.CharField(max_length=7, default="#212129")
    circle_color = models.CharField(max_length=7, default="#ffffff")

    def __str__(self):
        return f"WideHeaderCirclesBlock #{self.pk}"


@register
class TwoColumnContentBlock(BaseBlock):
    """Two-column content section block."""

    BLOCK_TYPE = "two_column_content"
    LABEL = "Two-Column Content Section"
    ICON = "bi-layout-split"
    FORM_CLASS = "cms.forms.TwoColumnContentBlockForm"
    MANAGER_TEMPLATE = "cms/manager/blocks/_two_column_content.html"
    PUBLIC_TEMPLATE = "includes/blocks/_two_column_content.html"
    COLOR_DEFAULTS = {
        "bg_color": "#ffffff",
        "text_color": "#212129",
    }

    section_title = models.CharField(max_length=200, default="About us.")
    col_1_title = models.CharField(max_length=200, default="Our vision.")
    col_1_body = models.TextField(blank=True)
    col_2_title = models.CharField(max_length=200, default="Our Mission.")
    col_2_body = models.TextField(blank=True)
    bg_color = models.CharField(max_length=7, default="#ffffff")
    text_color = models.CharField(max_length=7, default="#212129")

    def __str__(self):
        return f"TwoColumnContentBlock #{self.pk}"

    def save(self, *args, **kwargs):
        self.col_1_body = sanitize_html(self.col_1_body)
        self.col_2_body = sanitize_html(self.col_2_body)
        super().save(*args, **kwargs)


@register
class StatisticsBlock(BaseBlock):
    """Statistics block with 4 stat value/text pairs."""

    BLOCK_TYPE = "statistics"
    LABEL = "Statistics"
    ICON = "bi-bar-chart"
    FORM_CLASS = "cms.forms.StatisticsBlockForm"
    MANAGER_TEMPLATE = "cms/manager/blocks/_statistics.html"
    PUBLIC_TEMPLATE = "includes/blocks/_statistics.html"
    COLOR_DEFAULTS = {
        "bg_color": "#ffffff",
        "text_color": "#212129",
        "border_color": "#a5bfff",
    }

    stat_1_value = models.CharField(max_length=50, default="6")
    stat_1_text = models.TextField(blank=True)
    stat_2_value = models.CharField(max_length=50, default="60%")
    stat_2_text = models.TextField(blank=True)
    stat_3_value = models.CharField(max_length=50, default="3m")
    stat_3_text = models.TextField(blank=True)
    stat_4_value = models.CharField(max_length=50, default="300k")
    stat_4_text = models.TextField(blank=True)
    bg_color = models.CharField(max_length=7, default="#ffffff")
    text_color = models.CharField(max_length=7, default="#212129")
    border_color = models.CharField(max_length=7, default="#a5bfff")

    def __str__(self):
        return f"StatisticsBlock #{self.pk}"

    def save(self, *args, **kwargs):
        self.stat_1_text = sanitize_html(self.stat_1_text)
        self.stat_2_text = sanitize_html(self.stat_2_text)
        self.stat_3_text = sanitize_html(self.stat_3_text)
        self.stat_4_text = sanitize_html(self.stat_4_text)
        super().save(*args, **kwargs)


@register
class OrganizationCarouselBlock(BaseBlock):
    """Organization carousel block with logo-based quotes."""

    BLOCK_TYPE = "org_carousel"
    LABEL = "Organization Carousel"
    ICON = "bi-chat-quote"
    FORM_CLASS = "cms.forms.OrganizationCarouselBlockForm"
    FORMSET_CLASS = "cms.forms.OrgCarouselQuoteFormSet"
    MANAGER_TEMPLATE = "cms/manager/blocks/_org_carousel.html"
    PUBLIC_TEMPLATE = "includes/blocks/_org_carousel.html"
    COLOR_DEFAULTS = {
        "bg_color": "#a5bfff",
        "text_color": "#212129",
        "bullet_color": "#999999",
        "bullet_active_color": "#212129",
    }

    bg_color = models.CharField(max_length=7, default="#a5bfff")
    text_color = models.CharField(max_length=7, default="#212129")
    bullet_color = models.CharField(
        max_length=7,
        default="#999999",
        help_text="Carousel dot colour (unselected)",
    )
    bullet_active_color = models.CharField(
        max_length=7,
        default="#212129",
        help_text="Carousel dot colour (selected)",
    )

    def __str__(self):
        return f"OrganizationCarouselBlock #{self.pk}"

    def get_public_context(self):
        return {"org_quotes": self.quotes.all()}

    def create_children_from_config(self, children_config):
        import os

        from django.conf import settings as django_settings
        from django.core.files.base import ContentFile

        for child in children_config:
            static_image = child.pop("static_image", None)
            quote = OrgCarouselQuote.objects.create(block=self, **child)
            if static_image:
                static_path = os.path.join(
                    django_settings.BASE_DIR, static_image.lstrip("/")
                )
                if os.path.isfile(static_path):
                    ext = os.path.splitext(static_path)[1]
                    dest_name = f"blocks/org_carousel/{quote.pk}{ext}"
                    with open(static_path, "rb") as f:
                        quote.logo.save(
                            dest_name, ContentFile(f.read()), save=True
                        )


class OrgCarouselQuote(models.Model):
    """A quote in an organization carousel block."""

    block = models.ForeignKey(
        OrganizationCarouselBlock,
        on_delete=models.CASCADE,
        related_name="quotes",
    )
    logo = models.ImageField(
        upload_to="blocks/org_carousel/",
        blank=True,
        help_text="Organization logo image",
    )
    quote_text = models.TextField()
    author_name = models.CharField(max_length=255)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.author_name

    def save(self, *args, **kwargs):
        self.quote_text = sanitize_html(self.quote_text)
        super().save(*args, **kwargs)


class PageBlock(models.Model):
    """Junction model linking a concrete block to any singleton page."""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    page_id = models.PositiveIntegerField()
    page = GenericForeignKey("content_type", "page_id")
    block_type = models.CharField(max_length=30)
    object_id = models.PositiveIntegerField()
    sort_order = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]
        indexes = [models.Index(fields=["content_type", "page_id"])]

    def __str__(self):
        try:
            label = get_label(self.block_type)
        except KeyError:
            label = self.block_type
        return f"{label} (order={self.sort_order})"

    def get_block(self):
        try:
            model_cls = get_block_class(self.block_type)
        except KeyError:
            return None
        try:
            return model_cls.objects.get(pk=self.object_id)
        except model_cls.DoesNotExist:
            return None


# Backward-compatible alias (old migrations reference MembersPageBlock)
MembersPageBlock = PageBlock
