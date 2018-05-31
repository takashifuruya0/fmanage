from fmanage.settings import *

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "fkmanage",
        "USER": os.environ['FKMANAGE_DB_USER'],
        "PASSWORD": os.environ['FKMANAGE_DB_PASSWORD'],
        "HOST": "localhost",
        "POST": "",
    }
}
# update db settings
db_from_env = dj_database_url.config(conn_max_age=400)
DATABASES['default'].update(db_from_env)