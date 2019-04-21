import os
from celery import Celery
from django.conf import settings as django_settings

# set the default Django settings module for the 'celery' program.
environment = "fmanage.environment.metabase" if django_settings.ENVIRONMENT == "metabase" else "fmanage.settings"
settings = os.getenv(
   "DJANGO_SETTINGS_MODULE", environment)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

app = Celery('fmanage')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(['fmanage'])
