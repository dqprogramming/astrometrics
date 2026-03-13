from django import forms

from .models import ArchivingService, Journal, Language, PackageBand, Publisher, Subject


class ArchivingServiceForm(forms.ModelForm):
    class Meta:
        model = ArchivingService
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mgr-input", "placeholder": "e.g. CLOCKSS, Portico"}),
        }


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ["name", "website"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mgr-input"}),
            "website": forms.URLInput(attrs={"class": "mgr-input"}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mgr-input"}),
        }


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ["name", "code"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mgr-input"}),
            "code": forms.TextInput(attrs={"class": "mgr-input", "placeholder": "e.g. en, fr, de"}),
        }


class PackageBandForm(forms.ModelForm):
    class Meta:
        model = PackageBand
        fields = ["code", "name"]
        widgets = {
            "code": forms.TextInput(attrs={"class": "mgr-input", "placeholder": "e.g. C1"}),
            "name": forms.TextInput(attrs={"class": "mgr-input"}),
        }


class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = [
            "title", "year_established", "issn",
            "publisher", "journal_owner", "package_band",
            "journal_url", "publisher_url",
            "description",
            "cost_gbp", "normalized_articles",
            "in_doaj", "in_scopus", "wos_impact_factor",
            "licensing",
            "archive_available_diamond_oa", "archive_years",
            "usps",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "mgr-input"}),
            "year_established": forms.TextInput(attrs={"class": "mgr-input"}),
            "issn": forms.TextInput(attrs={"class": "mgr-input"}),
            "publisher": forms.Select(attrs={"class": "mgr-select"}),
            "journal_owner": forms.TextInput(attrs={"class": "mgr-input"}),
            "package_band": forms.Select(attrs={"class": "mgr-select"}),
            "journal_url": forms.URLInput(attrs={"class": "mgr-input"}),
            "publisher_url": forms.URLInput(attrs={"class": "mgr-input"}),
            "description": forms.Textarea(attrs={"class": "mgr-textarea", "rows": 5}),
            "cost_gbp": forms.NumberInput(attrs={"class": "mgr-input", "step": "0.01"}),
            "normalized_articles": forms.NumberInput(attrs={"class": "mgr-input", "step": "0.01"}),
            "wos_impact_factor": forms.NumberInput(attrs={"class": "mgr-input", "step": "0.01"}),
            "licensing": forms.Select(attrs={"class": "mgr-select"}),
            "archive_available_diamond_oa": forms.Textarea(attrs={"class": "mgr-textarea", "rows": 3}),
            "archive_years": forms.NumberInput(attrs={"class": "mgr-input"}),
            "usps": forms.Textarea(attrs={"class": "mgr-textarea", "rows": 3}),
        }
