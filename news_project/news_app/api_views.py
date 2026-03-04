"""REST API views for the news_app application.

This module exposes read-only API endpoints consumed by authenticated clients
(primarily readers). All views require authentication via Django session or
HTTP Basic Auth as configured in ``settings.REST_FRAMEWORK``.

Endpoints
---------
``GET /api/articles/``
    Returns the list of approved articles filtered to the requesting reader's
    subscriptions. See :class:`SubscribedArticlesAPIView`.
"""

from django.db.models import Q
from rest_framework import generics, permissions

from .models import Article, CustomUser
from .serializers import ArticleSerializer


class SubscribedArticlesAPIView(generics.ListAPIView):
    """Return approved articles relevant to the authenticated reader.

    Filters the article list to only include articles where:

    - The **publisher** is in the reader's ``subscribed_publishers`` list,
      **or**
    - The **author** (journalist) is in the reader's
      ``subscribed_journalists`` list.

    Additionally, only **approved** articles are returned regardless of
    subscription status.

    Non-reader users (journalists, editors) will receive an empty list
    because subscription-based filtering only applies to readers.

    Authentication:
        Session or HTTP Basic Auth (configured in ``REST_FRAMEWORK``
        settings).

    Permissions:
        ``IsAuthenticated`` — the client must be logged in.

    Responses:
        - ``200 OK`` – list of serialised articles (may be empty).
        - ``403 Forbidden`` – unauthenticated request.
    """

    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Build and return the subscription-filtered article queryset.

        Returns:
            QuerySet[Article]: Approved articles matching the reader's
            subscriptions, ordered newest-first. Returns an empty queryset
            for non-reader users.
        """
        user = self.request.user

        # Only readers have meaningful subscription data.
        if not isinstance(user, CustomUser) or user.role != CustomUser.Roles.READER:
            return Article.objects.none()

        subscribed_publishers = user.subscribed_publishers.all()
        subscribed_journalists = user.subscribed_journalists.all()

        queryset = Article.objects.filter(
            is_approved=True
        ).filter(
            Q(publisher__in=subscribed_publishers)
            | Q(author__in=subscribed_journalists)
        )

        return queryset.select_related("publisher", "author").order_by("-created_at")
