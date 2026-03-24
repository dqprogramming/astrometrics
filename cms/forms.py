from django import forms
from tinymce.widgets import TinyMCE

from .models import (
    AboutUsPageSettings,
    AboutUsQuote,
    BlockPage,
    BlockPageTemplate,
    BoardMember,
    BoardSection,
    Category,
    ContactFormSettings,
    ContactRecipient,
    FooterLink,
    FooterSettings,
    FreeAccessJournalsBlock,
    HeaderSettings,
    InstitutionEntry,
    LandingPageSettings,
    ManifestoHeroBlock,
    ManifestoOrganiseBlock,
    ManifestoPageSettings,
    ManifestoTextBlock,
    MembersHeaderBlock,
    MembersInstitutionsBlock,
    MenuItem,
    OurModelPackageTable,
    OurModelPageSettings,
    OurModelTableColumn,
    Page,
    PersonCarouselBlock,
    PersonCarouselQuote,
    Post,
    Snippet,
    TeamMember,
    TeamSection,
    WhoWeAreBlock,
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


class OurModelPageSettingsForm(forms.ModelForm):
    class Meta:
        model = OurModelPageSettings
        fields = [
            "slug",
            "hero_heading",
            "hero_image_alt",
            "model_heading",
            "model_body",
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
            "cta_button_url",
            "cta_button_visible",
            "cta_image_alt",
        ]
        widgets = {
            "slug": forms.TextInput(attrs={"class": "mgr-input"}),
            "hero_heading": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "hero_image_alt": forms.TextInput(attrs={"class": "mgr-input"}),
            "model_heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "model_body": TinyMCE(
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
            "funding_heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "funding_upper_image_alt": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "funding_lower_image_alt": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "funding_body": TinyMCE(
                attrs={"aria-label": "Funding body"},
                mce_attrs=_RESTRICTED_TINYMCE,
            ),
            "revenue_heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "revenue_description": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "revenue_callout": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "cta_heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "cta_description": TinyMCE(
                attrs={"aria-label": "CTA description"},
                mce_attrs=_RESTRICTED_TINYMCE,
            ),
            "cta_button_text": forms.TextInput(attrs={"class": "mgr-input"}),
            "cta_button_url": forms.TextInput(attrs={"class": "mgr-input"}),
            "cta_image_alt": forms.TextInput(attrs={"class": "mgr-input"}),
        }


class OurModelTableColumnForm(forms.ModelForm):
    class Meta:
        model = OurModelTableColumn
        fields = ["heading", "sort_order"]
        widgets = {
            "heading": forms.TextInput(
                attrs={"class": "mgr-input", "aria-label": "Column heading"}
            ),
            "sort_order": forms.HiddenInput(),
        }


OurModelTableColumnFormSet = forms.inlineformset_factory(
    OurModelPageSettings,
    OurModelTableColumn,
    form=OurModelTableColumnForm,
    extra=0,
    can_delete=True,
)


class OurModelPackageTableForm(forms.ModelForm):
    class Meta:
        model = OurModelPackageTable
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


OurModelPackageTableFormSet = forms.inlineformset_factory(
    OurModelPageSettings,
    OurModelPackageTable,
    form=OurModelPackageTableForm,
    extra=0,
    can_delete=True,
)


class TeamSectionForm(forms.ModelForm):
    class Meta:
        model = TeamSection
        fields = ["name", "sort_order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mgr-input"}),
            "sort_order": forms.HiddenInput(),
        }


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = [
            "name",
            "description",
            "linkedin_url",
            "image",
            "sort_order",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mgr-input"}),
            "description": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "linkedin_url": forms.TextInput(attrs={"class": "mgr-input"}),
            "image": forms.HiddenInput(),
            "sort_order": forms.HiddenInput(),
        }


TeamMemberFormSet = forms.inlineformset_factory(
    TeamSection,
    TeamMember,
    form=TeamMemberForm,
    extra=0,
    can_delete=True,
)


class BoardSectionForm(forms.ModelForm):
    class Meta:
        model = BoardSection
        fields = ["name", "sort_order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mgr-input"}),
            "sort_order": forms.HiddenInput(),
        }


class BoardMemberForm(forms.ModelForm):
    class Meta:
        model = BoardMember
        fields = [
            "name",
            "description",
            "linkedin_url",
            "image",
            "sort_order",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mgr-input"}),
            "description": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "linkedin_url": forms.TextInput(attrs={"class": "mgr-input"}),
            "image": forms.HiddenInput(),
            "sort_order": forms.HiddenInput(),
        }


BoardMemberFormSet = forms.inlineformset_factory(
    BoardSection,
    BoardMember,
    form=BoardMemberForm,
    extra=0,
    can_delete=True,
)


class ContactFormSettingsForm(forms.ModelForm):
    class Meta:
        model = ContactFormSettings
        fields = ["from_email"]
        widgets = {
            "from_email": forms.EmailInput(attrs={"class": "mgr-input"}),
        }


class ContactRecipientForm(forms.ModelForm):
    class Meta:
        model = ContactRecipient
        fields = ["email", "sort_order"]
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "mgr-input", "aria-label": "Recipient email"}
            ),
            "sort_order": forms.HiddenInput(),
        }


ContactRecipientFormSet = forms.inlineformset_factory(
    ContactFormSettings,
    ContactRecipient,
    form=ContactRecipientForm,
    extra=0,
    can_delete=True,
)


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


class ManifestoPageSettingsForm(forms.ModelForm):
    class Meta:
        model = ManifestoPageSettings
        fields = [
            "slug",
            "hero_heading",
            "hero_sub",
            "hero_image_alt",
            "text_body",
            "organise_heading",
            "organise_body",
            "achievable_heading",
            "achievable_body",
            "cta_button_text",
            "cta_button_url",
            "final_heading",
            "final_image_alt",
            "final_button_text",
            "final_button_url",
        ]
        widgets = {
            "slug": forms.TextInput(
                attrs={"class": "mgr-input", "placeholder": "our-manifesto"}
            ),
            "hero_heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "hero_sub": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "hero_image_alt": forms.TextInput(attrs={"class": "mgr-input"}),
            "text_body": TinyMCE(mce_attrs=_MANIFESTO_TINYMCE),
            "organise_heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "organise_body": TinyMCE(mce_attrs=_MANIFESTO_TINYMCE),
            "achievable_heading": forms.TextInput(
                attrs={"class": "mgr-input"}
            ),
            "achievable_body": TinyMCE(mce_attrs=_MANIFESTO_TINYMCE),
            "cta_button_text": forms.TextInput(attrs={"class": "mgr-input"}),
            "cta_button_url": forms.TextInput(attrs={"class": "mgr-input"}),
            "final_heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "final_image_alt": forms.TextInput(attrs={"class": "mgr-input"}),
            "final_button_text": forms.TextInput(attrs={"class": "mgr-input"}),
            "final_button_url": forms.TextInput(attrs={"class": "mgr-input"}),
        }


class AboutUsPageSettingsForm(forms.ModelForm):
    class Meta:
        model = AboutUsPageSettings
        fields = [
            "slug",
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
        ]
        widgets = {
            "slug": forms.TextInput(
                attrs={"class": "mgr-input", "placeholder": "about-us"}
            ),
            "hero_heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "hero_sub": forms.Textarea(
                attrs={"class": "mgr-textarea", "rows": 3}
            ),
            "section_title": forms.TextInput(attrs={"class": "mgr-input"}),
            "col_1_title": forms.TextInput(attrs={"class": "mgr-input"}),
            "col_1_body": TinyMCE(mce_attrs=_ABOUT_US_TINYMCE),
            "col_2_title": forms.TextInput(attrs={"class": "mgr-input"}),
            "col_2_body": TinyMCE(mce_attrs=_ABOUT_US_TINYMCE),
            "stat_1_value": forms.TextInput(attrs={"class": "mgr-input"}),
            "stat_1_text": TinyMCE(mce_attrs=_ABOUT_US_TINYMCE),
            "stat_2_value": forms.TextInput(attrs={"class": "mgr-input"}),
            "stat_2_text": TinyMCE(mce_attrs=_ABOUT_US_TINYMCE),
            "stat_3_value": forms.TextInput(attrs={"class": "mgr-input"}),
            "stat_3_text": TinyMCE(mce_attrs=_ABOUT_US_TINYMCE),
            "stat_4_value": forms.TextInput(attrs={"class": "mgr-input"}),
            "stat_4_text": TinyMCE(mce_attrs=_ABOUT_US_TINYMCE),
        }


class AboutUsQuoteForm(forms.ModelForm):
    class Meta:
        model = AboutUsQuote
        fields = ["logo", "quote_text", "author_name", "sort_order"]
        widgets = {
            "quote_text": TinyMCE(
                attrs={"class": "quote-tinymce"},
                mce_attrs=_ABOUT_US_TINYMCE,
            ),
            "author_name": forms.TextInput(attrs={"class": "mgr-input"}),
            "sort_order": forms.HiddenInput(),
        }


AboutUsQuoteFormSet = forms.inlineformset_factory(
    AboutUsPageSettings,
    AboutUsQuote,
    form=AboutUsQuoteForm,
    extra=0,
    can_delete=True,
)


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
            "bg_color",
            "text_color",
        ]
        widgets = {
            "heading": forms.TextInput(attrs={"class": "mgr-input"}),
            "image_alt": forms.TextInput(attrs={"class": "mgr-input"}),
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


class ContactSubmissionForm(forms.Form):
    """Public-facing contact form."""

    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    subject = forms.CharField(max_length=255, required=False)
    message = forms.CharField(widget=forms.Textarea)
