from fmanage.settings import *

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "fkmanage",
        "USER": env('FKMANAGE_DB_USER'),
        "PASSWORD": env('FKMANAGE_DB_PASSWORD'),
        'HOST': "127.0.0.1",
        "POST": "",
        "ATOMIC_REQUESTS": True,
    }
}

# Debug
DEBUG = False

# ENVIRONMENT
ENVIRONMENT = "metabase"

# LOG
LOGGING['loggers'] = {
    'django': {
        'level': 'DEBUG',
    },
}

