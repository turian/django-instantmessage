# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib.auth.models import User
from django.core.cache import cache
from useractivity.utils import get_online_users

def online_users(request):
    """Returns context variable with a set of users online."""
    if request.user.is_authenticated():
        return {"ONLINE_USERS": get_online_users()}
    return {}
