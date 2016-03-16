#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\sessions.py
import os
from collections import Mapping
from datetime import datetime
from .compat import cookielib, OrderedDict, urljoin, urlparse, builtin_str
from .cookies import cookiejar_from_dict, extract_cookies_to_jar, RequestsCookieJar, merge_cookies
from .models import Request, PreparedRequest
from .hooks import default_hooks, dispatch_hook
from .utils import to_key_val_list, default_headers, to_native_string
from .exceptions import TooManyRedirects, InvalidSchema
from .structures import CaseInsensitiveDict
from .adapters import HTTPAdapter
from .utils import requote_uri, get_environ_proxies, get_netrc_auth
from .status_codes import codes
REDIRECT_STATI = (codes.moved,
 codes.found,
 codes.other,
 codes.temporary_moved)
DEFAULT_REDIRECT_LIMIT = 30

def merge_setting(request_setting, session_setting, dict_class = OrderedDict):
    if session_setting is None:
        return request_setting
    if request_setting is None:
        return session_setting
    if not (isinstance(session_setting, Mapping) and isinstance(request_setting, Mapping)):
        return request_setting
    merged_setting = dict_class(to_key_val_list(session_setting))
    merged_setting.update(to_key_val_list(request_setting))
    for k, v in request_setting.items():
        if v is None:
            del merged_setting[k]

    return merged_setting


def merge_hooks(request_hooks, session_hooks, dict_class = OrderedDict):
    if session_hooks is None or session_hooks.get('response') == []:
        return request_hooks
    if request_hooks is None or request_hooks.get('response') == []:
        return session_hooks
    return merge_setting(request_hooks, session_hooks, dict_class)


class SessionRedirectMixin(object):

    def resolve_redirects(self, resp, req, stream = False, timeout = None, verify = True, cert = None, proxies = None):
        i = 0
        while 'location' in resp.headers and resp.status_code in REDIRECT_STATI:
            prepared_request = req.copy()
            resp.content
            if i >= self.max_redirects:
                raise TooManyRedirects('Exceeded %s redirects.' % self.max_redirects)
            resp.close()
            url = resp.headers['location']
            method = req.method
            if url.startswith('//'):
                parsed_rurl = urlparse(resp.url)
                url = '%s:%s' % (parsed_rurl.scheme, url)
            parsed = urlparse(url)
            url = parsed.geturl()
            if not urlparse(url).netloc:
                url = urljoin(resp.url, requote_uri(url))
            else:
                url = requote_uri(url)
            prepared_request.url = to_native_string(url)
            if resp.status_code == codes.see_other and method != 'HEAD':
                method = 'GET'
            if resp.status_code == codes.found and method != 'HEAD':
                method = 'GET'
            if resp.status_code == codes.moved and method == 'POST':
                method = 'GET'
            prepared_request.method = method
            if resp.status_code not in (codes.temporary, codes.resume):
                if 'Content-Length' in prepared_request.headers:
                    del prepared_request.headers['Content-Length']
                prepared_request.body = None
            headers = prepared_request.headers
            try:
                del headers['Cookie']
            except KeyError:
                pass

            extract_cookies_to_jar(prepared_request._cookies, prepared_request, resp.raw)
            prepared_request._cookies.update(self.cookies)
            prepared_request.prepare_cookies(prepared_request._cookies)
            resp = self.send(prepared_request, stream=stream, timeout=timeout, verify=verify, cert=cert, proxies=proxies, allow_redirects=False)
            extract_cookies_to_jar(self.cookies, prepared_request, resp.raw)
            i += 1
            yield resp


class Session(SessionRedirectMixin):
    __attrs__ = ['headers',
     'cookies',
     'auth',
     'timeout',
     'proxies',
     'hooks',
     'params',
     'verify',
     'cert',
     'prefetch',
     'adapters',
     'stream',
     'trust_env',
     'max_redirects']

    def __init__(self):
        self.headers = default_headers()
        self.auth = None
        self.proxies = {}
        self.hooks = default_hooks()
        self.params = {}
        self.stream = False
        self.verify = True
        self.cert = None
        self.max_redirects = DEFAULT_REDIRECT_LIMIT
        self.trust_env = True
        self.cookies = cookiejar_from_dict({})
        self.adapters = OrderedDict()
        self.mount('https://', HTTPAdapter())
        self.mount('http://', HTTPAdapter())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def prepare_request(self, request):
        cookies = request.cookies or {}
        if not isinstance(cookies, cookielib.CookieJar):
            cookies = cookiejar_from_dict(cookies)
        merged_cookies = merge_cookies(merge_cookies(RequestsCookieJar(), self.cookies), cookies)
        auth = request.auth
        if self.trust_env and not auth and not self.auth:
            auth = get_netrc_auth(request.url)
        p = PreparedRequest()
        p.prepare(method=request.method.upper(), url=request.url, files=request.files, data=request.data, headers=merge_setting(request.headers, self.headers, dict_class=CaseInsensitiveDict), params=merge_setting(request.params, self.params), auth=merge_setting(auth, self.auth), cookies=merged_cookies, hooks=merge_hooks(request.hooks, self.hooks))
        return p

    def request(self, method, url, params = None, data = None, headers = None, cookies = None, files = None, auth = None, timeout = None, allow_redirects = True, proxies = None, hooks = None, stream = None, verify = None, cert = None):
        method = builtin_str(method)
        req = Request(method=method.upper(), url=url, headers=headers, files=files, data=data or {}, params=params or {}, auth=auth, cookies=cookies, hooks=hooks)
        prep = self.prepare_request(req)
        proxies = proxies or {}
        if self.trust_env:
            env_proxies = get_environ_proxies(url) or {}
            for k, v in env_proxies.items():
                proxies.setdefault(k, v)

            if not verify and verify is not False:
                verify = os.environ.get('REQUESTS_CA_BUNDLE')
            if not verify and verify is not False:
                verify = os.environ.get('CURL_CA_BUNDLE')
        proxies = merge_setting(proxies, self.proxies)
        stream = merge_setting(stream, self.stream)
        verify = merge_setting(verify, self.verify)
        cert = merge_setting(cert, self.cert)
        send_kwargs = {'stream': stream,
         'timeout': timeout,
         'verify': verify,
         'cert': cert,
         'proxies': proxies,
         'allow_redirects': allow_redirects}
        resp = self.send(prep, **send_kwargs)
        return resp

    def get(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request('GET', url, **kwargs)

    def options(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request('OPTIONS', url, **kwargs)

    def head(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', False)
        return self.request('HEAD', url, **kwargs)

    def post(self, url, data = None, **kwargs):
        return self.request('POST', url, data=data, **kwargs)

    def put(self, url, data = None, **kwargs):
        return self.request('PUT', url, data=data, **kwargs)

    def patch(self, url, data = None, **kwargs):
        return self.request('PATCH', url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)

    def send(self, request, **kwargs):
        kwargs.setdefault('stream', self.stream)
        kwargs.setdefault('verify', self.verify)
        kwargs.setdefault('cert', self.cert)
        kwargs.setdefault('proxies', self.proxies)
        if not isinstance(request, PreparedRequest):
            raise ValueError('You can only send PreparedRequests.')
        allow_redirects = kwargs.pop('allow_redirects', True)
        stream = kwargs.get('stream')
        timeout = kwargs.get('timeout')
        verify = kwargs.get('verify')
        cert = kwargs.get('cert')
        proxies = kwargs.get('proxies')
        hooks = request.hooks
        adapter = self.get_adapter(url=request.url)
        start = datetime.utcnow()
        r = adapter.send(request, **kwargs)
        r.elapsed = datetime.utcnow() - start
        r = dispatch_hook('response', hooks, r, **kwargs)
        if r.history:
            for resp in r.history:
                extract_cookies_to_jar(self.cookies, resp.request, resp.raw)

        extract_cookies_to_jar(self.cookies, request, r.raw)
        gen = self.resolve_redirects(r, request, stream=stream, timeout=timeout, verify=verify, cert=cert, proxies=proxies)
        history = [ resp for resp in gen ] if allow_redirects else []
        if history:
            history.insert(0, r)
            r = history.pop()
            r.history = tuple(history)
        return r

    def get_adapter(self, url):
        for prefix, adapter in self.adapters.items():
            if url.lower().startswith(prefix):
                return adapter

        raise InvalidSchema("No connection adapters were found for '%s'" % url)

    def close(self):
        for v in self.adapters.values():
            v.close()

    def mount(self, prefix, adapter):
        self.adapters[prefix] = adapter
        keys_to_move = [ k for k in self.adapters if len(k) < len(prefix) ]
        for key in keys_to_move:
            self.adapters[key] = self.adapters.pop(key)

    def __getstate__(self):
        return dict(((attr, getattr(self, attr, None)) for attr in self.__attrs__))

    def __setstate__(self, state):
        for attr, value in state.items():
            setattr(self, attr, value)


def session():
    return Session()
