# -*- coding: utf-8 -*-

from django.template import Library
from django.template.defaultfilters import stringfilter
from im.local_settings import (IM_EMOTICONS_THEME,
                               IM_EMOTICONS_TEMPLATE)

register = Library()

def emoticons(value):
    """
    Filter substitutes all text emoticons by the appropriate images.
    For the filter to work you need three variables set in settings.py
    * IM_EMOTICONS_ROOT: absolute path to the directory with emoticons
    * IM_EMOTICONS_URL: relative url for the directory with emoticons
    * IM_EMOTICONS_THEME: a name of the theme directory, which must contain
      an __init__.py file.
    More detailed description can be found in
    """
    for name, pattern in IM_EMOTICONS_THEME.iteritems():
        value = pattern.sub(
            lambda match: IM_EMOTICONS_TEMPLATE % (name, match.group()), value)
    return value
emoticons = stringfilter(emoticons)
emoticons.is_safe=True

# If resolving the theme failed (either because there's no theme
# with a setup name, or the theme doesn't contain a mapping), we
# make emoticons as a bypass filter.
if not IM_EMOTICONS_THEME:
    register.filter("emoticons", lambda value: value)
else:
    register.filter("emoticons", emoticons)
