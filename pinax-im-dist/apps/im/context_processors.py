# -*- coding: utf-8 -*-

from im import local_settings as settings

def im_settings(request):
    return dict((key, getattr(settings, key)) for key in ("IM_CHATBOX_POLL_EVERY",
                                                          "IM_CHAT_POLL_EVERY",
                                                          "IM_USERLIST_POLL_EVERY"))
