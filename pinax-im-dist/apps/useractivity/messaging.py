# -*- coding: utf-8 -*-

from __future__ import with_statement
from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from carrot.connection import DjangoBrokerConnection
from carrot.messaging import Consumer, Publisher
from useractivity.models import UserActivity

try:
    UPDATE_DELAY = timedelta(seconds=settings.ACTIVITY_UPDATE_DELAY)
except AttributeError:
    raise ImproperlyConfigured

USER_ATTRS = getattr(settings, "ACTIVITY_USER_DATA", ["username"])

def update_online_users(**extraparams):
    with DjangoBrokerConnection() as connection:
        # First clearing the queue.
        get_online_users(auto_ack=True)

        publisher = Publisher(connection=connection,
                              exchange="onlineusers",
                              exchange_type="fanout",
                              **extraparams)

        now = datetime.now()
        objects = UserActivity.objects.select_related(depth=1)
        for activity in objects.filter(date__gte=now - UPDATE_DELAY,
                                       user__is_active=1).all():
            publisher.send(
                dict((attr, getattr(activity.user, attr)) for attr in USER_ATTRS))

def get_online_users(**extraparams):
    with DjangoBrokerConnection() as connection:
        consumer = Consumer(connection=connection,
                            exchange="onlineusers",
                            exchange_type="fanout",
                            queue="onlineusers",
                            **extraparams)
        return list([ message.payload for message in consumer.iterqueue() ])

# Binding the queue to the onlineusers exchange.
get_online_users()
