#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\watchdog\utils\decorators.py
import functools
import warnings
import threading
import sys

def synchronized(lock = None):
    if lock is None:
        lock = threading.Lock()

    def wrapper(function):

        def new_function(*args, **kwargs):
            lock.acquire()
            try:
                return function(*args, **kwargs)
            finally:
                lock.release()

        return new_function

    return wrapper


def propertyx(function):
    keys = ('fget', 'fset', 'fdel')
    func_locals = {'doc': function.__doc__}

    def probe_func(frame, event, arg):
        if event == 'return':
            locals = frame.f_locals
            func_locals.update(dict(((k, locals.get(k)) for k in keys)))
            sys.settrace(None)
        return probe_func

    sys.settrace(probe_func)
    function()
    return property(**func_locals)


def accepts(*types):

    def check_accepts(f):

        def new_f(*args, **kwds):
            for a, t in zip(args, types):
                pass

            return f(*args, **kwds)

        new_f.__name__ = f.__name__
        return new_f

    return check_accepts


def returns(rtype):

    def check_returns(f):

        def new_f(*args, **kwds):
            result = f(*args, **kwds)
            return result

        new_f.__name__ = f.__name__
        return new_f

    return check_returns


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


def attrs(**kwds):

    def decorate(f):
        for k in kwds:
            setattr(f, k, kwds[k])

        return f

    return decorate


def deprecated(func):

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn_explicit('Call to deprecated function %(funcname)s.' % {'funcname': func.__name__}, category=DeprecationWarning, filename=func.__code__.co_filename, lineno=func.__code__.co_firstlineno + 1)
        return func(*args, **kwargs)

    return new_func
