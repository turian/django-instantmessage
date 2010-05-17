# -*- coding: utf-8 -*-

from datetime import datetime
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST
from im import messaging
from im.models import Chat
from im.utils import JSONResponse

@login_required
def show(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if chat.users.filter(id=request.user.id).count():
        return render_to_response("im/chat.html",
                                  context_instance=RequestContext(request,
                                                                  {"chat": chat}))
    return HttpResponseForbidden()

@login_required
@require_GET
@never_cache
def sync(request, chat_id):
    """
    View checks new messages for the logged in user within a Chat
    session with a given chat_id, renders them and returnes as
    a JSON encoded list.
    """
    get_object_or_404(Chat, id=chat_id)
    messages = list()

    for message in messaging.recieve(chat_id, request.user.username):
        message = message.payload
        # Since json encoder doesn't support datetime objects,
        # message time is passed as a UNIX timestamp. Converting
        # it back to datetime, to allow pretty date formatting
        # in the template code.
        message.update(
            timestamp=datetime.fromtimestamp(message["timestamp"]))
        messages.append(
            render_to_string("im/message.html",
                             context_instance=RequestContext(request, message)))

    return JSONResponse(messages)

@login_required
@require_POST
@never_cache
def send_message(request, chat_id):
    """
    View sends message from the logged in user to the Chat session
    with a given chat_id and returns a JSON encoded hash code for
    the newly created message.
    """
    # We don't really need this one, but why duplicate a ready-to-use
    # shortcut?
    get_object_or_404(Chat, id=chat_id)
    text, event = request.POST.get("text"), request.POST.get("event")

    if text or event.isdigit():
        try:
            event = int(event)
        except ValueError:
            event = None

        hash = messaging.send(chat_id,
                              request.user.username,
                              text,
                              event)

        if hash:
            return JSONResponse(hash)

    # If there's no text to send or POST data contains a non-digit
    # event code (which is irrelevant, because EVENT_CHOICES should
    # be a list), or send() didn't return a hash code, the response
    # is HttpResponseBadRequest.
    return JSONResponse("Empty message or unknown event code..",
                        status=400)
