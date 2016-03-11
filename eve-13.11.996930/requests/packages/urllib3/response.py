#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\response.py
import logging
import zlib
import io
from .exceptions import DecodeError
from .packages.six import string_types as basestring, binary_type
from .util import is_fp_closed
log = logging.getLogger(__name__)

class DeflateDecoder(object):

    def __init__(self):
        self._first_try = True
        self._data = binary_type()
        self._obj = zlib.decompressobj()

    def __getattr__(self, name):
        return getattr(self._obj, name)

    def decompress(self, data):
        if not self._first_try:
            return self._obj.decompress(data)
        self._data += data
        try:
            return self._obj.decompress(data)
        except zlib.error:
            self._first_try = False
            self._obj = zlib.decompressobj(-zlib.MAX_WBITS)
            try:
                return self.decompress(self._data)
            finally:
                self._data = None


def _get_decoder(mode):
    if mode == 'gzip':
        return zlib.decompressobj(16 + zlib.MAX_WBITS)
    return DeflateDecoder()


class HTTPResponse(io.IOBase):
    CONTENT_DECODERS = ['gzip', 'deflate']
    REDIRECT_STATUSES = [301,
     302,
     303,
     307,
     308]

    def __init__(self, body = '', headers = None, status = 0, version = 0, reason = None, strict = 0, preload_content = True, decode_content = True, original_response = None, pool = None, connection = None):
        self.headers = headers or {}
        self.status = status
        self.version = version
        self.reason = reason
        self.strict = strict
        self.decode_content = decode_content
        self._decoder = None
        self._body = body if body and isinstance(body, basestring) else None
        self._fp = None
        self._original_response = original_response
        self._fp_bytes_read = 0
        self._pool = pool
        self._connection = connection
        if hasattr(body, 'read'):
            self._fp = body
        if preload_content and not self._body:
            self._body = self.read(decode_content=decode_content)

    def get_redirect_location(self):
        if self.status in self.REDIRECT_STATUSES:
            return self.headers.get('location')
        return False

    def release_conn(self):
        if not self._pool or not self._connection:
            return
        self._pool._put_conn(self._connection)
        self._connection = None

    @property
    def data(self):
        if self._body:
            return self._body
        if self._fp:
            return self.read(cache_content=True)

    def tell(self):
        return self._fp_bytes_read

    def read(self, amt = None, decode_content = None, cache_content = False):
        content_encoding = self.headers.get('content-encoding', '').lower()
        if self._decoder is None:
            if content_encoding in self.CONTENT_DECODERS:
                self._decoder = _get_decoder(content_encoding)
        if decode_content is None:
            decode_content = self.decode_content
        if self._fp is None:
            return
        flush_decoder = False
        try:
            if amt is None:
                data = self._fp.read()
                flush_decoder = True
            else:
                cache_content = False
                data = self._fp.read(amt)
                if amt != 0 and not data:
                    self._fp.close()
                    flush_decoder = True
            self._fp_bytes_read += len(data)
            try:
                if decode_content and self._decoder:
                    data = self._decoder.decompress(data)
            except (IOError, zlib.error) as e:
                raise DecodeError('Received response with content-encoding: %s, but failed to decode it.' % content_encoding, e)

            if flush_decoder and decode_content and self._decoder:
                buf = self._decoder.decompress(binary_type())
                data += buf + self._decoder.flush()
            if cache_content:
                self._body = data
            return data
        finally:
            if self._original_response and self._original_response.isclosed():
                self.release_conn()

    def stream(self, amt = 65536, decode_content = None):
        while not is_fp_closed(self._fp):
            data = self.read(amt=amt, decode_content=decode_content)
            if data:
                yield data

    @classmethod
    def from_httplib(ResponseCls, r, **response_kw):
        headers = {}
        for k, v in r.getheaders():
            k = k.lower()
            has_value = headers.get(k)
            if has_value:
                v = ', '.join([has_value, v])
            headers[k] = v

        strict = getattr(r, 'strict', 0)
        return ResponseCls(body=r, headers=headers, status=r.status, version=r.version, reason=r.reason, strict=strict, original_response=r, **response_kw)

    def getheaders(self):
        return self.headers

    def getheader(self, name, default = None):
        return self.headers.get(name, default)

    def close(self):
        if not self.closed:
            self._fp.close()

    @property
    def closed(self):
        if self._fp is None:
            return True
        elif hasattr(self._fp, 'closed'):
            return self._fp.closed
        elif hasattr(self._fp, 'isclosed'):
            return self._fp.isclosed()
        else:
            return True

    def fileno(self):
        if self._fp is None:
            raise IOError('HTTPResponse has no file to get a fileno from')
        else:
            if hasattr(self._fp, 'fileno'):
                return self._fp.fileno()
            raise IOError('The file-like object  this HTTPResponse is wrapped around has no file descriptor')

    def flush(self):
        if self._fp is not None and hasattr(self._fp, 'flush'):
            return self._fp.flush()

    def readable(self):
        return True
