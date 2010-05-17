# -*- coding: utf-8 -*-

from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models.query import QuerySet
from django.utils import simplejson
from django.utils.functional import curry, wraps

class JSONResponse(HttpResponse):
    def __init__(self, data={}, **kw):
        defaults = {"content_type": "application/json"}
        defaults.update(kw)
        if isinstance(data, QuerySet):
            data = serialize("json", data)
        else:
            data = simplejson.dumps(data, cls=DjangoJSONEncoder)
        super(JSONResponse, self).__init__(data, **defaults)


def require_variables(method, *variables):
    """
    Decorator to make a view only accept requests, that have non-None
    values in a given method's QueryDict for each of the variables from
    a given list.
    """
    def decorator(func):
        def inner(request, *args, **kw):
            data = getattr(request, method)
            for variable in variables:
                if not data.get(variable):
                    return HttpResponseBadRequest(
                        "Empty value for variable %s is not allowed."
                        % variable)
            return func(request, *args, **kw)
        return wraps(func)(inner)
    return decorator

require_POST_variables = curry(require_variables, "POST")
require_GET_variables = curry(require_variables, "GET")
