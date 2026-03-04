"""Data models for the news_app application.

This module defines the core database schema used by the news platform:

- ``CustomUser``  - extends Django's AbstractUser with a role field
  (Reader, Editor, Journalist) and subscription many-to-many relations.
- ``Publisher``   - an organisation that employs editors and journalists.
- ``Article``     - a piece of content authored by a journalist, subject to
  editorial approval before it becomes visible to readers.
- ``Newsletter``  - a broadcast message sent by a publisher or journalist.
"""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model that extends Django's built-in user with roles.

    Three distinct roles control what each user can do:

    - Reader: can view approved articles and newsletters, and subscribe to
      publishers and journalists.
    - Editor: can view, update, and delete articles/newsletters, and approve
      articles written by journalists.
    - Journalist: can create, view, update, and delete their own articles
      and newsletters.

    Attributes:
        role (str): The user's functional role. One of 'reader', 'editor',
            or 'journalist'.
        subscribed_publishers (ManyToManyField): Publishers the reader
            follows. Intended to be empty for non-readers.
        subscribed_journalists (ManyToManyField): Journalist accounts the
            reader follows. Self-referential and asymmetric.
    """

    class Roles(models.TextChoices):
        """Enumeration of valid user roles."""

        READER = "reader", "Reader"
        EDITOR = "editor", "Editor"
        JOURNALIST = "journalist", "Journalist"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.READER,
        help_text="User role determines group and permissions.",
    )

    # Reader-specific subscriptions
    subscribed_publishers = models.ManyToManyField(
        "Publisher",
        blank=True,
        related_name="subscribed_readers",
        help_text="Publishers this reader is subscribed to.",
    )

    subscribed_journalists = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="subscribed_readers",
        help_text="Journalists this reader is subscribed to.",
    )

    def enforce_role_subscription_rules(self):
        """Clear subscriptions that are incompatible with the user's role.

        Journalists must not hold reader-style subscriptions. This method
        must be called *after* the user has been saved (and has a primary
        key) because many-to-many operations require a persisted instance.

        Example::

            user.save()
            user.enforce_role_subscription_rules()
        """
        if self.role == CustomUser.Roles.JOURNALIST:
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()

    def __str__(self):
        """Return username and role as a human-readable string.

        Returns:
            str: e.g. ``'alice (journalist)'``.
        """
        return f"{self.username} ({self.role})"


class Publisher(models.Model):
    """An organisation that publishes articles and newsletters.

    Readers can subscribe to a publisher to receive all articles published
    under its banner via email notification.

    Attributes:
        name (str): Unique display name of the publisher.
        description (str): Optional longer description.
        editors (ManyToManyField): Editor users assigned to this publisher.
        journalists (ManyToManyField): Journalist users who write for this
            publisher.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="publishers_as_editor",
        help_text="Users (with role Editor) who edit for this publisher.",
    )

    journalists = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="publishers_as_journalist",
        help_text="Users (with role Journalist) who write for this publisher.",
    )

    def __str__(self):
        """Return the publisher's name.

        Returns:
            str: The unique name of this publisher.
        """
        return self.name


class Article(models.Model):
    """A news article authored by a journalist, subject to editorial approval.

    Articles must be approved by an editor (``is_approved=True``) before
    they become visible to readers. On approval, email notifications are
    sent to subscribed readers and a post is made to X (Twitter).

    Attributes:
        title (str): Short headline for the article.
        content (str): Full body text.
        publisher (Publisher): The publisher this article belongs to.
            May be ``None`` for independent journalists.
        author (CustomUser): The journalist who wrote the article.
        is_approved (bool): Whether an editor has approved the article.
        created_at (datetime): Timestamp set automatically on creation.
        updated_at (datetime): Timestamp updated automatically on save.
        approved_by (CustomUser): Editor who approved the article.
        approved_at (datetime): When the approval took place.
    """

    title = models.CharField(max_length=255)
    content = models.TextField()

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="articles",
        null=True,
        blank=True,
        help_text="Publisher of this article (may be null for independent pieces).",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles_authored",
        help_text="Journalist who wrote this article.",
    )

    is_approved = models.BooleanField(
        default=False,
        help_text="Has this article been approved by an editor?",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="articles_approved",
        help_text="Editor who approved this article.",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """Return the article title.

        Returns:
            str: The title of the article.
        """
        return self.title


class Newsletter(models.Model):
    """A newsletter broadcast sent by a publisher or an individual journalist.

    Unlike articles, newsletters do not go through an editorial approval
    workflow. They are associated with either a publisher, a journalist, or
    both.

    Attributes:
        title (str): Subject line / headline of the newsletter.
        content (str): Full body text.
        publisher (Publisher): The publisher sending this newsletter.
        journalist (CustomUser): The journalist who authored it.
        created_at (datetime): Timestamp set automatically on creation.
    """

    title = models.CharField(max_length=255)
    content = models.TextField()

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="newsletters",
        null=True,
        blank=True,
        help_text="Publisher sending this newsletter (optional).",
    )

    journalist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="newsletters_authored",
        help_text="Journalist who authored this newsletter.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the newsletter title.

        Returns:
            str: The title of this newsletter.
        """
        return self.title
