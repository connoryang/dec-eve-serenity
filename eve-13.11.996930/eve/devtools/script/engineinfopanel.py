#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\engineinfopanel.py
from carbonui import const as uiconst, const
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import Label
import blue
import util
import uthread2

def GetMemoryLabel(memory, last, base):
    RED = '0xffff0000'
    GREEN = '0xff00ff00'
    delta = last - memory
    if delta < 0:
        delta = -delta
        deltaColor = RED
    else:
        deltaColor = GREEN
    totalDelta = base - memory
    if totalDelta < 0:
        totalDelta = -totalDelta
        totalDeltaColor = RED
    else:
        totalDeltaColor = GREEN
    memoryStr = util.FmtAmt(memory / 1024)
    deltaStr = util.FmtAmt(delta / 1024)
    totalDeltaStr = util.FmtAmt(totalDelta / 1024)
    text = '%s / <color=%s>%s</color> / <color=%s>%s</color>' % (memoryStr,
     deltaColor,
     deltaStr,
     totalDeltaColor,
     totalDeltaStr)
    return text


class EngineInfoPanel(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        infoLeft = Container(parent=self, align=uiconst.TOLEFT_PROP, width=0.5)
        infoRight = Container(parent=self, align=uiconst.TOALL)
        self.fpsLabel = Label(parent=infoLeft, align=uiconst.TOTOP)
        self.workingSetLabel = Label(parent=infoLeft, align=uiconst.TOTOP)
        self.commitSizeLabel = Label(parent=infoLeft, align=uiconst.TOTOP)
        self.resCacheLabel = Label(parent=infoRight, align=uiconst.TOTOP)
        self.ciderVersionLabel = Label(parent=infoRight, align=uiconst.TOTOP)
        self.fpsStat = blue.statistics.Find('FPS')
        self.frameTimeStat = blue.statistics.Find('Trinity/SmoothedFrameTime')
        self.workingSetStat = blue.statistics.Find('Blue/Memory/WorkingSet')
        self.lastWorkingSetSize = 0
        self.baseWorkingSetSize = self.workingSetStat.value
        self.commitSizeStat = blue.statistics.Find('Blue/Memory/PageFileUsage')
        self.lastCommitSize = 0
        self.baseCommitSize = self.commitSizeStat.value
        self.ciderVersionLabel.text = 'Not running Cider'
        if blue.sysinfo.isTransgaming:
            self.ciderVersionLabel.text = 'Cider: %s' % blue.win32.TGGetVersion()
        uthread2.StartTasklet(self.Update)

    def Update(self):
        while not self.destroyed:
            self.UpdateInfo()
            uthread2.Sleep(0.5)

    def UpdateInfo(self):
        self.fpsLabel.text = 'Fps: %6.2f (%5.1fms)' % (self.fpsStat.value / 100.0, self.frameTimeStat.value * 1000.0)
        self.workingSetLabel.text = 'Working set: ' + GetMemoryLabel(self.workingSetStat.value, self.lastWorkingSetSize, self.baseWorkingSetSize)
        self.commitSizeLabel.text = 'Commit size: ' + GetMemoryLabel(self.commitSizeStat.value, self.lastCommitSize, self.baseCommitSize)
        self.lastWorkingSetSize = self.workingSetStat.value
        self.lastCommitSize = self.commitSizeStat.value
        inUse = util.FmtAmt(blue.motherLode.memUsage / 1024)
        total = util.FmtAmt(blue.motherLode.maxMemUsage / 1024)
        num = blue.motherLode.size()
        self.resCacheLabel.text = 'Resource Cache Usage: %sK / %sK - %s objects' % (inUse, total, num)
