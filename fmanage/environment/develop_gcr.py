from fmanage.settings import *

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "dev-fkmanage",
        "USER": env('FKMANAGE_DB_USER'),
        "PASSWORD": env('FKMANAGE_DB_PASSWORD'),
        'HOST': env('FKMANAGE_DB_HOST'),
        "PORT": env('FKMANAGE_DB_PORT'),
        "ATOMIC_REQUESTS": True,
    }
}

# Debug
DEBUG = True

# ENVIRONMENT
ENVIRONMENT = "develop_gcr"

# CORS_ORIGIN
CORS_ORIGIN_ALLOW_ALL = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LOGGING['handlers'] = {
    'stdout': {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
        'formatter': 'verbose',
    },
}

LOGGING['loggers'] = {
    'django': {
        'handlers': ['stdout', ],
        'level': 'INFO',
    },
}


# GCS
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_DEFAULT_ACL = "publicRead"
GS_FILE_OVERWRITE = True
GS_BUCKET_NAME = 'dev-back-fmanage'
# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = (os.path.join(BASE_DIR, "staticfiles"),)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"
# MEDIA
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
