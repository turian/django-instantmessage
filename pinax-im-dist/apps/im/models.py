# -*- coding: utf-8 -*-

from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

class Chat(models.Model):
    """
    User-to-user chat model.

    >>> c = Chat()
    >>> c.save()
    >>> c.created is not None
    True
    """
    users = models.ManyToManyField(User, related_name="chats")
    created = models.DateTimeField(editable=False)

    class Meta:
        ordering = ["created"]

    def save(self, **kw):
        if not self.created:
            self.created = datetime.now()
        super(Chat, self).save(**kw)

try:
    EVENT_CHOICES = settings.IM_EVENT_CHOICES
except AttributeError:
    # Using defaults.
    EVENT_CHOICES = ((0, "is online"),
                     (1, "is offline"))

class Message(models.Model):
    """
    Chat message model.

    >>> user = User(username="jack")
    >>> user.save()
    >>> chat = Chat()
    >>> chat.save()

    >>> message = Message(author=user, chat=chat, text="hello")
    >>> message.save()
    >>> message.created is not None
    True
    >>> print message
    [...] jack: hello

    >>> message = Message(author=user, chat=chat, event=0)
    >>> message.save()
    >>> message.created is not None
    True
    >>> print message
    [...] jack is online
    """
    hash = models.CharField(primary_key=True, max_length=36)
    author = models.ForeignKey(User, related_name="chat_messages")
    chat = models.ForeignKey(Chat, related_name="messages")
    event = models.IntegerField(null=True, blank=True, choices=EVENT_CHOICES)
    text = models.TextField(null=True, blank=True)
    created = models.DateTimeField()

    class Meta:
        ordering = ["created"]

    def __unicode__(self):
        if self.event is None:
            text, sep = self.text, ": "
        else:
            text, sep = dict(EVENT_CHOICES)[self.event], " "

        return u"[%s] %s%s%s" % (self.created,
                                 self.author,
                                 sep, text)

    def save(self, **kw):
        if not self.created:
            self.created = datetime.now()
        super(Message, self).save(**kw)
