# -*- coding: utf-8 -*-

from datetime import timedelta
from django.conf import settings

def define(name, default):
    return getattr(settings, name, default)

ACTIVITY_UPDATE_DELAY = define("ACTIVITY_UPDATE_DELAY", timedelta(seconds=60))
