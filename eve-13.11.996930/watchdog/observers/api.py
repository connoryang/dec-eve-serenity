#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\watchdog\observers\api.py
from __future__ import with_statement
import threading
from watchdog.utils import BaseThread
from watchdog.utils.compat import queue
from watchdog.utils.bricks import SkipRepeatsQueue
DEFAULT_EMITTER_TIMEOUT = 1
DEFAULT_OBSERVER_TIMEOUT = 1

class EventQueue(SkipRepeatsQueue):
    pass


class ObservedWatch(object):

    def __init__(self, path, recursive):
        self._path = path
        self._is_recursive = recursive

    @property
    def path(self):
        return self._path

    @property
    def is_recursive(self):
        return self._is_recursive

    @property
    def key(self):
        return (self.path, self.is_recursive)

    def __eq__(self, watch):
        return self.key == watch.key

    def __ne__(self, watch):
        return self.key != watch.key

    def __hash__(self):
        return hash(self.key)

    def __repr__(self):
        return '<ObservedWatch: path=%s, is_recursive=%s>' % (self.path, self.is_recursive)


class EventEmitter(BaseThread):

    def __init__(self, event_queue, watch, timeout = DEFAULT_EMITTER_TIMEOUT):
        BaseThread.__init__(self)
        self._event_queue = event_queue
        self._watch = watch
        self._timeout = timeout

    @property
    def timeout(self):
        return self._timeout

    @property
    def watch(self):
        return self._watch

    def queue_event(self, event):
        self._event_queue.put((event, self.watch))

    def queue_events(self, timeout):
        pass

    def run(self):
        try:
            while self.should_keep_running():
                self.queue_events(self.timeout)

        finally:
            pass


class EventDispatcher(BaseThread):

    def __init__(self, timeout = DEFAULT_OBSERVER_TIMEOUT):
        BaseThread.__init__(self)
        self._event_queue = EventQueue()
        self._timeout = timeout

    @property
    def timeout(self):
        return self._timeout

    @property
    def event_queue(self):
        return self._event_queue

    def dispatch_events(self, event_queue, timeout):
        pass

    def run(self):
        while self.should_keep_running():
            try:
                self.dispatch_events(self.event_queue, self.timeout)
            except queue.Empty:
                continue


class BaseObserver(EventDispatcher):

    def __init__(self, emitter_class, timeout = DEFAULT_OBSERVER_TIMEOUT):
        EventDispatcher.__init__(self, timeout)
        self._emitter_class = emitter_class
        self._lock = threading.RLock()
        self._watches = set()
        self._handlers = dict()
        self._emitters = set()
        self._emitter_for_watch = dict()

    def _add_emitter(self, emitter):
        self._emitter_for_watch[emitter.watch] = emitter
        self._emitters.add(emitter)

    def _remove_emitter(self, emitter):
        del self._emitter_for_watch[emitter.watch]
        self._emitters.remove(emitter)
        emitter.stop()
        try:
            emitter.join()
        except RuntimeError:
            pass

    def _clear_emitters(self):
        for emitter in self._emitters:
            emitter.stop()

        for emitter in self._emitters:
            try:
                emitter.join()
            except RuntimeError:
                pass

        self._emitters.clear()
        self._emitter_for_watch.clear()

    def _add_handler_for_watch(self, event_handler, watch):
        if watch not in self._handlers:
            self._handlers[watch] = set()
        self._handlers[watch].add(event_handler)

    def _remove_handlers_for_watch(self, watch):
        del self._handlers[watch]

    @property
    def emitters(self):
        return self._emitters

    def start(self):
        for emitter in self._emitters:
            emitter.start()

        super(BaseObserver, self).start()

    def schedule(self, event_handler, path, recursive = False):
        with self._lock:
            watch = ObservedWatch(path, recursive)
            self._add_handler_for_watch(event_handler, watch)
            if self._emitter_for_watch.get(watch) is None:
                emitter = self._emitter_class(event_queue=self.event_queue, watch=watch, timeout=self.timeout)
                self._add_emitter(emitter)
                if self.is_alive():
                    emitter.start()
            self._watches.add(watch)
        return watch

    def add_handler_for_watch(self, event_handler, watch):
        with self._lock:
            self._add_handler_for_watch(event_handler, watch)

    def remove_handler_for_watch(self, event_handler, watch):
        with self._lock:
            self._handlers[watch].remove(event_handler)

    def unschedule(self, watch):
        with self._lock:
            emitter = self._emitter_for_watch[watch]
            del self._handlers[watch]
            self._remove_emitter(emitter)
            self._watches.remove(watch)

    def unschedule_all(self):
        with self._lock:
            self._handlers.clear()
            self._clear_emitters()
            self._watches.clear()

    def on_thread_stop(self):
        self.unschedule_all()

    def dispatch_events(self, event_queue, timeout):
        event, watch = event_queue.get(block=True, timeout=timeout)
        with self._lock:
            for handler in list(self._handlers.get(watch, [])):
                if handler in self._handlers.get(watch, []):
                    handler.dispatch(event)

        event_queue.task_done()
