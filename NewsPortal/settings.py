from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-na!pd)o*d=28hma3vgd5=vj&(i4v#my2&j#ggn8go2nvgntp(^'

DEBUG = True

ALLOWED_HOSTS = []



# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'news',
    'django_filters',
    'django.contrib.sites',

# The following apps are required:
    'django.contrib.auth',
    'django.contrib.messages',

    'allauth',
    'allauth.account',

    # Optional -- requires install using `django-allauth[socialaccount]`.
    'allauth.socialaccount',

    # 'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.yandex',  # Для Yandex
    # 'allauth.socialaccount.providers.google', # Для Google
    # 'allauth.socialaccount.providers.facebook',  # Для Facebook
    'django_extensions',
]

SITE_ID = 1


AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Настройки allauth
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
LOGIN_REDIRECT_URL = '/profile/'  # Перенаправление после входа


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Add the account middleware:
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'NewsPortal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # Папка для пользовательских шаблонов
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request', # `allauth` needs this from django
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

            ],
        },
    },
]


WSGI_APPLICATION = 'NewsPortal.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


SOCIAL_AUTH_GOOGLE_CLIENT_ID = '771106077612-36vhkl5km7dadmp0kjrdtsg82rm2ur56.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_SECRET = '<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>'
SOCIAL_AUTH_YANDEX_OAUTH2_KEY = '9272275d143b4775a2e9cfa4156b5f83'
SOCIAL_AUTH_YANDEX_OAUTH2_SECRET = '04b41453a2144c61b96e53e5a9e26bb7'




SOCIALACCOUNT_PROVIDERS = {
    # 'google': {
    #     'APP': {
    #         'client_id': SOCIAL_AUTH_GOOGLE_CLIENT_ID,
    #         'secret': SOCIAL_AUTH_GOOGLE_SECRET,
    #         'key': ''
    #     }
    # },
    'yandex': {
        'APP': {
            'client_id': SOCIAL_AUTH_YANDEX_OAUTH2_KEY,
            'secret': SOCIAL_AUTH_YANDEX_OAUTH2_SECRET,
            'key': ''
        }
    }
}



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Путь к папке, где будут храниться статические файлы
STATIC_URL = '/static/'

STATICFILES_DIRS = [BASE_DIR / "static", ] # Путь к папке static в корне проекта

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
