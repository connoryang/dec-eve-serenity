#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\connectionpool.py
import errno
import logging
from socket import error as SocketError, timeout as SocketTimeout
import socket
try:
    from queue import LifoQueue, Empty, Full
except ImportError:
    from Queue import LifoQueue, Empty, Full
    import Queue as _

from .exceptions import ClosedPoolError, ConnectTimeoutError, EmptyPoolError, HostChangedError, MaxRetryError, SSLError, TimeoutError, ReadTimeoutError, ProxyError
from .packages.ssl_match_hostname import CertificateError
from .packages import six
from .connection import port_by_scheme, DummyConnection, HTTPConnection, HTTPSConnection, VerifiedHTTPSConnection, HTTPException, BaseSSLError
from .request import RequestMethods
from .response import HTTPResponse
from .util import assert_fingerprint, get_host, is_connection_dropped, Timeout
xrange = six.moves.xrange
log = logging.getLogger(__name__)
_Default = object()

class ConnectionPool(object):
    scheme = None
    QueueCls = LifoQueue

    def __init__(self, host, port = None):
        host = host.strip('[]')
        self.host = host
        self.port = port

    def __str__(self):
        return '%s(host=%r, port=%r)' % (type(self).__name__, self.host, self.port)


_blocking_errnos = set([errno.EAGAIN, errno.EWOULDBLOCK])

class HTTPConnectionPool(ConnectionPool, RequestMethods):
    scheme = 'http'
    ConnectionCls = HTTPConnection

    def __init__(self, host, port = None, strict = False, timeout = Timeout.DEFAULT_TIMEOUT, maxsize = 1, block = False, headers = None, _proxy = None, _proxy_headers = None):
        ConnectionPool.__init__(self, host, port)
        RequestMethods.__init__(self, headers)
        self.strict = strict
        if not isinstance(timeout, Timeout):
            timeout = Timeout.from_float(timeout)
        self.timeout = timeout
        self.pool = self.QueueCls(maxsize)
        self.block = block
        self.proxy = _proxy
        self.proxy_headers = _proxy_headers or {}
        for _ in xrange(maxsize):
            self.pool.put(None)

        self.num_connections = 0
        self.num_requests = 0

    def _new_conn(self):
        self.num_connections += 1
        log.info('Starting new HTTP connection (%d): %s' % (self.num_connections, self.host))
        extra_params = {}
        if not six.PY3:
            extra_params['strict'] = self.strict
        conn = self.ConnectionCls(host=self.host, port=self.port, timeout=self.timeout.connect_timeout, **extra_params)
        if self.proxy is not None:
            conn.tcp_nodelay = 0
        return conn

    def _get_conn(self, timeout = None):
        conn = None
        try:
            conn = self.pool.get(block=self.block, timeout=timeout)
        except AttributeError:
            raise ClosedPoolError(self, 'Pool is closed.')
        except Empty:
            if self.block:
                raise EmptyPoolError(self, 'Pool reached maximum size and no more connections are allowed.')

        if conn and is_connection_dropped(conn):
            log.info('Resetting dropped connection: %s' % self.host)
            conn.close()
        return conn or self._new_conn()

    def _put_conn(self, conn):
        try:
            self.pool.put(conn, block=False)
            return
        except AttributeError:
            pass
        except Full:
            log.warning('HttpConnectionPool is full, discarding connection: %s' % self.host)

        if conn:
            conn.close()

    def _get_timeout(self, timeout):
        if timeout is _Default:
            return self.timeout.clone()
        elif isinstance(timeout, Timeout):
            return timeout.clone()
        else:
            return Timeout.from_float(timeout)

    def _make_request(self, conn, method, url, timeout = _Default, **httplib_request_kw):
        self.num_requests += 1
        timeout_obj = self._get_timeout(timeout)
        try:
            timeout_obj.start_connect()
            conn.timeout = timeout_obj.connect_timeout
            conn.request(method, url, **httplib_request_kw)
        except SocketTimeout:
            raise ConnectTimeoutError(self, 'Connection to %s timed out. (connect timeout=%s)' % (self.host, timeout_obj.connect_timeout))

        read_timeout = timeout_obj.read_timeout
        if hasattr(conn, 'sock'):
            if read_timeout == 0:
                raise ReadTimeoutError(self, url, 'Read timed out. (read timeout=%s)' % read_timeout)
            if read_timeout is Timeout.DEFAULT_TIMEOUT:
                conn.sock.settimeout(socket.getdefaulttimeout())
            else:
                conn.sock.settimeout(read_timeout)
        try:
            try:
                httplib_response = conn.getresponse(buffering=True)
            except TypeError:
                httplib_response = conn.getresponse()

        except SocketTimeout:
            raise ReadTimeoutError(self, url, 'Read timed out. (read timeout=%s)' % read_timeout)
        except BaseSSLError as e:
            if 'timed out' in str(e) or 'did not complete (read)' in str(e):
                raise ReadTimeoutError(self, url, 'Read timed out.')
            raise
        except SocketError as e:
            if e.errno in _blocking_errnos:
                raise ReadTimeoutError(self, url, 'Read timed out. (read timeout=%s)' % read_timeout)
            raise

        http_version = getattr(conn, '_http_vsn_str', 'HTTP/?')
        log.debug('"%s %s %s" %s %s' % (method,
         url,
         http_version,
         httplib_response.status,
         httplib_response.length))
        return httplib_response

    def close(self):
        old_pool, self.pool = self.pool, None
        try:
            while True:
                conn = old_pool.get(block=False)
                if conn:
                    conn.close()

        except Empty:
            pass

    def is_same_host(self, url):
        if url.startswith('/'):
            return True
        scheme, host, port = get_host(url)
        if self.port and not port:
            port = port_by_scheme.get(scheme)
        elif not self.port and port == port_by_scheme.get(scheme):
            port = None
        return (scheme, host, port) == (self.scheme, self.host, self.port)

    def urlopen(self, method, url, body = None, headers = None, retries = 3, redirect = True, assert_same_host = True, timeout = _Default, pool_timeout = None, release_conn = None, **response_kw):
        if headers is None:
            headers = self.headers
        if retries < 0:
            raise MaxRetryError(self, url)
        if release_conn is None:
            release_conn = response_kw.get('preload_content', True)
        if assert_same_host and not self.is_same_host(url):
            raise HostChangedError(self, url, retries - 1)
        conn = None
        if self.scheme == 'http':
            headers = headers.copy()
            headers.update(self.proxy_headers)
        try:
            conn = self._get_conn(timeout=pool_timeout)
            httplib_response = self._make_request(conn, method, url, timeout=timeout, body=body, headers=headers)
            response_conn = not release_conn and conn
            response = HTTPResponse.from_httplib(httplib_response, pool=self, connection=response_conn, **response_kw)
        except Empty:
            raise EmptyPoolError(self, 'No pool connections are available.')
        except BaseSSLError as e:
            raise SSLError(e)
        except CertificateError as e:
            raise SSLError(e)
        except TimeoutError as e:
            conn = None
            err = e
            if retries == 0:
                raise
        except (HTTPException, SocketError) as e:
            conn = None
            err = e
            if retries == 0:
                if isinstance(e, SocketError) and self.proxy is not None:
                    raise ProxyError('Cannot connect to proxy. Socket error: %s.' % e)
                else:
                    raise MaxRetryError(self, url, e)
        finally:
            if release_conn:
                self._put_conn(conn)

        if not conn:
            log.warn("Retrying (%d attempts remain) after connection broken by '%r': %s" % (retries, err, url))
            return self.urlopen(method, url, body, headers, (retries - 1), redirect, assert_same_host, timeout=timeout, pool_timeout=pool_timeout, release_conn=release_conn, **response_kw)
        redirect_location = redirect and response.get_redirect_location()
        if redirect_location:
            if response.status == 303:
                method = 'GET'
            log.info('Redirecting %s -> %s' % (url, redirect_location))
            return self.urlopen(method, redirect_location, body, headers, (retries - 1), redirect, assert_same_host, timeout=timeout, pool_timeout=pool_timeout, release_conn=release_conn, **response_kw)
        return response


class HTTPSConnectionPool(HTTPConnectionPool):
    scheme = 'https'
    ConnectionCls = HTTPSConnection

    def __init__(self, host, port = None, strict = False, timeout = None, maxsize = 1, block = False, headers = None, _proxy = None, _proxy_headers = None, key_file = None, cert_file = None, cert_reqs = None, ca_certs = None, ssl_version = None, assert_hostname = None, assert_fingerprint = None):
        HTTPConnectionPool.__init__(self, host, port, strict, timeout, maxsize, block, headers, _proxy, _proxy_headers)
        self.key_file = key_file
        self.cert_file = cert_file
        self.cert_reqs = cert_reqs
        self.ca_certs = ca_certs
        self.ssl_version = ssl_version
        self.assert_hostname = assert_hostname
        self.assert_fingerprint = assert_fingerprint

    def _prepare_conn(self, conn):
        if isinstance(conn, VerifiedHTTPSConnection):
            conn.set_cert(key_file=self.key_file, cert_file=self.cert_file, cert_reqs=self.cert_reqs, ca_certs=self.ca_certs, assert_hostname=self.assert_hostname, assert_fingerprint=self.assert_fingerprint)
            conn.ssl_version = self.ssl_version
        if self.proxy is not None:
            try:
                set_tunnel = conn.set_tunnel
            except AttributeError:
                set_tunnel = conn._set_tunnel

            set_tunnel(self.host, self.port, self.proxy_headers)
            conn.connect()
        return conn

    def _new_conn(self):
        self.num_connections += 1
        log.info('Starting new HTTPS connection (%d): %s' % (self.num_connections, self.host))
        if not self.ConnectionCls or self.ConnectionCls is DummyConnection:
            raise SSLError("Can't connect to HTTPS URL because the SSL module is not available.")
        actual_host = self.host
        actual_port = self.port
        if self.proxy is not None:
            actual_host = self.proxy.host
            actual_port = self.proxy.port
        extra_params = {}
        if not six.PY3:
            extra_params['strict'] = self.strict
        conn = self.ConnectionCls(host=actual_host, port=actual_port, timeout=self.timeout.connect_timeout, **extra_params)
        if self.proxy is not None:
            conn.tcp_nodelay = 0
        return self._prepare_conn(conn)


def connection_from_url(url, **kw):
    scheme, host, port = get_host(url)
    if scheme == 'https':
        return HTTPSConnectionPool(host, port=port, **kw)
    else:
        return HTTPConnectionPool(host, port=port, **kw)
