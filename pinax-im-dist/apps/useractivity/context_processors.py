# -*- coding: utf-8 -*-

from useractivity.messaging import get_online_users

def online_users(request):
    """Returns context variable with a list of users online."""
    if request.user.is_authenticated():
        return {"online_users": get_online_users()}
    return {}
