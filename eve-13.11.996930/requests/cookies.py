#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\cookies.py
import time
import collections
from .compat import cookielib, urlparse, urlunparse, Morsel
try:
    import threading
    threading
except ImportError:
    import dummy_threading as threading

class MockRequest(object):

    def __init__(self, request):
        self._r = request
        self._new_headers = {}
        self.type = urlparse(self._r.url).scheme

    def get_type(self):
        return self.type

    def get_host(self):
        return urlparse(self._r.url).netloc

    def get_origin_req_host(self):
        return self.get_host()

    def get_full_url(self):
        if not self._r.headers.get('Host'):
            return self._r.url
        host = self._r.headers['Host']
        parsed = urlparse(self._r.url)
        return urlunparse([parsed.scheme,
         host,
         parsed.path,
         parsed.params,
         parsed.query,
         parsed.fragment])

    def is_unverifiable(self):
        return True

    def has_header(self, name):
        return name in self._r.headers or name in self._new_headers

    def get_header(self, name, default = None):
        return self._r.headers.get(name, self._new_headers.get(name, default))

    def add_header(self, key, val):
        raise NotImplementedError('Cookie headers should be added with add_unredirected_header()')

    def add_unredirected_header(self, name, value):
        self._new_headers[name] = value

    def get_new_headers(self):
        return self._new_headers

    @property
    def unverifiable(self):
        return self.is_unverifiable()

    @property
    def origin_req_host(self):
        return self.get_origin_req_host()

    @property
    def host(self):
        return self.get_host()


class MockResponse(object):

    def __init__(self, headers):
        self._headers = headers

    def info(self):
        return self._headers

    def getheaders(self, name):
        self._headers.getheaders(name)


def extract_cookies_to_jar(jar, request, response):
    if not (hasattr(response, '_original_response') and response._original_response):
        return
    req = MockRequest(request)
    res = MockResponse(response._original_response.msg)
    jar.extract_cookies(res, req)


def get_cookie_header(jar, request):
    r = MockRequest(request)
    jar.add_cookie_header(r)
    return r.get_new_headers().get('Cookie')


def remove_cookie_by_name(cookiejar, name, domain = None, path = None):
    clearables = []
    for cookie in cookiejar:
        if cookie.name == name:
            if domain is None or domain == cookie.domain:
                if path is None or path == cookie.path:
                    clearables.append((cookie.domain, cookie.path, cookie.name))

    for domain, path, name in clearables:
        cookiejar.clear(domain, path, name)


class CookieConflictError(RuntimeError):
    pass


class RequestsCookieJar(cookielib.CookieJar, collections.MutableMapping):

    def get(self, name, default = None, domain = None, path = None):
        try:
            return self._find_no_duplicates(name, domain, path)
        except KeyError:
            return default

    def set(self, name, value, **kwargs):
        if value is None:
            remove_cookie_by_name(self, name, domain=kwargs.get('domain'), path=kwargs.get('path'))
            return
        if isinstance(value, Morsel):
            c = morsel_to_cookie(value)
        else:
            c = create_cookie(name, value, **kwargs)
        self.set_cookie(c)
        return c

    def iterkeys(self):
        for cookie in iter(self):
            yield cookie.name

    def keys(self):
        return list(self.iterkeys())

    def itervalues(self):
        for cookie in iter(self):
            yield cookie.value

    def values(self):
        return list(self.itervalues())

    def iteritems(self):
        for cookie in iter(self):
            yield (cookie.name, cookie.value)

    def items(self):
        return list(self.iteritems())

    def list_domains(self):
        domains = []
        for cookie in iter(self):
            if cookie.domain not in domains:
                domains.append(cookie.domain)

        return domains

    def list_paths(self):
        paths = []
        for cookie in iter(self):
            if cookie.path not in paths:
                paths.append(cookie.path)

        return paths

    def multiple_domains(self):
        domains = []
        for cookie in iter(self):
            if cookie.domain is not None and cookie.domain in domains:
                return True
            domains.append(cookie.domain)

        return False

    def get_dict(self, domain = None, path = None):
        dictionary = {}
        for cookie in iter(self):
            if (domain is None or cookie.domain == domain) and (path is None or cookie.path == path):
                dictionary[cookie.name] = cookie.value

        return dictionary

    def __getitem__(self, name):
        return self._find_no_duplicates(name)

    def __setitem__(self, name, value):
        self.set(name, value)

    def __delitem__(self, name):
        remove_cookie_by_name(self, name)

    def set_cookie(self, cookie, *args, **kwargs):
        if hasattr(cookie.value, 'startswith') and cookie.value.startswith('"') and cookie.value.endswith('"'):
            cookie.value = cookie.value.replace('\\"', '')
        return super(RequestsCookieJar, self).set_cookie(cookie, *args, **kwargs)

    def update(self, other):
        if isinstance(other, cookielib.CookieJar):
            for cookie in other:
                self.set_cookie(cookie)

        else:
            super(RequestsCookieJar, self).update(other)

    def _find(self, name, domain = None, path = None):
        for cookie in iter(self):
            if cookie.name == name:
                if domain is None or cookie.domain == domain:
                    if path is None or cookie.path == path:
                        return cookie.value

        raise KeyError('name=%r, domain=%r, path=%r' % (name, domain, path))

    def _find_no_duplicates(self, name, domain = None, path = None):
        toReturn = None
        for cookie in iter(self):
            if cookie.name == name:
                if domain is None or cookie.domain == domain:
                    if path is None or cookie.path == path:
                        if toReturn is not None:
                            raise CookieConflictError('There are multiple cookies with name, %r' % name)
                        toReturn = cookie.value

        if toReturn:
            return toReturn
        raise KeyError('name=%r, domain=%r, path=%r' % (name, domain, path))

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('_cookies_lock')
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if '_cookies_lock' not in self.__dict__:
            self._cookies_lock = threading.RLock()

    def copy(self):
        new_cj = RequestsCookieJar()
        new_cj.update(self)
        return new_cj


def create_cookie(name, value, **kwargs):
    result = dict(version=0, name=name, value=value, port=None, domain='', path='/', secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
    badargs = set(kwargs) - set(result)
    if badargs:
        err = 'create_cookie() got unexpected keyword arguments: %s'
        raise TypeError(err % list(badargs))
    result.update(kwargs)
    result['port_specified'] = bool(result['port'])
    result['domain_specified'] = bool(result['domain'])
    result['domain_initial_dot'] = result['domain'].startswith('.')
    result['path_specified'] = bool(result['path'])
    return cookielib.Cookie(**result)


def morsel_to_cookie(morsel):
    expires = None
    if morsel['max-age']:
        expires = time.time() + morsel['max-age']
    elif morsel['expires']:
        time_template = '%a, %d-%b-%Y %H:%M:%S GMT'
        expires = time.mktime(time.strptime(morsel['expires'], time_template)) - time.timezone
    return create_cookie(comment=morsel['comment'], comment_url=bool(morsel['comment']), discard=False, domain=morsel['domain'], expires=expires, name=morsel.key, path=morsel['path'], port=None, rest={'HttpOnly': morsel['httponly']}, rfc2109=False, secure=bool(morsel['secure']), value=morsel.value, version=morsel['version'] or 0)


def cookiejar_from_dict(cookie_dict, cookiejar = None, overwrite = True):
    if cookiejar is None:
        cookiejar = RequestsCookieJar()
    if cookie_dict is not None:
        names_from_jar = [ cookie.name for cookie in cookiejar ]
        for name in cookie_dict:
            if overwrite or name not in names_from_jar:
                cookiejar.set_cookie(create_cookie(name, cookie_dict[name]))

    return cookiejar


def merge_cookies(cookiejar, cookies):
    if not isinstance(cookiejar, cookielib.CookieJar):
        raise ValueError('You can only merge into CookieJar')
    if isinstance(cookies, dict):
        cookiejar = cookiejar_from_dict(cookies, cookiejar=cookiejar, overwrite=False)
    elif isinstance(cookies, cookielib.CookieJar):
        try:
            cookiejar.update(cookies)
        except AttributeError:
            for cookie_in_jar in cookies:
                cookiejar.set_cookie(cookie_in_jar)

    return cookiejar
