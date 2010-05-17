# -*- coding: utf-8 -*-

from __future__ import with_statement
from carrot.connection import DjangoBrokerConnection
from carrot.messaging import Consumer, Publisher
from django.utils.functional import curry
from im.models import EVENT_CHOICES
from time import time as now
from uuid import uuid4

REQUEST_READY = 0
REQUEST_ACCEPTED = 1
REQUEST_DECLINED = 2
EVENT_MESSAGES = [message for event, message in EVENT_CHOICES]

defaults = {"auto_ack": True,
            "auto_delete": True,
            "exchange_type": "topic"}

def chatlog():
    with DjangoBrokerConnection() as connection:
        consumer = Consumer(connection=connection,
                            exchange="im.messages",
                            routing_key="chat.*",
                            queue="log",
                            **defaults)
        return list(consumer.iterqueue())

# Chat message exchange is handled by creating a queue
# for each of the participants, binded to the messages
# coming through the chat.ID route.
#
# Routes:
# ------
# chat.ID
#
# Queues:
# ID.USERNAME

def send(chat_id, author, text=None, event=None):
    if event is not None:
        try:
            text = EVENT_MESSAGES[event]
        except IndexError:
            return
    elif not text:
        return

    with DjangoBrokerConnection() as connection:
        publisher = Publisher(connection=connection,
                              exchange="im.messages",
                              routing_key="chat.%s" % chat_id,
                              **defaults)
        hash = str(uuid4())
        publisher.send({
            "hash": hash,
            "author": author,
            "text": text,
            "event": event,
            "timestamp": now()})

        return hash

def recieve(chat_id, user):
    with DjangoBrokerConnection() as connection:
        consumer = Consumer(connection=connection,
                            exchange="im.messages",
                            routing_key="chat.%s" % chat_id,
                            queue="%s.%s" % (chat_id, user),
                            **defaults)
        return list(consumer.iterqueue())

# Routes:
# ------
# requests.USER
#
# Queues:
# requests.USER

def status(user):
    with DjangoBrokerConnection() as connection:
        key = "requests.%s" % user
        consumer = Consumer(connection=connection,
                            exchange="im.requests",
                            routing_key=key,
                            queue=key,
                            **defaults)
        return list(consumer.iterqueue())

def _request(target, user, state, **extraparams):
    with DjangoBrokerConnection() as connection:
        publisher = Publisher(connection=connection,
                              exchange="im.requests",
                              routing_key="requests.%s" % target,
                              **defaults)
        hash = str(uuid4())
        data = {"hash": hash,
                "user": user,
                "state": state,
                "timestamp": now()}
        data.update(extraparams)

        publisher.send(data)

        return hash

request = curry(_request, state=REQUEST_READY)
accept  = curry(_request, state=REQUEST_ACCEPTED)
decline = curry(_request, state=REQUEST_DECLINED)
