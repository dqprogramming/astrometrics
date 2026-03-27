from django import forms
from tinymce.widgets import TinyMCE

from .models import (
    BlockPage,
    BlockPageTemplate,
    Category,
    ContactFormBlock,
    ContactFormRecipient,
    FeatureCardsBlock,
    FooterLink,
    FooterSettings,
    FreeAccessJournalsBlock,
    HeaderSettings,
    InstitutionEntry,
    JournalFundingBlock,
    LandingHeroBlock,
    LandingPageSettings,
    LandingStatsBlock,
    ManifestoHeroBlock,
    ManifestoOrganiseBlock,
    ManifestoTextBlock,
    MembersHeaderBlock,
    MembersInstitutionsBlock,
    MenuItem,
    OJCModelBlock,
    OrganizationCarouselBlock,
    OrgCarouselQuote,
    OurModelHeroBlock,
    Page,
    PeopleListBlock,
    PeopleListPerson,
    PersonCarouselBlock,
    PersonCarouselQuote,
    Post,
    RevenueDistributionBlock,
    RevenuePackageTable,
    RevenueTableColumn,
    Snippet,
    StatisticsBlock,
    TextImageCTABlock,
    TwoColumnContentBlock,
    WhoWeAreBlock,
    WideHeaderCirclesBlock,
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mgr-input"}),
        }


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = [
            "title",
            "slug",
            "body",
            "meta_description",
            "is_published",
            "sort_order",
            "hero_bg",
            "hero_arc_position",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "mgr-input"}),
            "slug": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "auto-generated from title if left blank",
                }
            ),
            "body": TinyMCE(),
            "meta_description": forms.TextInput(attrs={"class": "mgr-input"}),
            "sort_order": forms.NumberInput(
                attrs={"class": "mgr-input", "style": "max-width:120px;"}
            ),
            "hero_bg": forms.Select(attrs={"class": "mgr-input"}),
            "hero_arc_position": forms.Select(attrs={"class": "mgr-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "slug",
            "summary",
            "body",
            "byline",
            "meta_description",
            "featured_image",
            "is_published",
            "published_at",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "mgr-input"}),
            "slug": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "auto-generated from title if left blank",
                }
            ),
            "summary": TinyMCE(attrs={"rows": 6}),
            "body": TinyMCE(),
            "byline": forms.TextInput(attrs={"class": "mgr-input"}),
            "meta_description": forms.TextInput(attrs={"class": "mgr-input"}),
            "featured_image": forms.HiddenInput(),
            "published_at": forms.DateTimeInput(
                attrs={"class": "mgr-input", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["published_at"].input_formats = ["%Y-%m-%dT%H:%M"]


class LandingPageSettingsForm(forms.ModelForm):
    class Meta:
        model = LandingPageSettings
        fields = [
            "hero_heading",
            "hero_subheading",
            "hero_button_text",
            "hero_button_url",
            "feature_1_title",
            "feature_1_text",
            "feature_1_button_text",
            "feature_1_button_url",
            "feature_2_title",
            "feature_2_text",
            "feature_2_button_text",
            "feature_2_button_url",
            "feature_3_title",
            "feature_3_text",
            "feature_3_button_text",
            "feature_3_button_url",
            "stats_fundraising_target",
            "stats_amount_raised",
            "stats_description",
            "stats_button_1_text",
            "stats_button_1_url",
            "stats_button_2_text",
            "stats_button_2_url",
        ]
        widgets = {
            "hero_heading": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "hero_subheading": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "hero_button_text": forms.TextInput(attrs={"class": "mgr-input"}),
            "hero_button_url": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "e.g. mailto:info@example.org or https://...",
                }
            ),
            "feature_1_title": forms.TextInput(attrs={"class": "mgr-input"}),
            "feature_1_text": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 4}
            ),
            "feature_1_button_text": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "feature_1_button_url": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "feature_2_title": forms.TextInput(attrs={"class": "mgr-input"}),
            "feature_2_text": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 4}
            ),
            "feature_2_button_text": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "feature_2_button_url": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "feature_3_title": forms.TextInput(attrs={"class": "mgr-input"}),
            "feature_3_text": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 4}
            ),
            "feature_3_button_text": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "feature_3_button_url": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "stats_fundraising_target": forms.NumberInput(
                attrs={"class": "mgr-input", "style": "max-width:200px;"}
            ),
            "stats_amount_raised": forms.NumberInput(
                attrs={"class": "mgr-input", "style": "max-width:200px;"}
            ),
            "stats_description": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "stats_button_1_text": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "stats_button_1_url": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "stats_button_2_text": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "stats_button_2_url": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
        }


class FooterSettingsForm(forms.ModelForm):
    class Meta:
        model = FooterSettings
        fields = [
            "tagline_1",
            "tagline_2",
            "tagline_3",
            "column_1_heading",
            "column_2_heading",
            "legal_text",
        ]
        widgets = {
            "tagline_1": forms.TextInput(attrs={"class": "mgr-input"}),
            "tagline_2": forms.TextInput(attrs={"class": "mgr-input"}),
            "tagline_3": forms.TextInput(attrs={"class": "mgr-input"}),
            "column_1_heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "column_2_heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "legal_text": TinyMCE(
                attrs={"aria-label": "Legal text"},
                mce_attrs={
                    "height": 200,
                    "menubar": False,
                    "plugins": "link",
                    "toolbar": ("bold italic underline | link"),
                },
            ),
        }


class FooterLinkForm(forms.ModelForm):
    class Meta:
        model = FooterLink
        fields = ["label", "url", "sort_order"]
        widgets = {
            "label": forms.TextInput(
                attrs={"class": "mgr-input", "aria-label": "Link label"}
            ),
            "url": forms.TextInput(
                attrs={"class": "mgr-input", "aria-label": "Link URL"}
            ),
            "sort_order": forms.HiddenInput(),
        }


Column1LinkFormSet = forms.inlineformset_factory(
    FooterSettings,
    FooterLink,
    form=FooterLinkForm,
    extra=0,
    can_delete=True,
)

Column2LinkFormSet = forms.inlineformset_factory(
    FooterSettings,
    FooterLink,
    form=FooterLinkForm,
    extra=0,
    can_delete=True,
)


class HeaderSettingsForm(forms.ModelForm):
    class Meta:
        model = HeaderSettings
        fields = [
            "logo_line_1",
            "logo_line_2",
            "logo_line_3",
            "cta_label",
            "cta_url",
            "show_mobile_sub_items",
        ]
        widgets = {
            "logo_line_1": forms.TextInput(attrs={"class": "mgr-input"}),
            "logo_line_2": forms.TextInput(attrs={"class": "mgr-input"}),
            "logo_line_3": forms.TextInput(attrs={"class": "mgr-input"}),
            "cta_label": forms.TextInput(attrs={"class": "mgr-input"}),
            "cta_url": forms.TextInput(attrs={"class": "mgr-input"}),
        }


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = [
            "label",
            "url",
            "sort_order",
            "parent",
            "show_cta_in_dropdown",
            "cta_text",
            "cta_url",
        ]
        widgets = {
            "label": forms.TextInput(
                attrs={"class": "mgr-input", "aria-label": "Menu item label"}
            ),
            "url": forms.TextInput(
                attrs={"class": "mgr-input", "aria-label": "Menu item URL"}
            ),
            "sort_order": forms.HiddenInput(),
            "parent": forms.HiddenInput(),
            "cta_text": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "aria-label": "Call-to-action button text",
                    "placeholder": "Call to action display name",
                }
            ),
            "cta_url": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "aria-label": "Call-to-action button URL",
                    "placeholder": "Call to action URL",
                }
            ),
        }


MenuItemFormSet = forms.inlineformset_factory(
    HeaderSettings,
    MenuItem,
    form=MenuItemForm,
    extra=0,
    can_delete=True,
)


class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ["name", "key", "body"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mgr-input"}),
            "key": forms.TextInput(
                attrs={"class": "mgr-input", "placeholder": "e.g. footer-cta"}
            ),
            "body": TinyMCE(),
        }


_RESTRICTED_TINYMCE = {
    "height": 200,
    "menubar": False,
    "plugins": "",
    "toolbar": "bold italic underline",
}


_MANIFESTO_TINYMCE = {
    "height": 200,
    "menubar": False,
    "plugins": "",
    "toolbar": "bold italic underline | sub sup",
}


_ABOUT_US_TINYMCE = {
    "height": 200,
    "menubar": False,
    "plugins": "",
    "toolbar": "bold italic underline | sub sup",
    "valid_elements": "p,br,strong/b,em/i,u,sub,sup",
    "invalid_elements": "script,iframe,object,embed,form,input",
    "formats": {
        "underline": {"inline": "u"},
    },
}


# ── Block System Forms ───────────────────────────────────────────────────────

_COLOR_ATTRS = {
    "type": "color",
    "class": "mgr-color-input",
}


class MembersHeaderBlockForm(forms.ModelForm):
    class Meta:
        model = MembersHeaderBlock
        fields = ["heading", "bg_color", "text_color"]
        widgets = {
            "heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class WhoWeAreBlockForm(forms.ModelForm):
    class Meta:
        model = WhoWeAreBlock
        fields = [
            "section_heading",
            "circle_1_title",
            "circle_1_body",
            "circle_2_title",
            "circle_2_body",
            "circle_3_title",
            "circle_3_body",
            "bg_color",
            "text_color",
            "show_cta",
            "cta_text",
            "cta_url",
        ]
        widgets = {
            "section_heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "circle_1_title": forms.TextInput(attrs={"class": "mgr-input"}),
            "circle_1_body": TinyMCE(mce_attrs=_ABOUT_US_TINYMCE),
            "circle_2_title": forms.TextInput(attrs={"class": "mgr-input"}),
            "circle_2_body": TinyMCE(mce_attrs=_ABOUT_US_TINYMCE),
            "circle_3_title": forms.TextInput(attrs={"class": "mgr-input"}),
            "circle_3_body": TinyMCE(mce_attrs=_ABOUT_US_TINYMCE),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_text": forms.TextInput(attrs={"class": "mgr-input"}),
            "cta_url": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "e.g. /contact/ or https://...",
                }
            ),
        }


class PersonCarouselBlockForm(forms.ModelForm):
    class Meta:
        model = PersonCarouselBlock
        fields = [
            "bg_color",
            "text_color",
            "bullet_color",
            "bullet_active_color",
        ]
        widgets = {
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "bullet_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "bullet_active_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class PersonCarouselQuoteForm(forms.ModelForm):
    class Meta:
        model = PersonCarouselQuote
        fields = ["image", "quote_text", "author_name", "sort_order"]
        widgets = {
            "quote_text": TinyMCE(
                attrs={"class": "quote-tinymce"},
                mce_attrs=_ABOUT_US_TINYMCE,
            ),
            "author_name": forms.TextInput(attrs={"class": "mgr-input"}),
            "sort_order": forms.HiddenInput(),
        }


PersonCarouselQuoteFormSet = forms.inlineformset_factory(
    PersonCarouselBlock,
    PersonCarouselQuote,
    form=PersonCarouselQuoteForm,
    extra=0,
    can_delete=True,
)


class PeopleListBlockForm(forms.ModelForm):
    class Meta:
        model = PeopleListBlock
        fields = ["name", "bg_color", "text_color", "card_bg_color"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mgr-input"}),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "card_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class PeopleListPersonForm(forms.ModelForm):
    class Meta:
        model = PeopleListPerson
        fields = ["name", "description", "linkedin_url", "image", "sort_order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mgr-input"}),
            "description": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "linkedin_url": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "https://linkedin.com/in/...",
                }
            ),
            "sort_order": forms.HiddenInput(),
        }


PeopleListPersonFormSet = forms.inlineformset_factory(
    PeopleListBlock,
    PeopleListPerson,
    form=PeopleListPersonForm,
    extra=0,
    can_delete=True,
)


class MembersInstitutionsBlockForm(forms.ModelForm):
    class Meta:
        model = MembersInstitutionsBlock
        fields = [
            "heading",
            "bg_color",
            "text_color",
            "show_cta",
            "cta_text",
            "cta_url",
        ]
        widgets = {
            "heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_text": forms.TextInput(attrs={"class": "mgr-input"}),
            "cta_url": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "e.g. /contact/ or https://...",
                }
            ),
        }


class InstitutionEntryForm(forms.ModelForm):
    class Meta:
        model = InstitutionEntry
        fields = ["name", "sort_order"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "mgr-input", "aria-label": "Institution name"}
            ),
            "sort_order": forms.HiddenInput(),
        }


InstitutionEntryFormSet = forms.inlineformset_factory(
    MembersInstitutionsBlock,
    InstitutionEntry,
    form=InstitutionEntryForm,
    extra=0,
    can_delete=True,
)


# ── Block Page Forms ──────────────────────────────────────────────────────


class BlockPageForm(forms.ModelForm):
    class Meta:
        model = BlockPage
        fields = ["name", "slug"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mgr-input"}),
            "slug": forms.TextInput(attrs={"class": "mgr-input"}),
        }


class BlockPageCreateForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"class": "mgr-input"}),
    )
    template = forms.CharField(
        required=False,
        widget=forms.Select(attrs={"class": "mgr-input"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [("", "Empty block page")]
        choices += [(t.key, t.name) for t in BlockPageTemplate.objects.all()]
        self.fields["template"].widget.choices = choices


class ManifestoHeroBlockForm(forms.ModelForm):
    class Meta:
        model = ManifestoHeroBlock
        fields = [
            "heading",
            "sub_heading",
            "hero_image",
            "hero_image_alt",
            "bg_color",
            "text_color",
        ]
        widgets = {
            "heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "sub_heading": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "hero_image_alt": forms.TextInput(attrs={"class": "mgr-input"}),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class ManifestoTextBlockForm(forms.ModelForm):
    class Meta:
        model = ManifestoTextBlock
        fields = ["body", "bg_color", "text_color"]
        widgets = {
            "body": TinyMCE(mce_attrs=_MANIFESTO_TINYMCE),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class ManifestoOrganiseBlockForm(forms.ModelForm):
    class Meta:
        model = ManifestoOrganiseBlock
        fields = [
            "organise_heading",
            "organise_body",
            "achievable_heading",
            "achievable_body",
            "show_cta",
            "cta_text",
            "cta_url",
            "cta_bg_color",
            "cta_text_color",
            "cta_hover_bg_color",
            "cta_hover_text_color",
            "bg_color",
            "text_color",
        ]
        widgets = {
            "organise_heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "organise_body": TinyMCE(mce_attrs=_MANIFESTO_TINYMCE),
            "achievable_heading": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "achievable_body": TinyMCE(mce_attrs=_MANIFESTO_TINYMCE),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_hover_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_hover_text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_text": forms.TextInput(attrs={"class": "mgr-input"}),
            "cta_url": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "e.g. /contact/ or https://...",
                }
            ),
        }


class FreeAccessJournalsBlockForm(forms.ModelForm):
    class Meta:
        model = FreeAccessJournalsBlock
        fields = [
            "heading",
            "image",
            "image_alt",
            "show_cta",
            "cta_text",
            "cta_url",
            "cta_bg_color",
            "cta_text_color",
            "cta_hover_bg_color",
            "cta_hover_text_color",
            "bg_color",
            "text_color",
        ]
        widgets = {
            "heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "image_alt": forms.TextInput(attrs={"class": "mgr-input"}),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_hover_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_hover_text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_text": forms.TextInput(attrs={"class": "mgr-input"}),
            "cta_url": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "e.g. /contact/ or https://...",
                }
            ),
        }


class OurModelHeroBlockForm(forms.ModelForm):
    class Meta:
        model = OurModelHeroBlock
        fields = [
            "heading",
            "hero_image",
            "hero_image_alt",
            "circle_color",
            "bg_color",
            "text_color",
        ]
        widgets = {
            "heading": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "hero_image_alt": forms.TextInput(attrs={"class": "mgr-input"}),
            "circle_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class OJCModelBlockForm(forms.ModelForm):
    class Meta:
        model = OJCModelBlock
        fields = [
            "heading",
            "body",
            "collections_label",
            "collection_1_number",
            "collection_1_title",
            "collection_1_link_text",
            "collection_1_link_url",
            "collection_2_number",
            "collection_2_title",
            "collection_2_link_text",
            "collection_2_link_url",
            "collection_3_number",
            "collection_3_title",
            "collection_3_link_text",
            "collection_3_link_url",
            "circle_bg_color",
            "circle_text_color",
            "bg_color",
            "text_color",
        ]
        widgets = {
            "heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "body": TinyMCE(
                attrs={"aria-label": "OJC Model body"},
                mce_attrs=_RESTRICTED_TINYMCE,
            ),
            "collections_label": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 2}
            ),
            "collection_1_number": forms.TextInput(
                attrs={"class": "mgr-input", "style": "max-width:80px;"}
            ),
            "collection_1_title": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "collection_1_link_text": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "collection_1_link_url": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "collection_2_number": forms.TextInput(
                attrs={"class": "mgr-input", "style": "max-width:80px;"}
            ),
            "collection_2_title": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "collection_2_link_text": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "collection_2_link_url": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "collection_3_number": forms.TextInput(
                attrs={"class": "mgr-input", "style": "max-width:80px;"}
            ),
            "collection_3_title": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "collection_3_link_text": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "collection_3_link_url": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "circle_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "circle_text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class JournalFundingBlockForm(forms.ModelForm):
    class Meta:
        model = JournalFundingBlock
        fields = [
            "heading",
            "body",
            "upper_image",
            "upper_image_alt",
            "lower_image",
            "lower_image_alt",
            "bg_color",
            "text_color",
        ]
        widgets = {
            "heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "body": TinyMCE(
                attrs={"aria-label": "Funding body"},
                mce_attrs=_RESTRICTED_TINYMCE,
            ),
            "upper_image_alt": forms.TextInput(attrs={"class": "mgr-input"}),
            "lower_image_alt": forms.TextInput(attrs={"class": "mgr-input"}),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class RevenueDistributionBlockForm(forms.ModelForm):
    class Meta:
        model = RevenueDistributionBlock
        fields = [
            "heading",
            "description",
            "callout",
            "bg_color",
            "text_color",
        ]
        widgets = {
            "heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "description": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "callout": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class RevenueTableColumnForm(forms.ModelForm):
    class Meta:
        model = RevenueTableColumn
        fields = ["heading", "sort_order"]
        widgets = {
            "heading": forms.TextInput(
                attrs={"class": "mgr-input", "aria-label": "Column heading"}
            ),
            "sort_order": forms.HiddenInput(),
        }


RevenueTableColumnFormSet = forms.inlineformset_factory(
    RevenueDistributionBlock,
    RevenueTableColumn,
    form=RevenueTableColumnForm,
    extra=0,
    can_delete=True,
)


class RevenuePackageTableForm(forms.ModelForm):
    class Meta:
        model = RevenuePackageTable
        fields = [
            "title",
            "description",
            "colour_preset",
            "custom_header_bg",
            "custom_row_bg",
            "custom_text_colour",
            "sort_order",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "mgr-input"}),
            "description": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 2}
            ),
            "colour_preset": forms.Select(attrs={"class": "mgr-input"}),
            "custom_header_bg": forms.TextInput(
                attrs={
                    "type": "color",
                    "class": "mgr-input",
                    "style": "max-width:80px;",
                }
            ),
            "custom_row_bg": forms.TextInput(
                attrs={
                    "type": "color",
                    "class": "mgr-input",
                    "style": "max-width:80px;",
                }
            ),
            "custom_text_colour": forms.TextInput(
                attrs={
                    "type": "color",
                    "class": "mgr-input",
                    "style": "max-width:80px;",
                }
            ),
            "sort_order": forms.HiddenInput(),
        }


RevenuePackageTableFormSet = forms.inlineformset_factory(
    RevenueDistributionBlock,
    RevenuePackageTable,
    form=RevenuePackageTableForm,
    extra=0,
    can_delete=True,
)


class TextImageCTABlockForm(forms.ModelForm):
    class Meta:
        model = TextImageCTABlock
        fields = [
            "heading",
            "body",
            "image",
            "image_alt",
            "show_cta",
            "cta_text",
            "cta_url",
            "cta_bg_color",
            "cta_text_color",
            "cta_hover_bg_color",
            "cta_hover_text_color",
            "bg_color",
            "text_color",
        ]
        widgets = {
            "heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "body": TinyMCE(
                attrs={"aria-label": "CTA description"},
                mce_attrs=_RESTRICTED_TINYMCE,
            ),
            "image_alt": forms.TextInput(attrs={"class": "mgr-input"}),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_hover_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_hover_text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_text": forms.TextInput(attrs={"class": "mgr-input"}),
            "cta_url": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "e.g. /contact/ or https://...",
                }
            ),
        }


class WideHeaderCirclesBlockForm(forms.ModelForm):
    class Meta:
        model = WideHeaderCirclesBlock
        fields = [
            "heading",
            "sub_heading",
            "bg_color",
            "text_color",
            "circle_color",
        ]
        widgets = {
            "heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "sub_heading": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "circle_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class TwoColumnContentBlockForm(forms.ModelForm):
    class Meta:
        model = TwoColumnContentBlock
        fields = [
            "section_title",
            "col_1_title",
            "col_1_body",
            "col_2_title",
            "col_2_body",
            "bg_color",
            "text_color",
        ]
        widgets = {
            "section_title": forms.TextInput(attrs={"class": "mgr-input"}),
            "col_1_title": forms.TextInput(attrs={"class": "mgr-input"}),
            "col_1_body": TinyMCE(mce_attrs=_ABOUT_US_TINYMCE),
            "col_2_title": forms.TextInput(attrs={"class": "mgr-input"}),
            "col_2_body": TinyMCE(mce_attrs=_ABOUT_US_TINYMCE),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class StatisticsBlockForm(forms.ModelForm):
    class Meta:
        model = StatisticsBlock
        fields = [
            "stat_1_value",
            "stat_1_text",
            "stat_2_value",
            "stat_2_text",
            "stat_3_value",
            "stat_3_text",
            "stat_4_value",
            "stat_4_text",
            "bg_color",
            "text_color",
            "border_color",
        ]
        widgets = {
            "stat_1_value": forms.TextInput(attrs={"class": "mgr-input"}),
            "stat_1_text": TinyMCE(mce_attrs=_ABOUT_US_TINYMCE),
            "stat_2_value": forms.TextInput(attrs={"class": "mgr-input"}),
            "stat_2_text": TinyMCE(mce_attrs=_ABOUT_US_TINYMCE),
            "stat_3_value": forms.TextInput(attrs={"class": "mgr-input"}),
            "stat_3_text": TinyMCE(mce_attrs=_ABOUT_US_TINYMCE),
            "stat_4_value": forms.TextInput(attrs={"class": "mgr-input"}),
            "stat_4_text": TinyMCE(mce_attrs=_ABOUT_US_TINYMCE),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "border_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class OrganizationCarouselBlockForm(forms.ModelForm):
    class Meta:
        model = OrganizationCarouselBlock
        fields = [
            "bg_color",
            "text_color",
            "bullet_color",
            "bullet_active_color",
        ]
        widgets = {
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "bullet_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "bullet_active_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class OrgCarouselQuoteForm(forms.ModelForm):
    class Meta:
        model = OrgCarouselQuote
        fields = ["logo", "quote_text", "author_name", "sort_order"]
        widgets = {
            "quote_text": TinyMCE(
                attrs={"class": "quote-tinymce"},
                mce_attrs=_ABOUT_US_TINYMCE,
            ),
            "author_name": forms.TextInput(attrs={"class": "mgr-input"}),
            "sort_order": forms.HiddenInput(),
        }


OrgCarouselQuoteFormSet = forms.inlineformset_factory(
    OrganizationCarouselBlock,
    OrgCarouselQuote,
    form=OrgCarouselQuoteForm,
    extra=0,
    can_delete=True,
)


class ContactFormBlockForm(forms.ModelForm):
    class Meta:
        model = ContactFormBlock
        fields = ["intro_text", "from_email", "bg_color", "text_color"]
        widgets = {
            "intro_text": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "from_email": forms.EmailInput(attrs={"class": "mgr-input"}),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class ContactFormRecipientForm(forms.ModelForm):
    class Meta:
        model = ContactFormRecipient
        fields = ["email", "sort_order"]
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "mgr-input", "aria-label": "Recipient email"}
            ),
            "sort_order": forms.HiddenInput(),
        }


ContactFormRecipientFormSet = forms.inlineformset_factory(
    ContactFormBlock,
    ContactFormRecipient,
    form=ContactFormRecipientForm,
    extra=0,
    can_delete=True,
)


class LandingHeroBlockForm(forms.ModelForm):
    class Meta:
        model = LandingHeroBlock
        fields = [
            "heading",
            "sub_heading",
            "cta_text",
            "cta_url",
            "cta_bg_color",
            "cta_text_color",
            "cta_hover_bg_color",
            "cta_hover_text_color",
            "bg_color",
            "text_color",
            "circle_color",
        ]
        widgets = {
            "heading": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "sub_heading": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "cta_text": forms.TextInput(attrs={"class": "mgr-input"}),
            "cta_url": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "e.g. mailto:info@example.org or https://...",
                }
            ),
            "cta_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_hover_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_hover_text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "circle_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class FeatureCardsBlockForm(forms.ModelForm):
    class Meta:
        model = FeatureCardsBlock
        fields = [
            # Card 1
            "card_1_title",
            "card_1_text",
            "card_1_image",
            "card_1_image_alt",
            "card_1_number",
            "card_1_cta_text",
            "card_1_cta_url",
            "card_1_bg_color",
            # Card 2
            "card_2_title",
            "card_2_text",
            "card_2_image",
            "card_2_image_alt",
            "card_2_number",
            "card_2_cta_text",
            "card_2_cta_url",
            "card_2_bg_color",
            # Card 3
            "card_3_title",
            "card_3_text",
            "card_3_image",
            "card_3_image_alt",
            "card_3_number",
            "card_3_cta_text",
            "card_3_cta_url",
            "card_3_bg_color",
            # Shared colours
            "text_color",
            "cta_bg_color",
            "cta_text_color",
            "cta_hover_bg_color",
            "cta_hover_text_color",
        ]
        widgets = {
            # Card 1
            "card_1_title": forms.TextInput(attrs={"class": "mgr-input"}),
            "card_1_text": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 4}
            ),
            "card_1_image_alt": forms.TextInput(attrs={"class": "mgr-input"}),
            "card_1_number": forms.TextInput(
                attrs={"class": "mgr-input", "style": "max-width:80px;"}
            ),
            "card_1_cta_text": forms.TextInput(attrs={"class": "mgr-input"}),
            "card_1_cta_url": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "e.g. /contact/ or https://...",
                }
            ),
            "card_1_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            # Card 2
            "card_2_title": forms.TextInput(attrs={"class": "mgr-input"}),
            "card_2_text": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 4}
            ),
            "card_2_image_alt": forms.TextInput(attrs={"class": "mgr-input"}),
            "card_2_number": forms.TextInput(
                attrs={"class": "mgr-input", "style": "max-width:80px;"}
            ),
            "card_2_cta_text": forms.TextInput(attrs={"class": "mgr-input"}),
            "card_2_cta_url": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "e.g. /contact/ or https://...",
                }
            ),
            "card_2_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            # Card 3
            "card_3_title": forms.TextInput(attrs={"class": "mgr-input"}),
            "card_3_text": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 4}
            ),
            "card_3_image_alt": forms.TextInput(attrs={"class": "mgr-input"}),
            "card_3_number": forms.TextInput(
                attrs={"class": "mgr-input", "style": "max-width:80px;"}
            ),
            "card_3_cta_text": forms.TextInput(attrs={"class": "mgr-input"}),
            "card_3_cta_url": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "e.g. /contact/ or https://...",
                }
            ),
            "card_3_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            # Shared colours
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_hover_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "cta_hover_text_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class LandingStatsBlockForm(forms.ModelForm):
    class Meta:
        model = LandingStatsBlock
        fields = [
            "fundraising_target",
            "amount_raised",
            "description",
            "button_1_text",
            "button_1_url",
            "button_1_bg_color",
            "button_1_text_color",
            "button_1_hover_bg_color",
            "button_1_hover_text_color",
            "button_2_text",
            "button_2_url",
            "button_2_bg_color",
            "button_2_text_color",
            "button_2_hover_bg_color",
            "button_2_hover_text_color",
            "bg_color",
            "text_color",
            "ring_color",
        ]
        widgets = {
            "fundraising_target": forms.NumberInput(
                attrs={"class": "mgr-input", "style": "max-width:200px;"}
            ),
            "amount_raised": forms.NumberInput(
                attrs={"class": "mgr-input", "style": "max-width:200px;"}
            ),
            "description": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "button_1_text": forms.TextInput(attrs={"class": "mgr-input"}),
            "button_1_url": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "e.g. mailto:... or https://...",
                }
            ),
            "button_1_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "button_1_text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "button_1_hover_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "button_1_hover_text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "button_2_text": forms.TextInput(attrs={"class": "mgr-input"}),
            "button_2_url": forms.TextInput(
                attrs={
                    "class": "mgr-input",
                    "placeholder": "e.g. mailto:... or https://...",
                }
            ),
            "button_2_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "button_2_text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "button_2_hover_bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "button_2_hover_text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "bg_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "text_color": forms.TextInput(attrs=_COLOR_ATTRS),
            "ring_color": forms.TextInput(attrs=_COLOR_ATTRS),
        }


class ContactSubmissionForm(forms.Form):
    """Public-facing contact form."""

    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    subject = forms.CharField(max_length=255, required=False)
    message = forms.CharField(widget=forms.Textarea)
