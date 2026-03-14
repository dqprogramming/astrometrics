"""
CMS views for static content pages.
"""

from django.shortcuts import render

from .models import LandingPageSettings


def index_view(request):
    landing = LandingPageSettings.load()
    return render(request, "landing.html", {"landing": landing})


def board_view(request):
    return render(request, "board.html")


def partial_view(request, filename):
    return render(request, f"partial/{filename}")
