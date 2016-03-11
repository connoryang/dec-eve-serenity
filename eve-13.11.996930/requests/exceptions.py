#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\exceptions.py
from .packages.urllib3.exceptions import HTTPError as BaseHTTPError

class RequestException(IOError):
    pass


class HTTPError(RequestException):

    def __init__(self, *args, **kwargs):
        self.response = kwargs.pop('response', None)
        super(HTTPError, self).__init__(*args, **kwargs)


class ConnectionError(RequestException):
    pass


class ProxyError(ConnectionError):
    pass


class SSLError(ConnectionError):
    pass


class Timeout(RequestException):
    pass


class URLRequired(RequestException):
    pass


class TooManyRedirects(RequestException):
    pass


class MissingSchema(RequestException, ValueError):
    pass


class InvalidSchema(RequestException, ValueError):
    pass


class InvalidURL(RequestException, ValueError):
    pass


class ChunkedEncodingError(RequestException):
    pass


class ContentDecodingError(RequestException, BaseHTTPError):
    pass
