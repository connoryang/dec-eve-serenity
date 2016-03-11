#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\jumptimer.py
import logging
import ccpmetrics
import gametime
import uthread2
logger = logging.getLogger(__name__)

def GetJumpTimer():
    jt = JumpTimer(JumpTimeReporter())
    sm.RegisterNotify(jt)
    return jt


class JumpTimer(object):
    __notifyevents__ = ['OnSpecialFX', 'DoBallClear']

    def __init__(self, reportJumpTime):
        self.reportJumpTime = reportJumpTime
        self._ResetJump()

    def OnSpecialFX(self, *args, **kwargs):
        guid = args[5]
        if guid in ('effects.JumpOut',):
            self.JumpStarted(args[13][0], session.solarsystemid)

    def DoBallClear(self, solarSystemItem):
        uthread2.StartTasklet(self.JumpEnded, solarSystemItem.itemID)

    def JumpStarted(self, toSolarSystemID, fromSolarSystemID):
        self.toSolarSystemID, self.fromSolarSystemID = toSolarSystemID, fromSolarSystemID
        self.jumpStarted = gametime.GetWallclockTimeNow()

    def JumpEnded(self, solarSystemID):
        if self.toSolarSystemID is None:
            logger.info("toSolarSystemID hasn't been initialized so ignoring this event")
        if solarSystemID != self.toSolarSystemID:
            logger.info('was expecting a jump from %s to %s but actually loaded up %s', self.fromSolarSystemID, self.toSolarSystemID, solarSystemID)
        else:
            self.reportJumpTime(self.toSolarSystemID, self.fromSolarSystemID, gametime.GetWallclockTimeNow() - self.jumpStarted)
            self._ResetJump()

    def _ResetJump(self):
        self.fromSolarSystemID = None
        self.toSolarSystemID = None
        self.jumpStarted = None


class JumpTimeReporter(object):

    def __init__(self):
        self.metrics = ccpmetrics.CCPMetrics(ccpmetrics.METRICS_SERVER, ccpmetrics.METRICS_SERVER_PORT)
        self.serverIp = _GetServerIP()

    def __call__(self, toSolarSystemID, fromSolarSystemID, jumpTimeInBlue):
        try:
            jumpTimeInMsec = jumpTimeInBlue / gametime.MSEC
            self.metrics.gauge('jump_time', jumpTimeInMsec, secondaryValues={'toSolarSystemID': str(toSolarSystemID),
             'fromSolarSystemID': str(fromSolarSystemID)}, tags={'server': self.serverIp})
        except UnicodeDecodeError:
            logger.warn('Failed to report jump time')
        except Exception:
            logger.warn('Failed to report jump time statistic')


def PrintReportJumpTime(toSolarSystemID, fromSolarSystemID, jumpTimeInBlue):
    print '--------', toSolarSystemID, fromSolarSystemID, jumpTimeInBlue


def _GetServerIP():
    try:
        import login
        import utillib
        return login.GetServerIP(utillib.GetServerName())
    except Exception:
        return 'unknown'


if __name__ == '__main__':
    jtr = JumpTimeReporter()
    jtr(1, 2, 30 * gametime.SEC)
