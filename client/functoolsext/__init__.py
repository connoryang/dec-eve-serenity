#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\functoolsext\__init__.py
from collections import namedtuple
from functools import *
import inspect
from threading import RLock
_CacheInfo = namedtuple('CacheInfo', ['hits',
 'misses',
 'maxsize',
 'currsize'])

class _HashedSeq(list):
    __slots__ = 'hashvalue'

    def __init__(self, tup, hash = hash):
        self[:] = tup
        self.hashvalue = hash(tup)

    def __hash__(self):
        return self.hashvalue


def _make_key(args, kwds, typed, kwd_mark = (object(),), fasttypes = set([int,
 str,
 frozenset,
 type(None)]), sorted = sorted, tuple = tuple, type = type, len = len):
    key = args
    if kwds:
        sorted_items = sorted(kwds.items())
        key += kwd_mark
        for item in sorted_items:
            key += item

    if typed:
        key += tuple((type(v) for v in args))
        if kwds:
            key += tuple((type(v) for k, v in sorted_items))
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedSeq(key)


def lru_cache(maxsize = 128, typed = False):

    def decorating_function(user_function):
        cache = dict()
        stats = [0, 0]
        HITS, MISSES = (0, 1)
        make_key = _make_key
        cache_get = cache.get
        _len = len
        lock = RLock()
        root = []
        root[:] = [root,
         root,
         None,
         None]
        nonlocal_root = [root]
        PREV, NEXT, KEY, RESULT = (0, 1, 2, 3)
        if maxsize == 0:

            def wrapper(*args, **kwds):
                result = user_function(*args, **kwds)
                stats[MISSES] += 1
                return result

        elif maxsize is None:

            def wrapper(*args, **kwds):
                key = make_key(args, kwds, typed)
                result = cache_get(key, root)
                if result is not root:
                    stats[HITS] += 1
                    return result
                result = user_function(*args, **kwds)
                cache[key] = result
                stats[MISSES] += 1
                return result

        else:

            def wrapper(*args, **kwds):
                key = make_key(args, kwds, typed) if kwds or typed else args
                with lock:
                    link = cache_get(key)
                    if link is not None:
                        root, = nonlocal_root
                        link_prev, link_next, key, result = link
                        link_prev[NEXT] = link_next
                        link_next[PREV] = link_prev
                        last = root[PREV]
                        last[NEXT] = root[PREV] = link
                        link[PREV] = last
                        link[NEXT] = root
                        stats[HITS] += 1
                        return result
                result = user_function(*args, **kwds)
                with lock:
                    root, = nonlocal_root
                    if key in cache:
                        pass
                    elif _len(cache) >= maxsize:
                        oldroot = root
                        oldroot[KEY] = key
                        oldroot[RESULT] = result
                        root = nonlocal_root[0] = oldroot[NEXT]
                        oldkey = root[KEY]
                        oldvalue = root[RESULT]
                        root[KEY] = root[RESULT] = None
                        del cache[oldkey]
                        cache[key] = oldroot
                    else:
                        last = root[PREV]
                        link = [last,
                         root,
                         key,
                         result]
                        last[NEXT] = root[PREV] = cache[key] = link
                    stats[MISSES] += 1
                return result

        def cache_info():
            with lock:
                return _CacheInfo(stats[HITS], stats[MISSES], maxsize, len(cache))

        def cache_clear():
            with lock:
                cache.clear()
                root = nonlocal_root[0]
                root[:] = [root,
                 root,
                 None,
                 None]
                stats[:] = [0, 0]

        wrapper.__wrapped__ = user_function
        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return update_wrapper(wrapper, user_function)

    return decorating_function


def func_takes_arguments(f):
    try:
        fc = f.func_code
    except AttributeError:
        raise AttributeError('Cannot inspect built-ins: %s.' % f)

    arguments, varargs, keywords = inspect.getargs(fc)
    if inspect.ismethod(f):
        arguments.pop(0)
    if any([arguments, varargs, keywords]):
        return True
    return False
