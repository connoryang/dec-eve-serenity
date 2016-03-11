#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\adapters.py
import socket
from .models import Response
from .packages.urllib3.poolmanager import PoolManager, proxy_from_url
from .packages.urllib3.response import HTTPResponse
from .packages.urllib3.util import Timeout as TimeoutSauce
from .compat import urlparse, basestring, urldefrag, unquote
from .utils import DEFAULT_CA_BUNDLE_PATH, get_encoding_from_headers, except_on_missing_scheme, get_auth_from_url
from .structures import CaseInsensitiveDict
from .packages.urllib3.exceptions import MaxRetryError
from .packages.urllib3.exceptions import TimeoutError
from .packages.urllib3.exceptions import SSLError as _SSLError
from .packages.urllib3.exceptions import HTTPError as _HTTPError
from .packages.urllib3.exceptions import ProxyError as _ProxyError
from .cookies import extract_cookies_to_jar
from .exceptions import ConnectionError, Timeout, SSLError, ProxyError
from .auth import _basic_auth_str
DEFAULT_POOLBLOCK = False
DEFAULT_POOLSIZE = 10
DEFAULT_RETRIES = 0

class BaseAdapter(object):

    def __init__(self):
        super(BaseAdapter, self).__init__()

    def send(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class HTTPAdapter(BaseAdapter):
    __attrs__ = ['max_retries',
     'config',
     '_pool_connections',
     '_pool_maxsize',
     '_pool_block']

    def __init__(self, pool_connections = DEFAULT_POOLSIZE, pool_maxsize = DEFAULT_POOLSIZE, max_retries = DEFAULT_RETRIES, pool_block = DEFAULT_POOLBLOCK):
        self.max_retries = max_retries
        self.config = {}
        self.proxy_manager = {}
        super(HTTPAdapter, self).__init__()
        self._pool_connections = pool_connections
        self._pool_maxsize = pool_maxsize
        self._pool_block = pool_block
        self.init_poolmanager(pool_connections, pool_maxsize, block=pool_block)

    def __getstate__(self):
        return dict(((attr, getattr(self, attr, None)) for attr in self.__attrs__))

    def __setstate__(self, state):
        self.proxy_manager = {}
        self.config = {}
        for attr, value in state.items():
            setattr(self, attr, value)

        self.init_poolmanager(self._pool_connections, self._pool_maxsize, block=self._pool_block)

    def init_poolmanager(self, connections, maxsize, block = DEFAULT_POOLBLOCK):
        self._pool_connections = connections
        self._pool_maxsize = maxsize
        self._pool_block = block
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block)

    def cert_verify(self, conn, url, verify, cert):
        if url.lower().startswith('https') and verify:
            cert_loc = None
            if verify is not True:
                cert_loc = verify
            if not cert_loc:
                cert_loc = DEFAULT_CA_BUNDLE_PATH
            if not cert_loc:
                raise Exception('Could not find a suitable SSL CA certificate bundle.')
            conn.cert_reqs = 'CERT_REQUIRED'
            conn.ca_certs = cert_loc
        else:
            conn.cert_reqs = 'CERT_NONE'
            conn.ca_certs = None
        if cert:
            if not isinstance(cert, basestring):
                conn.cert_file = cert[0]
                conn.key_file = cert[1]
            else:
                conn.cert_file = cert

    def build_response(self, req, resp):
        response = Response()
        response.status_code = getattr(resp, 'status', None)
        response.headers = CaseInsensitiveDict(getattr(resp, 'headers', {}))
        response.encoding = get_encoding_from_headers(response.headers)
        response.raw = resp
        response.reason = response.raw.reason
        if isinstance(req.url, bytes):
            response.url = req.url.decode('utf-8')
        else:
            response.url = req.url
        extract_cookies_to_jar(response.cookies, req, resp)
        response.request = req
        response.connection = self
        return response

    def get_connection(self, url, proxies = None):
        proxies = proxies or {}
        proxy = proxies.get(urlparse(url.lower()).scheme)
        if proxy:
            except_on_missing_scheme(proxy)
            proxy_headers = self.proxy_headers(proxy)
            if proxy not in self.proxy_manager:
                self.proxy_manager[proxy] = proxy_from_url(proxy, proxy_headers=proxy_headers, num_pools=self._pool_connections, maxsize=self._pool_maxsize, block=self._pool_block)
            conn = self.proxy_manager[proxy].connection_from_url(url)
        else:
            parsed = urlparse(url)
            url = parsed.geturl()
            conn = self.poolmanager.connection_from_url(url)
        return conn

    def close(self):
        self.poolmanager.clear()

    def request_url(self, request, proxies):
        proxies = proxies or {}
        scheme = urlparse(request.url).scheme
        proxy = proxies.get(scheme)
        if proxy and scheme != 'https':
            url, _ = urldefrag(request.url)
        else:
            url = request.path_url
        return url

    def add_headers(self, request, **kwargs):
        pass

    def proxy_headers(self, proxy):
        headers = {}
        username, password = get_auth_from_url(proxy)
        if username and password:
            headers['Proxy-Authorization'] = _basic_auth_str(username, password)
        return headers

    def send(self, request, stream = False, timeout = None, verify = True, cert = None, proxies = None):
        conn = self.get_connection(request.url, proxies)
        self.cert_verify(conn, request.url, verify, cert)
        url = self.request_url(request, proxies)
        self.add_headers(request)
        chunked = not (request.body is None or 'Content-Length' in request.headers)
        if stream:
            timeout = TimeoutSauce(connect=timeout)
        else:
            timeout = TimeoutSauce(connect=timeout, read=timeout)
        try:
            if not chunked:
                resp = conn.urlopen(method=request.method, url=url, body=request.body, headers=request.headers, redirect=False, assert_same_host=False, preload_content=False, decode_content=False, retries=self.max_retries, timeout=timeout)
            else:
                if hasattr(conn, 'proxy_pool'):
                    conn = conn.proxy_pool
                low_conn = conn._get_conn(timeout=timeout)
                try:
                    low_conn.putrequest(request.method, url, skip_accept_encoding=True)
                    for header, value in request.headers.items():
                        low_conn.putheader(header, value)

                    low_conn.endheaders()
                    for i in request.body:
                        low_conn.send(hex(len(i))[2:].encode('utf-8'))
                        low_conn.send('\r\n')
                        low_conn.send(i)
                        low_conn.send('\r\n')

                    low_conn.send('0\r\n\r\n')
                    r = low_conn.getresponse()
                    resp = HTTPResponse.from_httplib(r, pool=conn, connection=low_conn, preload_content=False, decode_content=False)
                except:
                    low_conn.close()
                    raise
                else:
                    conn._put_conn(low_conn)

        except socket.error as sockerr:
            raise ConnectionError(sockerr)
        except MaxRetryError as e:
            raise ConnectionError(e)
        except _ProxyError as e:
            raise ProxyError(e)
        except (_SSLError, _HTTPError) as e:
            if isinstance(e, _SSLError):
                raise SSLError(e)
            elif isinstance(e, TimeoutError):
                raise Timeout(e)
            else:
                raise

        r = self.build_response(request, resp)
        if not stream:
            r.content
        return r
