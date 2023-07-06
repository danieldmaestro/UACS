from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UACS.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery('UACS')
app.conf.enable_utc=False

app.config_from_object(settings, namespace='CELERY')

app.conf.timezone='Africa/Lagos'

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)