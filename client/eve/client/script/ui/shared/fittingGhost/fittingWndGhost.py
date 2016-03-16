#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\fittingWndGhost.py
from carbon.common.script.util.format import FmtAmt
from eve.client.script.ui.shared.fittingGhost.baseFittingGhost import FittingGhost
from eve.client.script.ui.shared.fittingGhost.shipFittingControllerGhost import ShipFittingControllerGhost
from eve.client.script.ui.shared.fittingGhost.fittingUtilGhost import GetColoredText
from eve.client.script.ui.shared.fittingGhost.statsPanel import StatsPanelGhost
from eve.client.script.ui.shared.fittingGhost.ghostFittingPanels.minihangar import CargoCargoSlots, CargoDroneSlots
import locks
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.util.various_unsorted import SetOrder
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelMedium
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.shared.fitting.fittingUtil import GetBaseShapeSize, PANEL_WIDTH
from eve.client.script.ui.shared.fittingGhost.leftPanel import LeftPanel
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from eve.common.script.sys.eveCfg import GetActiveShip
from localization import GetByLabel
import uthread
WND_HEIGHT = 560
ANIM_DURATION = 0.25

class FittingWindowGhost(Window):
    __guid__ = 'form.FittingWindowGhost'
    __notifyevents__ = ['OnSetDevice']
    default_topParentHeight = 0
    default_fixedHeight = WND_HEIGHT
    default_windowID = 'fittingGhost'
    default_captionLabelPath = 'Tooltips/StationServices/ShipFitting'
    default_descriptionLabelPath = 'Tooltips/StationServices/ShipFitting_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/fitting.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnResizeable()
        self.HideHeaderFill()
        self.controller = None
        itemID = attributes.shipID or GetActiveShip()
        self._layoutLock = locks.Lock()
        self.controller = ShipFittingControllerGhost(itemID=itemID)
        self.controller.on_stats_changed.connect(self.UpdateStats)
        self.controller.on_new_itemID.connect(self.UpdateStats)
        self.ConstructLayout()

    def ConstructLayout(self):
        with self._layoutLock:
            self.sr.main.Flush()
            width = PANEL_WIDTH if self.IsLeftPanelExpanded() else 0
            self.leftPanel = LeftPanel(name='leftPanel', parent=self.sr.main, align=uiconst.TOLEFT, width=width, idx=0, padding=(0, 0, 10, 10))
            if self.IsLeftPanelExpanded():
                uthread.new(self.leftPanel.Load)
            width = PANEL_WIDTH if self.IsRightPanelExpanded() else 0
            self.rightPanel = StatsPanelGhost(name='rightside', parent=self.sr.main, align=uiconst.TORIGHT, width=width, idx=0, padding=(0, 0, 10, 10), controller=self.controller)
            mainCont = Container(name='mainCont', parent=self.sr.main, top=-8)
            self.overlayCont = Container(name='overlayCont', parent=mainCont)
            self.ConstructPanelExpanderBtn()
            self.ConstructInventoryIcons()
            self.ConstructPowerAndCpuLabels()
            FittingGhost(parent=mainCont, owner=self, controller=self.controller)
            self.width = self.GetWindowWidth()
            self.SetFixedWidth(self.width)
            self.UpdateStats()

    def ConstructInventoryIcons(self):
        cargoDroneCont = ContainerAutoSize(name='cargoDroneCont', parent=self.overlayCont, align=uiconst.BOTTOMLEFT, width=110, left=const.defaultPadding, top=4)
        cargoSlot = CargoCargoSlots(name='cargoSlot', parent=cargoDroneCont, align=uiconst.TOTOP, height=32, controller=self.controller)
        SetFittingTooltipInfo(cargoSlot, 'CargoHold')
        droneSlot = CargoDroneSlots(name='cargoSlot', parent=cargoDroneCont, align=uiconst.TOTOP, height=32, controller=self.controller)
        SetFittingTooltipInfo(droneSlot, 'DroneBay')

    def IsRightPanelExpanded(self):
        return settings.user.ui.Get('fittingPanelRight', 1)

    def IsLeftPanelExpanded(self):
        return settings.user.ui.Get('fittingPanelLeft2', 1)

    def ConstructPanelExpanderBtn(self):
        if self.IsLeftPanelExpanded():
            texturePath = 'res:/UI/Texture/Icons/73_16_196.png'
            tooltipName = 'CollapseSidePane'
        else:
            texturePath = 'res:/UI/Texture/Icons/73_16_195.png'
            tooltipName = 'ExpandSidePane'
        self.toggleLeftBtn = ButtonIcon(texturePath=texturePath, parent=self.overlayCont, align=uiconst.CENTERLEFT, pos=(2, 0, 16, 16), func=self.ToggleLeftPanel)
        SetFittingTooltipInfo(self.toggleLeftBtn, tooltipName=tooltipName, includeDesc=False)
        if self.IsRightPanelExpanded():
            texturePath = 'res:/UI/Texture/Icons/73_16_195.png'
            tooltipName = 'CollapseSidePane'
        else:
            texturePath = 'res:/UI/Texture/Icons/73_16_196.png'
            tooltipName = 'ExpandSidePane'
        self.toggleRightBtn = ButtonIcon(texturePath=texturePath, parent=self.overlayCont, align=uiconst.CENTERRIGHT, pos=(2, 0, 16, 16), func=self.ToggleRight)
        SetFittingTooltipInfo(self.toggleRightBtn, tooltipName=tooltipName, includeDesc=False)

    def ToggleRight(self, *args):
        isExpanded = not self.IsRightPanelExpanded()
        settings.user.ui.Set('fittingPanelRight', isExpanded)
        self._fixedWidth = self.GetWindowWidth()
        self.toggleRightBtn.state = uiconst.UI_DISABLED
        if isExpanded:
            self.toggleRightBtn.SetTexturePath('res:/UI/Texture/Icons/73_16_195.png')
            self.toggleRightBtn.tooltipPanelClassInfo.headerText = GetByLabel('Tooltips/FittingWindow/CollapseSidePane')
            uicore.animations.MorphScalar(self, 'width', self.width, self._fixedWidth, duration=ANIM_DURATION)
            uicore.animations.MorphScalar(self.rightPanel, 'width', self.rightPanel.width, PANEL_WIDTH, duration=ANIM_DURATION)
            uicore.animations.FadeTo(self.rightPanel, self.rightPanel.opacity, 1.0, duration=ANIM_DURATION, sleep=True)
        else:
            self.toggleRightBtn.SetTexturePath('res:/UI/Texture/Icons/73_16_196.png')
            self.toggleRightBtn.tooltipPanelClassInfo.headerText = GetByLabel('Tooltips/FittingWindow/ExpandSidePane')
            uicore.animations.MorphScalar(self, 'width', self.width, self._fixedWidth, duration=ANIM_DURATION)
            uicore.animations.MorphScalar(self.rightPanel, 'width', self.rightPanel.width, 0, duration=ANIM_DURATION)
            uicore.animations.FadeTo(self.rightPanel, self.rightPanel.opacity, 0.0, duration=ANIM_DURATION, sleep=True)
        self.toggleRightBtn.state = uiconst.UI_NORMAL

    def ToggleLeftPanel(self, *args):
        isExpanded = not self.IsLeftPanelExpanded()
        settings.user.ui.Set('fittingPanelLeft2', isExpanded)
        self._fixedWidth = self.GetWindowWidth()
        self.toggleLeftBtn.state = uiconst.UI_DISABLED
        if isExpanded:
            self.toggleLeftBtn.SetTexturePath('res:/UI/Texture/Icons/73_16_196.png')
            self.toggleLeftBtn.tooltipPanelClassInfo.headerText = GetByLabel('Tooltips/FittingWindow/CollapseSidePane')
            uicore.animations.MorphScalar(self, 'width', self.width, self._fixedWidth, duration=ANIM_DURATION)
            uicore.animations.MorphScalar(self, 'left', self.left, self.left - PANEL_WIDTH, duration=ANIM_DURATION)
            uicore.animations.MorphScalar(self.leftPanel, 'width', self.leftPanel.width, PANEL_WIDTH, duration=ANIM_DURATION)
            uicore.animations.FadeTo(self.leftPanel, self.leftPanel.opacity, 1.0, duration=ANIM_DURATION, sleep=True)
            uthread.new(self.leftPanel.Load)
        else:
            self.toggleLeftBtn.SetTexturePath('res:/UI/Texture/Icons/73_16_195.png')
            self.toggleLeftBtn.tooltipPanelClassInfo.headerText = GetByLabel('Tooltips/FittingWindow/ExpandSidePane')
            uicore.animations.MorphScalar(self, 'width', self.width, self._fixedWidth, duration=ANIM_DURATION)
            uicore.animations.MorphScalar(self, 'left', self.left, self.left + PANEL_WIDTH, duration=ANIM_DURATION)
            uicore.animations.MorphScalar(self.leftPanel, 'width', self.leftPanel.width, 0, duration=ANIM_DURATION)
            uicore.animations.FadeTo(self.leftPanel, self.leftPanel.opacity, 0.0, duration=ANIM_DURATION, sleep=True)
        self.toggleLeftBtn.state = uiconst.UI_NORMAL

    def GetWindowWidth(self):
        width = GetBaseShapeSize() + 16
        if self.IsLeftPanelExpanded():
            width += PANEL_WIDTH
        if self.IsRightPanelExpanded():
            width += PANEL_WIDTH
        return width

    def OnSetDevice(self):
        if self.controller and self.controller.GetItemID():
            uthread.new(self.ConstructLayout)

    def InitializeStatesAndPosition(self, *args, **kw):
        current = self.GetRegisteredPositionAndSize()
        default = self.GetDefaultSizeAndPosition()
        fixedHeight = self._fixedHeight
        fixedWidth = self.GetWindowWidth()
        Window.InitializeStatesAndPosition(self, *args, **kw)
        if fixedWidth is not None:
            self.width = fixedWidth
            self._fixedWidth = fixedWidth
        if fixedHeight is not None:
            self.height = fixedHeight
            self._fixedHeight = fixedHeight
        if list(default) == list(current)[:4]:
            settings.user.ui.Set('defaultFittingPosition', 1)
            dw = uicore.desktop.width
            dh = uicore.desktop.height
            self.left = (dw - self.width) / 2
            self.top = (dh - self.height) / 2
        self.MakeUnpinable()
        self.Unlock()
        uthread.new(uicore.registry.SetFocus, self)
        self._collapseable = 0

    def _OnClose(self, *args):
        settings.user.ui.Set('defaultFittingPosition', 0)

    def MouseDown(self, *args):
        uthread.new(uicore.registry.SetFocus, self)
        SetOrder(self, 0)

    def GhostFitItem(self, ghostItem = None):
        if not self.controller:
            return
        self.controller.SetGhostFittedItem(ghostItem)

    def OnStartMinimize_(self, *args):
        sm.ChainEvent('ProcessFittingWindowStartMinimize')

    def OnEndMinimize_(self, *args):
        sm.ChainEvent('ProcessFittingWindowEndMinimize')

    def OnUIScalingChange(self, *args):
        pass

    def UpdateStats(self):
        self.UpdateCPU()
        self.UpdatePower()
        self.UpdateCalibration()

    def ConstructPowerAndCpuLabels(self):
        powerGridAndCpuCont = LayoutGrid(parent=self.overlayCont, columns=1, state=uiconst.UI_PICKCHILDREN, align=uiconst.BOTTOMRIGHT, top=10, left=10)
        cpu_statustextHeader = EveLabelMediumBold(text=GetByLabel('UI/Fitting/FittingWindow/CPUStatusHeader'), name='cpu_statustextHeader', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        SetFittingTooltipInfo(targetObject=cpu_statustextHeader, tooltipName='CPU')
        powerGridAndCpuCont.AddCell(cpu_statustextHeader)
        self.cpu_statustext = EveLabelMedium(text='', name='cpu_statustext', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        SetFittingTooltipInfo(targetObject=self.cpu_statustext, tooltipName='CPU')
        powerGridAndCpuCont.AddCell(self.cpu_statustext)
        powerGridAndCpuCont.AddCell(cellObject=Container(name='spacer', align=uiconst.TOTOP, height=10))
        power_statustextHeader = EveLabelMediumBold(text=GetByLabel('UI/Fitting/FittingWindow/PowergridHeader'), name='power_statustextHeader', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        SetFittingTooltipInfo(targetObject=power_statustextHeader, tooltipName='PowerGrid')
        powerGridAndCpuCont.AddCell(power_statustextHeader)
        self.power_statustext = EveLabelMedium(text='', name='power_statustext', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        powerGridAndCpuCont.AddCell(self.power_statustext)
        SetFittingTooltipInfo(targetObject=self.power_statustext, tooltipName='PowerGrid')
        self.calibration_statustext = EveLabelMedium(text='', parent=self.overlayCont, name='calibrationstatustext', pos=(8, 50, 0, 0), idx=0, state=uiconst.UI_NORMAL)
        SetFittingTooltipInfo(targetObject=self.calibration_statustext, tooltipName='Calibration')

    def UpdateCPU(self):
        cpuLoadInfo = self.controller.GetCPULoad()
        cpuOutputInfo = self.controller.GetCPUOutput()
        cpuLoadText = FmtAmt(cpuOutputInfo.value - cpuLoadInfo.value)
        coloredCpuLoadText = GetColoredText(isBetter=cpuLoadInfo.isBetterThanBefore, text=cpuLoadText) + '</color>'
        cpuOutputText = FmtAmt(cpuOutputInfo.value)
        coloredCpuOutputText = GetColoredText(isBetter=cpuOutputInfo.isBetterThanBefore, text=cpuOutputText) + '</color>'
        self.cpu_statustext.text = '%s/%s' % (coloredCpuLoadText, coloredCpuOutputText)

    def UpdatePower(self):
        powerLoadInfo = self.controller.GetPowerLoad()
        powerOutputInfo = self.controller.GetPowerOutput()
        powerLoadText = FmtAmt(powerOutputInfo.value - powerLoadInfo.value)
        coloredPowerLoadText = GetColoredText(isBetter=powerLoadInfo.isBetterThanBefore, text=powerLoadText) + '</color>'
        powerOutputText = FmtAmt(powerOutputInfo.value)
        coloredPowerOutputText = GetColoredText(isBetter=powerOutputInfo.isBetterThanBefore, text=powerOutputText) + '</color>'
        self.power_statustext.text = '%s/%s' % (coloredPowerLoadText, coloredPowerOutputText)

    def UpdateCalibration(self):
        calibrationLoadInfo = self.controller.GetCalibrationLoad()
        calibrationOutputInfo = self.controller.GetCalibrationOutput()
        calibrationLoadText = FmtAmt(calibrationOutputInfo.value - calibrationLoadInfo.value)
        coloredCalibrationLoadText = GetColoredText(isBetter=calibrationLoadInfo.isBetterThanBefore, text=calibrationLoadText) + '</color>'
        calibrationOutputText = FmtAmt(calibrationOutputInfo.value)
        coloredCalibrationOutputText = GetColoredText(isBetter=calibrationOutputInfo.isBetterThanBefore, text=calibrationOutputText) + '</color>'
        self.calibration_statustext.text = '%s/%s' % (coloredCalibrationLoadText, coloredCalibrationOutputText)

    def Close(self, setClosed = False, *args, **kwds):
        Window.Close(self, setClosed, *args, **kwds)
        self.controller.Close()
