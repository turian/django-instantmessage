# -*- coding: utf-8 -*-

CELERY_BACKEND = "amqp"
CELERY_IMPORTS = ("tasks", )

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_VHOST = "/"
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"

ACTIVITY_UPDATE_DELAY = 60 # seconds
ACTIVITY_USER_DATA = ("username", )

IM_EMOTICONS_URL = "/images/emoticons/"
IM_CHATLOG_DELAY = 1 # seconds
IM_POLL_DELAY = 5 # seconds

# MIDDLEWARE_CLASSES += ("useractivity.middleware.UserActivityMiddleware", )
# TEMPLATE_CONTEXT_PROCESSORS += ("im.context_processors.im_settings", )
# INSTALLED_APPS += ("im",
#                    "useractivity",
#                    "celery")
