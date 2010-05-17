# -*- coding: utf-8 -*-

import os.path
import posixpath
import re
import sys
from datetime import timedelta
from django.conf import settings
from pinax.utils.importlib import import_module

def define(name, default=None):
    return getattr(settings, name, default)

IM_EVENT_CHOICES = define("IM_EVENT_CHOICES", ((0, "is online"),
                                               (1, "is offline")))
IM_HISTORY_SIZE = define("IM_HISTORY_SIZE", 20)
IM_REQUESTS_EXPIRE_IN = define("IM_REQUESTS_EXPIRE_IN", timedelta(minutes=5))
IM_CHAT_POLL_EVERY = define("IM_POLL_EVERY", timedelta(seconds=5))
IM_CHATBOX_POLL_EVERY = define("IM_POLL_EVERY", timedelta(seconds=10))
IM_USERLIST_POLL_EVERY = define("IM_POLL_EVERY",
                                IM_CHATBOX_POLL_EVERY * 10)

IM_EMOTICONS_ROOT = define("IM_EMOTICONS_ROOT",
                           os.path.join(settings.PROJECT_ROOT,
                                        "media", "images", "emoticons"))

IM_EMOTICONS_URL = define("IM_EMOTICONS_URL",
                          posixpath.join(settings.STATIC_URL,
                                         "images", "emoticons"))

IM_EMOTICONS_THEME = define("IM_EMOTICONS_THEME", "16px_emoticons")

IM_EMOTICONS_TEMPLATE = u"<img src=\"%s/%%s\" alt=\"%%s\" />" \
                        % posixpath.join(IM_EMOTICONS_URL, IM_EMOTICONS_THEME)

sys.path.append(IM_EMOTICONS_ROOT)

# Trying to import the setup theme.
try:
    module = import_module(IM_EMOTICONS_THEME)
    theme = getattr(module, "theme")
except (ImportError, AttributeError), exc:
    IM_EMOTICONS_THEME = None
else:
    # Compiling the theme.
    IM_EMOTICONS_THEME = dict((name, re.compile(pattern)) \
                              for name, pattern in theme.iteritems())
