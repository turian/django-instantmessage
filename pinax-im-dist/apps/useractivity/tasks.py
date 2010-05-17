# -*- coding: utf-8 -*-

from celery.task import PeriodicTask
from datetime import timedelta
from useractivity.messaging import update_online_users
from useractivity import local_settings as settings

class UpdateOnlineUsersTask(PeriodicTask):
    run_every = timedelta(seconds=settings.ACTIVITY_UPDATE_DELAY)

    def run(self, **kw):
        log = self.get_logger(**kw)
        log.info("Updating online users.")
        update_online_users()
