#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\gametime\__init__.py
from carbon.common.lib.const import SEC, MIN, DAY, MSEC

class BlueTimeImplementation(object):

    def __init__(self):
        import blue
        self.GetSimTime = blue.os.GetSimTime
        self.GetWallclockTime = blue.os.GetWallclockTime
        self.GetWallclockTimeNow = blue.os.GetWallclockTimeNow


class PythonTimeImplementation(object):

    def __init__(self):
        import time
        GetTime = lambda : long(time.time() * SEC)
        self.GetSimTime = GetTime
        self.GetWallclockTime = GetTime
        self.GetWallclockTimeNow = GetTime


try:
    implementation = BlueTimeImplementation()
except ImportError:
    implementation = PythonTimeImplementation()

GetSimTime = implementation.GetSimTime
GetWallclockTime = implementation.GetWallclockTime
GetWallclockTimeNow = implementation.GetWallclockTimeNow

def GetTimeDiff(a, b):
    return b - a


def GetSecondsSinceSimTime(time):
    return float(GetSimTime() - time) / SEC


def GetSecondsUntilSimTime(time):
    return -GetSecondsSinceSimTime(time)


def GetSimTimeAfterSeconds(seconds):
    return GetSimTime() + long(seconds * SEC)


def GetTimeOffsetInHours():
    try:
        import eveLocalization
        return int(eveLocalization.GetTimeDelta() / 3600)
    except ImportError:
        return 0


def GetDurationInClient(startTime, duration):
    return duration + (startTime - GetSimTime()) / MSEC


class Timer(object):

    def __init__(self, GetTime, Sleep, maxSleepTime):
        self.maxSleepTime = maxSleepTime
        self.GetTime = GetTime
        self.Sleep = Sleep

    def SleepUntil(self, wakeUpTime, minSleep = 5000):
        sleepTime = wakeUpTime - self.GetTime()
        if sleepTime > 0:
            while True:
                sleepTime = wakeUpTime - self.GetTime()
                if sleepTime <= self.maxSleepTime:
                    self.Sleep(sleepTime / MSEC)
                    break
                else:
                    self.Sleep(self.maxSleepTime / MSEC)

        else:
            self.Sleep(minSleep)
