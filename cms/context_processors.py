from .models import BlockPage, FooterSettings, HeaderSettings


def footer_settings(request):
    return {"footer": FooterSettings.load()}


def header_settings(request):
    return {"header": HeaderSettings.load()}


def block_pages(request):
    if request.path.startswith("/manager/"):
        return {"block_pages": BlockPage.objects.all().order_by("name")}
    return {}
