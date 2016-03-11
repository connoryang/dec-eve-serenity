#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\typeutils\__init__.py
from __future__ import print_function
import sys
import itertools
import collections
import re
REGEX_TYPE = type(re.compile(''))

class ComparableMixin(object):

    def __new__(cls, *args):
        obj = object.__new__(cls, *args)
        if not hasattr(obj, '__lt__'):
            raise NotImplementedError('__lt__ must be overridden.')
        return obj

    def __eq__(self, other):
        return not self < other and not other < self

    def __ne__(self, other):
        return self < other or other < self

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return not self < other

    def __le__(self, other):
        return not other < self


def float_eval(value, default = 0.0):
    if isinstance(value, float):
        return value
    if isinstance(value, (int, long)):
        return float(value)
    if isinstance(value, basestring):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    else:
        return default


def int_eval(value, default = 0):
    if isinstance(value, int):
        return value
    if isinstance(value, (long, float)):
        return int(value)
    if isinstance(value, basestring):
        try:
            if '.' in value:
                return int(float(value))
            return int(value)
        except (TypeError, ValueError):
            return default

    else:
        return default


def bool_eval(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, basestring):
        if value.strip().lower() == 'true':
            return True
        elif value.isdigit():
            return bool(int(value))
        else:
            neg = False
            if value.startswith('-'):
                value = value[1:]
                neg = True
                if value.isdigit():
                    return bool(-int(value))
            parts = value.split('.')
            if len(parts) == 2:
                if parts[0].isdigit() and parts[1].isdigit():
                    if neg:
                        return bool(-float(value))
                    else:
                        return bool(float(value))
            return False
    else:
        if isinstance(value, (int, long, float)):
            return bool(value)
        return False


def total_size(o, handlers = None, verbose = False):
    dict_handler = lambda d: itertools.chain.from_iterable(d.items())
    all_handlers = {tuple: iter,
     list: iter,
     collections.deque: iter,
     dict: dict_handler,
     set: iter,
     frozenset: iter}
    handlers = handlers or {}
    all_handlers.update(handlers)
    seen = set()
    default_size = sys.getsizeof(0)

    def sizeof(o):
        if id(o) in seen:
            return 0
        seen.add(id(o))
        s = sys.getsizeof(o, default_size)
        if verbose:
            print(s, type(o), repr(o), file=sys.stderr)
        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break

        return s

    return sizeof(o)


def ip_to_int(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        raise ValueError('Not a valid IP address')
    i = 0
    ii = int(parts[0])
    if ii < 0 or ii > 255:
        raise ValueError('Not a valid IP address')
    i += ii << 24
    ii = int(parts[1])
    if ii < 0 or ii > 255:
        raise ValueError('Not a valid IP address')
    i += ii << 16
    ii = int(parts[2])
    if ii < 0 or ii > 255:
        raise ValueError('Not a valid IP address')
    i += ii << 8
    ii = int(parts[3])
    if ii < 0 or ii > 255:
        raise ValueError('Not a valid IP address')
    i += ii
    return i


def int_to_ip(i):
    d = i & 255
    i >>= 8
    c = i & 255
    i >>= 8
    b = i & 255
    a = i >> 8
    return '%s.%s.%s.%s' % (a,
     b,
     c,
     d)


def split_bitmask(composite_value):
    buff = []
    bitval = 1
    while composite_value > 0:
        if composite_value & 1:
            buff.append(bitval)
        bitval *= 2
        composite_value >>= 1

    return buff


class _SentientClassBuilder(type):

    def __new__(mcs, clsname, bases, dct):
        the_class = super(_SentientClassBuilder, mcs).__new__(mcs, clsname, bases, dct)
        my_map = {}
        for name, attr in dct.iteritems():
            if hasattr(attr, '__call__'):
                sentience = getattr(attr, '__sentience__', None)
                if sentience is not None and isinstance(sentience, dict):
                    my_map[name] = sentience

        current_map = getattr(the_class, '__sentient_method_map__', None) or {}
        current_map[clsname] = my_map
        setattr(the_class, '__sentient_method_map__', current_map)
        return the_class


class SentientObject(object):
    __metaclass__ = _SentientClassBuilder
    __sentient_method_map__ = {}

    @classmethod
    def sentient_methods(cls, inherited = True):
        buff = cls.__sentient_method_map__[cls.__name__]
        if inherited:
            for basecls in cls.__bases__:
                if issubclass(basecls, SentientObject):
                    buff.update(basecls.sentient_methods())

        return buff

    @staticmethod
    def sentient(**kwargs):

        def inner(function):
            setattr(function, '__sentience__', kwargs)
            return function

        return inner
