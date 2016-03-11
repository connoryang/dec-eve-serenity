#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\control\loadingindicator.py
import blue
import uthread2
import math
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color

class LoadingIndicator(Container):
    default_name = 'loadingindicator'
    default_align = uiconst.TOPLEFT
    default_width = 48
    default_height = default_width

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        barWidth = self.width / 3
        x = 0
        y = self.height
        self.downloadingBar = Fill(parent=self, align=uiconst.TOPLEFT, left=x, top=y, width=barWidth, height=0, color=Color.RED, state=uiconst.UI_HIDDEN)
        x += barWidth
        self.loadingBar = Fill(parent=self, align=uiconst.TOPLEFT, left=x, top=y, width=barWidth, height=0, color=Color.GREEN, state=uiconst.UI_HIDDEN)
        x += barWidth
        self.queueBar = Fill(parent=self, align=uiconst.TOPLEFT, left=x, top=y, width=barWidth, height=0, color=Color.BLUE, state=uiconst.UI_HIDDEN)
        self.wheel = Sprite(parent=self, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/loadingWheel.png')
        uthread2.StartTasklet(self._Update_t)

    def _UpdateHelper(self):
        status = blue.threadMonitor.GetStatus()
        downloads = 0
        loads = 0
        for threadId, threadStatus in status:
            if threadStatus == 3:
                downloads += 1
            elif threadStatus > 0:
                loads += 1

        if self.downloadingBar.display:
            self.downloadingBar.height = min(downloads, self.height)
            self.downloadingBar.top = self.height - self.downloadingBar.height
            self.loadingBar.height = min(loads, self.height)
            self.loadingBar.top = self.height - self.loadingBar.height
            inQueue = blue.resMan.pendingLoads + blue.resMan.pendingPrepares
            self.queueBar.height = min(inQueue, self.height)
            self.queueBar.top = self.height - self.queueBar.height
        if not self.wheel.display and downloads + loads > 0:
            self.wheel.display = True
            uicore.animations.MorphScalar(self.wheel, 'rotation', 0.0, -2 * math.pi, duration=1.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        elif self.wheel.display and downloads + loads == 0:
            uicore.animations.StopAnimation(self.wheel, 'rotation')
            self.wheel.display = False

    def _Update_t(self):
        while not self.destroyed:
            self._UpdateHelper()
            uthread2.Sleep(0.25)

    def SetBarsActive(self, active):
        self.downloadingBar.display = active
        self.loadingBar.display = active
        self.downloadingBar.display = active
