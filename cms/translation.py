"""
Model translation registration for CMS models.

Registers translatable fields so django-modeltranslation creates
per-language columns (e.g. title_en, title_fr) automatically.
"""

from modeltranslation.translator import TranslationOptions, register

from cms.models import LandingPageSettings, Page, Post, Snippet


@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ("title", "body", "meta_description")


@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ("title", "summary", "body", "meta_description")


@register(LandingPageSettings)
class LandingPageSettingsTranslationOptions(TranslationOptions):
    fields = (
        "hero_heading",
        "hero_subheading",
        "hero_button_text",
        "feature_1_title",
        "feature_1_text",
        "feature_1_button_text",
        "feature_2_title",
        "feature_2_text",
        "feature_2_button_text",
        "feature_3_title",
        "feature_3_text",
        "feature_3_button_text",
        "stats_description",
        "stats_button_1_text",
        "stats_button_2_text",
    )


@register(Snippet)
class SnippetTranslationOptions(TranslationOptions):
    fields = ("name", "body")
