# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

class Chat(models.Model):
    """User-to-user chat model."""
    users = models.ManyToManyField(User, related_name="chats")
    created = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        ordering = ["created"]

try:
    EVENT_CHOICES = settings.IM_EVENT_CHOICES
except AttributeError:
    # Using defaults.
    EVENT_CHOICES = ((0, "is online"),
                     (1, "is offline"))

class Message(models.Model):
    """Chat message model."""
    hash = models.CharField(primary_key=True, max_length=36)
    author = models.ForeignKey(User, related_name="chat_messages")
    chat = models.ForeignKey(Chat, related_name="messages")
    event = models.IntegerField(null=True, blank=True, choices=EVENT_CHOICES)
    text = models.TextField(null=True, blank=True)
    created = models.DateTimeField()

    class Meta:
        ordering = ["created"]

    def __unicode__(self):
        if not self.event:
            return u"[%s] %s: %s" % (self.created,
                                     self.user.username,
                                     self.text)
        else:
            return u"[%s] %s" % (self.created,
                                 dict(EVENT_CHOICES)[self.event])
