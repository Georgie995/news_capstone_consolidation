"""Notification utilities for the news_app application.

This module provides two outbound notification functions that are triggered
when an editor approves an article:

1. :func:`send_article_email_to_subscribers` – sends an email to all readers
   who are subscribed to the article's publisher or author.
2. :func:`post_article_to_x` – posts a short announcement to X (Twitter)
   using the X API v2 via an HTTP POST request.

The helper :func:`get_article_subscribers` is extracted as a separate
function so it can be tested and reused independently.

Configuration
-------------
Email is controlled by Django's standard email settings (``EMAIL_BACKEND``,
``DEFAULT_FROM_EMAIL``). In development the console backend is recommended::

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

X (Twitter) integration requires the following settings (typically loaded
from environment variables via a ``.env`` file and **never** committed to
version control)::

    X_API_URL   = "https://api.twitter.com/2/tweets"
    X_API_TOKEN = "<your-bearer-token>"
"""

from typing import Iterable

from django.conf import settings
from django.core.mail import send_mail

import requests

from .models import Article, CustomUser


def get_article_subscribers(article: Article) -> Iterable[CustomUser]:
    """Return all readers who should be notified about the given article.

    A reader qualifies if they are subscribed to:

    - the article's **publisher** (if the article has one), **or**
    - the article's **author** (the journalist).

    The queryset uses ``distinct()`` to prevent duplicate entries when a
    reader is subscribed to both the publisher and the journalist.

    Args:
        article (Article): The article that was just approved.

    Returns:
        QuerySet[CustomUser]: A distinct queryset of Reader-role users who
        should receive a notification.
    """
    readers = CustomUser.objects.filter(role=CustomUser.Roles.READER)

    qs = readers.none()

    if article.publisher is not None:
        qs = qs | readers.filter(subscribed_publishers=article.publisher)

    qs = qs | readers.filter(subscribed_journalists=article.author)

    return qs.distinct()


def send_article_email_to_subscribers(article: Article) -> None:
    """Send an email notification about a newly approved article.

    Composes an email containing the article title, author, optional
    publisher, and full content, then delivers it to every subscribed
    reader using Django's email framework.

    If no subscribers have email addresses, the function returns early
    without making any network calls. Email failures are silenced
    (``fail_silently=True``) to avoid crashing the approval request.

    Args:
        article (Article): The article that was just approved.

    Returns:
        None
    """
    subscribers = get_article_subscribers(article)
    recipient_list = [user.email for user in subscribers if user.email]

    if not recipient_list:
        return

    subject = f"New article: {article.title}"
    body_lines = [
        f"Title: {article.title}",
        f"Author: {article.author.username}",
        "",
        article.content,
    ]
    if article.publisher:
        body_lines.insert(2, f"Publisher: {article.publisher.name}")

    message = "\n".join(body_lines)

    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=recipient_list,
        fail_silently=True,
    )


def post_article_to_x(article: Article) -> None:
    """Post a short announcement to X (Twitter) when an article is approved.

    Uses the X API v2 ``POST /2/tweets`` endpoint with Bearer Token
    authentication. The tweet text is truncated at 280 characters to comply
    with X's character limit.

    Credentials are read from Django settings (``X_API_URL`` and
    ``X_API_TOKEN``). If neither is configured, the function uses placeholder
    values and will not succeed — this is intentional for development
    environments where X credentials are not available.

    All exceptions are caught silently so that a failure to post to X
    never prevents an article from being approved.

    Args:
        article (Article): The article that was just approved.

    Returns:
        None
    """
    api_url = getattr(
        settings,
        "X_API_URL",
        "https://api.example.com/x/post",  # placeholder for development
    )
    api_token = getattr(settings, "X_API_TOKEN", "YOUR_X_API_TOKEN_HERE")

    text = f"New article: {article.title} by {article.author.username}"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    payload = {"text": text[:280]}

    try:
        requests.post(api_url, json=payload, headers=headers, timeout=5)
    except Exception:
        # Failures here must never crash the article approval workflow.
        pass
