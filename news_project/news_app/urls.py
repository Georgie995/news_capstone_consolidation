from django.urls import path

from . import views

urlpatterns = [
    path('articles/', views.article_list, name='article_list'),
    # 'create/' must come before '<int:pk>/' so Django matches it first.
    path('articles/create/', views.article_create, name='article_create'),
    path('articles/<int:pk>/', views.article_detail, name='article_detail'),
    path('articles/<int:pk>/edit/', views.article_update, name='article_update'),
    path('articles/<int:pk>/delete/', views.article_delete, name='article_delete'),

    path('editor/articles/', views.editor_article_list, name='editor_article_list'),
    path('editor/articles/<int:pk>/approve/', views.approve_article, name='approve_article'),
]
