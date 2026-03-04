"""Django signal handlers for the news_app application.

This module registers a ``post_migrate`` signal receiver that creates the
three default permission groups required by the application:

- **Reader**     – view-only access to articles and newsletters.
- **Editor**     – view, change, and delete access to articles and newsletters
  (used to approve and manage submitted content).
- **Journalist** – full CRUD access to articles and newsletters (can create,
  view, update, and delete their own content).

The signal fires automatically after every ``migrate`` or ``migrate --run-syncdb``
management command, making it safe to run repeatedly (groups and permissions
are created idempotently via ``get_or_create`` and ``set``).

Note:
    This module is imported in :meth:`news_app.apps.NewsAppConfig.ready`
    to ensure the signal is registered before any migrations run.
"""

from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """Create Reader, Editor, and Journalist groups with correct permissions.

    This receiver is connected to Django's ``post_migrate`` signal and fires
    after every migration run. It is scoped to the ``news_app`` app label so
    it only executes once per migration run rather than once per installed app.

    Permissions granted:

    - Reader:     view_article, view_newsletter
    - Editor:     view/change/delete article + view/change/delete newsletter
    - Journalist: add/view/change/delete article + add/view/change/delete newsletter

    Args:
        sender: The app config that sent the signal (filtered to ``news_app``).
        **kwargs: Additional keyword arguments passed by the signal framework
            (including ``verbosity``, ``interactive``, etc.).

    Returns:
        None: Exits early if ``sender.label != 'news_app'``.
    """
    if sender.label != "news_app":
        return

    Article = apps.get_model("news_app", "Article")
    Newsletter = apps.get_model("news_app", "Newsletter")

    def model_perms(model):
        """Fetch the four standard permissions for a given model.

        Args:
            model: A Django model class.

        Returns:
            dict: Mapping of ``'add'``, ``'change'``, ``'delete'``,
            ``'view'`` to the corresponding Permission instances.
        """
        opts = model._meta
        return {
            action: Permission.objects.get(
                content_type__app_label=opts.app_label,
                codename=f"{action}_{opts.model_name}",
            )
            for action in ("add", "change", "delete", "view")
        }

    article_perms = model_perms(Article)
    newsletter_perms = model_perms(Newsletter)

    # Reader: view only.
    reader_group, _ = Group.objects.get_or_create(name="Reader")
    reader_group.permissions.set([
        article_perms["view"],
        newsletter_perms["view"],
    ])

    # Editor: view, change, delete (no add — editors don't create articles).
    editor_group, _ = Group.objects.get_or_create(name="Editor")
    editor_group.permissions.set([
        article_perms["view"],
        article_perms["change"],
        article_perms["delete"],
        newsletter_perms["view"],
        newsletter_perms["change"],
        newsletter_perms["delete"],
    ])

    # Journalist: full CRUD.
    journalist_group, _ = Group.objects.get_or_create(name="Journalist")
    journalist_group.permissions.set([
        article_perms["add"],
        article_perms["view"],
        article_perms["change"],
        article_perms["delete"],
        newsletter_perms["add"],
        newsletter_perms["view"],
        newsletter_perms["change"],
        newsletter_perms["delete"],
    ])
