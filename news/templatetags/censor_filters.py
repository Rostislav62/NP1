from django import template
import re

register = template.Library()

# Список запрещенных слов
PROHIBITED_WORDS = ['редиска', 'вредитель', 'вредители', 'подлец', 'сруны', 'срун', 'ссыкуны', 'лжец', 'подлеца', 'подлецы', 'редиски', 'ссыкунами']

@register.filter
def censor(value):
    if not isinstance(value, str):
        raise ValueError('Filter can only be applied to strings')

    def replace_word(match):
        word = match.group()
        if word.lower() in PROHIBITED_WORDS:
            return word[0] + '*' * (len(word) - 1)
        return word

    # Паттерн для поиска слов с учетом кавычек
    pattern = r'\b(?:' + '|'.join(re.escape(word) for word in PROHIBITED_WORDS) + r')\b'
    censored_text = re.sub(pattern, replace_word, value, flags=re.IGNORECASE)

    return censored_text

# from django import template
# import re
#
# register = template.Library()
#
# # Префиксы для поиска запрещенных слов
# PROHIBITED_WORD_PREFIXES = ['редис', 'вреди', 'подле', 'сру', 'ссыку', 'лже']
#
# @register.filter
# def censor(value):
#     if not isinstance(value, str):
#         raise ValueError('Filter can only be applied to strings')
#
#     def replace_word(match):
#         word = match.group()
#         # Проверяем, начинается ли слово с любого из префиксов
#         for prefix in PROHIBITED_WORD_PREFIXES:
#             if word.lower().startswith(prefix):
#                 return word[0] + '*' * (len(word) - 1)
#         return word
#
#     # Создаём паттерн для поиска слов, начинающихся с префиксов
#     pattern = r'\b(?:' + '|'.join(re.escape(prefix) for prefix in PROHIBITED_WORD_PREFIXES) + r'\w*)\b'
#     censored_text = re.sub(pattern, replace_word, value, flags=re.IGNORECASE)
#
#     return censored_text

