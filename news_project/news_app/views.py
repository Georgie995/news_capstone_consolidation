"""HTTP view functions for the news_app application.

This module contains all Django view functions that handle web requests for
the news platform. Views are protected with ``@login_required`` and, where
appropriate, ``@permission_required`` to enforce role-based access control.

Role–permission mapping enforced here:

- Reader:     article_list, article_detail (approved only)
- Journalist: article_create, article_update (own), article_delete (own)
- Editor:     editor_article_list, approve_article, article_update, article_delete
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CustomUserCreationForm
from .models import Article, CustomUser
from .notifications import post_article_to_x, send_article_email_to_subscribers


@login_required
def home(request):
    """Render the authenticated home page.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Rendered ``home.html`` template.
    """
    return render(request, "home.html")


@login_required
def article_list(request):
    """Display a list of articles appropriate to the requesting user's role.

    - Readers and editors see all approved articles.
    - Journalists see all approved articles **plus** their own unapproved
      articles so they can track the status of their submissions.

    Results are ordered newest-first.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Rendered ``news_app/article_list.html`` with the
        ``articles`` queryset in context.
    """
    qs = Article.objects.filter(is_approved=True).select_related("publisher", "author")

    if request.user.role == CustomUser.Roles.JOURNALIST:
        # Include own unapproved articles so journalists can track submissions.
        own_qs = Article.objects.filter(author=request.user).select_related(
            "publisher", "author"
        )
        qs = qs | own_qs

    articles = qs.distinct().order_by("-created_at")
    return render(request, "news_app/article_list.html", {"articles": articles})


@login_required
def article_detail(request, pk):
    """Display a single article, with access control for readers.

    Readers are only permitted to view approved articles. Journalists and
    editors may view any article.

    Args:
        request (HttpRequest): The incoming HTTP request.
        pk (int): Primary key of the :class:`~news_app.models.Article` to
            display.

    Returns:
        HttpResponse: Rendered ``news_app/article_detail.html`` with
        ``article`` in context, or a redirect to ``article_list`` if the
        reader is not permitted to view the article.
    """
    article = get_object_or_404(Article, pk=pk)
    if request.user.role == CustomUser.Roles.READER and not article.is_approved:
        messages.error(request, "You are not allowed to view unapproved articles.")
        return redirect("article_list")

    return render(request, "news_app/article_detail.html", {"article": article})


@login_required
@permission_required("news_app.add_article", raise_exception=True)
def article_create(request):
    """Handle creation of a new article by a journalist.

    Only users with the ``add_article`` permission (Journalists) may access
    this view. The new article is saved in an unapproved state pending editor
    review.

    Args:
        request (HttpRequest): The incoming HTTP request. POST body must
            contain ``title`` and ``content`` fields.

    Returns:
        HttpResponse: On GET, renders ``news_app/article_form.html``.
        On valid POST, redirects to ``article_list``.
    """
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        if not title or not content:
            messages.error(request, "Title and content are required.")
        else:
            Article.objects.create(
                title=title,
                content=content,
                author=request.user,
            )
            messages.success(request, "Article created (pending editor approval).")
            return redirect("article_list")

    return render(request, "news_app/article_form.html")


@login_required
@permission_required("news_app.change_article", raise_exception=True)
def article_update(request, pk):
    """Allow permitted users to update an existing article.

    Journalists may only edit articles they authored themselves. Editors may
    edit any article. Editing an approved article resets its approval status
    so it must be re-reviewed by an editor.

    Args:
        request (HttpRequest): The incoming HTTP request. POST body must
            contain ``title`` and ``content`` fields.
        pk (int): Primary key of the article to update.

    Returns:
        HttpResponse: On GET, renders ``news_app/article_form.html`` with
        the existing article data. On valid POST, redirects to
        ``article_detail``.
    """
    article = get_object_or_404(Article, pk=pk)

    if request.user.role == CustomUser.Roles.JOURNALIST and article.author != request.user:
        messages.error(request, "You can only edit your own articles.")
        return redirect("article_list")

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        if not title or not content:
            messages.error(request, "Title and content are required.")
        else:
            article.title = title
            article.content = content
            # Reset approval so the updated article is re-reviewed.
            article.is_approved = False
            article.approved_by = None
            article.approved_at = None
            article.save()
            messages.success(request, "Article updated and marked as pending approval.")
            return redirect("article_detail", pk=article.pk)

    return render(request, "news_app/article_form.html", {"article": article})


@login_required
@permission_required("news_app.delete_article", raise_exception=True)
def article_delete(request, pk):
    """Allow permitted users to delete an article.

    Journalists may only delete articles they authored themselves. Editors
    may delete any article. A GET request shows a confirmation page; a POST
    request performs the deletion.

    Args:
        request (HttpRequest): The incoming HTTP request.
        pk (int): Primary key of the article to delete.

    Returns:
        HttpResponse: On GET, renders ``news_app/article_confirm_delete.html``.
        On POST, deletes the article and redirects to ``article_list``.
    """
    article = get_object_or_404(Article, pk=pk)

    if request.user.role == CustomUser.Roles.JOURNALIST and article.author != request.user:
        messages.error(request, "You can only delete your own articles.")
        return redirect("article_list")

    if request.method == "POST":
        article.delete()
        messages.success(request, "Article deleted.")
        return redirect("article_list")

    return render(request, "news_app/article_confirm_delete.html", {"article": article})


@login_required
@permission_required("news_app.change_article", raise_exception=True)
def editor_article_list(request):
    """Show all unapproved articles to editors for review.

    Only users with the Editor role may access this view. Other authenticated
    users (including Journalists) are redirected to the home page.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Rendered ``news_app/editor_article_list.html`` with
        ``articles`` (unapproved only) in context, or a redirect to ``home``
        for non-editors.
    """
    if request.user.role != CustomUser.Roles.EDITOR:
        messages.error(request, "Only editors can access this page.")
        return redirect("home")

    articles = Article.objects.filter(is_approved=False).select_related(
        "publisher", "author"
    )
    return render(request, "news_app/editor_article_list.html", {"articles": articles})


@login_required
@permission_required("news_app.change_article", raise_exception=True)
def approve_article(request, pk):
    """Allow an editor to approve a pending article.

    On approval the following side-effects are triggered:

    1. The article's ``is_approved`` flag is set to ``True``.
    2. ``approved_by`` and ``approved_at`` are recorded.
    3. An email notification is sent to all subscribed readers via
       :func:`~news_app.notifications.send_article_email_to_subscribers`.
    4. A post is made to X (Twitter) via
       :func:`~news_app.notifications.post_article_to_x`.

    Args:
        request (HttpRequest): The incoming HTTP request.
        pk (int): Primary key of the article to approve.

    Returns:
        HttpResponse: On GET, renders ``news_app/article_detail.html`` for
        preview. On POST, approves the article and redirects to
        ``editor_article_list``.
    """
    if request.user.role != CustomUser.Roles.EDITOR:
        messages.error(request, "Only editors can approve articles.")
        return redirect("home")

    article = get_object_or_404(Article, pk=pk)

    if request.method == "POST":
        article.is_approved = True
        article.approved_by = request.user
        article.approved_at = timezone.now()
        article.save()

        send_article_email_to_subscribers(article)
        post_article_to_x(article)

        messages.success(request, "Article approved and notifications sent.")
        return redirect("editor_article_list")

    return render(request, "news_app/article_detail.html", {"article": article})


def register_view(request):
    """Handle new user registration.

    Presents :class:`~news_app.forms.CustomUserCreationForm` on GET and
    processes the submitted form on POST. On successful registration the
    user is immediately logged in and redirected to the home page.

    This view is intentionally **not** protected by ``@login_required`` so
    that unauthenticated visitors can create an account.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: On GET or invalid POST, renders ``register.html``
        with the form. On valid POST, redirects to ``home``.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created. You are now logged in.")
            return redirect("home")
    else:
        form = CustomUserCreationForm()

    return render(request, "register.html", {"form": form})
