from django.urls import path, include
from django.contrib import admin
from . import views
from .views import article_search, create_news, create_article, CustomPasswordChangeView, CustomPasswordChangeDoneView
from django.contrib.auth import views as auth_views
from .views import edit_profile

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),

    path('news/', views.article_list, name='article_list'),
    path('news/<int:id>/', views.article_detail, name='article_detail'),
    path('news/search/', article_search, name='article_search'),  # Маршрут для поиска

    path('news/create/', create_news, name='create_news'),  # Создание новости
    path('news/<int:pk>/edit/', views.edit_news, name='edit_news'),
    path('news/<int:pk>/delete/', views.delete_news, name='delete_news'),  # Удаление новости

    path('news/articles/create/', create_article, name='create_article'),  # Создание статьи
    path('news/articles/<int:pk>/edit/', views.edit_article, name='edit_article'),
    path('news/articles/<int:pk>/delete/', views.delete_article, name='delete_article'),  # Удаление статьи

    path('login/', auth_views.LoginView.as_view(template_name='news/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('register/', views.register, name='register'),

    path('profile/', views.profile_view, name='profile'),

    path('permission_denied/', views.permission_denied_view, name='permission_denied'),

    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),

    path('edit_profile/', edit_profile, name='edit_profile'),

    path('accounts/', include('allauth.urls')),

]
