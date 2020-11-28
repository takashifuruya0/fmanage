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
        "POST": "",
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
        'class': 'logging.FileHandler',
        'formatter': 'verbose',
        'filename': "/var/log/gunicorn/logfile",
    },
    'elogfile': {
        'level': 'ERROR',
        'class': 'logging.FileHandler',
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

