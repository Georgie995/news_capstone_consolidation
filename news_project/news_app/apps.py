from django.apps import AppConfig


class NewsAppConfig(AppConfig):
    """Django app configuration for the news_app application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news_app'

    def ready(self):
        """Import signal handlers when the app is ready."""
        import news_app.signals  # noqa: F401

