#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\trinutils\callbackmanager.py
import trinity

class CallbackManager(object):
    _globalInstance = None

    def __init__(self):
        self._callbacks = []
        self._job = trinity.CreateRenderJob('CallbackJob')
        self._job.PythonCB(self.Pump)
        self._callBackRegistry = {}

    def _isJobRunning(self):
        return self._job in trinity.renderJobs.recurring

    def ScheduleCallback(self, callback, tag = None):
        self._callbacks.append(callback)
        if tag:
            self.UnscheduleCallbackByTag(tag)
            self._callBackRegistry[tag] = callback
        if not self._isJobRunning():
            self._job.ScheduleRecurring()

    def Pump(self):
        for cb in self._callbacks:
            cb()

    def UnscheduleCallbackByTag(self, tag):
        if tag in self._callBackRegistry:
            callback = self._callBackRegistry.pop(tag)
            self.UnscheduleCallback(callback)

    def UnscheduleCallback(self, callback):
        self._callbacks.remove(callback)
        if len(self._callbacks) < 1:
            self._job.UnscheduleRecurring()

    @staticmethod
    def GetGlobal():
        if CallbackManager._globalInstance is None:
            CallbackManager._globalInstance = CallbackManager()
        return CallbackManager._globalInstance
