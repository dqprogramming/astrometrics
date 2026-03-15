"""
Portal forms: limited field sets that portal users are allowed to edit.
"""

from django import forms

from journals.models import Journal, Publisher


class PublisherPortalForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ["name", "website"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "portal-input"}),
            "website": forms.URLInput(attrs={"class": "portal-input"}),
        }


class JournalPortalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = [
            "title",
            "description",
            "journal_url",
            "publisher_url",
            "issn",
            "year_established",
            "in_doaj",
            "in_scopus",
            "wos_impact_factor",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "portal-input"}),
            "description": forms.Textarea(
                attrs={"class": "portal-textarea", "rows": 6}
            ),
            "journal_url": forms.URLInput(attrs={"class": "portal-input"}),
            "publisher_url": forms.URLInput(attrs={"class": "portal-input"}),
            "issn": forms.TextInput(attrs={"class": "portal-input"}),
            "year_established": forms.TextInput(
                attrs={"class": "portal-input"}
            ),
            "wos_impact_factor": forms.NumberInput(
                attrs={"class": "portal-input", "step": "0.01"}
            ),
        }
