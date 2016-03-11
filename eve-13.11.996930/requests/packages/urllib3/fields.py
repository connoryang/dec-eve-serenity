#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\fields.py
import email.utils
import mimetypes
from .packages import six

def guess_content_type(filename, default = 'application/octet-stream'):
    if filename:
        return mimetypes.guess_type(filename)[0] or default
    return default


def format_header_param(name, value):
    if not any((ch in value for ch in '"\\\r\n')):
        result = '%s="%s"' % (name, value)
        try:
            result.encode('ascii')
        except UnicodeEncodeError:
            pass
        else:
            return result

    if not six.PY3:
        value = value.encode('utf-8')
    value = email.utils.encode_rfc2231(value, 'utf-8')
    value = '%s*=%s' % (name, value)
    return value


class RequestField(object):

    def __init__(self, name, data, filename = None, headers = None):
        self._name = name
        self._filename = filename
        self.data = data
        self.headers = {}
        if headers:
            self.headers = dict(headers)

    @classmethod
    def from_tuples(cls, fieldname, value):
        if isinstance(value, tuple):
            if len(value) == 3:
                filename, data, content_type = value
            else:
                filename, data = value
                content_type = guess_content_type(filename)
        else:
            filename = None
            content_type = None
            data = value
        request_param = cls(fieldname, data, filename=filename)
        request_param.make_multipart(content_type=content_type)
        return request_param

    def _render_part(self, name, value):
        return format_header_param(name, value)

    def _render_parts(self, header_parts):
        parts = []
        iterable = header_parts
        if isinstance(header_parts, dict):
            iterable = header_parts.items()
        for name, value in iterable:
            if value:
                parts.append(self._render_part(name, value))

        return '; '.join(parts)

    def render_headers(self):
        lines = []
        sort_keys = ['Content-Disposition', 'Content-Type', 'Content-Location']
        for sort_key in sort_keys:
            if self.headers.get(sort_key, False):
                lines.append('%s: %s' % (sort_key, self.headers[sort_key]))

        for header_name, header_value in self.headers.items():
            if header_name not in sort_keys:
                if header_value:
                    lines.append('%s: %s' % (header_name, header_value))

        lines.append('\r\n')
        return '\r\n'.join(lines)

    def make_multipart(self, content_disposition = None, content_type = None, content_location = None):
        self.headers['Content-Disposition'] = content_disposition or 'form-data'
        self.headers['Content-Disposition'] += '; '.join(['', self._render_parts((('name', self._name), ('filename', self._filename)))])
        self.headers['Content-Type'] = content_type
        self.headers['Content-Location'] = content_location
