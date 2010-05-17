# -*- coding: utf-8 -*-

import re
from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from useractivity.models import UserActivity

try:
    UPDATE_DELAY = timedelta(seconds=settings.ACTIVITY_UPDATE_DELAY)
except AttributeError:
    raise ImproperlyConfigured

RE_IP = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

def getip(request):
    """
    Function tries to extract remote IP address from request
    headers (REMOTE_ADDR, HTTP_X_FORWARDED_FOR). Returnes the
    IP address in case of success or an empty string elsewise.
    """
    raw_ip = request.META.get("HTTP_X_FORWARDED_FOR",
                          request.META.get("REMOTE_ADDR"))
    if raw_ip:
        # Some proxy servers use a list of IP addreses as a value
        # for the above headers, in such a case only the first IP
        # address is used (c) django-tracking
        match = RE_IP.match(raw_ip)
        if match:
            return match.group(0)
    return ""

class UserActivityMiddleware(object):
    """
    Middleware class, updating user activity information.

    To lower the database load, update only occurs when the
    difference between last update time, and current time
    exceeds settings.IM_UPDATE_DELAY.
    """
    def process_request(self, request):
        if not request.user.is_authenticated():
            return

        now, ip = datetime.now(), getip(request)
        try:
            activity = UserActivity.objects.get(user=request.user)
        except UserActivity.DoesNotExist:
            activity = UserActivity(user=request.user)

        # If the activity was just created or timestamp offset exceeds
        # maximum delay, updating timestamp and ip address.
        if not activity.pk or now - activity.date >= UPDATE_DELAY:
            activity.date = now
            activity.ip = ip
            activity.save()
