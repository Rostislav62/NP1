# Путь: news/views.py
# Этот файл содержит представления (views) для обработки запросов и генерации ответов.
# Этот файл содержит представления для работы с новостями и пользователями.
# from .mixins import user_passes_test  # Импортируем декоратор
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeDoneView
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import CustomUserChangeForm, CustomUserCreationForm
from .mixins import is_author_or_superuser
from .models import Article, Category, Rating
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .filters import ArticleFilter
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.conf import settings  # Импортируем настройки
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import Group
from django.core.mail import get_connection, send_mail
from django.contrib.auth import get_user_model



# Функция для проверки лимита публикаций
@user_passes_test(is_author_or_superuser, login_url='permission_denied')
def check_post_limit(request):
    """
    Проверка лимита публикаций за последние 24 часа и перенаправление на создание поста или страницу с сообщением.
    """
    # Получаем текущего пользователя и тип статьи
    user = request.user
    article_type = request.GET.get('article_type')

    # Проверяем, что параметр article_type указан и корректен
    if article_type not in ['news', 'article']:
        return HttpResponseBadRequest("Invalid article_type parameter")

    # Определяем лимиты для пользователя
    post_limit = 5 if user.groups.filter(name='premium').exists() else 3

    # Определяем временную метку для проверки публикаций за последние 24 часа
    time_threshold = timezone.now() - timezone.timedelta(days=1)

    # Считаем количество публикаций текущего пользователя за последние 24 часа
    posts_last_24_hours = Article.objects.filter(
        author_profile=user.profile,
        publication_date__gte=time_threshold
    ).count()

    # Проверка превышения лимита
    if posts_last_24_hours < post_limit:
        # Лимит не превышен, перенаправляем на страницу создания поста с параметром `article_type`
        return redirect(f'/create/?article_type={article_type}')
    else:
        # Лимит превышен, отправляем уведомление по email
        group_name = 'premium' if user.groups.filter(name='premium').exists() else 'basic'
        subject, message = EmailContentBuilder.generate_limit_email(user, post_limit, group_name)

        # Отправка письма пользователю
        send_custom_email(subject, message, [user.email], html_message=False)

        # Лимит превышен, отображаем сообщение об ошибке
        error_message = f"Вы не можете публиковать более {post_limit} постов в сутки."
        return render(request, 'news/post_limit_exceeded.html', {'error_message': error_message})


@user_passes_test(is_author_or_superuser, login_url='permission_denied')
def edit_post(request, pk):
    """
    Универсальное представление для редактирования статьи или новости.
    """
    # Извлечение article_type из параметров запроса
    article_type = request.GET.get('article_type')

    # Преобразование параметра в булево значение
    if article_type == '1':
        type_value = True
    elif article_type == '0':
        type_value = False
    else:
        return HttpResponseBadRequest("Invalid article_type")

    # Получение статьи или новости на основе pk и типа
    article = get_object_or_404(Article, pk=pk, article_type=type_value)

    # Выбор шаблона в зависимости от типа
    template_name = 'news/edit_news.html' if type_value else 'news/articles/edit_article.html'

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        if not title or not content:
            return render(request, template_name, {
                'error': 'Все поля должны быть заполнены.',
                'article': article
            })

        article.title = title
        article.content = content
        article.publication_date = timezone.now()
        article.save()
        return redirect('article_detail', id=article.pk)

    return render(request, template_name, {'article': article})



@user_passes_test(is_author_or_superuser, login_url='permission_denied')
def delete_post(request, pk):
    """
    Универсальное представление для удаления статьи или новости.
    """
    # Извлечение параметра article_type из GET-запроса
    article_type = request.GET.get('article_type')

    # Преобразование article_type в булевое значение (True или False)
    if article_type == '1':
        type_value = True
    elif article_type == '0':
        type_value = False
    else:
        return HttpResponseBadRequest("Invalid article_type")

    # Получаем объект статьи или новости на основе pk и типа
    item = get_object_or_404(Article, pk=pk, article_type=type_value)

    # Если запрос является POST, удаляем объект
    if request.method == 'POST':
        item.delete()
        return redirect('article_list')  # Перенаправляем на список статей

    # Выбираем шаблон в зависимости от типа статьи (True — новость, False — статья)
    template_name = 'news/delete_news.html' if type_value else 'news/articles/delete_article.html'
    return render(request, template_name, {'item': item})


@user_passes_test(is_author_or_superuser, login_url='permission_denied')
def create_post(request):
    # Получаем параметр article_type из GET запроса
    article_type = request.GET.get('article_type')

    # Проверка, что параметр указан
    if article_type not in ['news', 'article']:
        return HttpResponseBadRequest("Invalid article_type")

    # Определяем шаблон на основе типа статьи
    template_name = 'news/create_news.html' if article_type == 'news' else 'news/articles/create_article.html'

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')

        # Проверка обязательных полей
        if not title or not category_id or not content:
            return render(request, template_name, {
                'error': 'Все поля должны быть заполнены.',
                'categories': Category.objects.all()
            })

        # Получаем категорию, если она выбрана
        category = Category.objects.filter(id=category_id).first() if category_id else None

        # Создание статьи или новости
        article = Article.objects.create(
            title=title,
            author_profile=request.user.profile,  # Берем профиль текущего пользователя
            content=content,
            publication_date=timezone.now(),
            article_type=(article_type == 'news'),  # Если новость, то article_type = True, иначе False
            category=category,
        )

        # Отправка уведомления подписчикам категории
        send_notification(article, use_console_backend=True)

        return redirect('article_list')

    # Передаем категории в форму при GET-запросе
    return render(request, template_name, {
        'categories': Category.objects.all()
    })


# *************************************************
# Импорт необходимых модулей

class EmailContentBuilder:
    """
    Класс для создания содержимого писем.
    """

    @staticmethod
    def generate_welcome_email(user, variant=1):
        """
        Создаёт приветственное письмо для пользователя.

        Аргументы:
        - `user`: Объект пользователя (User), для которого создаётся письмо.
        - `variant`: Номер варианта письма (1, 2 или 3).

        Варианты:
        1. Приветственное сообщение и ссылка на активацию.
        2. Полное содержание профиля (логин, пароль, имя, фамилия, email, дата регистрации, группы и статус активации).
        3. Полное содержание профиля (логин, пароль, имя и фамилия).
        """
        subject = "Добро пожаловать на наш сайт!"

        if variant == 1:
            message = f"Здравствуй, {user.username}!\n\nСпасибо за регистрацию на нашем сайте. Пожалуйста, активируйте свой аккаунт, перейдя по следующей ссылке:\n\nhttp://127.0.0.1:8000/activate/{user.pk}/\n\nС уважением,\nКоманда сайта"
        elif variant == 2:
            message = (f"Здравствуй, {user.first_name} {user.last_name}!\n\n"
                       f"Спасибо за регистрацию на нашем сайте. Пожалуйста, активируйте свой аккаунт, перейдя по следующей ссылке:\n\n"
                       f"http://127.0.0.1:8000/activate/{user.pk}/\n\n"
                       f"Ваш профиль:\n"
                       f"Логин: {user.username}\n"
                       f"Email: {user.email}\n"
                       f"Дата регистрации: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}\n"
                       f"Группы: {', '.join([group.name for group in user.groups.all()])}\n"
                       f"Статус активации: {'Активен' if user.is_active else 'Не активен'}\n\n"
                       f"С уважением,\nКоманда сайта")
        elif variant == 3:
            message = (f"Здравствуй, {user.first_name} {user.last_name}!\n\n"
                       f"Спасибо за регистрацию на нашем сайте. Пожалуйста, активируйте свой аккаунт, перейдя по следующей ссылке:\n\n"
                       f"http://127.0.0.1:8000/activate/{user.pk}/\n\n"
                       f"Ваш профиль:\n"
                       f"Логин: {user.username}\n"
                       f"Пароль: {user.password} (пожалуйста, смените его после первого входа)\n\n"
                       f"С уважением,\nКоманда сайта")
        else:
            raise ValueError("Invalid variant specified for welcome email generation.")

        return subject, message

    @staticmethod
    def generate_subscription_email(user, category):
        """
        Создаёт письмо для уведомления пользователя о подписке на категорию.

        Аргументы:
        - `user`: Объект пользователя (User), который подписывается.
        - `category`: Объект категории (Category), на которую происходит подписка.
        """
        subject = f"Подписка на категорию {category.name}"
        message = f"Здравствуй, {user.username}!\n\nВы успешно подписались на категорию \"{category.name}\".\nС уважением,\nКоманда сайта."
        return subject, message

    @staticmethod
    def generate_notification_email(article, subscriber=None):
        """
        Создаёт письмо-уведомление для подписчиков о новой статье в категории.

        Аргументы:
        - `article`: Объект статьи (Article), о которой будет отправлено уведомление.
        - `subscriber`: Объект пользователя (User), которому будет отправлено письмо (для персонализированного приветствия).
        """
        category = article.category
        subject = article.title

        # Используем имя и фамилию подписчика, если они указаны, иначе используем "Здравствуй!"
        greeting = f"Здравствуй, {subscriber.first_name} {subscriber.last_name}!" if subscriber else "Здравствуй!"

        # Формируем краткое содержание письма
        message = (f"{greeting}\n\n"
                   f"В разделе {category.name} появилась новая публикация:\n\n"
                   f"Название: {article.title}\n"
                   f"Автор: {article.author_profile.user.get_full_name() or article.author_profile.user.username}\n\n"
                   f"Краткое содержание:\n"
                   f"{article.content[:50]}...\n\n"
                   f"Перейдите по ссылке, чтобы прочитать полностью: http://127.0.0.1:8000/news/{article.pk}\n\n"
                   f"С уважением,\n"
                   f"Команда сайта")

        return subject, message

    @staticmethod
    def generate_limit_email(user, post_limit, group_name):
        """
        Формирует письмо для уведомления пользователя о превышении лимита постов.

        Аргументы:
        - `user`: Объект пользователя, которому будет отправлено письмо.
        - `post_limit`: Лимит постов, который был достигнут (3 или 5).
        - `group_name`: Название группы пользователя (`basic` или `premium`).
        """
        if group_name == 'basic':
            subject = "Лимит публикаций достигнут"
            message = (
                f"Здравствуй, {user.first_name} {user.last_name}!\n\n"
                f"Вы не можете публиковать более 3 постов в сутки.\n"
                f"Для получения лимита в 5 постов в сутки, перейдите в группу Premium.\n\n"
                f"С уважением,\nКоманда сайта"
            )
        elif group_name == 'premium':
            subject = "Лимит публикаций для Premium-пользователей достигнут"
            message = (
                f"Здравствуй, {user.first_name} {user.last_name}!\n\n"
                f"Как пользователь группы Premium, Вы не можете публиковать более 5 постов в сутки.\n\n"
                f"С уважением,\nКоманда сайта"
            )
        return subject, message

    @staticmethod
    def generate_weekly_digest_email(category, new_articles):
        """
        Создание еженедельного дайджеста новых статей в категории.

        Аргументы:
        - `category`: Категория, по которой генерируется дайджест.
        - `new_articles`: Список новых статей в категории за последнюю неделю.
        """
        # Составляем заголовок письма
        subject = f"Еженедельный дайджест новых статей в категории {category.name}"

        # Формируем содержание письма
        message = f"Здравствуй!\n\nВот список новых статей в категории {category.name} за последнюю неделю:\n\n"

        for article in new_articles:
            message += f"Название: {article.title}\n"
            message += f"Автор: {article.author_profile.user.get_full_name() or article.author_profile.user.username}\n"
            message += f"Краткое содержание: {article.content[:100]}...\n"
            message += f"Прочитать статью: http://127.0.0.1:8000/news/{article.pk}\n\n"

        message += "С уважением,\nКоманда сайта"
        return subject, message



# *************************************************

@login_required
def subscribe_to_category(request, category_id):
    """
    Представление для подписки пользователя на категорию и отправки уведомления.
    """
    # Получаем категорию по ID
    category = get_object_or_404(Category, id=category_id)

    # Проверяем, если пользователь ещё не подписан на категорию
    if request.user not in category.subscribers.all():
        category.subscribers.add(request.user)

        # Создаём письмо о подписке
        subject, message = EmailContentBuilder.generate_subscription_email(request.user, category)

        # Отправка письма пользователю
        send_custom_email(subject, message, [request.user.email], html_message=False)

    return redirect('article_list')


def send_notification(article, use_console_backend=False):
    """
    Отправка уведомления подписчикам категории о новой статье.
    Параметр `use_console_backend` позволяет переключаться на консольный backend для тестирования.
    """
    # Получаем категорию статьи и всех подписчиков
    subscribers = article.category.subscribers.all()

    # Отправка письма каждому подписчику
    for subscriber in subscribers:
        # Генерируем письмо с указанием текущего подписчика
        subject, message = EmailContentBuilder.generate_notification_email(article=article, subscriber=subscriber)

        # Отправка письма
        send_custom_email(subject, message, [subscriber.email], use_console_backend=use_console_backend, html_message=True)


def send_custom_email(subject, message, recipient_list, use_console_backend=None, html_message=False):
    """
    Вспомогательная функция для отправки email.
    - `subject`: Тема письма.
    - `message`: Сообщение.
    - `recipient_list`: Список email адресов получателей.
    - `use_console_backend`: Переопределяет глобальную настройку использования консольного backend (True/False).
    - `html_message`: Использовать HTML формат сообщения (True/False).
    """
    # Используем глобальную настройку, если параметр use_console_backend не указан
    use_console_backend = settings.USE_CONSOLE_EMAIL_BACKEND if use_console_backend is None else use_console_backend

    # Получаем значение backend для использования
    email_backend = settings.EMAIL_BACKEND_CONSOLE if use_console_backend else settings.EMAIL_BACKEND_SMTP

    # Создаём подключение на основе выбранного backend
    connection = get_connection(backend=email_backend)

    # Отправка письма с использованием реального или консольного backend
    send_mail(
        subject=subject,
        message=message if not html_message else '',  # Если используется HTML, обычное сообщение не отправляется
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipient_list,
        fail_silently=False,
        html_message=message if html_message else None,
        connection=connection  # Используем тестовый или реальный backend на основе выбора
    )


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Регистрация как неактивного пользователя
            user.save()

            # Добавление пользователя в группу "basic"
            basic_group = Group.objects.get(name='basic')
            user.groups.add(basic_group)

            # Генерация приветственного письма в зависимости от варианта, указанного в .env
            email_variant = int(settings.WELCOME_EMAIL_VARIANT)
            subject, message = EmailContentBuilder.generate_welcome_email(user, variant=email_variant)

            # Отправка приветственного письма с ссылкой на активацию
            send_custom_email(subject, message, [user.email], html_message=False)

            return redirect('login')  # Перенаправляем на страницу входа
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def activate_account(request, user_id):
    """
    Активация пользователя по ссылке.
    """
    User = get_user_model()
    user = get_object_or_404(User, pk=user_id)

    # Активация аккаунта пользователя
    user.is_active = True
    user.save()
    return redirect('login')



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
    """
    Отображает страницу с сообщением о запрете доступа и перенаправлением.
    Сообщение и редирект зависят от статуса пользователя.
    """
    if not request.user.is_authenticated:
        # Пользователь не залогинен
        message = "Вы должны войти или зарегистрироваться"
        redirect_url = 'login'
    elif request.user.is_authenticated and not request.user.groups.filter(name='authors').exists():
        # Пользователь залогинен, но не является автором
        message = "Вы имеете только право на просмотр постов. Чтобы писать посты, смените тип пользователя на Author."
        redirect_url = 'profile'
    else:
        # Пользователь является автором или суперпользователем
        return redirect('/')  # На случай, если страница открыта по ошибке

    # Отладочная информация
    print(f"Message: {message}, Redirect URL: {redirect_url}")


    # Передача сообщения и URL для перенаправления в шаблон
    return render(request, 'news/permission_denied.html', {'message': message, 'redirect_url': redirect_url})



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


@login_required
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

# @login_required
# def admin_page(request):
#     if request.method == 'POST':
#         request.session.pop('edit_mode', None)
#         request.session.pop('delete_mode', None)
#
#         record_type = request.POST.get('record_type')
#
#         if 'create' in request.POST:
#             if record_type == 'news':
#                 return redirect('create_news')
#             elif record_type == 'article':
#                 return redirect('create_article')
#
#         elif 'edit' in request.POST:
#             request.session['edit_mode'] = True
#             request.session['delete_mode'] = False
#             request.session['record_type'] = record_type
#             return redirect('article_search')
#
#         elif 'delete' in request.POST:
#             request.session['edit_mode'] = False
#             request.session['delete_mode'] = True
#             request.session['record_type'] = record_type
#             return redirect('article_search')
#
#     return render(request, 'news/admin_page.html')


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
