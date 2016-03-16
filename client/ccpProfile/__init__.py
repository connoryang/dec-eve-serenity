#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\ccpProfile\__init__.py
try:
    from . import blueTaskletImplementation as implementation
except (ImportError, AttributeError):
    from . import noopImplementation as implementation

Timer = implementation.Timer
TimerPush = implementation.TimerPush
TimedFunction = implementation.TimedFunction
PushTimer = implementation.PushTimer
PopTimer = implementation.PopTimer
CurrentTimer = implementation.CurrentTimer
EnterTasklet = implementation.EnterTasklet
ReturnFromTasklet = implementation.ReturnFromTasklet
