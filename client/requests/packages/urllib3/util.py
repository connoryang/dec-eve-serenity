#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\util.py
from base64 import b64encode
from binascii import hexlify, unhexlify
from collections import namedtuple
from hashlib import md5, sha1
from socket import error as SocketError, _GLOBAL_DEFAULT_TIMEOUT
import time
try:
    from select import poll, POLLIN
except ImportError:
    poll = False
    try:
        from select import select
    except ImportError:
        select = False

try:
    SSLContext = None
    HAS_SNI = False
    import ssl
    from ssl import wrap_socket, CERT_NONE, PROTOCOL_SSLv23
    from ssl import SSLContext
    from ssl import HAS_SNI
except ImportError:
    pass

from .packages import six
from .exceptions import LocationParseError, SSLError, TimeoutStateError
_Default = object()

def current_time():
    return time.time()


class Timeout(object):
    DEFAULT_TIMEOUT = _GLOBAL_DEFAULT_TIMEOUT

    def __init__(self, total = None, connect = _Default, read = _Default):
        self._connect = self._validate_timeout(connect, 'connect')
        self._read = self._validate_timeout(read, 'read')
        self.total = self._validate_timeout(total, 'total')
        self._start_connect = None

    def __str__(self):
        return '%s(connect=%r, read=%r, total=%r)' % (type(self).__name__,
         self._connect,
         self._read,
         self.total)

    @classmethod
    def _validate_timeout(cls, value, name):
        if value is _Default:
            return cls.DEFAULT_TIMEOUT
        if value is None or value is cls.DEFAULT_TIMEOUT:
            return value
        try:
            float(value)
        except (TypeError, ValueError):
            raise ValueError('Timeout value %s was %s, but it must be an int or float.' % (name, value))

        try:
            if value < 0:
                raise ValueError('Attempted to set %s timeout to %s, but the timeout cannot be set to a value less than 0.' % (name, value))
        except TypeError:
            raise ValueError('Timeout value %s was %s, but it must be an int or float.' % (name, value))

        return value

    @classmethod
    def from_float(cls, timeout):
        return Timeout(read=timeout, connect=timeout)

    def clone(self):
        return Timeout(connect=self._connect, read=self._read, total=self.total)

    def start_connect(self):
        if self._start_connect is not None:
            raise TimeoutStateError('Timeout timer has already been started.')
        self._start_connect = current_time()
        return self._start_connect

    def get_connect_duration(self):
        if self._start_connect is None:
            raise TimeoutStateError("Can't get connect duration for timer that has not started.")
        return current_time() - self._start_connect

    @property
    def connect_timeout(self):
        if self.total is None:
            return self._connect
        if self._connect is None or self._connect is self.DEFAULT_TIMEOUT:
            return self.total
        return min(self._connect, self.total)

    @property
    def read_timeout(self):
        if self.total is not None and self.total is not self.DEFAULT_TIMEOUT and self._read is not None and self._read is not self.DEFAULT_TIMEOUT:
            if self._start_connect is None:
                return self._read
            return max(0, min(self.total - self.get_connect_duration(), self._read))
        elif self.total is not None and self.total is not self.DEFAULT_TIMEOUT:
            return max(0, self.total - self.get_connect_duration())
        else:
            return self._read


class Url(namedtuple('Url', ['scheme',
 'auth',
 'host',
 'port',
 'path',
 'query',
 'fragment'])):
    slots = ()

    def __new__(cls, scheme = None, auth = None, host = None, port = None, path = None, query = None, fragment = None):
        return super(Url, cls).__new__(cls, scheme, auth, host, port, path, query, fragment)

    @property
    def hostname(self):
        return self.host

    @property
    def request_uri(self):
        uri = self.path or '/'
        if self.query is not None:
            uri += '?' + self.query
        return uri

    @property
    def netloc(self):
        if self.port:
            return '%s:%d' % (self.host, self.port)
        return self.host


def split_first(s, delims):
    min_idx = None
    min_delim = None
    for d in delims:
        idx = s.find(d)
        if idx < 0:
            continue
        if min_idx is None or idx < min_idx:
            min_idx = idx
            min_delim = d

    if min_idx is None or min_idx < 0:
        return (s, '', None)
    return (s[:min_idx], s[min_idx + 1:], min_delim)


def parse_url(url):
    scheme = None
    auth = None
    host = None
    port = None
    path = None
    fragment = None
    query = None
    if '://' in url:
        scheme, url = url.split('://', 1)
    url, path_, delim = split_first(url, ['/', '?', '#'])
    if delim:
        path = delim + path_
    if '@' in url:
        auth, url = url.rsplit('@', 1)
    if url and url[0] == '[':
        host, url = url.split(']', 1)
        host += ']'
    if ':' in url:
        _host, port = url.split(':', 1)
        if not host:
            host = _host
        if port:
            if not port.isdigit():
                raise LocationParseError('Failed to parse: %s' % url)
            port = int(port)
        else:
            port = None
    elif not host and url:
        host = url
    if not path:
        return Url(scheme, auth, host, port, path, query, fragment)
    if '#' in path:
        path, fragment = path.split('#', 1)
    if '?' in path:
        path, query = path.split('?', 1)
    return Url(scheme, auth, host, port, path, query, fragment)


def get_host(url):
    p = parse_url(url)
    return (p.scheme or 'http', p.hostname, p.port)


def make_headers(keep_alive = None, accept_encoding = None, user_agent = None, basic_auth = None, proxy_basic_auth = None):
    headers = {}
    if accept_encoding:
        if isinstance(accept_encoding, str):
            pass
        elif isinstance(accept_encoding, list):
            accept_encoding = ','.join(accept_encoding)
        else:
            accept_encoding = 'gzip,deflate'
        headers['accept-encoding'] = accept_encoding
    if user_agent:
        headers['user-agent'] = user_agent
    if keep_alive:
        headers['connection'] = 'keep-alive'
    if basic_auth:
        headers['authorization'] = 'Basic ' + b64encode(six.b(basic_auth)).decode('utf-8')
    if proxy_basic_auth:
        headers['proxy-authorization'] = 'Basic ' + b64encode(six.b(proxy_basic_auth)).decode('utf-8')
    return headers


def is_connection_dropped(conn):
    sock = getattr(conn, 'sock', False)
    if not sock:
        return False
    if not poll:
        if not select:
            return False
        try:
            return select([sock], [], [], 0.0)[0]
        except SocketError:
            return True

    p = poll()
    p.register(sock, POLLIN)
    for fno, ev in p.poll(0.0):
        if fno == sock.fileno():
            return True


def resolve_cert_reqs(candidate):
    if candidate is None:
        return CERT_NONE
    if isinstance(candidate, str):
        res = getattr(ssl, candidate, None)
        if res is None:
            res = getattr(ssl, 'CERT_' + candidate)
        return res
    return candidate


def resolve_ssl_version(candidate):
    if candidate is None:
        return PROTOCOL_SSLv23
    if isinstance(candidate, str):
        res = getattr(ssl, candidate, None)
        if res is None:
            res = getattr(ssl, 'PROTOCOL_' + candidate)
        return res
    return candidate


def assert_fingerprint(cert, fingerprint):
    hashfunc_map = {16: md5,
     20: sha1}
    fingerprint = fingerprint.replace(':', '').lower()
    digest_length, rest = divmod(len(fingerprint), 2)
    if rest or digest_length not in hashfunc_map:
        raise SSLError('Fingerprint is of invalid length.')
    fingerprint_bytes = unhexlify(fingerprint.encode())
    hashfunc = hashfunc_map[digest_length]
    cert_digest = hashfunc(cert).digest()
    if not cert_digest == fingerprint_bytes:
        raise SSLError('Fingerprints did not match. Expected "{0}", got "{1}".'.format(hexlify(fingerprint_bytes), hexlify(cert_digest)))


def is_fp_closed(obj):
    if hasattr(obj, 'fp'):
        return obj.fp is None
    return obj.closed


if SSLContext is not None:

    def ssl_wrap_socket(sock, keyfile = None, certfile = None, cert_reqs = None, ca_certs = None, server_hostname = None, ssl_version = None):
        context = SSLContext(ssl_version)
        context.verify_mode = cert_reqs
        OP_NO_COMPRESSION = 131072
        context.options |= OP_NO_COMPRESSION
        if ca_certs:
            try:
                context.load_verify_locations(ca_certs)
            except Exception as e:
                raise SSLError(e)

        if certfile:
            context.load_cert_chain(certfile, keyfile)
        if HAS_SNI:
            return context.wrap_socket(sock, server_hostname=server_hostname)
        return context.wrap_socket(sock)


else:

    def ssl_wrap_socket(sock, keyfile = None, certfile = None, cert_reqs = None, ca_certs = None, server_hostname = None, ssl_version = None):
        return wrap_socket(sock, keyfile=keyfile, certfile=certfile, ca_certs=ca_certs, cert_reqs=cert_reqs, ssl_version=ssl_version)
