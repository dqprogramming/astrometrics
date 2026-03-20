"""
CMS views for static content pages.
"""

from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import (
    Category,
    LandingPageSettings,
    OurModelPageSettings,
    Page,
    Post,
)


def index_view(request):
    landing = LandingPageSettings.load()
    return render(request, "landing.html", {"landing": landing})


def our_model_view(request, slug=None):
    settings = OurModelPageSettings.load()
    if slug and slug != settings.slug:
        raise Http404

    columns = settings.get_table_columns()
    tables = settings.get_package_tables()
    num_columns = len(columns)
    col_width_pct = (100 // num_columns) if num_columns else 25

    # Pre-build ordered cell lists for template rendering
    for table in tables:
        for row in table.rows.all():
            cells_by_col = {
                cell.column_id: cell.value for cell in row.cells.all()
            }
            row.ordered_cells = [
                cells_by_col.get(col.pk, "") for col in columns
            ]

    return render(
        request,
        "our_model.html",
        {
            "settings": settings,
            "columns": columns,
            "tables": tables,
            "num_columns": num_columns,
            "col_width_pct": col_width_pct,
        },
    )


def board_view(request):
    return render(request, "board.html")


def our_team_view(request):
    return render(request, "our_team.html")


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
