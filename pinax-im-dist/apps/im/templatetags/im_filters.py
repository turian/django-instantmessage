# -*- coding: utf-8 -*-

import re
from django.conf import settings
from django.template import Library
from django.template.defaultfilters import stringfilter

register = Library()

theme = getattr(
    settings, "IM_EMOTICONS_THEME",
    {"angry.png": ":-X",
     "cheeky.png": "\^_+\^",
     "confused.png": ":-?S",
     "cringe.png": "&gt;\.&lt;",
     "cry.png": ":(?:&#39;-?|_)\(+",
     "echeeky.png": "\]:-&gt;",
     "grin.png": "(?<!]):->|:-?D+",
     "heart.png": "&lt;3+",
     "plain.png": ":-?\|",
     "sad.png": ":-?\(",
     "shades.png": "[8B]-?\)",
     "shock.png": "[oO]_[oO]",
     "sidelook.png": "&lt;_&lt;",
     "smile.png": ":\)+",
     "smile_nose1.png": ":-\)+",
     "tease.png": ":-?[pP]",
     "unsure.png": ":-?/",
     "wink.png": ";-?\)+"})

# Test string:
# :-X ^____^ :-S :S >.< :'-( :'( :_( ]:-> :-> :DD :-DD <3 <333 :| :-| :-( :(
# 8) 8-) B-) B) o_O O_O <_< :))))) :-)))) :-P :-p :-/ :/ ;-))) ;)))

# Compiling the theme.
theme = dict((name, re.compile(pattern)) \
             for name, pattern in theme.iteritems())

def emoticons(value):
    """
    Filter substitutes all text emoticons by the appropriate images.
    For the filter to work you need two variables set in settings.py
    * IM_EMOTICONS_URL: relative url for the directory with emoticons
    * IM_EMOTICONS_THEME: a mapping of filenames to emoticon regexps.
    """
    base = u"<img src=\"%s%s%%s\" alt=\"%%s\"/>" \
           % (settings.STATIC_URL,
              settings.IM_EMOTICONS_URL.lstrip("/"))
    for name, pattern in theme.iteritems():
        value = pattern.sub(lambda match: base % (name, match.group()), value)
    return value
emoticons = stringfilter(emoticons)
emoticons.is_safe=True

# If there's no emoticons url in the settings module,
# silently failing.
if not hasattr(settings, "IM_EMOTICONS_URL"):
    register.filter("emoticons", lambda value: value)
else:
    register.filter("emoticons", emoticons)
