# -*- coding: utf-8 -*-

from celery.task import PeriodicTask
from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from useractivity.messaging import update_online_users

try:
    UPDATE_DELAY = timedelta(seconds=settings.ACTIVITY_UPDATE_DELAY)
except AttributeError:
    raise ImproperlyConfigured

class UpdateOnlineUsersTask(PeriodicTask):
    run_every = UPDATE_DELAY

    def run(self, **kw):
        log = self.get_logger(**kw)
        log.info("Updating online users.")
        update_online_users()
