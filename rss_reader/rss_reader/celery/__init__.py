from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from rss_reader.celery.celery import TASKS

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rss_reader.settings')

app = Celery('rss_reader')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.beat_schedule = TASKS
app.conf.ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {'url': settings.CELERY_BROKER_URL, 'default_timeout': 60 * 5},
}
app.autodiscover_tasks()
