"""
Model translation registration for CMS models.

Registers translatable fields so django-modeltranslation creates
per-language columns (e.g. title_en, title_fr) automatically.
"""

from modeltranslation.translator import TranslationOptions, register

from cms.models import (
    AboutUsPageSettings,
    AboutUsQuote,
    BoardMember,
    BoardSection,
    FooterLink,
    FooterSettings,
    HeaderSettings,
    LandingPageSettings,
    MenuItem,
    OurModelPackageCell,
    OurModelPackageTable,
    OurModelPageSettings,
    OurModelTableColumn,
    Page,
    Post,
    Snippet,
    TeamMember,
    TeamSection,
)


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


@register(OurModelPageSettings)
class OurModelPageSettingsTranslationOptions(TranslationOptions):
    fields = (
        "hero_heading",
        "hero_image_alt",
        "model_heading",
        "model_body",
        "collections_label",
        "collection_1_title",
        "collection_1_link_text",
        "collection_2_title",
        "collection_2_link_text",
        "collection_3_title",
        "collection_3_link_text",
        "funding_heading",
        "funding_upper_image_alt",
        "funding_lower_image_alt",
        "funding_body",
        "revenue_heading",
        "revenue_description",
        "revenue_callout",
        "cta_heading",
        "cta_description",
        "cta_button_text",
        "cta_image_alt",
    )


@register(OurModelTableColumn)
class OurModelTableColumnTranslationOptions(TranslationOptions):
    fields = ("heading",)


@register(OurModelPackageTable)
class OurModelPackageTableTranslationOptions(TranslationOptions):
    fields = ("title", "description")


@register(OurModelPackageCell)
class OurModelPackageCellTranslationOptions(TranslationOptions):
    fields = ("value",)


@register(BoardSection)
class BoardSectionTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(BoardMember)
class BoardMemberTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(TeamSection)
class TeamSectionTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(TeamMember)
class TeamMemberTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(AboutUsPageSettings)
class AboutUsPageSettingsTranslationOptions(TranslationOptions):
    fields = (
        "hero_heading",
        "hero_sub",
        "section_title",
        "col_1_title",
        "col_1_body",
        "col_2_title",
        "col_2_body",
        "stat_1_value",
        "stat_1_text",
        "stat_2_value",
        "stat_2_text",
        "stat_3_value",
        "stat_3_text",
        "stat_4_value",
        "stat_4_text",
    )


@register(AboutUsQuote)
class AboutUsQuoteTranslationOptions(TranslationOptions):
    fields = ("quote_text", "author_name")
