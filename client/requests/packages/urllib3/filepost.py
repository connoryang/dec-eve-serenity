#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\filepost.py
import codecs
import mimetypes
from uuid import uuid4
from io import BytesIO
from .packages import six
from .packages.six import b
from .fields import RequestField
writer = codecs.lookup('utf-8')[3]

def choose_boundary():
    return uuid4().hex


def iter_field_objects(fields):
    if isinstance(fields, dict):
        i = six.iteritems(fields)
    else:
        i = iter(fields)
    for field in i:
        if isinstance(field, RequestField):
            yield field
        else:
            yield RequestField.from_tuples(*field)


def iter_fields(fields):
    if isinstance(fields, dict):
        return ((k, v) for k, v in six.iteritems(fields))
    return ((k, v) for k, v in fields)


def encode_multipart_formdata(fields, boundary = None):
    body = BytesIO()
    if boundary is None:
        boundary = choose_boundary()
    for field in iter_field_objects(fields):
        body.write(b('--%s\r\n' % boundary))
        writer(body).write(field.render_headers())
        data = field.data
        if isinstance(data, int):
            data = str(data)
        if isinstance(data, six.text_type):
            writer(body).write(data)
        else:
            body.write(data)
        body.write('\r\n')

    body.write(b('--%s--\r\n' % boundary))
    content_type = str('multipart/form-data; boundary=%s' % boundary)
    return (body.getvalue(), content_type)
