"""
Django settings for fmanage project.

Generated by 'django-admin startproject' using Django 1.11.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from datetime import timedelta
import environ
env = environ.Env(DEBUG=(bool, False),)  # set default values and casting
environ.Env.read_env('.env')  # reading .env file


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^wvs5k)58b0g&wuwso^o@40ua728l1d_59w!81-b*93r8*ohv9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'dal',  # autocomplete-light
    'dal_select2',  # autocomplete-light
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',  # 追加
    'django.contrib.staticfiles',
    'kakeibo',
    'api',
    'accounts',
    'command',
    "asset",
    'web',
    'lancers',
    'django_extensions',
    'django.contrib.humanize',
    'pure_pagination',
    'django_nose',
    'rest_framework',
    'rest_framework.authtoken',  # <-- Here
    'djoser',  # jwt-simle, djoser
    'django_filters',
    'django_celery_results',
    'import_export',
    'allauth',  # 追加
    'allauth.account',  # 追加
    'allauth.socialaccount',  # 追加
    'allauth.socialaccount.providers.line',  # 追加
    'allauth.socialaccount.providers.twitter',  # 追加
    'allauth.socialaccount.providers.google',  # 追加
    'debug_toolbar',  # debug-toolbar
    'bootstrap_datepicker_plus',

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_currentuser.middleware.ThreadLocalUserMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',  # debug-toolbar
]

# debug-toolbar
INTERNAL_IPS = ['127.0.0.1', "172.22.0.1"]

ROOT_URLCONF = 'fmanage.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'fmanage.wsgi.application'

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, "staticfiles"),)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

######################################
# Authentication                     #
######################################

# Don't forget this little dude.
SITE_ID = 1

# ログインのリダイレクトURL
LOGIN_REDIRECT_URL = '/kakeibo'

# ログアウトのリダイレクトURL
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    "allauth.account.auth_backends.AuthenticationBackend",
)

SOCIALACCOUNT_PROVIDERS = {
    'line': {
        'SCOPE': ['profile', 'openid'],
    },
    'google': {
        "SCOPE": [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}
# loginURL
LOGIN_URL = '/accounts/login'
LOGOUT_REDIRECT_URL = '/accounts/login'
# login settings
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_LOGOUT_ON_GET = True


MEDIA_URL = '/document/'
MEDIA_ROOT = (
    os.path.join(BASE_DIR, 'document')
)


# Font Path
FONT_PATH = 'document/font/ipaexg.ttf'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format':
                '%(asctime)s [%(levelname)s] [%(process)d-%(thread)d] [%(module)s:%(lineno)d] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}

# django.conf.humanize
NUMBER_GROUPING = 3

# pagination
PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 10,
    'MARGIN_PAGES_DISPLAYED': 2,
    'SHOW_FIRST_PAGE_WHEN_INVALID': True,
}

# Goldpoint
GOLDPOINT_ID = env("GOLDPOINT_ID")
GOLDPOINT_PASSWORD = env("GOLDPOINT_PASSWORD")

# Slack
URL_SLACK_NAMS = env("URL_SLACK_NAMS")
URL_SLACK_LOG = env("URL_LOG_GAS")

# messages framework
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'info',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# test
# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
# NOSE_ARGS = [
#     '--with-coverage',  # get coverage
#     '--cover-html',  # output coverage to cover/ in html
#     '--cover-xml',   # output coverage to cover/ in xml
#     '--cover-package=kakeibo,asset,api,web',
# ]
# environment
ENVIRONMENT = "develop"

# Datastore
# from google.cloud import datastore
# client = datastore.Client()
# query = client.query(kind='SECRET')
# SECRET = {
#     d['key']: d['value'] for d in (query.fetch())
# }

# Twitter
TWITTER_ACCESS_KEY = env("TWITTER_ACCESS_KEY")
TWITTER_CONSUMER_SECRET = env('TWITTER_CONSUMER_SECRET')
TWITTER_CONSUMER_KEY = env("TWITTER_CONSUMER_KEY")
TWITTER_ACCESS_SECRET = env("TWITTER_ACCESS_SECRET")

# SBI
SBI_PASSWORD_ORDER = env("SBI_PASSWORD_ORDER")
SBI_PASSWORD_LOGIN = env("SBI_PASSWORD_LOGIN")
SBI_USER_ID = env("SBI_USER_ID")

# django-rest-framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # <-- And here
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
# simple-jwt
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT', ),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
}

# CELERY
CELERY_BROKER_URL = "redis://127.0.0.1:6379/1"
CELERY_RESULT_BACKEND = "django-db"


# CHOINCES
CHOICES_KAKEIBO_WAY = ((c, c) for c in [
    "支出（現金）", "支出（クレジット）", "支出（Suica）", "引き落とし", "収入", "振替"
])
CHOICES_TARGET_TYPE = ((c, c) for c in (
    "総資産目標", "投資目標", "投資元本",
))
CHOICES_ENTRY_TYPE = (
    ("短期", "短期"), ("中期", "中期"), ("長期", "長期"),
)
CHOICES_CURRENCY = (
    ("JPY", "JPY"), ("USD", "USD"),
)

# LANCERS
LANCERS_PASSWORD = env('LANCERS_PASSWORD')
LANCERS_USER_ID = env('LANCERS_USER_ID')
TOKEN_DRF = None
