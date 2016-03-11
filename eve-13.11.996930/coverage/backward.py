#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\backward.py
import os, re, sys
try:
    set = set
except NameError:
    from sets import Set as set

try:
    sorted = sorted
except NameError:

    def sorted(iterable):
        lst = list(iterable)
        lst.sort()
        return lst


try:
    reversed = reversed
except NameError:

    def reversed(iterable):
        lst = list(iterable)
        return lst[::-1]


try:
    ''.rpartition
except AttributeError:

    def rpartition(s, sep):
        i = s.rfind(sep)
        if i == -1:
            return ('', '', s)
        else:
            return (s[:i], sep, s[i + len(sep):])


else:

    def rpartition(s, sep):
        return s.rpartition(sep)


try:
    from cStringIO import StringIO
    BytesIO = StringIO
except ImportError:
    from io import StringIO, BytesIO

try:
    string_class = basestring
except NameError:
    string_class = str

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    range = xrange
except NameError:
    range = range

try:
    {}.iteritems
except AttributeError:

    def iitems(d):
        return d.items()


else:

    def iitems(d):
        return d.iteritems()


if sys.version_info >= (3, 0):

    def exec_code_object(code, global_map):
        exec (code, global_map)


else:
    eval(compile('def exec_code_object(code, global_map):\n    exec code in global_map\n', '<exec_function>', 'exec'))
if sys.version_info >= (3, 0):
    import tokenize
    try:
        open_source = tokenize.open
    except AttributeError:
        from io import TextIOWrapper
        detect_encoding = tokenize.detect_encoding

        def open_source(fname):
            buffer = open(fname, 'rb')
            encoding, _ = detect_encoding(buffer.readline)
            buffer.seek(0)
            text = TextIOWrapper(buffer, encoding, line_buffering=True)
            text.mode = 'r'
            return text


else:

    def open_source(fname):
        return open(fname, 'rU')


if sys.version_info >= (3, 0):

    def to_bytes(s):
        return s.encode('utf8')


    def to_string(b):
        return b.decode('utf8')


    def binary_bytes(byte_values):
        return bytes(byte_values)


    def byte_to_int(byte_value):
        return byte_value


    def bytes_to_ints(bytes_value):
        return bytes_value


else:

    def to_bytes(s):
        return s


    def to_string(b):
        return b


    def binary_bytes(byte_values):
        return ''.join([ chr(b) for b in byte_values ])


    def byte_to_int(byte_value):
        return ord(byte_value)


    def bytes_to_ints(bytes_value):
        for byte in bytes_value:
            yield ord(byte)


try:
    import hashlib
    md5 = hashlib.md5
except ImportError:
    import md5
    md5 = md5.new
