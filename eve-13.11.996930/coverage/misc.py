#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\misc.py
import errno
import inspect
import os
import sys
from coverage.backward import md5, sorted
from coverage.backward import string_class, to_bytes

def nice_pair(pair):
    start, end = pair
    if start == end:
        return '%d' % start
    else:
        return '%d-%d' % (start, end)


def format_lines(statements, lines):
    pairs = []
    i = 0
    j = 0
    start = None
    while i < len(statements) and j < len(lines):
        if statements[i] == lines[j]:
            if start == None:
                start = lines[j]
            end = lines[j]
            j += 1
        elif start:
            pairs.append((start, end))
            start = None
        i += 1

    if start:
        pairs.append((start, end))
    ret = ', '.join(map(nice_pair, pairs))
    return ret


def short_stack():
    stack = inspect.stack()[:0:-1]
    return '\n'.join([ '%30s : %s @%d' % (t[3], t[1], t[2]) for t in stack ])


def expensive(fn):
    attr = '_cache_' + fn.__name__

    def _wrapped(self):
        if not hasattr(self, attr):
            setattr(self, attr, fn(self))
        return getattr(self, attr)

    return _wrapped


def bool_or_none(b):
    if b is None:
        return
    else:
        return bool(b)


def join_regex(regexes):
    if len(regexes) > 1:
        return '|'.join([ '(%s)' % r for r in regexes ])
    elif regexes:
        return regexes[0]
    else:
        return ''


def file_be_gone(path):
    try:
        os.remove(path)
    except OSError:
        _, e, _ = sys.exc_info()
        if e.errno != errno.ENOENT:
            raise


class Hasher(object):

    def __init__(self):
        self.md5 = md5()

    def update(self, v):
        self.md5.update(to_bytes(str(type(v))))
        if isinstance(v, string_class):
            self.md5.update(to_bytes(v))
        elif isinstance(v, (int, float)):
            self.update(str(v))
        elif isinstance(v, (tuple, list)):
            for e in v:
                self.update(e)

        elif isinstance(v, dict):
            keys = v.keys()
            for k in sorted(keys):
                self.update(k)
                self.update(v[k])

        else:
            for k in dir(v):
                if k.startswith('__'):
                    continue
                a = getattr(v, k)
                if inspect.isroutine(a):
                    continue
                self.update(k)
                self.update(a)

    def digest(self):
        return self.md5.digest()


class CoverageException(Exception):
    pass


class NoSource(CoverageException):
    pass


class NoCode(NoSource):
    pass


class NotPython(CoverageException):
    pass


class ExceptionDuringRun(CoverageException):
    pass
