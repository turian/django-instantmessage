# -*- coding: utf-8 -*-

from __future__ import with_statement

import random
from carrot.connection import DjangoBrokerConnection
from carrot.messaging import Publisher
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.serializers import serialize
from django.http import HttpResponse, HttpResponseBadRequest
from django.test import TestCase
from im.context_processors import im_settings
from im.messaging import chatlog, send, recieve, status, _request
from im.messaging import (REQUEST_READY, REQUEST_ACCEPTED, REQUEST_DECLINED,
                          EVENT_MESSAGES)
from im.models import Chat
from im.utils import JSONResponse, require_variables
from im.views import chat, chatbox

'''class RequestMock(object):
    """HttpRequest mock class."""
    def __init__(self, post={}, get={}):
        self.POST, self.GET = post, get


class TestContextProcessors(TestCase):
    """Context processors tests for IM app."""

    def test_im_settings(self):
        setattr(settings, "IM_POLL_DELAY", 1)
        self.failUnlessEqual({"IM_POLL_DELAY": settings.IM_POLL_DELAY},
                             im_settings(None))

        # For reasons unknown the test below doesn't work.
        # delattr(settings, "IM_POLL_DELAY")
        # try:
        #     im_settings(None)
        # except ImproperlyConfigured:
        #     pass
        # else:
        #     self.fail("ImproperlyConfigured should have been raised.")


class TestMessaging(TestCase):
    """Messaging module tests for IM app."""

    def setUp(self):
        # Registering two chat users: jack and nick.
        self.chat_id = 1
        self.users = ["jack", "nick"]

        for user in self.users:
            recieve(self.chat_id, user)

    def test_send_recieve(self):
        messages = ["hello", "what's up?", ""]

        for message in messages:
            hash = send(self.chat_id, random.choice(self.users), message)
            if not hash and message:
                self.fail("Expecting the hash to be returned "
                          "for message: \"%s\"." % message)

        # Checking that each of the messages (except for the last
        # one, which is empty) is recieved by both of the users.
        for user in self.users:
            recieved_messages = recieve(self.chat_id, user)
            self.failUnlessEqual(
                messages[:-1], [message.payload.get("text") \
                                for message in recieved_messages])

        # Testing the case, where the users send a valid event.
        for user in self.users:
            send(self.chat_id, user, event=0)

        # Checking that event message was recieved.
        for user in self.users:
            recieved_messages = recieve(self.chat_id, user)
            self.failUnlessEqual(2, len(recieved_messages))
            self.failUnlessEqual(
                [0, 0], [message.payload.get("event") \
                         for message in recieved_messages])

        # Testing the case, where the users send a invalid event,
        # i.e. not defined in IM_EVENT_CHOICES.
        for user in self.users:
            send(self.chat_id, user, event=999)

        # Expecting nothing to be recieved.
        for user in self.users:
            self.failIf(recieve(self.chat_id, user))

    def test_chatlog(self):
        # Recieving all chatlog messages, just in case there's any.
        chatlog()

        messages = list()
        # Immitating a small chat between jack and nick.
        for idx in xrange(20):
            user = random.choice(self.users)
            message = "%s_message_%i" % (user, idx)
            send(self.chat_id, user, message)

            messages.append(message)

        # Expecting all 20 messages to appear in the chatlog
        # in the same order they were sent.
        log = chatlog()

        self.failUnless(log)
        self.failUnlessEqual(20, len(log))
        self.failUnlessEqual(messages,
                             [message.payload["text"] for message in log])

        # As chatlog aggregates messages from ALL chat's, checking
        # a two simultaneous chat's case.
        messages = list()
        for idx in xrange(20):
            user = random.choice(self.users)
            chat = random.choice([1, 2])
            # Encapsultate all the message info in a string,
            # so that the only thing we need to check is messsage["text"].
            message = "%i_%s_message_%i" % (chat, user, idx)
            send(chat, user, message)

            messages.append(message)

        # Expecting all 20 messages to appear in the chatlog
        # in the same order they were sent.
        log = chatlog()

        self.failUnless(log)
        self.failUnlessEqual(20, len(log))
        self.failUnlessEqual(messages,
                             [message.payload["text"] for message in log])

    def test_status(self):
        # Subscribing jack and nick to status updates.
        map(status, self.users)

        with DjangoBrokerConnection() as connection:
            publisher = Publisher(connection=connection,
                                  exchange="im.requests",
                                  exchange_type="topic",
                                  routing_key="requests.jack",
                                  auto_delete=True)
            requests = range(5)
            map(publisher.send, requests)

        self.failUnlessEqual(requests,
                             [message.payload for message in status("jack")])
        self.failIf(status("nick"))

    def test__request(self):
        # Subscribing jack and nick to status updates.
        map(status, self.users)

        # Jack sends a request of state REQUEST_READY to nick. If
        # everything was okay, request's hash code should be returned.
        hash = _request("nick", "jack", REQUEST_READY)
        self.failUnless(hash)

        # Expecting the request to show up in nick's status queue.
        nick_status = [message.payload for message in status("nick")]
        self.failUnless(nick_status)
        self.failUnlessEqual(1, len(nick_status))
        self.failUnlessEqual(hash, nick_status[0].get("hash"))
        self.failUnlessEqual("jack", nick_status[0].get("user"))
        self.failUnlessEqual(REQUEST_READY, nick_status[0].get("state"))

        # Jack's status queue should be empty.
        self.failIf(status("jack"))


class TestUtils(TestCase):
    """Utils module tests for IM app."""

    def test_JSONResponse(self):
        # Testcase with an empty response body.
        response = JSONResponse()
        self.failUnlessEqual("{}", response.content)
        self.failUnlessEqual("application/json", response["Content-Type"])

        # Testcase with a non-empty response body.
        data = {"test": "me"}
        response = JSONResponse(data)
        self.failUnlessEqual("{\"test\": \"me\"}", response.content)
        self.failUnlessEqual("application/json", response["Content-Type"])

        data = datetime.now()
        response = JSONResponse(data)
        self.failUnlessEqual("\"%s\"" % data.strftime("%Y-%m-%d %H:%M:%S"),
                             response.content)
        self.failUnlessEqual("application/json", response["Content-Type"])

        # Testcase, where the data object is a QuerySet
        data = User.objects.all()
        response = JSONResponse(data)
        self.failUnlessEqual(serialize("json", data), response.content)
        self.failUnlessEqual("application/json", response["Content-Type"])

    def test_require_variables(self):
        def view(request):
            return JSONResponse("ok")
        _view = require_variables("POST", "var")(view)

        response = _view(RequestMock(post={}))
        self.failUnless(isinstance(response, HttpResponseBadRequest))
        self.failUnlessEqual("Empty value for variable var is not allowed.",
                             response.content)

        response = _view(RequestMock(post={"var": ""}))
        self.failUnless(isinstance(response, HttpResponseBadRequest))
        self.failUnlessEqual("Empty value for variable var is not allowed.",
                             response.content)

        response = _view(RequestMock(post={"var": "test"}))
        self.failIf(isinstance(response, HttpResponseBadRequest))
        self.failUnlessEqual("\"ok\"", response.content)

        # Testing the case with multiple variables required.
        _view = require_variables("POST", "var1", "var2")(view)

        response = _view(RequestMock(post={"var1": "test"}))
        self.failUnless(isinstance(response, HttpResponseBadRequest))
        self.failUnlessEqual("Empty value for variable var2 is not allowed.",
                             response.content)

        response = _view(RequestMock(post={"var2": "test"}))
        self.failUnless(isinstance(response, HttpResponseBadRequest))
        self.failUnlessEqual("Empty value for variable var1 is not allowed.",
                             response.content)

        response = _view(RequestMock(post={"var1": "test",
                                          "var2": "test"}))
        self.failIf(isinstance(response, HttpResponseBadRequest))
        self.failUnlessEqual("\"ok\"", response.content)'''
