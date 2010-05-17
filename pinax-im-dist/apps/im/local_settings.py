# -*- coding: utf-8 -*-

import os.path
import posixpath
import re
import sys
from django.conf import settings
from pinax.utils.importlib import import_module

def define(name, default):
    return getattr(settings, name, default)

IM_CHATLOG = define("IM_CHATLOG", True)
IM_CHATLOG_DELAY = define("IM_CHATLOG_DELAY", 5) # minutes

IM_POLL_DELAY = define("IM_POLL_DELAY", 5) # seconds

IM_EMOTICONS_ROOT = define("IM_EMOTICONS_ROOT",
                           os.path.join(settings.PROJECT_ROOT,
                                        "media", "images", "emoticons"))

IM_EMOTICONS_URL = define("IM_EMOTICONS_URL",
                          posixpath.join(settings.STATIC_URL,
                                         "images", "emoticons"))

IM_EMOTICONS_THEME = define("IM_EMOTICONS_THEME", "16px_emoticons")

# This one is undocumented, right :)
IM_EMOTICONS_TEMPLATE = u"<img src=\"%s/%%s\" alt=\"%%s\" />" \
                        % posixpath.join(IM_EMOTICONS_URL, IM_EMOTICONS_THEME)

# Appending emoticons dir to PYTHONPATH.
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
