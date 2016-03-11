#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\eventCounters.py
from contextlib import contextmanager

class EventCount(object):

    def __init__(self):
        self.__eventCount = {}

    @contextmanager
    def Event(self, key):
        self._AddEventCount(key)
        try:
            yield
        finally:
            self._DecreaseEventCount(key)

        self._OnEvent(key)

    def _AddEventCount(self, key):
        if key not in self.__eventCount:
            self.__eventCount[key] = 1
        else:
            self.__eventCount[key] += 1

    def _DecreaseEventCount(self, key):
        self.__eventCount[key] -= 1
        if self.__eventCount[key] < 1:
            del self.__eventCount[key]

    def IsEventHappening(self, key):
        if key is None:
            return False
        return self.__eventCount.get(key, 0) > 0

    def _OnEvent(self, key):
        pass


class BrainUpdate(EventCount):

    def __init__(self, callback):
        super(BrainUpdate, self).__init__()
        self.__callback = callback

    def _OnEvent(self, key):
        self.__callback(key)
