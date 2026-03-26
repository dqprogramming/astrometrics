"""
CMS views for static content pages.
"""

import structlog
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .forms import ContactSubmissionForm
from .models import (
    BlockPage,
    Category,
    ContactFormBlock,
    LandingPageSettings,
    Page,
    Post,
)

logger = structlog.get_logger(__name__)


def index_view(request):
    landing = LandingPageSettings.load()
    return render(request, "landing.html", {"landing": landing})


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


def _build_public_blocks(page):
    blocks = []
    for p in page.blocks.order_by("sort_order"):
        if not p.is_visible:
            continue
        block = p.get_block()
        if not block:
            continue
        bd = {
            "type": p.block_type,
            "block": block,
            "template": block.PUBLIC_TEMPLATE,
        }
        bd.update(block.get_public_context())
        blocks.append(bd)
    return blocks


def block_page_view(request, slug):
    page = get_object_or_404(BlockPage, slug=slug)
    blocks = _build_public_blocks(page)
    return render(request, "block_page.html", {"page": page, "blocks": blocks})


def slug_page_view(request, slug):
    """Serve block pages by slug."""
    page = get_object_or_404(BlockPage, slug=slug)
    contact_sent = False

    if request.method == "POST" and "contact_block_pk" in request.POST:
        contact_block_pk = request.POST.get("contact_block_pk")
        try:
            contact_block = ContactFormBlock.objects.get(pk=contact_block_pk)
            form = ContactSubmissionForm(request.POST)
            if form.is_valid():
                recipients = list(
                    contact_block.recipients.values_list("email", flat=True)
                )
                if recipients:
                    cd = form.cleaned_data
                    subject = cd["subject"] or "Contact form submission"
                    body = (
                        f"Name: {cd['name']}\n"
                        f"Email: {cd['email']}\n\n"
                        f"{cd['message']}"
                    )
                    email_msg = EmailMessage(
                        subject=subject,
                        body=body,
                        from_email=contact_block.from_email,
                        to=recipients,
                        reply_to=[cd["email"]],
                    )
                    try:
                        email_msg.send()
                    except Exception:
                        logger.exception("contact_form_email_failed")
                contact_sent = True
        except ContactFormBlock.DoesNotExist:
            pass

    blocks = _build_public_blocks(page)
    return render(
        request,
        "block_page.html",
        {"page": page, "blocks": blocks, "contact_sent": contact_sent},
    )


def page_preview_view(request, token):
    page = get_object_or_404(Page, preview_token=token)
    return render(
        request, "page_detail.html", {"page": page, "is_preview": True}
    )
