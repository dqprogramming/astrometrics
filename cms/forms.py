from django import forms
from tinymce.widgets import TinyMCE

from .models import LandingPageSettings, Page, Post, Snippet


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
            "byline",
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
            "byline": forms.TextInput(attrs={"class": "mgr-input"}),
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
