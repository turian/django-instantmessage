# -*- coding: utf-8 -*-

from datetime import datetime
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST
from friends.models import friend_set_for
from im.models import ChatRequest, Chat, Message
from useractivity.utils import get_online_users

def render_to(request, template, context, string=True):
    func = render_to_response if not string else render_to_string
    return func(template, context_instance=RequestContext(request, context))

def json_response(data=None,
                  hash_func=lambda data: hash(repr(data)), **kwargs):
    return HttpResponse(simplejson.dumps({"payload": data,
                                          "hash": hash_func(data)}),
                        content_type="application/json",
                        **kwargs)


@login_required
def show_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if chat.users.filter(id=request.user.id).count():
        return render_to(request,
                         "im/chat.html",
                         {"chat": chat},
                         string=False)
    return HttpResponseForbidden()

@login_required
@require_GET
@never_cache
def sync_chat(request, chat_id):
    """
    View checks new messages for the logged in user within a Chat
    session with a given chat_id, renders them and returnes as
    a JSON encoded list.
    """
    chat = get_object_or_404(Chat, id=chat_id)

    # We store last sync timestamp to make sure the user recieves
    # all the messages since the last sync.
    now = datetime.now()
    timestamp = request.session.get(chat_id, now)
    request.session[chat_id] = now

    messages = chat.messages.exclude(author=request.user).filter(created__gt=timestamp)
    return json_response(map(lambda message: render_to(request,
                                                       "im/message.html",
                                                       {"message": message}),
                            messages))

@login_required
@require_POST
@never_cache
def send_message(request, chat_id):
    """
    View sends message from the logged in user to the Chat session
    with a given chat_id and returns a JSON encoded hash code for
    the newly created message.
    """
    chat = get_object_or_404(Chat, id=chat_id)
    text, event = request.POST.get("text"), request.POST.get("event", "")

    if text or event.isdigit():
        try:
            event = int(event)
        except ValueError:
            event = None

        message = Message(chat=chat,
                          author=request.user,
                          text=text,
                          event=event,
                          created=datetime.now())
        message.save()
        return json_response(render_to(request,
                                       "im/message.html",
                                       {"message": message}))

    # If there's no text to send or POST data contains a non-digit
    # event code (which is irrelevant, because EVENT_CHOICES should
    # be a list), or send() didn't return a hash code, the response
    # is HttpResponseBadRequest.
    return HttpResponseBadRequest("Empty message or unknown event code.")

@login_required
@require_GET
@never_cache
def sync_chatbox(request, target):
    """
    Depending on the target argument value, the view either returns
    new chat requests for the logged in user or a list of online users,
    provided by the useractivity app.
    """
    if target == "chat_requests":
        now = datetime.now()

        # Checking for the timestamp in session data, explanations
        # are below.
        timestamp = request.session.get("im:chat_requests:sync", now)
        chat_requests = ChatRequest.objects.incoming(request.user,
                                                     timestamp,)
        data = map(lambda chat_request: render_to(request,
                                                  "im/chat_request.html",
                                                  {"chat_request": chat_request}),
                   chat_requests)

        # Saving last check timestamp in session data, so we can later
        # determine which requests were already sent to the browser.
        request.session["im:chat_requests:sync"] = now
    elif target == "online_users":
        friends = friend_set_for(request.user)
        others = get_online_users() - friends
        if request.user in others:
            others.remove(request.user)

        data = render_to(request,
                         "im/userlist.html",
                         {"friends": friends,
                          "others": others})

    return json_response(data)

@login_required
@require_POST
def request_chat(request, user_id):
    """
    View creates a chat request from the logged in user to the
    user with a given id. If there's an active request for this
    pair of users, the view raises bad request, else json encoded
    success message is returned.
    """
    kwargs = {"user_to": get_object_or_404(User, id=user_id),
              "user_from": request.user}
    if not ChatRequest.objects.sent(**kwargs):
        chat_request = ChatRequest(created=datetime.now(), **kwargs)
        chat_request.save()

        return json_response(render_to(request,
                                       "im/chat_request.html",
                                       {"chat_request": chat_request}))
    return HttpResponseBadRequest("Duplicate request.")

@login_required
@require_POST
def accept_chat(request, chat_request_id):
    """
    View accepts chat request with a given id, creates a Chat instance
    for chat request sender and reciever and returns a json encoded url
    for the newly created chatroom.
    """
    chat_request = get_object_or_404(ChatRequest, id=chat_request_id)
    chat_request.accept()

    chat = Chat(request=chat_request,
                created=datetime.now())
    chat.save()
    chat.users.add(chat_request.user_to,
                   chat_request.user_from)

    return json_response(reverse("im_show_chat", args=[chat.id]))

@login_required
@require_POST
def decline_chat(request, chat_request_id):
    """
    View declines chat requets with a given id and returns an empty
    response.
    """
    chat_request = get_object_or_404(ChatRequest, id=chat_request_id)
    chat_request.decline()
    return json_response()
