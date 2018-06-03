from fmanage.settings import *

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
# update db settings
db_from_env = dj_database_url.config(conn_max_age=400)
DATABASES['default'].update(db_from_env)
