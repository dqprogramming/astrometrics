"""
Admin configuration for CMS models with translation support.
"""

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from modeltranslation.admin import TranslationAdmin

from cms.block_registry import _registry as _block_registry
from cms.models import (
    BlockPage,
    BlockPageTemplate,
    Category,
    ContactFormRecipient,
    FooterLink,
    FooterSettings,
    HeaderSettings,
    InstitutionEntry,
    MenuItem,
    OrgCarouselQuote,
    Page,
    PageBlock,
    PeopleListPerson,
    PersonCarouselQuote,
    Post,
    RevenuePackageCell,
    RevenuePackageRow,
    RevenuePackageTable,
    RevenueTableColumn,
    Snippet,
)


@admin.register(Page)
class PageAdmin(TranslationAdmin):
    list_display = [
        "title",
        "slug",
        "is_published",
        "sort_order",
        "updated_at",
    ]
    list_filter = ["is_published"]
    search_fields = ["title", "slug", "body"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("title", "slug", "body")}),
        (
            "SEO",
            {"fields": ("meta_description",)},
        ),
        (
            "Publishing",
            {"fields": ("is_published", "sort_order")},
        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Post)
class PostAdmin(TranslationAdmin):
    list_display = [
        "title",
        "byline",
        "is_published",
        "published_at",
        "updated_at",
    ]
    list_filter = ["is_published", "published_at"]
    search_fields = ["title", "slug", "summary", "body", "byline"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "published_at"
    fieldsets = (
        (None, {"fields": ("title", "slug", "summary", "body")}),
        (
            "SEO",
            {"fields": ("meta_description",)},
        ),
        (
            "Publishing",
            {"fields": ("byline", "is_published", "published_at")},
        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 1


@admin.register(FooterSettings)
class FooterSettingsAdmin(TranslationAdmin):
    inlines = [FooterLinkInline]


@admin.register(FooterLink)
class FooterLinkAdmin(TranslationAdmin):
    list_display = ["label", "column", "url", "sort_order"]
    list_filter = ["column"]


@admin.register(Snippet)
class SnippetAdmin(TranslationAdmin):
    list_display = ["name", "key", "updated_at"]
    search_fields = ["name", "key", "body"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    fk_name = "header"
    extra = 1
    fields = ["label", "url", "parent", "sort_order"]


@admin.register(HeaderSettings)
class HeaderSettingsAdmin(TranslationAdmin):
    list_display = ["pk", "updated_at"]
    inlines = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(TranslationAdmin):
    list_display = ["label", "url", "parent", "sort_order"]
    list_filter = ["header"]
    search_fields = ["label", "url"]


class PageBlockInline(GenericTabularInline):
    model = PageBlock
    ct_field = "content_type"
    ct_fk_field = "page_id"
    extra = 0
    fields = ["block_type", "object_id", "sort_order", "is_visible"]
    ordering = ["sort_order"]


@admin.register(BlockPage)
class BlockPageAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "is_landing_page",
        "template_key",
        "updated_at",
    ]
    list_filter = ["is_landing_page", "template_key"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PageBlockInline]


@admin.register(BlockPageTemplate)
class BlockPageTemplateAdmin(admin.ModelAdmin):
    list_display = ["key", "name"]
    search_fields = ["key", "name"]


@admin.register(PageBlock)
class PageBlockAdmin(admin.ModelAdmin):
    list_display = [
        "block_type",
        "page_id",
        "object_id",
        "sort_order",
        "is_visible",
    ]
    list_filter = ["block_type", "is_visible", "content_type"]
    search_fields = ["block_type"]


# ── Block child models ─────────────────────────────────────────────────────


@admin.register(PersonCarouselQuote)
class PersonCarouselQuoteAdmin(admin.ModelAdmin):
    list_display = ["author_name", "block", "sort_order"]
    list_filter = ["block"]
    search_fields = ["author_name", "quote_text"]


@admin.register(PeopleListPerson)
class PeopleListPersonAdmin(admin.ModelAdmin):
    list_display = ["name", "block", "sort_order"]
    list_filter = ["block"]
    search_fields = ["name", "description"]


@admin.register(InstitutionEntry)
class InstitutionEntryAdmin(admin.ModelAdmin):
    list_display = ["name", "block", "sort_order"]
    list_filter = ["block"]
    search_fields = ["name"]


@admin.register(RevenueTableColumn)
class RevenueTableColumnAdmin(admin.ModelAdmin):
    list_display = ["heading", "block", "sort_order"]
    list_filter = ["block"]
    search_fields = ["heading"]


@admin.register(RevenuePackageTable)
class RevenuePackageTableAdmin(admin.ModelAdmin):
    list_display = ["title", "block"]
    list_filter = ["block"]
    search_fields = ["title", "description"]


@admin.register(RevenuePackageRow)
class RevenuePackageRowAdmin(admin.ModelAdmin):
    list_display = ["__str__", "table", "sort_order"]
    list_filter = ["table"]


@admin.register(RevenuePackageCell)
class RevenuePackageCellAdmin(admin.ModelAdmin):
    list_display = ["row", "column", "value"]
    list_filter = ["row__table", "column"]
    search_fields = ["value"]


@admin.register(OrgCarouselQuote)
class OrgCarouselQuoteAdmin(admin.ModelAdmin):
    list_display = ["author_name", "block", "sort_order"]
    list_filter = ["block"]
    search_fields = ["author_name", "quote_text"]


@admin.register(ContactFormRecipient)
class ContactFormRecipientAdmin(admin.ModelAdmin):
    list_display = ["email", "block", "sort_order"]
    list_filter = ["block"]
    search_fields = ["email"]


# ── Block models (auto-registered from registry) ───────────────────────────
#
# Each concrete BaseBlock subclass gets a default ModelAdmin so it shows up
# in /admin/ for inspection. Day-to-day editing happens via the bespoke CMS
# manager UI, but admin access is useful for ops and debugging.
def _register_block_admins():
    for cls in _block_registry.values():
        if admin.site.is_registered(cls):
            continue
        admin.site.register(cls)


_register_block_admins()
