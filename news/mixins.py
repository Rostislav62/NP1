# Путь: news/mixins.py
# Этот файл содержит декораторы и миксины для проверки прав доступа пользователей.

# from functools import wraps
# from django.shortcuts import redirect
# from django.contrib import messages

# def user_passes_test(test_func):
#     """
#     Декоратор для проверки, проходит ли пользователь тест.
#     Если не проходит, перенаправляет на страницу с сообщением о недостатке прав.
#     """
#     def decorator(view_func):
#         @wraps(view_func)
#         def _wrapped_view(request, *args, **kwargs):
#             if not test_func(request):
#                 messages.error(request, 'У вас недостаточно прав для выполнения этого действия.')
#                 return redirect('permission_denied')  # Страница с сообщением о недостатке прав
#             return view_func(request, *args, **kwargs)
#         return _wrapped_view
#     return decorator

def is_author_or_superuser(user):
    """
    Проверка, является ли пользователь автором или суперпользователем.
    Если пользователь суперпользователь, проверка авторства не требуется.
    """
    if user.is_authenticated:
        # Проверяем, есть ли у пользователя профиль и является ли он автором
        return user.is_superuser or user.groups.filter(name='authors').exists()
    return False
