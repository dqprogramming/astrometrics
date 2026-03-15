from .models import FooterSettings, HeaderSettings


def footer_settings(request):
    return {"footer": FooterSettings.load()}


def header_settings(request):
    return {"header": HeaderSettings.load()}
