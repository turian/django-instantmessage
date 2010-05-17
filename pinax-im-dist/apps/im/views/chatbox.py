# -*- coding: utf-8 -*-

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST
from friends.models import friend_set_for
from im import messaging
from im.models import Chat
from im.utils import JSONResponse, require_POST_variables
from useractivity.messaging import get_online_users

@login_required
@require_GET
@never_cache
def sync(request):
    """
    View checks chat requests for the logged in user and returns
    them as a dict, together with a list of online users for the
    last settings.ACTIVITY_UPDATE_DELAY seconds.
    """
    requests = list()
    for message in messaging.status(unicode(request.user)):
        data = message.payload
        # We still need request's state value, since the js-part
        # will act differently based on the state.
        requests.append({"state": data["state"],
                         "hash": data["hash"],
                         "content": render_to_string("im/request.html", data)})

    online = list()
    friends = map(unicode, friend_set_for(request.user))
    for user in sorted(user["username"] for user in get_online_users()):
        # Preventing request user from appearing in the chatbox.
        if user == unicode(request.user):
            continue

        type = "friend" if user in friends else "user"
        online.append(
            render_to_string("im/user.html", {"user": user,
                                              "type": type}))

    return JSONResponse({"online": online,
                         "requests": requests})

@login_required
@require_POST
@never_cache
def request_chat(request, user):
    # Making sure the user with a given name actually exists.
    get_object_or_404(User, username=user)
    hash = messaging.request(user, unicode(request.user))

    # Creating a "check key", that will later be checked by the user
    # accepting the request.
    cache.set(hash, unicode(request.user))
    return JSONResponse(hash)

@login_required
@require_POST
@require_POST_variables("hash")
@never_cache
def decline_chat(request, user):
    # Making sure the user with a given name actually exists.
    get_object_or_404(User, username=user)

    # Making sure we had a chat request from user to request.user
    if cache.get(request.POST["hash"]) != user:
        return JSONResponse(
            "No chat request from %s to %s found." % (user, unicode(request.user)),
            status=400)

    # Removing the "check key".
    cache.delete(request.POST["hash"])

    return JSONResponse(messaging.decline(user, unicode(request.user)))

@login_required
@require_POST
@require_POST_variables("hash")
@never_cache
def accept_chat(request, user):
    # Making sure the user with a given name actually exists.
    user = get_object_or_404(User, username=user)

    # Making sure we had a chat request from user to request.user
    if cache.get(request.POST["hash"]) != unicode(user):
        return JSONResponse(
            "No chat request from %s to %s found." % (user, request.user),
            status=400)

    # Removing the "check key".
    cache.delete(request.POST["hash"])

    # Creating a Chat object and adding both users to participants.
    chat = Chat.objects.create()
    chat.save()
    chat.users.add(user, request.user)

    # Notifying chat initiator that chat request was accepted
    # and the chatroom is created.
    messaging.accept(unicode(user),
                     unicode(request.user),
                     chat_id=chat.id)

    # Initilizing message queues for the users. So that even
    # if one of the users joins late, he'll recieve all of
    # the messages sent when he was absent.
    messaging.recieve(chat.id, unicode(user))
    messaging.recieve(chat.id, unicode(request.user))

    return JSONResponse({"url": reverse("im_show_chat", args=[chat.id])})
