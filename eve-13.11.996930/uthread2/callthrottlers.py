#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\uthread2\callthrottlers.py
from . import sleep

class CallCombiner(object):

    def __init__(self, func, throttleTime):
        self.isBeingCalled = False
        self.func = func
        self.throttleTime = throttleTime

    def __call__(self, *args, **kwargs):
        if self.isBeingCalled:
            return
        self.isBeingCalled = True
        try:
            sleep(self.throttleTime)
            return self.func(*args, **kwargs)
        finally:
            self.isBeingCalled = False
