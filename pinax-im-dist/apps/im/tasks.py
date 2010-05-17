# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

from celery.decorators import periodic_task
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from im import local_settings
from im.messaging import chatlog
from im.models import Chat, Message

def _chatlog(**kw):
    """Task periodically logs all "new" chat messages to the database."""
    log = chatlog.get_logger(**kw)
    log.info("Dumping chat messages to the database.")

    for message in chatlog():
        # Extracting chat_id from message routing_key.
        # Note: all routing keys are of form USER.CHAT_ID
        key = message.delivery_info["routing_key"]
        chat_id = key.split(".")[-1]

        # Payload keys were converted to unicode, converting
        # them back to strings, so that they can be used
        # as keyword args.
        data = dict((k.encode("utf-8"), v) \
                    for k, v in message.payload.iteritems())

        try:
            data["chat"] = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            log.debug("Chat %i doesn't exist, how come?", chat_id)
            continue

        try:
            data["author"] = User.objects.get(username=data["author"])
        except User.DoesNotExist:
            log.debug("Chat participant %s doesn't exist, how come?",
                      data["author"])
            continue

        # Converting UNIX timestamp to datetime.
        data["created"] = datetime.fromtimestamp(data["timestamp"])
        del data["timestamp"] # XXX: The field name should be timestamp also?

        Message(**data).save()


if local_settings.IM_CHATLOG:w
    delay = timedelta(minutes=local_settings.IM_CHATLOG_DELAY)
    chatlog = periodic_task(run_every=delay)(_chatlog)
else:
    chatlog = lambda: None
