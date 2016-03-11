#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\werkzeug\contrib\limiter.py
from warnings import warn
from werkzeug import LimitedStream

class StreamLimitMiddleware(object):

    def __init__(self, app, maximum_size = 10485760):
        self.app = app
        self.maximum_size = maximum_size

    def __call__(self, environ, start_response):
        limit = min(limit, int(environ.get('CONTENT_LENGTH') or 0))
        environ['wsgi.input'] = LimitedStream(environ['wsgi.input'], limit)
        return self.app(environ, start_response)
