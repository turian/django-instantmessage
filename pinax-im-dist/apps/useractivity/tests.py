# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from useractivity import local_settings as settings
from useractivity.models import UserActivity
from useractivity.middleware import getip, UserActivityMiddleware

class RequestMock(object):
    """HttpRequest mock class."""

    def __init__(self, user=None, **kw):
        self.META, self.session = kw, {}

        if user:
            self.user = user


class TestMiddleware(TestCase):
    """Middleware module tests for UserActivity app."""

    def test_getip(self):
        ip = "85.84.72.63"
        trash = "85.84.ab.cd"

        self.failUnlessEqual("", getip(RequestMock()))
        self.failUnlessEqual(ip, getip(RequestMock(HTTP_X_FORWARDED_FOR=ip)))
        self.failUnlessEqual(ip, getip(RequestMock(REMOTE_ADDR=ip)))
        # HTTP_X_FORWARDED_FOR is extracted first.
        self.failUnlessEqual(ip, getip(RequestMock(HTTP_X_FORWARDED_FOR=ip,
                                                   REMOTE_ADDR="85.84.0.63")))

        # The case with a not well formed header.
        self.failUnlessEqual("", getip(
            RequestMock(HTTP_X_FORWARDED_FOR=trash)))
        self.failUnlessEqual("", getip(RequestMock(REMOTE_ADDR=trash)))

        # The case with a list of ip's in the header.
        self.failUnlessEqual(
            ip, getip(RequestMock(HTTP_X_FORWARDED_FOR="%s, 85.84.0.63" % ip)))
        self.failUnlessEqual(
            ip, getip(RequestMock(REMOTE_ADDR="%s, 85.84.0.63" % ip)))

    def test_user_activity(self):
        jack = User(username="jack")
        jack.save()

        # Making sure user jack wasn't spotted before.
        self.failIf(UserActivity.objects.filter(user=jack).count())

        UserActivityMiddleware().process_request(
            RequestMock(user=jack, REMOTE_ADDR="192.168.255.1"))

        # Middleware class should have created a new UserActivity
        # object for the user jack.
        activities = UserActivity.objects.filter(user=jack)
        self.failUnless(activities.count())

        activity  = activities[0]
        self.failUnlessEqual(jack, activity.user)
        self.failUnlessEqual("192.168.255.1", activity.ip)

        # Changing UserActivity for jack, so that the middleware
        # should update it once executed.
        delay = settings.ACTIVITY_UPDATE_DELAY * 20
        activity.date = datetime.now() - delay
        activity.save()

        # Changing user's ip address, to we can track the changes
        # done by middleware class.
        UserActivityMiddleware().process_request(
            RequestMock(user=jack, REMOTE_ADDR="192.168.255.2"))

        activities = UserActivity.objects.filter(user=jack)
        self.failUnless(activities.count())

        new_activity = activities[0]
        # The user should've stayed the same, but...
        self.failUnlessEqual(activity.user, new_activity.user)
        # ...date and ip address should've been updated!
        self.failIfEqual(activity.date, new_activity.date)
        self.failIfEqual(activity.ip, new_activity.ip)

        self.failUnlessEqual("192.168.255.2", new_activity.ip)
