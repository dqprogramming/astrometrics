"""
CMS views for static content pages.
"""

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Category, LandingPageSettings, Page, Post


def index_view(request):
    landing = LandingPageSettings.load()
    return render(request, "landing.html", {"landing": landing})


def board_view(request):
    return render(request, "board.html")


def partial_view(request, filename):
    return render(request, f"partial/{filename}")


def news_index_view(request):
    posts = Post.objects.filter(is_published=True).order_by("-published_at")
    categories = Category.objects.all()
    active_category = None
    category_slug = request.GET.get("category")
    if category_slug:
        active_category = Category.objects.filter(slug=category_slug).first()
        if active_category:
            posts = posts.filter(categories=active_category)
    paginator = Paginator(posts, 8)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "news.html",
        {
            "page_obj": page_obj,
            "categories": categories,
            "active_category": active_category,
        },
    )


def news_detail_view(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    return render(request, "news_detail.html", {"post": post})


def post_preview_view(request, token):
    post = get_object_or_404(Post, preview_token=token)
    return render(
        request, "news_detail.html", {"post": post, "is_preview": True}
    )


def page_preview_view(request, token):
    page = get_object_or_404(Page, preview_token=token)
    return render(
        request, "page_detail.html", {"page": page, "is_preview": True}
    )
