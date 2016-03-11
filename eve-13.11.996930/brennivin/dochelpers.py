#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\brennivin\dochelpers.py


def pretty_func(func, reprstr):

    class pretty(object):

        def __call__(self, *args, **kwargs):
            return func(*args, **kwargs)

        def __repr__(self):
            return reprstr

        __str__ = __repr__

    return pretty()


def pretty_module_func(func):
    s = '.'.join([func.__module__, func.__name__])
    return pretty_func(func, s)


def pretty_value(value, reprstr):

    class pretty(object):

        def __call__(self):
            return value

        def __repr__(self):
            return reprstr

        __str__ = __repr__

    return pretty()


identity = pretty_func(lambda x: x, 'lambda x: x')

class _Sentinel(object):

    def __init__(self, s, nonzero):
        self.s = s
        self.nonzero = nonzero

    def __repr__(self):
        return self.s

    __str__ = __repr__

    def __nonzero__(self):
        return self.nonzero

    def __bool__(self):
        return self.nonzero


default = _Sentinel('DEFAULT', True)
unsupplied = _Sentinel('DEFAULT', True)
ignore = _Sentinel('<IGNORE>', False)

def named_none(s):
    return _Sentinel(s, False)
