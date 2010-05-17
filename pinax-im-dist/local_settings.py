# -*- coding: utf-8 -*-

CELERY_BACKEND = "amqp"
CELERY_IMPORTS = ("tasks", )

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_VHOST = "/"
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"

# MIDDLEWARE_CLASSES += ("useractivity.middleware.UserActivityMiddleware", )
# TEMPLATE_CONTEXT_PROCESSORS += ("im.context_processors.im_settings", )
# INSTALLED_APPS += ("im",
#                    "useractivity",
#                    "celery")
