from fmanage.settings import *

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "fkmanage",
        "USER": env('FKMANAGE_DB_USER'),
        "PASSWORD": env('FKMANAGE_DB_PASSWORD'),
        'HOST': env('FKMANAGE_DB_HOST'),
        "PORT": env('FKMANAGE_DB_PORT'),
        "ATOMIC_REQUESTS": True,
    }
}

# Debug
DEBUG = False

# ENVIRONMENT
ENVIRONMENT = "gke"

# CORS_ORIGIN
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
)