from fmanage.settings import *

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "fkmanage_dev",
        "USER": env('FKMANAGE_DB_USER'),
        "PASSWORD": env('FKMANAGE_DB_PASSWORD'),
        'HOST': env("FKMANAGE_DB_HOST"),
        "POST": "",
        "ATOMIC_REQUESTS": True,
    }
}
# update db settings
db_from_env = dj_database_url.config(conn_max_age=400)
DATABASES['default'].update(db_from_env)

# Logging
LOGGING['loggers'] = {
    'django': {
        'level': 'DEBUG',
    },
}

TOKEN_DRF = env("DRF_TOKEN")