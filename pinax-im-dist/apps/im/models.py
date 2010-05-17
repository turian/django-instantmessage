# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from im import local_settings as settings


STATE_SENT = 0
STATE_ACCEPTED = 1
STATE_DECLINED = 2
STATE_CHOICES = ((STATE_SENT, "Sent"),
                 (STATE_ACCEPTED, "Accepted"),
                 (STATE_DECLINED, "Declined"))
STATE_CHOICES_DICT = dict(STATE_CHOICES)

class ChatRequestManager(models.Manager):
    def incoming(self, user, timestamp):
        """
        Method returns a list of incoming chat requests for a given
        user, created after the given timestamp. This includes:

        * chat requests, sent by a given user, either accepter or
          declined,
        * chat requests, sent to a given user from other users.
        """
        return self.get_query_set().filter(
            models.Q(created__gt=timestamp) & (
                models.Q(user_from=user,
                         state__in=[STATE_ACCEPTED, STATE_DECLINED]) |
                models.Q(user_to=user, state=STATE_SENT))
            )

    def sent(self, **kwargs):
        """
        Method returns a list of active chat requests, which don't have
        a related chat attached. A chat request is considered active
        if it is created within the expiration interval, defined by
        IM_REQUESTS_EXPIRE_IN option in the settings module.
        """
        timestamp = datetime.now() - settings.IM_REQUESTS_EXPIRE_IN
        return self.get_query_set().filter(state=STATE_SENT,
                                           created__gt=timestamp,
                                           chat=None,  **kwargs)


class ChatRequest(models.Model):
    """Chat request model."""
    user_to = models.ForeignKey(User, related_name="recieved_chat_requests")
    user_from = models.ForeignKey(User, related_name="sent_chat_requests")
    state = models.SmallIntegerField(choices=STATE_CHOICES, default=0)
    created = models.DateTimeField()

    objects = ChatRequestManager()

    class Meta:
        ordering = ["created"]

    def __unicode__(self):
        return u"%s -> %s [%s: %s]" % (self.user_from,
                                       self.user_to,
                                       self.created,
                                       STATE_CHOICES_DICT[self.state])

    def accept(self):
        self.state = STATE_ACCEPTED
        self.created = datetime.now()
        self.save()

    def decline(self):
        self.state = STATE_DECLINED
        self.created = datetime.now()
        self.save()

class Chat(models.Model):
    """
    User-to-user chat model.

    >>> c = Chat()
    >>> c.save()
    >>> c.created is not None
    True
    """
    request = models.OneToOneField(ChatRequest, related_name="chat", blank=True, null=True)
    users = models.ManyToManyField(User, related_name="chats")
    created = models.DateTimeField()

    class Meta:
        ordering = ["created"]

EVENT_CHOICES_DICT = dict(settings.IM_EVENT_CHOICES)

class MessageManager(models.Manager):
    def latest(self):
        return self.get_query_set()[:settings.IM_HISTORY_SIZE]


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
    author = models.ForeignKey(User, related_name="chat_messages")
    chat = models.ForeignKey(Chat, related_name="messages")
    event = models.IntegerField(null=True, blank=True,
                                choices=settings.IM_EVENT_CHOICES)
    text = models.TextField(null=True, blank=True)
    created = models.DateTimeField()

    objects = MessageManager()

    class Meta:
        ordering = ["created"]

    def __unicode__(self):
        if self.event is None:
            return unicode(self.text)
        return unicode(EVENT_CHOICES_DICT[self.event])
