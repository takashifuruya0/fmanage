from fmanage.settings import *

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "dev_fkmanage",
        "USER": env('FKMANAGE_DB_USER'),
        "PASSWORD": env('FKMANAGE_DB_PASSWORD'),
        'HOST': env("CLOUDSQL_IP"),
        "POST": env("CLOUDSQL_PORT"),
        "ATOMIC_REQUESTS": True,
    }
}
