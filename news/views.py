# Путь: news/views.py
# Этот файл содержит представления (views) для обработки запросов и генерации ответов.
# Этот файл содержит представления для работы с новостями и пользователями.
from .mixins import user_passes_test  # Импортируем декоратор
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeDoneView
from django.shortcuts import render, get_object_or_404, redirect
from datetime import date
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import Article, Category, Rating
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .filters import ArticleFilter
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Получаем группы
            basic_group = Group.objects.get(name='basic')
            premium_group = Group.objects.get(name='premium')

            # Проверяем тип аккаунта
            if form.cleaned_data[
                'account_type'] == 'premium':  # Предполагается, что 'premium' соответствует выбранному премиум аккаунту
                user.groups.add(basic_group, premium_group)  # Добавляем в обе группы

                # Сохраняем реквизиты карточки
                user.card_number = request.POST.get('card_number')
                user.expiration_date = request.POST.get('expiration_date')
                user.cvv = request.POST.get('cvv')
                user.save()  # Сохраняем изменения
            else:
                user.groups.add(basic_group)  # Добавляем только в группу basic

            # Авторизуем пользователя с указанием backend
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('profile')  # Переход на профиль пользователя
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            # Обработка выбора статуса аккаунта
            account_type = request.POST.get('account_type', 'False')  # Получаем значение из формы
            user = form.save()

            # Обрабатываем выбор Premium/Basic
            if account_type == 'True':  # Если Premium
                premium_group = Group.objects.get(name='premium')
                user.groups.add(premium_group)  # Добавляем в группу premium
            else:  # Если Basic
                premium_group = Group.objects.get(name='premium')
                user.groups.remove(premium_group)  # Удаляем из группы premium

            # Обрабатываем выбор Reader/Author
            is_author = request.POST.get('is_author', 'False')  # Получаем значение из формы
            author_group = Group.objects.get(name='authors')  # Получаем группу authors

            if is_author == 'True':  # Если выбран Author
                user.groups.add(author_group)  # Добавляем в группу authors
            else:  # Если выбран Reader
                user.groups.remove(author_group)  # Убираем из группы authors

            user.save()  # Сохраняем изменения
            return redirect('profile')  # Перенаправляем обратно на страницу профиля
    else:
        form = CustomUserChangeForm(instance=request.user)

    # Проверяем группы пользователя для установки статуса
    is_premium = request.user.groups.filter(name='premium').exists()
    is_author = request.user.groups.filter(name='authors').exists()

    return render(request, 'news/edit_profile.html', {
        'form': form,
        'is_premium': is_premium,
        'is_author': is_author,
    })


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Сохранение новой сессии для пользователя после изменения пароля
            return redirect('profile')  # Перенаправление на страницу профиля после успешного изменения пароля
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'news/password_change_form.html', {'form': form})


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('password_change_done')

def permission_denied_view(request):
    return render(request, 'news/permission_denied.html')


def is_author_or_superuser(user):
    """
    Проверяет, является ли пользователь автором или суперпользователем.
    Если пользователь суперпользователь, проверка авторства не выполняется.
    """
    if user.is_authenticated:
        # Проверяем, является ли пользователь суперпользователем
        if user.is_superuser:
            return True

        # Проверяем, состоит ли пользователь в группе "authors"
        is_author = user.groups.filter(name='authors').exists()
        return is_author

    return False



def profile_view(request):
    return render(request, 'news/profile.html', {'user': request.user})



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('article_list')  # Перенаправление на список статей
    else:
        form = AuthenticationForm()
    return render(request, 'news/login.html', {'form': form})

def home(request):
    return render(request, 'news/home.html')

@user_passes_test(is_author_or_superuser)
def edit_news(request, pk):
    article = get_object_or_404(Article, pk=pk, article_type=True)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        if not title or not content:
            return render(request, 'news/edit_news.html', {
                'error': 'Все поля должны быть заполнены.',
                'article': article
            })

        article.title = title
        article.content = content
        article.publication_date = timezone.now()
        article.save()
        return redirect('article_detail', id=article.pk)

    return render(request, 'news/edit_news.html', {'article': article})

@user_passes_test(is_author_or_superuser)
def edit_article(request, pk):
    article = get_object_or_404(Article, pk=pk, article_type=False)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        if not title or not content:
            return render(request, 'news/articles/edit_article.html', {
                'error': 'Все поля должны быть заполнены.',
                'article': article
            })

        article.title = title
        article.content = content
        article.publication_date = timezone.now()
        article.save()
        return redirect('article_detail', id=article.pk)

    return render(request, 'news/articles/edit_article.html', {'article': article})

@user_passes_test(is_author_or_superuser)
def delete_news(request, pk):
    item = get_object_or_404(Article, pk=pk, type=True)
    if request.method == 'POST':
        item.delete()
        return redirect('article_list')
    return render(request, 'news/delete_news.html', {'item': item})

@user_passes_test(is_author_or_superuser)
def delete_article(request, pk):
    item = get_object_or_404(Article, pk=pk, type=False)
    if request.method == 'POST':
        item.delete()
        return redirect('article_list')
    return render(request, 'news/articles/delete_article.html', {'item': item})


@user_passes_test(is_author_or_superuser)
def create_news(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')

        # Проверка обязательных полей
        if not title or not category_id or not content:
            return render(request, 'news/create_news.html', {
                'error': 'Все поля должны быть заполнены.',
                'categories': Category.objects.all()
            })

        # Получаем категорию, если она выбрана
        category = Category.objects.filter(id=category_id).first() if category_id else None

        # Создание статьи с type_value = True
        Article.objects.create(
            title=title,
            author_profile=request.user.profile,  # Берем профиль текущего пользователя
            content=content,
            publication_date=timezone.now(),
            article_type=True,  # type_value всегда True
            category=category,
        )
        return redirect('article_list')

    # Передаем категории в форму при GET-запросе
    return render(request, 'news/create_news.html', {
        'categories': Category.objects.all()
    })


@user_passes_test(is_author_or_superuser)
def create_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')

        # Проверка обязательных полей
        if not title or not category_id or not content:
            return render(request, 'news/articles/create_article.html', {
                'error': 'Все поля должны быть заполнены.'
            })

        # Получаем категорию, если она выбрана
        category = Category.objects.filter(id=category_id).first() if category_id else None

        # Создание статьи с type_value = True
        Article.objects.create(
            title=title,
            author_profile=request.user.profile,  # Берем профиль текущего пользователя
            content=content,
            publication_date=timezone.now(),
            article_type=False,  # type_value всегда False
            category=category,
        )
        return redirect('article_list')

    # Передаем категории в форму при GET-запросе
    return render(request, 'news/articles/create_article.html', {
        'categories': Category.objects.all()
    })



def article_list(request):
    articles = Article.objects.all().order_by('-publication_date')

    # Пагинация
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    total_count = articles.count()

    return render(request, 'news/article_list.html', {
        'page_obj': page_obj,
        'total_count': total_count
    })

def article_detail(request, id):
    article = get_object_or_404(Article, id=id)
    return render(request, 'news/article_detail.html', {'article': article})

@login_required
def admin_page(request):
    if request.method == 'POST':
        request.session.pop('edit_mode', None)
        request.session.pop('delete_mode', None)

        record_type = request.POST.get('record_type')

        if 'create' in request.POST:
            if record_type == 'news':
                return redirect('create_news')
            elif record_type == 'article':
                return redirect('create_article')

        elif 'edit' in request.POST:
            request.session['edit_mode'] = True
            request.session['delete_mode'] = False
            request.session['record_type'] = record_type
            return redirect('article_search')

        elif 'delete' in request.POST:
            request.session['edit_mode'] = False
            request.session['delete_mode'] = True
            request.session['record_type'] = record_type
            return redirect('article_search')

    return render(request, 'news/admin_page.html')


def article_search(request):
    # Получаем все статьи, отсортированные по дате публикации
    queryset = Article.objects.all().order_by('-publication_date')

    # Фильтрация по типу статья или новость
    article_type_filter = request.GET.get('article_type')
    if article_type_filter == '1':
        queryset = queryset.filter(article_type=False)  # Статья
    elif article_type_filter == '0':
        queryset = queryset.filter(article_type=True)  # Новость

    # Фильтрация по автору
    author_filter = request.GET.get('author_profile')
    if author_filter:
        queryset = queryset.filter(author_profile__id=author_filter)

    # Фильтрация по рейтингу
    rating_filter = request.GET.get('type')
    if rating_filter:
        queryset = queryset.filter(rating__value=rating_filter)

    # Фильтрация по содержимому
    content_filter = request.GET.get('content')
    if content_filter:
        queryset = queryset.filter(content__icontains=content_filter)

    # Фильтрация по категории
    category_filter = request.GET.get('category')
    if category_filter:
        queryset = queryset.filter(category__id=category_filter)

    # Применяем фильтры
    filterset = ArticleFilter(request.GET, queryset=queryset)
    queryset = filterset.qs

    # Пагинация
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    # Получаем список авторов, состоящих в группе 'authors'
    authors = User.objects.filter(groups__name='authors')

    # Получаем список рейтингов
    ratings = Rating.objects.all()

    # Получаем список категорий
    categories = Category.objects.all()

    # Рендерим страницу
    return render(request, 'news/article_search.html', {
        'filterset': filterset,
        'page_obj': page_obj,
        'filter_params': request.GET.urlencode(),
        'authors': authors,
        'ratings': ratings,
        'categories': categories,
    })
