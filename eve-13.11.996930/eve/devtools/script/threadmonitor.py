#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\threadmonitor.py
import blue
import uicontrols
import uthread2
import collections
import carbonui.const as uiconst
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.util.color import Color
STATUS_TO_COLOR = [(1, 1, 1, 0.25),
 Color.GREEN,
 Color.YELLOW,
 Color.RED]

class ThreadStatusLine(VectorLineTrace):
    default_name = 'threadstatusline'
    default_align = uiconst.TOALL
    default_lineWidth = 4.0
    pixelsPerSample = 2

    def ApplyAttributes(self, attributes):
        VectorLineTrace.ApplyAttributes(self, attributes)
        self.data = attributes.get('data', [])
        self.Build()

    def Build(self):
        self.Flush()
        if not self.data:
            return
        width, height = self.GetCurrentAbsoluteSize()
        prevValue = -1
        x = 0
        halfHeight = self.lineWidth / 2
        for value in self.data:
            if value != prevValue:
                if prevValue != -1:
                    self.AddPoint((x, halfHeight), STATUS_TO_COLOR[prevValue])
                self.AddPoint((x, halfHeight), STATUS_TO_COLOR[value])
            x += self.pixelsPerSample
            if x > width:
                break

        self.AddPoint((x, halfHeight), STATUS_TO_COLOR[value])


class ThreadMonitor(uicontrols.Window):
    __guid__ = 'form.ThreadMonitor'
    default_caption = 'Thread Monitor'
    default_windowID = 'ThreadMonitor'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(0)
        self.threads = {}
        self.threadLines = {}
        self.main = GridContainer(parent=self.sr.main, align=uiconst.TOALL, padding=(4, 4, 4, 4), clipChildren=True)
        uthread2.StartTasklet(self._Update_t)

    def _UpdateHelper(self):
        status = blue.threadMonitor.GetStatus()
        threads = []
        for threadId, threadStatus in status:
            threads.append(threadId)
            history = self.threads.get(threadId, collections.deque(maxlen=256))
            history.appendleft(threadStatus)
            self.threads[threadId] = history

        self.UpdateThreadLines(threads)

    def _Update_t(self):
        while not self.destroyed:
            self._UpdateHelper()
            uthread2.Sleep(0.5)

    def UpdateThreadLines(self, threads):
        self.main.lines = len(threads)
        for threadId in threads:
            if threadId not in self.threadLines:
                line = ThreadStatusLine(parent=self.main, data=self.threads[threadId], height=6)
                self.threadLines[threadId] = line
            else:
                self.threadLines[threadId].Build()
