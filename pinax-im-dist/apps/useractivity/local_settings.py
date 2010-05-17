# -*- coding: utf-8 -*-

from django.conf import settings

def define(name, default):
    return getattr(settings, name, default)

ACTIVITY_SERIALIZER = define("ACTIVITY_SERIALIZER", "json")
ACTIVITY_USER_FIELDS = define("ACTIVITY_USER_FIELDS", ("username", ))
ACTIVITY_UPDATE_DELAY = define("ACTIVITY_UPDATE_DELAY", 60) # seconds
