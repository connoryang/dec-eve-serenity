#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\connection.py
import socket
from socket import timeout as SocketTimeout
try:
    from http.client import HTTPConnection as _HTTPConnection, HTTPException
except ImportError:
    from httplib import HTTPConnection as _HTTPConnection, HTTPException

class DummyConnection(object):
    pass


try:
    ssl = None
    HTTPSConnection = DummyConnection

    class BaseSSLError(BaseException):
        pass


    try:
        from http.client import HTTPSConnection as _HTTPSConnection
    except ImportError:
        from httplib import HTTPSConnection as _HTTPSConnection

    import ssl
    BaseSSLError = ssl.SSLError
except (ImportError, AttributeError):
    pass

from .exceptions import ConnectTimeoutError
from .packages.ssl_match_hostname import match_hostname
from .util import assert_fingerprint, resolve_cert_reqs, resolve_ssl_version, ssl_wrap_socket
port_by_scheme = {'http': 80,
 'https': 443}

class HTTPConnection(_HTTPConnection, object):
    default_port = port_by_scheme['http']
    tcp_nodelay = 1

    def _new_conn(self):
        try:
            conn = socket.create_connection((self.host, self.port), self.timeout, self.source_address)
        except AttributeError:
            conn = socket.create_connection((self.host, self.port), self.timeout)

        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, self.tcp_nodelay)
        return conn

    def _prepare_conn(self, conn):
        self.sock = conn
        if self._tunnel_host:
            self._tunnel()

    def connect(self):
        conn = self._new_conn()
        self._prepare_conn(conn)


class HTTPSConnection(HTTPConnection):
    default_port = port_by_scheme['https']

    def __init__(self, host, port = None, key_file = None, cert_file = None, strict = None, timeout = socket._GLOBAL_DEFAULT_TIMEOUT, source_address = None):
        try:
            HTTPConnection.__init__(self, host, port, strict, timeout, source_address)
        except TypeError:
            HTTPConnection.__init__(self, host, port, strict, timeout)

        self.key_file = key_file
        self.cert_file = cert_file

    def connect(self):
        conn = self._new_conn()
        self._prepare_conn(conn)
        self.sock = ssl.wrap_socket(conn, self.key_file, self.cert_file)


class VerifiedHTTPSConnection(HTTPSConnection):
    cert_reqs = None
    ca_certs = None
    ssl_version = None

    def set_cert(self, key_file = None, cert_file = None, cert_reqs = None, ca_certs = None, assert_hostname = None, assert_fingerprint = None):
        self.key_file = key_file
        self.cert_file = cert_file
        self.cert_reqs = cert_reqs
        self.ca_certs = ca_certs
        self.assert_hostname = assert_hostname
        self.assert_fingerprint = assert_fingerprint

    def connect(self):
        try:
            sock = socket.create_connection(address=(self.host, self.port), timeout=self.timeout)
        except SocketTimeout:
            raise ConnectTimeoutError(self, 'Connection to %s timed out. (connect timeout=%s)' % (self.host, self.timeout))

        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, self.tcp_nodelay)
        resolved_cert_reqs = resolve_cert_reqs(self.cert_reqs)
        resolved_ssl_version = resolve_ssl_version(self.ssl_version)
        if getattr(self, '_tunnel_host', None):
            self.sock = sock
            self._tunnel()
        self.sock = ssl_wrap_socket(sock, self.key_file, self.cert_file, cert_reqs=resolved_cert_reqs, ca_certs=self.ca_certs, server_hostname=self.host, ssl_version=resolved_ssl_version)
        if resolved_cert_reqs != ssl.CERT_NONE:
            if self.assert_fingerprint:
                assert_fingerprint(self.sock.getpeercert(binary_form=True), self.assert_fingerprint)
            elif self.assert_hostname is not False:
                match_hostname(self.sock.getpeercert(), self.assert_hostname or self.host)


if ssl:
    UnverifiedHTTPSConnection = HTTPSConnection
    HTTPSConnection = VerifiedHTTPSConnection
