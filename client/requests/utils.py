#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\utils.py
import cgi
import codecs
import collections
import io
import os
import platform
import re
import sys
import socket
import struct
from . import __version__
from . import certs
from .compat import parse_http_list as _parse_list_header
from .compat import quote, urlparse, bytes, str, OrderedDict, unquote, is_py2, builtin_str, getproxies, proxy_bypass
from .cookies import RequestsCookieJar, cookiejar_from_dict
from .structures import CaseInsensitiveDict
from .exceptions import MissingSchema, InvalidURL
_hush_pyflakes = (RequestsCookieJar,)
NETRC_FILES = ('.netrc', '_netrc')
DEFAULT_CA_BUNDLE_PATH = certs.where()

def dict_to_sequence(d):
    if hasattr(d, 'items'):
        d = d.items()
    return d


def super_len(o):
    if hasattr(o, '__len__'):
        return len(o)
    if hasattr(o, 'len'):
        return o.len
    if hasattr(o, 'fileno'):
        try:
            fileno = o.fileno()
        except io.UnsupportedOperation:
            pass
        else:
            return os.fstat(fileno).st_size

    if hasattr(o, 'getvalue'):
        return len(o.getvalue())


def get_netrc_auth(url):
    try:
        from netrc import netrc, NetrcParseError
        netrc_path = None
        for f in NETRC_FILES:
            try:
                loc = os.path.expanduser('~/{0}'.format(f))
            except KeyError:
                return

            if os.path.exists(loc):
                netrc_path = loc
                break

        if netrc_path is None:
            return
        ri = urlparse(url)
        host = ri.netloc.split(':')[0]
        try:
            _netrc = netrc(netrc_path).authenticators(host)
            if _netrc:
                login_i = 0 if _netrc[0] else 1
                return (_netrc[login_i], _netrc[2])
        except (NetrcParseError, IOError):
            pass

    except (ImportError, AttributeError):
        pass


def guess_filename(obj):
    name = getattr(obj, 'name', None)
    if name and name[0] != '<' and name[-1] != '>':
        return os.path.basename(name)


def from_key_val_list(value):
    if value is None:
        return
    if isinstance(value, (str,
     bytes,
     bool,
     int)):
        raise ValueError('cannot encode objects that are not 2-tuples')
    return OrderedDict(value)


def to_key_val_list(value):
    if value is None:
        return
    if isinstance(value, (str,
     bytes,
     bool,
     int)):
        raise ValueError('cannot encode objects that are not 2-tuples')
    if isinstance(value, collections.Mapping):
        value = value.items()
    return list(value)


def parse_list_header(value):
    result = []
    for item in _parse_list_header(value):
        if item[:1] == item[-1:] == '"':
            item = unquote_header_value(item[1:-1])
        result.append(item)

    return result


def parse_dict_header(value):
    result = {}
    for item in _parse_list_header(value):
        if '=' not in item:
            result[item] = None
            continue
        name, value = item.split('=', 1)
        if value[:1] == value[-1:] == '"':
            value = unquote_header_value(value[1:-1])
        result[name] = value

    return result


def unquote_header_value(value, is_filename = False):
    if value and value[0] == value[-1] == '"':
        value = value[1:-1]
        if not is_filename or value[:2] != '\\\\':
            return value.replace('\\\\', '\\').replace('\\"', '"')
    return value


def dict_from_cookiejar(cj):
    cookie_dict = {}
    for cookie in cj:
        cookie_dict[cookie.name] = cookie.value

    return cookie_dict


def add_dict_to_cookiejar(cj, cookie_dict):
    cj2 = cookiejar_from_dict(cookie_dict)
    cj.update(cj2)
    return cj


def get_encodings_from_content(content):
    charset_re = re.compile('<meta.*?charset=["\\\']*(.+?)["\\\'>]', flags=re.I)
    pragma_re = re.compile('<meta.*?content=["\\\']*;?charset=(.+?)["\\\'>]', flags=re.I)
    xml_re = re.compile('^<\\?xml.*?encoding=["\\\']*(.+?)["\\\'>]')
    return charset_re.findall(content) + pragma_re.findall(content) + xml_re.findall(content)


def get_encoding_from_headers(headers):
    content_type = headers.get('content-type')
    if not content_type:
        return None
    content_type, params = cgi.parse_header(content_type)
    if 'charset' in params:
        return params['charset'].strip('\'"')
    if 'text' in content_type:
        return 'ISO-8859-1'


def stream_decode_response_unicode(iterator, r):
    if r.encoding is None:
        for item in iterator:
            yield item

        return
    decoder = codecs.getincrementaldecoder(r.encoding)(errors='replace')
    for chunk in iterator:
        rv = decoder.decode(chunk)
        if rv:
            yield rv

    rv = decoder.decode('', final=True)
    if rv:
        yield rv


def iter_slices(string, slice_length):
    pos = 0
    while pos < len(string):
        yield string[pos:pos + slice_length]
        pos += slice_length


def get_unicode_from_response(r):
    tried_encodings = []
    encoding = get_encoding_from_headers(r.headers)
    if encoding:
        try:
            return str(r.content, encoding)
        except UnicodeError:
            tried_encodings.append(encoding)

    try:
        return str(r.content, encoding, errors='replace')
    except TypeError:
        return r.content


UNRESERVED_SET = frozenset('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' + '0123456789-._~')

def unquote_unreserved(uri):
    parts = uri.split('%')
    for i in range(1, len(parts)):
        h = parts[i][0:2]
        if len(h) == 2 and h.isalnum():
            try:
                c = chr(int(h, 16))
            except ValueError:
                raise InvalidURL("Invalid percent-escape sequence: '%s'" % h)

            if c in UNRESERVED_SET:
                parts[i] = c + parts[i][2:]
            else:
                parts[i] = '%' + parts[i]
        else:
            parts[i] = '%' + parts[i]

    return ''.join(parts)


def requote_uri(uri):
    return quote(unquote_unreserved(uri), safe="!#$%&'()*+,/:;=?@[]~")


def address_in_network(ip, net):
    ipaddr = struct.unpack('=L', socket.inet_aton(ip))[0]
    netaddr, bits = net.split('/')
    netmask = struct.unpack('=L', socket.inet_aton(dotted_netmask(int(bits))))[0]
    network = struct.unpack('=L', socket.inet_aton(netaddr))[0] & netmask
    return ipaddr & netmask == network & netmask


def dotted_netmask(mask):
    bits = 4294967295L ^ (1 << 32 - mask) - 1
    return socket.inet_ntoa(struct.pack('>I', bits))


def is_ipv4_address(string_ip):
    try:
        socket.inet_aton(string_ip)
    except socket.error:
        return False

    return True


def is_valid_cidr(string_network):
    if string_network.count('/') == 1:
        try:
            mask = int(string_network.split('/')[1])
        except ValueError:
            return False

        if mask < 1 or mask > 32:
            return False
        try:
            socket.inet_aton(string_network.split('/')[0])
        except socket.error:
            return False

    else:
        return False
    return True


def get_environ_proxies(url):
    get_proxy = lambda k: os.environ.get(k) or os.environ.get(k.upper())
    no_proxy = get_proxy('no_proxy')
    netloc = urlparse(url).netloc
    if no_proxy:
        no_proxy = no_proxy.replace(' ', '').split(',')
        ip = netloc.split(':')[0]
        if is_ipv4_address(ip):
            for proxy_ip in no_proxy:
                if is_valid_cidr(proxy_ip):
                    if address_in_network(ip, proxy_ip):
                        return {}

        else:
            for host in no_proxy:
                if netloc.endswith(host) or netloc.split(':')[0].endswith(host):
                    return {}

    try:
        bypass = proxy_bypass(netloc)
    except (TypeError, socket.gaierror):
        bypass = False

    if bypass:
        return {}
    return getproxies()


def default_user_agent(name = 'python-requests'):
    _implementation = 'python-requests'
    if _implementation == 'CPython':
        _implementation_version = platform.python_version()
    elif _implementation == 'PyPy':
        _implementation_version = '%s.%s.%s' % (sys.pypy_version_info.major, sys.pypy_version_info.minor, sys.pypy_version_info.micro)
        if sys.pypy_version_info.releaselevel != 'final':
            _implementation_version = ''.join([_implementation_version, sys.pypy_version_info.releaselevel])
    elif _implementation == 'Jython':
        _implementation_version = platform.python_version()
    elif _implementation == 'IronPython':
        _implementation_version = platform.python_version()
    else:
        _implementation_version = 'Unknown'
    try:
        p_system = platform.system()
        p_release = platform.release()
    except IOError:
        p_system = 'Unknown'
        p_release = 'Unknown'

    return ' '.join(['%s/%s' % (name, __version__), '%s/%s' % (_implementation, _implementation_version), '%s/%s' % (p_system, p_release)])


def default_headers():
    return CaseInsensitiveDict({'User-Agent': default_user_agent(),
     'Accept-Encoding': ', '.join(('gzip', 'deflate', 'compress')),
     'Accept': '*/*'})


def parse_header_links(value):
    links = []
    replace_chars = ' \'"'
    for val in value.split(','):
        try:
            url, params = val.split(';', 1)
        except ValueError:
            url, params = val, ''

        link = {}
        link['url'] = url.strip('<> \'"')
        for param in params.split(';'):
            try:
                key, value = param.split('=')
            except ValueError:
                break

            link[key.strip(replace_chars)] = value.strip(replace_chars)

        links.append(link)

    return links


_null = '\x00'.encode('ascii')
_null2 = _null * 2
_null3 = _null * 3

def guess_json_utf(data):
    sample = data[:4]
    if sample in (codecs.BOM_UTF32_LE, codecs.BOM32_BE):
        return 'utf-32'
    if sample[:3] == codecs.BOM_UTF8:
        return 'utf-8-sig'
    if sample[:2] in (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE):
        return 'utf-16'
    nullcount = sample.count(_null)
    if nullcount == 0:
        return 'utf-8'
    if nullcount == 2:
        if sample[::2] == _null2:
            return 'utf-16-be'
        if sample[1::2] == _null2:
            return 'utf-16-le'
    if nullcount == 3:
        if sample[:3] == _null3:
            return 'utf-32-be'
        if sample[1:] == _null3:
            return 'utf-32-le'


def except_on_missing_scheme(url):
    scheme, netloc, path, params, query, fragment = urlparse(url)
    if not scheme:
        raise MissingSchema('Proxy URLs must have explicit schemes.')


def get_auth_from_url(url):
    parsed = urlparse(url)
    try:
        auth = (unquote(parsed.username), unquote(parsed.password))
    except (AttributeError, TypeError):
        auth = ('', '')

    return auth


def to_native_string(string, encoding = 'ascii'):
    out = None
    if isinstance(string, builtin_str):
        out = string
    elif is_py2:
        out = string.encode(encoding)
    else:
        out = string.decode(encoding)
    return out
