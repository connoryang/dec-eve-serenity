#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\exceptions.py


class HTTPError(Exception):
    pass


class PoolError(HTTPError):

    def __init__(self, pool, message):
        self.pool = pool
        HTTPError.__init__(self, '%s: %s' % (pool, message))

    def __reduce__(self):
        return (self.__class__, (None, None))


class RequestError(PoolError):

    def __init__(self, pool, url, message):
        self.url = url
        PoolError.__init__(self, pool, message)

    def __reduce__(self):
        return (self.__class__, (None, self.url, None))


class SSLError(HTTPError):
    pass


class ProxyError(HTTPError):
    pass


class DecodeError(HTTPError):
    pass


class MaxRetryError(RequestError):

    def __init__(self, pool, url, reason = None):
        self.reason = reason
        message = 'Max retries exceeded with url: %s' % url
        if reason:
            message += ' (Caused by %s: %s)' % (type(reason), reason)
        else:
            message += ' (Caused by redirect)'
        RequestError.__init__(self, pool, url, message)


class HostChangedError(RequestError):

    def __init__(self, pool, url, retries = 3):
        message = 'Tried to open a foreign host with url: %s' % url
        RequestError.__init__(self, pool, url, message)
        self.retries = retries


class TimeoutStateError(HTTPError):
    pass


class TimeoutError(HTTPError):
    pass


class ReadTimeoutError(TimeoutError, RequestError):
    pass


class ConnectTimeoutError(TimeoutError):
    pass


class EmptyPoolError(PoolError):
    pass


class ClosedPoolError(PoolError):
    pass


class LocationParseError(ValueError, HTTPError):

    def __init__(self, location):
        message = 'Failed to parse: %s' % location
        HTTPError.__init__(self, message)
        self.location = location
