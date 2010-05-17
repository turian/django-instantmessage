# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib.auth.models import User
from django.db import models

class UserActivity(models.Model):
    """
    User activity model.

    Note: we don't force user uniqueness, but there allways
    will be one and only one UserActivity instance per user,
    because of the way UserActivityMiddleware works.

    >>> user = User(username="charlie")
    >>> user.save()
    >>> a = UserActivity(user=user, ip="192.168.255.1")
    >>> a.save()
    >>> a in user.last_activity.all()
    True

    >>> a = UserActivity(user=user, ip="192.168.255.1")
    >>> a.save()
    Traceback (most recent call last):
      File "<console>", line 1, in <module>
    IntegrityError: columns user_id, ip are not unique

    >>> print a
    charlie from 192.168.255.1 at ...
    """
    user = models.ForeignKey(User, related_name="last_activity")
    ip = models.IPAddressField()
    date = models.DateTimeField()

    class Meta:
        unique_together = [("user", "ip")]

    def __unicode__(self):
        return u"%s from %s at %s" % (self.user,
                                      self.ip,
                                      self.date)

    def save(self, **kwargs):
        if not self.date:
            self.date = datetime.now()
        super(UserActivity, self).save(**kwargs)
