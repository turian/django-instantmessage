# -*- coding: utf-8 -*-

from im import local_settings

def im_settings(request):
    return {"IM_POLL_DELAY": local_settings.IM_POLL_DELAY}
