# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns(
    "im.views",
    url("chat/(?P<chat_id>\d+)/$",
        "show_chat",
        name="im_show_chat"),
    url("chat/(?P<chat_id>\d+)/sync/$",
        "sync_chat",
        name="im_sync_chat"),
    url("chat/(?P<chat_id>\d+)/send/$",
        "send_message",
        name="im_send_message"),

    url("chat/sync/online_users/$",
        "sync_chatbox",
        name="im_sync_users",
        kwargs={"target": "online_users"}),
    url("chat/sync/chat_requests/$",
        "sync_chatbox",
        name="im_sync_requests",
        kwargs={"target": "chat_requests"}),
    url("chat/request/(?P<user_id>\d+)/$",
        "request_chat",
        name="im_request_chat"),
    url("chat/decline/(?P<chat_request_id>\d+)/$",
        "decline_chat",
        name="im_decline_chat"),
    url("chat/accept/(?P<chat_request_id>\d+)/$",
        "accept_chat",
        name="im_accept_chat"),
)
