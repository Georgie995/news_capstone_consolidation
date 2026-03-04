from django.urls import path

from . import api_views

urlpatterns = [
    path("articles/", api_views.SubscribedArticlesAPIView.as_view(), name="api_articles"),
]
