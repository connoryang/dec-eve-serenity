#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\modules\monitor.py
import blue
from carbon.common.script.sys.service import Service
import uthread

class FpsMonitorSvc(Service):
    __guid__ = 'svc.fpsMonitorSvc'
    __servicename__ = 'Fps Monitor Service'
    __displayname__ = 'Fps Monitor Service'

    def Run(self, *args):
        self.collectingFpsStats = False
        self.fpsStat = blue.statistics.Find('FPS')
        self.frameTimeStat = blue.statistics.Find('Trinity/FrameTime')

    def GetFPS(self):
        return self.fpsStat.value

    def IsCollectingStats(self):
        return self.collectingFpsStats

    def GetStatsCollectionTime(self):
        return blue.os.GetWallclockTime() - self.collectingFpsStats

    def GetStatsData(self):
        return self.statsData

    def StartCollectingData(self, *args):
        self.fpsStats = []
        self.statsData = {'fps': [],
         'frametime': []}
        uthread.new(self.CollectDataThread)

    def CollectDataThread(self):
        MAX_STATS = 36000
        self.collectingFpsStats = blue.os.GetWallclockTime()
        while self.collectingFpsStats:
            deltaTime = blue.os.GetWallclockTime() - self.collectingFpsStats
            self.fpsStats.append((deltaTime, self.fpsStat.value))
            fps = self.fpsStat.value
            frametime = self.frameTimeStat.value
            if fps:
                self.statsData['fps'].append(fps)
            if frametime:
                self.statsData['frametime'].append(frametime)
            if deltaTime > const.HOUR:
                self.StopCollectingData()
                return
            blue.synchro.SleepWallclock(200)

    def StopCollectingData(self, *args):
        self.collectingFpsStats = None
        ret = self.fpsStats[:]
        self.fpsStats = []
        return ret
