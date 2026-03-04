"""DRF serializers for the news_app application.

Serializers convert model instances to JSON (and vice versa) for the REST API.
This module defines three serializers used by :mod:`news_app.api_views`:

- :class:`PublisherSerializer` – lightweight read-only representation of a
  :class:`~news_app.models.Publisher`.
- :class:`JournalistSerializer` – lightweight read-only representation of a
  journalist :class:`~news_app.models.CustomUser`.
- :class:`ArticleSerializer` – full representation of an
  :class:`~news_app.models.Article`, embedding nested publisher and author
  data.
"""

from rest_framework import serializers

from .models import Article, Publisher, CustomUser


class PublisherSerializer(serializers.ModelSerializer):
    """Read-only serializer for the Publisher model.

    Exposes the publisher's ``id`` and ``name`` fields. Used as a nested
    serializer inside :class:`ArticleSerializer`.

    Example JSON output::

        {"id": 1, "name": "The Daily News"}
    """

    class Meta:
        model = Publisher
        fields = ["id", "name"]


class JournalistSerializer(serializers.ModelSerializer):
    """Read-only serializer for a journalist (CustomUser) instance.

    Exposes only the ``id`` and ``username`` fields — personal details such
    as email are intentionally excluded from the public API. Used as a nested
    serializer inside :class:`ArticleSerializer`.

    Example JSON output::

        {"id": 3, "username": "jane_writes"}
    """

    class Meta:
        model = CustomUser
        fields = ["id", "username"]


class ArticleSerializer(serializers.ModelSerializer):
    """Full read-only serializer for the Article model.

    Embeds nested :class:`PublisherSerializer` and :class:`JournalistSerializer`
    representations so API consumers receive complete context without
    needing to make additional requests.

    Example JSON output::

        {
          "id": 42,
          "title": "Breaking: Something Happened",
          "content": "Full article text...",
          "publisher": {"id": 1, "name": "The Daily News"},
          "author": {"id": 3, "username": "jane_writes"},
          "is_approved": true,
          "created_at": "2025-01-01T10:00:00Z",
          "approved_at": "2025-01-02T08:30:00Z"
        }
    """

    publisher = PublisherSerializer(read_only=True)
    author = JournalistSerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "publisher",
            "author",
            "is_approved",
            "created_at",
            "approved_at",
        ]
