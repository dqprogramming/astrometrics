"""
CMS models for translatable rich-text content pages and snippets.
"""

import uuid

import bleach
from django.core.cache import cache
from django.db import models
from django.utils import timezone
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


class OurModelPageSettings(models.Model):
    """Singleton model for the Our Model page content.

    Only one row should exist — use OurModelPageSettings.load() to
    fetch-or-create it.
    """

    # URL
    slug = models.SlugField(
        default="our-model",
        help_text="URL slug for the page",
    )

    # Hero section
    hero_heading = models.TextField(
        help_text="Main hero heading — may contain <span class='highlight'> markup (translatable)",
    )
    hero_image_alt = models.CharField(
        max_length=255,
        default="",
        help_text="Alt text for the hero image (translatable)",
    )

    # OJC Model section
    model_heading = models.CharField(
        max_length=255,
        help_text="OJC Model section heading (translatable)",
    )
    model_body = models.TextField(
        blank=True,
        help_text="OJC Model section body — rich text (translatable)",
    )
    collections_label = models.TextField(
        blank=True,
        help_text="Label above collection cards (translatable)",
    )

    # Collection 1
    collection_1_number = models.CharField(max_length=10, default="01")
    collection_1_title = models.CharField(
        max_length=255, help_text="Collection 1 title (translatable)"
    )
    collection_1_link_text = models.CharField(
        max_length=100,
        default="BROWSE JOURNALS",
        help_text="Collection 1 link label (translatable)",
    )
    collection_1_link_url = models.CharField(max_length=500, blank=True)

    # Collection 2
    collection_2_number = models.CharField(max_length=10, default="02")
    collection_2_title = models.CharField(
        max_length=255, help_text="Collection 2 title (translatable)"
    )
    collection_2_link_text = models.CharField(
        max_length=100,
        default="BROWSE JOURNALS",
        help_text="Collection 2 link label (translatable)",
    )
    collection_2_link_url = models.CharField(max_length=500, blank=True)

    # Collection 3
    collection_3_number = models.CharField(max_length=10, default="03")
    collection_3_title = models.CharField(
        max_length=255, help_text="Collection 3 title (translatable)"
    )
    collection_3_link_text = models.CharField(
        max_length=100,
        default="BROWSE JOURNALS",
        help_text="Collection 3 link label (translatable)",
    )
    collection_3_link_url = models.CharField(max_length=500, blank=True)

    # Funding section
    funding_heading = models.CharField(
        max_length=255, help_text="Funding section heading (translatable)"
    )
    funding_upper_image_alt = models.CharField(
        max_length=255,
        default="",
        help_text="Alt text for upper funding image (translatable)",
    )
    funding_lower_image_alt = models.CharField(
        max_length=255,
        default="",
        help_text="Alt text for lower funding image (translatable)",
    )
    funding_body = models.TextField(
        blank=True,
        help_text="Funding section body — rich text (translatable)",
    )

    # Revenue section
    revenue_heading = models.CharField(
        max_length=255,
        help_text="Revenue distribution heading (translatable)",
    )
    revenue_description = models.TextField(
        blank=True,
        help_text="Revenue description — plain text (translatable)",
    )
    revenue_callout = models.TextField(
        blank=True,
        help_text="Revenue callout text (translatable)",
    )

    # CTA section
    cta_heading = models.CharField(
        max_length=255, help_text="CTA heading (translatable)"
    )
    cta_description = models.TextField(
        blank=True,
        help_text="CTA description — rich text (translatable)",
    )
    cta_button_text = models.CharField(
        max_length=100, help_text="CTA button label (translatable)"
    )
    cta_button_url = models.CharField(max_length=500, blank=True)
    cta_button_visible = models.BooleanField(default=True)
    cta_image_alt = models.CharField(
        max_length=255,
        default="",
        help_text="Alt text for CTA image (translatable)",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Our Model Page Settings")
        verbose_name_plural = _("Our Model Page Settings")

    def __str__(self):
        return "Our Model Page Settings"

    CACHE_KEY = "our_model_page_settings"
    CACHE_TTL = 60 * 60  # 1 hour

    @classmethod
    def load(cls):
        """Return the singleton instance, serving from cache when possible."""
        obj = cache.get(cls.CACHE_KEY)
        if obj is None:
            obj, _created = cls.objects.get_or_create(pk=1)
            # Prefetch related data for template rendering
            columns = list(obj.table_columns.order_by("sort_order"))
            tables = list(
                obj.package_tables.prefetch_related("rows__cells").order_by(
                    "sort_order"
                )
            )
            obj._prefetched_columns = columns
            obj._prefetched_tables = tables
            cache.set(cls.CACHE_KEY, obj, cls.CACHE_TTL)
        return obj

    def get_table_columns(self):
        if hasattr(self, "_prefetched_columns"):
            return self._prefetched_columns
        return list(self.table_columns.order_by("sort_order"))

    def get_package_tables(self):
        if hasattr(self, "_prefetched_tables"):
            return self._prefetched_tables
        return list(
            self.package_tables.prefetch_related("rows__cells").order_by(
                "sort_order"
            )
        )

    def save(self, *args, **kwargs):
        self.pk = 1
        self.model_body = sanitize_html(self.model_body)
        self.funding_body = sanitize_html(self.funding_body)
        self.cta_description = sanitize_html(self.cta_description)
        super().save(*args, **kwargs)
        cache.delete(self.CACHE_KEY)

    def delete(self, *args, **kwargs):
        pass


class OurModelTableColumn(models.Model):
    """Column header shared across all package tables."""

    settings = models.ForeignKey(
        OurModelPageSettings,
        related_name="table_columns",
        on_delete=models.CASCADE,
    )
    heading = models.CharField(
        max_length=100, help_text="Column heading (translatable)"
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.heading

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(OurModelPageSettings.CACHE_KEY)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete(OurModelPageSettings.CACHE_KEY)


class OurModelPackageTable(models.Model):
    """A colour-coded package table in the revenue distribution section."""

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

    settings = models.ForeignKey(
        OurModelPageSettings,
        related_name="package_tables",
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        max_length=255, help_text="Table title (translatable)"
    )
    description = models.TextField(
        blank=True, help_text="Table description (translatable)"
    )
    colour_preset = models.CharField(
        max_length=10, choices=COLOUR_CHOICES, default=COLOUR_PINK
    )
    custom_header_bg = models.CharField(
        max_length=7,
        blank=True,
        help_text="Hex colour for header (custom only)",
    )
    custom_row_bg = models.CharField(
        max_length=7, blank=True, help_text="Hex colour for rows (custom only)"
    )
    custom_text_colour = models.CharField(
        max_length=7, blank=True, help_text="Hex colour for text (custom only)"
    )
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(OurModelPageSettings.CACHE_KEY)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete(OurModelPageSettings.CACHE_KEY)


class OurModelPackageRow(models.Model):
    """A row in a package table. Cell values are stored in OurModelPackageCell."""

    table = models.ForeignKey(
        OurModelPackageTable,
        related_name="rows",
        on_delete=models.CASCADE,
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"Row {self.sort_order} of {self.table}"

    def get_cells_by_column(self):
        """Return a dict of {column_id: cell_value}."""
        return {cell.column_id: cell.value for cell in self.cells.all()}

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(OurModelPageSettings.CACHE_KEY)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete(OurModelPageSettings.CACHE_KEY)


class OurModelPackageCell(models.Model):
    """A single cell value at the intersection of a row and a column."""

    row = models.ForeignKey(
        OurModelPackageRow,
        related_name="cells",
        on_delete=models.CASCADE,
    )
    column = models.ForeignKey(
        OurModelTableColumn,
        on_delete=models.CASCADE,
    )
    value = models.CharField(
        max_length=255, blank=True, help_text="Cell value (translatable)"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["row", "column"],
                name="unique_cell_per_row_column",
            )
        ]

    def __str__(self):
        return self.value

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(OurModelPageSettings.CACHE_KEY)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete(OurModelPageSettings.CACHE_KEY)


class TeamSection(models.Model):
    """A section grouping team members (e.g. Directors, Executive, Staff)."""

    name = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = _("Team Section")
        verbose_name_plural = _("Team Sections")

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    """A team member belonging to a section."""

    section = models.ForeignKey(
        TeamSection,
        related_name="members",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    linkedin_url = models.CharField(max_length=500, blank=True)
    image = models.CharField(max_length=500, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.description = sanitize_html(self.description)
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
