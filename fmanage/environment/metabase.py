from fmanage.settings import *

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "fkmanage",
        "USER": env('FKMANAGE_DB_USER'),
        "PASSWORD": env('FKMANAGE_DB_PASSWORD'),
        #"HOST": "10.142.0.2",
        'HOST': "127.0.0.1",
        "PORT": env('FKMANAGE_DB_PORT'),
        "ATOMIC_REQUESTS": True,
    }
}

# Debug
DEBUG = False

# ENVIRONMENT
ENVIRONMENT = "metabase"

# LOG

LOGGING['handlers'] = {
    'logfile': {
        'level': 'INFO',
        # 'class': 'logging.FileHandler',
        'class': 'logging.handlers.RotatingFileHandler',
        'maxBytes': 50000,
        'backupCount': 2,
        'formatter': 'verbose',
        'filename': "/var/log/gunicorn/logfile",
    },
    'elogfile': {
        'level': 'ERROR',
        # 'class': 'logging.FileHandler',
        'class': 'logging.handlers.RotatingFileHandler',
        'maxBytes': 50000,
        'backupCount': 2,
        'formatter': 'verbose',
        'filename': "/var/log/gunicorn/elogfile",
    },
}

LOGGING['loggers'] = {
    'django': {
        'handlers': ['logfile', 'elogfile'],
        'level': 'INFO',
    },
}

# CORS_ORIGIN
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
)