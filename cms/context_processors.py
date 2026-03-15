from .models import FooterSettings


def footer_settings(request):
    return {"footer": FooterSettings.load()}
