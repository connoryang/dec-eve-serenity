#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\brennivin\signals.py
import logging
from weakref import WeakKeyDictionary
from weakness import callable_proxy, WeakMethod
logger = logging.getLogger(__name__)

class Signal(object):

    def __init__(self):
        self._delegates = set()

    def connect(self, callback):
        self._delegates.add(callback)

    def emit(self, *args, **kwargs):
        delegates = list(self._delegates)
        for d in delegates:
            try:
                d(*args, **kwargs)
            except:
                logger.exception('Signal handler %s raise and exception', d)

        return len(delegates)

    def disconnect(self, callback):
        self._delegates.discard(callback)

    def clear(self):
        self._delegates = set()


class WeakReferenceSignal(object):

    def __init__(self):
        self._delegates = []

    def connect(self, callback):
        self._delegates.append(WeakMethod(callback))

    def emit(self, *args, **kwargs):
        for weak_method in self._delegates[:]:
            try:
                weak_method(*args, **kwargs)
            except ReferenceError:
                self.disconnect(weak_method)
            except:
                logger.exception('Signal handler %s raise and exception', weak_method)

    def disconnect(self, callback):
        try:
            self._delegates = [ weak_method for weak_method in self._delegates if weak_method != callback ]
        except ValueError:
            pass

    def clear(self):
        self._delegates = []

    def count(self):
        return len(self._delegates)
