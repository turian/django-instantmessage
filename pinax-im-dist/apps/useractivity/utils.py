# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib.auth.models import User
from django.core.cache import cache
from useractivity import local_settings as settings

def get_online_users():
    # First, checking if we have a cached set of online users.
    users = cache.get("useractivity:online_users")
    if users is None:
        # ..nothing? creating (updating) online users set in
        # cache and populating the template variable.
        interval = datetime.now() - settings.ACTIVITY_UPDATE_DELAY
        users = set(User.objects.filter(last_activity__date__gte=interval,
                                        is_active=1))
        cache.set("useractivity:online_users",
                  users,
                  settings.ACTIVITY_UPDATE_DELAY.seconds)
    return users
