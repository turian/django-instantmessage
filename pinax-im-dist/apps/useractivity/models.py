# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models

class UserActivity(models.Model):
    """User activity model."""
    user = models.ForeignKey(User, related_name="last_activity")
    ip = models.IPAddressField()
    date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "ip")]
