#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\resourceLoadingIndicator.py
import blue
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.base import ReverseScaleDpi
from eve.client.script.ui.control.themeColored import FillThemeColored, SpriteThemeColored
from localization import GetByLabel
import uthread2
import math
import weakref
import carbonui.const as uiconst
from carbonui.primitives.container import Container

class ResourceLoadingIndicator(Container):
    default_name = 'loadingindicator'
    default_align = uiconst.TOPLEFT
    default_width = 48
    default_height = 32
    default_state = uiconst.UI_NORMAL
    tooltip = None
    isGlobal = False
    enabled = True
    active = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isGlobal = bool(attributes.isGlobal)
        if not self.isGlobal:
            sm.GetService('gameui').DisableResourceLoadingIndicator()
        self.wheel = SpriteThemeColored(parent=self, align=uiconst.CENTER, pos=(0, 0, 48, 48), texturePath='res:/UI/Texture/loadingWheel.png', state=uiconst.UI_DISABLED, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.0)
        self.wheelfull = SpriteThemeColored(parent=self, align=uiconst.CENTER, pos=(0, 0, 48, 48), texturePath='res:/UI/Texture/loadingWheel_full.png', state=uiconst.UI_DISABLED, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.1)
        self.downloadingBar = FillThemeColored(parent=self, align=uiconst.BOTTOMLEFT, state=uiconst.UI_HIDDEN, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        self.loadingBar = FillThemeColored(parent=self, align=uiconst.BOTTOMLEFT, state=uiconst.UI_HIDDEN, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        self.queueBar = FillThemeColored(parent=self, align=uiconst.BOTTOMLEFT, state=uiconst.UI_HIDDEN, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        uthread2.StartTasklet(self._Update_t)

    def Close(self, *args):
        if not self.isGlobal:
            sm.GetService('gameui').EnableResourceLoadingIndicator()
        Container.Close(self, *args)

    def Enable(self):
        self.enabled = True
        self.display = True

    def Disable(self):
        self.enabled = False
        self.display = False

    def LoadTooltipPanel(self, tooltipPanel, *args, **kwds):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=GetByLabel('Tooltips/Neocom/ResourceLoadingIndicator'), bold=True)
        if self.downloadingBar.display:
            tooltipPanel.readout = tooltipPanel.AddLabelMedium()
        self.tooltip = weakref.ref(tooltipPanel)

    def GetTooltipPointer(self):
        if self.downloadingBar.display:
            return uiconst.POINT_LEFT_3
        else:
            return uiconst.POINT_LEFT_2

    def _UpdateHelper(self):
        if not self.enabled:
            return
        status = blue.threadMonitor.GetStatus()
        downloads = 0
        loads = 0
        for threadId, threadStatus in status:
            if threadStatus == 3:
                downloads += 1
            elif threadStatus > 0:
                loads += 1

        if self.downloadingBar.display:
            barWidth = ReverseScaleDpi(self.displayWidth) / 3 - 2
            barHeight = ReverseScaleDpi(self.displayHeight)
            self.downloadingBar.height = min(downloads, barHeight)
            self.downloadingBar.width = barWidth
            self.loadingBar.height = min(loads, barHeight)
            self.loadingBar.width = barWidth
            self.loadingBar.left = barWidth + 1
            inQueue = blue.resMan.pendingLoads + blue.resMan.pendingPrepares
            self.queueBar.height = min(inQueue, barHeight)
            self.queueBar.width = barWidth
            self.queueBar.left = barWidth * 2 + 2
            if self.tooltip:
                tooltip = self.tooltip()
                if tooltip and not tooltip.destroyed:
                    tooltip.readout.text = 'downloads: %s<br>loads: %s<br>inQueue: %s' % (downloads, loads, inQueue)
        if downloads > 0:
            if not self.active:
                self.active = True
                uicore.animations.FadeTo(self.wheel, startVal=self.wheel.opacity, endVal=1.0, duration=0.3)
            if not self.wheel.HasAnimation('rotation'):
                uicore.animations.MorphScalar(self.wheel, 'rotation', self.wheel.rotation, -2 * math.pi + self.wheel.rotation, duration=1.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        elif self.active:
            self.active = False
            uicore.animations.FadeTo(self.wheel, startVal=self.wheel.opacity, endVal=0.0, duration=0.3)

    def _Update_t(self):
        while not self.destroyed:
            self._UpdateHelper()
            uthread2.Sleep(1.0)

    def SetBarsActive(self, active):
        self.downloadingBar.display = active
        self.loadingBar.display = active
        self.queueBar.display = active
