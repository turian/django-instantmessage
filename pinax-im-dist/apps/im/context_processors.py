# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from template_utils.context_processors import settings_processor

if not hasattr(settings, "IM_POLL_DELAY"):
    raise ImproperlyConfigured("IM_POLL_DELAY missing in settings.py")
else:
    im_settings = settings_processor("IM_POLL_DELAY")
