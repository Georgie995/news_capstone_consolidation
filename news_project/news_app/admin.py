from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Publisher, Article, Newsletter


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser."""
    # Use Django's built-in UserAdmin but add our custom fields
    fieldsets = UserAdmin.fieldsets + (
        ("Role and Subscriptions", {
            "fields": ("role", "subscribed_publishers", "subscribed_journalists"),
        }),
    )
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_superuser", "is_active", "groups")


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """Admin configuration for Publisher."""
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin configuration for Article."""
    list_display = ("title", "publisher", "author", "is_approved", "created_at")
    list_filter = ("is_approved", "publisher", "author")
    search_fields = ("title", "content")


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Admin configuration for Newsletter."""
    list_display = ("title", "publisher", "journalist", "created_at")
    list_filter = ("publisher", "journalist")
    search_fields = ("title", "content")

