#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\common\eventExceptionEater.py
from contextlib import contextmanager

@contextmanager
def AchievementEventExceptionEater():
    try:
        yield
    except Exception as e:
        import log
        log.LogTraceback('Failed when recording event, e = %s' % e)
