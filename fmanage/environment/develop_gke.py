from fmanage.settings import *

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "fkmanage_gke",
        "USER": env('FKMANAGE_DB_USER'),
        "PASSWORD": env('FKMANAGE_DB_PASSWORD'),
        'HOST': env("FKMANAGE_DB_HOST"),
        "POST": "",
        "ATOMIC_REQUESTS": True,
    }
}

# Logging
LOGGING['handlers'] = {
    'console': {
        'level': 'DEBUG',
        'filters': ['require_debug_true'],
        'class': 'logging.StreamHandler',
        'formatter': 'verbose',
    },
}
LOGGING['loggers'] = {
    'django': {
        'level': 'INFO',
        'handlers': ['console'],
    },
    'django.db.backends': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
}

TOKEN_DRF = env("DRF_TOKEN")

# CORS_ORIGIN
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
)