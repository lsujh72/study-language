from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "study_language.settings")

app = Celery("study_language")

app.config_from_object("django.conf:settings")
app.conf.broker_url = settings.CELERY_BROKER_URL
app.autodiscover_tasks(settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
