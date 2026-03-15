"""
CMS views for static content pages.
"""

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import LandingPageSettings, Post


def index_view(request):
    landing = LandingPageSettings.load()
    return render(request, "landing.html", {"landing": landing})


def board_view(request):
    return render(request, "board.html")


def partial_view(request, filename):
    return render(request, f"partial/{filename}")


def news_index_view(request):
    posts = Post.objects.filter(is_published=True).order_by("-published_at")
    paginator = Paginator(posts, 8)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "news.html", {"page_obj": page_obj})


def news_detail_view(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    return render(request, "news_detail.html", {"post": post})
