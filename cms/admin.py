"""
Admin configuration for CMS models with translation support.
"""

from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from cms.models import Page, Post, Snippet


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


@admin.register(Snippet)
class SnippetAdmin(TranslationAdmin):
    list_display = ["name", "key", "updated_at"]
    search_fields = ["name", "key", "body"]
    readonly_fields = ["created_at", "updated_at"]
