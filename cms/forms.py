from django import forms
from tinymce.widgets import TinyMCE

from .models import (
    FooterLink,
    FooterSettings,
    HeaderSettings,
    LandingPageSettings,
    MenuItem,
    Page,
    Post,
    Snippet,
)


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
            "meta_description",
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
            "meta_description": forms.TextInput(attrs={"class": "mgr-input"}),
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
