# Путь: news/apps.py

from django.apps import AppConfig

class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        import news.signals  # Импортируем signals для обработки сигналов приложения
        from .tasks import start_scheduler  # Импортируем функцию для запуска планировщика
        start_scheduler()  # Запускаем планировщик при инициализации приложения


