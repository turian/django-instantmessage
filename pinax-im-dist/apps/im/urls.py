# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns(
    "im.views",
    url("sync$", "chatbox.sync", name="im_sync_chatbox"),
    url("request/(?P<user>.+)/$", "chatbox.request_chat", name="im_request_chat"),
    url("decline/(?P<user>.+)/$", "chatbox.decline_chat", name="im_decline_chat"),
    url("accept/(?P<user>.+)/$", "chatbox.accept_chat", name="im_accept_chat"),
    url("chat/(?P<chat_id>\d+)/$", "chat.show", name="im_show_chat"),
    url("chat/(?P<chat_id>\d+)/sync/$", "chat.sync", name="im_sync_chat"),
    url("chat/(?P<chat_id>\d+)/send/$", "chat.send_message", name="im_send_message"),
    # FIXME: probably it's a good idea to change chat_id to username,
    # for the sacke of usability. Obviously, "im/chat/bobry" looks better
    # then "im/chat/12".
)
