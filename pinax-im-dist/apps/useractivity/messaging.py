# -*- coding: utf-8 -*-

from __future__ import with_statement
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.serializers import serialize, deserialize
from django.utils.functional import curry
from carrot.connection import DjangoBrokerConnection
from carrot.messaging import Consumer, Publisher
from carrot.serialization import registry

try:
    delay = timedelta(seconds=settings.ACTIVITY_UPDATE_DELAY)
except AttributeError:
    raise ImproperlyConfigured

# Fetching settings.
fields = getattr(settings, "ACTIVITY_FIELDS", ["username"])
_serializer_type = getattr(settings,
                           "ACTIVITY_SERIALIZER",
                           "json")

# Registering Django serializer.
registry.register("django",
                  curry(serialize, _serializer_type, fields=fields),
                  curry(deserialize, _serializer_type),
                  content_type="application/django",
                  content_encoding="utf-8")

defaults = {"exchange": "onlineusers",
            "exchange_type": "fanout"}

def update_online_users(**extraparams):
    """
    Function exports all users, active within the last ACTIVITY_UPDATE_DELAY
    seconds, from the database to the "onlineusers" exchange. For efficiency
    reasons User models aren't serialized completely, only the fields, listed
    in ACTIVITY_FIELDS extracted.
    """
    with DjangoBrokerConnection() as connection:
        # Discarding all messages in the queue, before updating it.
        get_online_users(empty=True)
        interval = datetime.now() - delay

        params = defaults.copy()
        params.update(extraparams)
        publisher = Publisher(connection, **params)
        publisher.send(User.objects.filter(last_activity__date__gte=interval,
                                           is_active=1),
                       serializer="django")

def get_online_users(empty=False, **extraparams):
    with DjangoBrokerConnection() as connection:
        params = defaults.copy()
        params.update(extraparams)
        consumer = Consumer(connection,
                            queue="onlineusers",
                            **params)

        if empty:
            message = consumer.fetch(auto_ack=True)
            consumer.discard_all()
        else:
            message = consumer.fetch()
        return message.payload if message else ()

# Binding the queue to the onlineusers exchange.
get_online_users()
