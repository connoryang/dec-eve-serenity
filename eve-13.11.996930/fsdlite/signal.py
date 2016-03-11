#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsdlite\signal.py
import inspect
import weakref

class Signal(object):

    def __init__(self):
        self._functions = weakref.WeakSet()
        self._methods = weakref.WeakKeyDictionary()

    def __call__(self, *args, **kargs):
        for func in self._functions:
            func(*args, **kargs)

        for obj, funcs in self._methods.items():
            for func in funcs:
                func(obj, *args, **kargs)

    def connect(self, slot):
        if inspect.ismethod(slot):
            if slot.__self__ not in self._methods:
                self._methods[slot.__self__] = weakref.WeakSet()
            self._methods[slot.__self__].add(slot.__func__)
        else:
            self._functions.add(slot)

    def disconnect(self, slot):
        if inspect.ismethod(slot):
            if slot.__self__ in self._methods:
                self._methods[slot.__self__].remove(slot.__func__)
        elif slot in self._functions:
            self._functions.remove(slot)

    def clear(self):
        self._functions.clear()
        self._methods.clear()

    def wait(self):

        def callback(*args, **kwargs):
            callback.called = True

        callback.called = False
        self.connect(callback)
        while True:
            if callback.called:
                return
