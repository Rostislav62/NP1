# # Путь: news/urls.py
#
# from django.urls import path, include
# from django.contrib import admin
# from . import views
# from .views import article_search, create_news, create_article, CustomPasswordChangeView, CustomPasswordChangeDoneView
# from django.contrib.auth import views as auth_views
# from .views import edit_profile
# from django.shortcuts import redirect
# from django.urls import path
# from .views import edit_post
#
# urlpatterns = [
#     path('', views.home, name='home'),
#     path('admin/', admin.site.urls),
#
#     # Редактирование статьи или новости
#     path('news/<int:pk>/edit/', edit_post, {'article_type': True}, name='edit_news'),  # Редактирование новости
#     path('articles/<int:pk>/edit/', edit_post, {'article_type': False}, name='edit_article'),  # Редактирование статьи
#     # Универсальный маршрут для удаления статей и новостей
#     path('news/<int:pk>/delete/', views.delete_post, {'article_type': True}, name='delete_news'),
#     path('articles/<int:pk>/delete/', views.delete_post, {'article_type': False}, name='delete_article'),
#     # Универсальный маршрут для создания статей и новостей
#     path('news/create/', views.create_post, {'article_type': True}, name='create_news'),  # Создание новости
#     path('articles/create/', views.create_post, {'article_type': False}, name='create_article'),  # Создание статьи
#
#     path('news/', views.article_list, name='article_list'),
#     path('news/<int:id>/', views.article_detail, name='article_detail'),
#     path('news/search/', article_search, name='article_search'),  # Маршрут для поиска
#
#     # path('news/create/', create_news, name='create_news'),  # Создание новости
#     # path('news/<int:pk>/edit/', views.edit_news, name='edit_news'),
#     # path('news/<int:pk>/delete/', views.delete_news, name='delete_news'),  # Удаление новости
#
#     # path('news/articles/create/', create_article, name='create_article'),  # Создание статьи
#     # path('news/articles/<int:pk>/edit/', views.edit_article, name='edit_article'),
#     # path('news/articles/<int:pk>/delete/', views.delete_article, name='delete_article'),  # Удаление статьи
#
#     path('login/', auth_views.LoginView.as_view(template_name='news/login.html'), name='login'),
#     path('logout/', auth_views.LogoutView.as_view(), name='logout'),
#
#     path('register/', views.register, name='register'),
#
#     path('profile/', views.profile_view, name='profile'),
#
#     path('permission_denied/', views.permission_denied_view, name='permission_denied'),
#
#     path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
#     path('password_change/done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
#
#     path('edit_profile/', edit_profile, name='edit_profile'),
#
#     path('accounts/', include('allauth.urls')),
#     # Временное решение: перенаправление с /accounts/login/ на /login/
#     path('accounts/login/', lambda request: redirect('login'), name='accounts_login_redirect'),
#     path('subscribe/<int:category_id>/', views.subscribe_to_category, name='subscribe_to_category'),
#
# ]

# Путь: news/urls.py

from django.urls import path, include
from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

# Универсальные представления для обработки CRUD операций
from .views import (
    edit_post,
    delete_post,
    create_post,
    article_search,
    CustomPasswordChangeView,
    CustomPasswordChangeDoneView,
    edit_profile
)

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),

    # Административная панель
    path('admin/', admin.site.urls),

    # Просмотр и детали статей и новостей
    path('news/', views.article_list, name='article_list'),
    path('news/<int:id>/', views.article_detail, name='article_detail'),

    # Поиск статей и новостей
    path('news/search/', article_search, name='article_search'),

    # Универсальные маршруты для создания, редактирования и удаления статей и новостей
    path('create/', create_post, name='create_post'),  # Универсальный маршрут для создания статей и новостей
    path('edit/<int:pk>/', edit_post, name='edit_post'),  # Универсальный маршрут для редактирования статей и новостей
    path('delete/<int:pk>/', delete_post, name='delete_post'),  # Универсальный маршрут для удаления статей и новостей

    # Примеры использования:
    # - Создание новости: '/create/?article_type=news'
    # - Создание статьи: '/create/?article_type=article'
    # - Редактирование новости: '/edit/1/?article_type=news'
    # - Редактирование статьи: '/edit/1/?article_type=article'
    # - Удаление новости: '/delete/1/?article_type=news'
    # - Удаление статьи: '/delete/1/?article_type=article'

    # Авторизация и регистрация
    path('login/', auth_views.LoginView.as_view(template_name='news/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    # Профиль пользователя и изменение пароля
    path('profile/', views.profile_view, name='profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),

    # Разрешение на доступ
    path('permission_denied/', views.permission_denied_view, name='permission_denied'),

    # Подписка на категорию
    path('subscribe/<int:category_id>/', views.subscribe_to_category, name='subscribe_to_category'),

    # Временное решение: перенаправление с /accounts/login/ на /login/
    path('accounts/', include('allauth.urls')),
    path('accounts/login/', lambda request: redirect('login'), name='accounts_login_redirect'),

    # URL, который будет обрабатывать активацию пользователя при переходе по ссылке.
    path('activate/<int:user_id>/', views.activate_account, name='activate_account'),

    # Маршрут для запроса сброса пароля
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='news/password_reset.html'),
         name='password_reset'),

    # Маршрут для уведомления об отправке письма
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='news/password_reset_done.html'),
         name='password_reset_done'),

    # Маршрут для сброса пароля по ссылке из письма
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='news/password_reset_confirm.html'),
         name='password_reset_confirm'),

    # Маршрут для уведомления об успешном сбросе пароля
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='news/password_reset_complete.html'),
         name='password_reset_complete'),

    # Проверка лимита постов перед перенаправлением на создание
    path('check_post_limit/', views.check_post_limit, name='check_post_limit'),

]
