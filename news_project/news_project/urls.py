from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from news_app.views import home, register_view


urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', auth_views.LoginView.as_view(
        template_name='login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', register_view, name='register'),

    path('', home, name='home'),
    path('news/', include('news_app.urls')),

    # API endpoints
    path('api/', include('news_app.api_urls')),
]

