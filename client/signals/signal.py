#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\signals\signal.py
import inspect
import weakref
import logging

class Signal(object):

    def __init__(self):
        self._functions = weakref.WeakSet()
        self._methods = weakref.WeakKeyDictionary()

    def __call__(self, *args, **kwargs):
        for call in self:
            try:
                call(*args, **kwargs)
            except Exception:
                logging.exception('Exception in signal handler: {}'.format(call))

    def __len__(self):
        return len(self._functions) + sum([ len(methods) for methods in self._methods.itervalues() ])

    def __iter__(self):
        callables = []
        callables.extend(self._functions)
        for obj, funcs in self._methods.items():
            callables.extend([ func.__get__(obj) for func in funcs ])

        return iter(callables)

    def connect(self, slot):
        if inspect.ismethod(slot):
            if slot.__self__ not in self._methods:
                self._methods[slot.__self__] = weakref.WeakSet()
            self._methods[slot.__self__].add(slot.__func__)
        elif inspect.isfunction(slot) and slot.__name__ == '<lambda>':
            raise TypeError('Signal cannot connect lambda methods')
        elif callable(slot):
            self._functions.add(slot)
        else:
            raise TypeError('Signal connect requires a callable slot')

    def disconnect(self, slot):
        if inspect.ismethod(slot):
            if slot.__self__ in self._methods:
                self._methods[slot.__self__].discard(slot.__func__)
        else:
            self._functions.discard(slot)

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
