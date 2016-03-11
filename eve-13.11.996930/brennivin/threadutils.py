#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\brennivin\threadutils.py
import inspect as _inspect
import sys as _sys
import threading as _threading
import time as _time
import traceback as _traceback
from . import compat as _compat, dochelpers as _dochelpers

class ChunkIter(object):

    @classmethod
    def start_thread(cls, target, name):
        thread = _threading.Thread(target=target, name=name)
        thread.daemon = True
        thread.start()
        return thread

    def __init__(self, iterable_, callback, chunksize = 50):
        self._isFinished = False
        self._cancelReq = False
        self.chunksize = chunksize
        self.fireCount = 0
        self.iterable = iterable_
        self._fireCallback = Signal('list')
        self._fireCallback.connect(callback)
        self.threading = _threading
        self.sleep = _time.sleep
        self.thread = type(self).start_thread(self._run_thread, 'ChunkIterWorker')

    def _run_thread(self):
        chunk = []
        for item in self.iterable:
            chunk.append(item)
            if len(chunk) == self.chunksize:
                self._fireCallback.emit(list(chunk))
                del chunk[:]
            if self._cancelReq:
                break

        if chunk and not self._cancelReq:
            self._fireCallback.emit(chunk)
        self._isFinished = True

    def wait_for_completion(self, timeout = None):
        self.thread.join(timeout)

    def wait_chunks(self, chunks = 1, sleep_interval = 1):
        if self._isFinished:
            return
        fireCnt = [0]

        def onChunk(_):
            fireCnt[0] += 1

        self._fireCallback.connect(onChunk)
        while not self._isFinished and fireCnt[0] < chunks:
            self.sleep(sleep_interval)

    WaitChunks = wait_chunks

    def is_finished(self):
        return self._isFinished

    IsFinished = is_finished

    def cancel(self):
        self._cancelReq = True

    Cancel = cancel


class Signal(object):

    def __init__(self, eventdoc = None, onerror = _dochelpers.pretty_module_func(_traceback.print_exception)):
        self._delegates = []
        self.eventdoc = eventdoc
        self.onerror = onerror

    def connect(self, callback):
        self._delegates.append(callback)

    def emit(self, *args, **kwargs):
        dels = list(self._delegates)
        for d in dels:
            try:
                d(*args, **kwargs)
            except Exception:
                self.onerror(*_sys.exc_info())

        return len(dels)

    def disconnect(self, callback):
        self._delegates.remove(callback)

    def clear(self):
        self._delegates = []


class ExceptionalThread(_threading.Thread):

    def __init__(self, *args, **kwargs):
        self.reraise = kwargs.pop('reraise', None)
        _threading.Thread.__init__(self, *args, **kwargs)
        self.excepted = Signal('(etype, value, tb)')
        self.exc_info = None

    def run(self):
        try:
            _threading.Thread.run(self)
        except Exception:
            self.exc_info = _sys.exc_info()
            defaultExceptHook = _sys.excepthook == _sys.__excepthook__
            if not defaultExceptHook:
                _sys.excepthook(*self.exc_info)
            hadlisteners = self.excepted.emit(self.exc_info)
            reraise = self.reraise
            if reraise is None:
                if not defaultExceptHook:
                    reraise = False
                elif hadlisteners:
                    reraise = False
                else:
                    reraise = True
            if reraise is True:
                raise

    def join(self, timeout = None):
        _threading.Thread.join(self, timeout)
        if self.exc_info:
            _compat.reraise(self.exc_info[0], self.exc_info[1], self.exc_info[2])


class NotAThread(_threading.Thread):
    exc_info = None
    _started_nota = False

    def start(self):
        self._started_nota = True
        self.run()

    def join(self, timeout = None):
        if not self._started_nota:
            raise RuntimeError('cannot join thread before it is started')


class TimerExt(_compat.TimerCls):

    def __init__(self, interval, function, args = (), kwargs = None):
        if float(interval) <= 0:
            raise ValueError('interval must be > 0, got %s' % interval)
        if function is None:
            raise ValueError('function cannot be None.')
        _compat.TimerCls.__init__(self, interval, function, args, kwargs or {})
        self._lock = _threading.Lock()
        self._restartRequested = False
        self.name = 'TimerExtThread'

    def restart(self):
        with self._lock:
            if self._restartRequested:
                return
            if self.finished.isSet():
                raise RuntimeError('Thread has already finished, cannot be restarted.')
            self._restartRequested = True
            self.finished.set()

    def run(self):
        while True:
            self.finished.wait(self.interval)
            with self._lock:
                timedOut = not self.finished.isSet()
                if timedOut:
                    self.finished.set()
                else:
                    cancelled = not self._restartRequested
                    if cancelled:
                        return
                    self.finished.clear()
                    self._restartRequested = False
            if timedOut:
                self.function(*self.args, **self.kwargs)
                return


def join_timeout(thread, timeout = 8, errtype = RuntimeError):
    thread.join(timeout)
    if thread.is_alive():
        raise errtype('%s is still alive!' % thread)


class Token(object):

    def __init__(self):
        self._isSet = False

    def set(self):
        self._isSet = True

    def is_set(self):
        return self._isSet


def memoize(func = None, uselock = False, _lockcls = _dochelpers.ignore):

    def hasParameterless(func_):
        argspec = _inspect.getargspec(func_)
        return any(argspec)

    if not func and not uselock:
        raise AssertionError('If not using lock, must provide func (decorate without params)')
    cache = []
    if callable(func):
        if hasParameterless(func):
            raise ValueError('Function cannot have parameters.')

        def inner(*args, **kwargs):
            if not cache:
                cache.append(func(*args, **kwargs))
            return cache[0]

        return inner
    lock = (_lockcls or _threading.Lock)()

    def inner(func_):

        def inner2(*args, **kwargs):
            if not cache:
                with lock:
                    if not cache:
                        cache.append(func_(*args, **kwargs))
            return cache[0]

        return inner2

    return inner


class expiring_memoize(object):

    def __init__(self, expiry = 0, gettime = None):
        self.expiry = expiry
        self.gettime = gettime or _time.time

    def __call__(self, func):

        def wrapped(*args):
            try:
                cache = func._cache
            except AttributeError:
                cache = func._cache = {}

            try:
                result, timestamp = cache[args]
                if self.gettime() - timestamp < self.expiry:
                    return result
            except KeyError:
                pass

            result = func(*args)
            cache[args] = (result, self.gettime())
            return result

        def clear_cache():
            try:
                cache = func._cache
                cache.clear()
            except AttributeError:
                pass

        def prime_cache_result(args, result):
            try:
                cache = func._cache
            except AttributeError:
                cache = func._cache = {}

            cache[args] = (result, self.gettime())

        def remove_from_cache(args):
            try:
                cache = func._cache
            except AttributeError:
                return

            if args in cache:
                del cache[args]

        wrapped.clear_cache = clear_cache
        wrapped.prime_cache_result = prime_cache_result
        wrapped.remove_from_cache = remove_from_cache
        return wrapped
