"""
Model translation registration for CMS models.

Registers translatable fields so django-modeltranslation creates
per-language columns (e.g. title_en, title_fr) automatically.
"""

from modeltranslation.translator import TranslationOptions, register

from cms.models import (
    FooterLink,
    FooterSettings,
    HeaderSettings,
    MenuItem,
    Page,
    Post,
    Snippet,
)


@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ("title", "body", "meta_description")


@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ("title", "summary", "body", "meta_description")


@register(FooterSettings)
class FooterSettingsTranslationOptions(TranslationOptions):
    fields = (
        "tagline_1",
        "tagline_2",
        "tagline_3",
        "column_1_heading",
        "column_2_heading",
        "legal_text",
    )


@register(FooterLink)
class FooterLinkTranslationOptions(TranslationOptions):
    fields = ("label",)


@register(HeaderSettings)
class HeaderSettingsTranslationOptions(TranslationOptions):
    fields = ("logo_line_1", "logo_line_2", "logo_line_3", "cta_label")


@register(MenuItem)
class MenuItemTranslationOptions(TranslationOptions):
    fields = ("label", "cta_text")


@register(Snippet)
class SnippetTranslationOptions(TranslationOptions):
    fields = ("name", "body")
