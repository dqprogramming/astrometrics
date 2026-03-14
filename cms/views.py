"""
CMS views for static content pages.
"""

from django.shortcuts import render


def index_view(request):
    return render(request, "landing.html")


def board_view(request):
    return render(request, "board.html")


def partial_view(request, filename):
    return render(request, f"partial/{filename}")
