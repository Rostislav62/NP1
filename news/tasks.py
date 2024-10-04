# Путь: news/tasks.py
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore, register_events
from news.models import Article, Category
from .views import EmailContentBuilder

# Функция для отправки еженедельного дайджеста подписчикам категорий
def send_weekly_digest():
    """
    Отправка еженедельного дайджеста подписчикам категорий.
    """
    one_week_ago = timezone.now() - timedelta(days=7)

    # Находим все категории, в которых появились новые статьи за последнюю неделю
    categories_with_new_articles = Category.objects.filter(
        article__publication_date__gte=one_week_ago
    ).distinct()

    for category in categories_with_new_articles:
        # Получаем всех подписчиков данной категории
        subscribers = category.subscribers.all()

        # Формируем список новых статей
        new_articles = Article.objects.filter(
            category=category,
            publication_date__gte=one_week_ago
        )

        # Генерация содержимого письма
        subject, message = EmailContentBuilder.generate_weekly_digest_email(category, new_articles)

        # Отправляем письмо каждому подписчику
        for subscriber in subscribers:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[subscriber.email],
                fail_silently=False
            )


# Функция для отправки ежедневного дайджеста
def send_daily_digest():
    """
    Отправка ежедневного дайджеста подписчикам категорий.
    """
    one_day_ago = timezone.now() - timedelta(days=1)

    # Находим все категории, в которых появились новые статьи за последний день
    categories_with_new_articles = Category.objects.filter(
        article__publication_date__gte=one_day_ago
    ).distinct()

    for category in categories_with_new_articles:
        # Получаем всех подписчиков данной категории
        subscribers = category.subscribers.all()

        # Формируем список новых статей
        new_articles = Article.objects.filter(
            category=category,
            publication_date__gte=one_day_ago
        )

        # Генерация содержимого письма
        subject, message = EmailContentBuilder.generate_weekly_digest_email(category, new_articles)

        # Отправляем письмо каждому подписчику
        for subscriber in subscribers:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[subscriber.email],
                fail_silently=False
            )


def start_scheduler():
    """
    Функция для запуска планировщика и регистрации задач.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # # Регистрируем задачу с помощью cron: каждое воскресенье в 00:00 (еженедельный дайджест)
    # scheduler.add_job(
    #     send_weekly_digest,
    #     trigger=CronTrigger(day_of_week='sun', hour=0, minute=0),
    #     id="weekly_digest",
    #     name="Отправка еженедельного дайджеста",
    #     replace_existing=True,
    # )
    #
    # # Регистрируем задачу с интервалом: каждые 24 часа (ежедневный дайджест)
    # scheduler.add_job(
    #     send_daily_digest,
    #     trigger=IntervalTrigger(days=1),
    #     id="daily_digest",
    #     name="Отправка ежедневного дайджеста",
    #     replace_existing=True,
    # )
# для тестирования ***********************************************************
    scheduler.add_job(
        send_daily_digest,
        trigger="interval",
        minutes=1,  # Интервал в 1 минуту для быстрого тестирования
        id="daily_digest",
        replace_existing=True,
    )

    scheduler.add_job(
        send_weekly_digest,
        trigger="cron",
        day_of_week="*",
        hour=13,  # Текущий час
        minute=(timezone.now().minute + 1) % 60,  # Через 1 минуту от текущего времени
        id="weekly_digest",
        replace_existing=True,
    )

    # для тестирования ***********************************************************
    # Регистрируем события для планировщика и запускаем его
    register_events(scheduler)
    scheduler.start()
    print("Scheduler started!\nПланировщик запущен!")
