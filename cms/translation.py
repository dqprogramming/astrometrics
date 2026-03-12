"""
Model translation registration for CMS models.

Registers translatable fields so django-modeltranslation creates
per-language columns (e.g. title_en, title_fr) automatically.
"""

from modeltranslation.translator import TranslationOptions, register

from cms.models import Page, Post, Snippet


@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ("title", "body", "meta_description")


@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ("title", "summary", "body", "meta_description")


@register(Snippet)
class SnippetTranslationOptions(TranslationOptions):
    fields = ("name", "body")
