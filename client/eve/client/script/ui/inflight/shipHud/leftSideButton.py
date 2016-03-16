#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\leftSideButton.py
from carbonui import const as uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.environment.invControllers import ShipCargo
from eve.client.script.ui.inflight.radialMenuCamera import RadialMenuCamera
from eve.client.script.ui.inflight.radialMenuScanner import RadialMenuScanner
import evecamera
import uthread
from eve.client.script.ui.shared.inventory.invWindow import Inventory
from eve.common.script.sys.eveCfg import GetActiveShip
import localization
import trinity
import uicontrols
import uiprimitives
BTN_SIZE = 36

class LeftSideButton(uiprimitives.Container):
    default_texturePath = None
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_width = BTN_SIZE
    default_height = BTN_SIZE
    cmdName = None

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        texturePath = attributes.get('texturePath', self.default_texturePath)
        self.orgTop = None
        self.pickRadius = self.width / 2
        self.icon = uicontrols.Icon(parent=self, name='icon', pos=(0, 0, 32, 32), align=uiconst.CENTER, state=uiconst.UI_DISABLED, icon=texturePath)
        self.transform = uiprimitives.Transform(parent=self, name='icon', pos=(0, 0, 32, 32), align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.hilite = uiprimitives.Sprite(parent=self, name='hilite', align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnBaseAndShadow.png', color=(0.63, 0.63, 0.63, 1.0), blendMode=trinity.TR2_SBM_ADD)
        slot = uiprimitives.Sprite(parent=self, name='slot', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnBaseAndShadow.png')
        self.busy = uiprimitives.Sprite(parent=self, name='busy', align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnGlow.png', color=(0.27, 0.72, 1.0, 0.53))
        self.blinkBG = uiprimitives.Sprite(parent=self, name='blinkBG', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnGlow.png', opacity=0.0, blendMode=trinity.TR2_SBM_ADD)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.cmdName:
            tooltipPanel.LoadGeneric2ColumnTemplate()
            cmd = uicore.cmd.commandMap.GetCommandByName(self.cmdName)
            tooltipPanel.AddCommandTooltip(cmd)

    def LoadIcon(self, iconPath):
        self.icon.LoadIcon(iconPath)

    def OnClick(self, *args):
        sm.GetService('ui').StopBlink(self.icon)

    def OnMouseDown(self, btn, *args):
        if getattr(self, 'orgTop', None) is None:
            self.orgTop = self.top
        self.top = self.orgTop + 2

    def OnMouseUp(self, *args):
        if getattr(self, 'orgTop', None) is not None:
            self.top = self.orgTop

    def OnMouseEnter(self, *args):
        self.hilite.state = uiconst.UI_DISABLED

    def OnMouseExit(self, *args):
        self.hilite.state = uiconst.UI_HIDDEN
        if getattr(self, 'orgTop', None) is not None:
            self.top = self.orgTop

    def Blink(self, loops = 3):
        uicore.animations.FadeTo(self.blinkBG, 0.0, 0.9, duration=0.15, loops=loops, callback=self._BlinkFadeOut)

    def _BlinkFadeOut(self):
        uicore.animations.FadeOut(self.blinkBG, duration=0.6)


def ExpandRadialMenu(button, radialClass):
    if button.destroyed:
        return
    uicore.layer.menu.Flush()
    if not uicore.uilib.leftbtn:
        return
    radialMenu = radialClass(name='radialMenu', parent=uicore.layer.menu, state=uiconst.UI_HIDDEN, align=uiconst.TOPLEFT, anchorObject=button)
    uicore.layer.menu.radialMenu = radialMenu
    uicore.uilib.SetMouseCapture(radialMenu)
    radialMenu.state = uiconst.UI_NORMAL


class LeftSideButtonCargo(LeftSideButton):
    default_name = 'inFlightCargoBtn'
    default_texturePath = 'res:/UI/Texture/icons/44_32_10.png'
    label = 'UI/Generic/Cargo'
    cmdName = 'OpenCargoHoldOfActiveShip'

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        shipID = GetActiveShip()
        if shipID is None:
            return
        Inventory.OpenOrShow(('ShipCargo', shipID), usePrimary=False, toggle=True)

    def OnDropData(self, dragObj, nodes):
        ShipCargo().OnDropData(nodes)


class LeftSideButtonCamera(LeftSideButton):
    default_name = 'inFlightCameraControlsBtn'
    default_texturePath = 'res:/UI/Texture/Icons/44_32_46.png'
    label = 'UI/Inflight/Camera/CameraControls'
    __notifyevents__ = ['OnActiveTrackingChange']

    def ApplyAttributes(self, attributes):
        LeftSideButton.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        isActivelyTracking = sm.GetService('targetTrackingService').GetActiveTrackingState()
        self.OnActiveTrackingChange(isActivelyTracking)

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        sm.GetService('sceneManager').GetActiveCamera().ResetCamera()

    def OnMouseDown(self, *args):
        uthread.new(ExpandRadialMenu, self, RadialMenuCamera)

    def OnActiveTrackingChange(self, isActivelyTracking):
        if isActivelyTracking is True or isActivelyTracking is None:
            self.busy.state = uiconst.UI_DISABLED
        else:
            self.busy.state = uiconst.UI_HIDDEN
        if isActivelyTracking is not False:
            if sm.GetService('targetTrackingService').GetCenteredState():
                self.LoadIcon('res:/UI/Texture/classes/CameraRadialMenu/centerTrackingActive.png')
            else:
                self.LoadIcon('res:/UI/Texture/classes/CameraRadialMenu/customTrackingActive.png')
        else:
            self.LoadIcon('res:/UI/Texture/classes/CameraRadialMenu/noTracking_ButtonIcon.png')

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=localization.GetByLabel('Tooltips/Hud/CameraControls'), colSpan=tooltipPanel.columns)
        tooltipPanel.AddLabelMedium(text=localization.GetByLabel('Tooltips/Hud/CameraControls_description'), wrapWidth=200, colSpan=tooltipPanel.columns, color=(0.6, 0.6, 0.6, 1))


class LeftSideButtonScanner(LeftSideButton):
    default_name = 'inFlightScannerBtn'
    default_texturePath = 'res:/UI/Texture/classes/SensorSuite/radar.png'
    label = 'UI/Generic/Scanner'
    cmdName = 'OpenScanner'

    def ApplyAttributes(self, attributes):
        LeftSideButton.ApplyAttributes(self, attributes)
        self.sweep = Sprite(parent=self.transform, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/SensorSuite/radar_sweep.png')

    def OnMouseDown(self, *args):
        uthread.new(ExpandRadialMenu, self, RadialMenuScanner)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelShortcut(localization.GetByLabel('Tooltips/Hud/Scanners'), '')
        tooltipPanel.AddLabelMedium(text=localization.GetByLabel('Tooltips/Hud/Scanners_description'), wrapWidth=200, colSpan=tooltipPanel.columns, color=(0.6, 0.6, 0.6, 1))


class LeftSideButtonTactical(LeftSideButton):
    default_name = 'inFlightTacticalBtn'
    default_texturePath = 'res:/UI/Texture/Icons/44_32_42.png'
    label = 'UI/Generic/Tactical'
    cmdName = 'CmdToggleTacticalOverlay'
    __notifyevents__ = ['OnTacticalOverlayChange']

    def ApplyAttributes(self, attributes):
        LeftSideButton.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.UpdateButtonState()

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        sm.GetService('tactical').ToggleOnOff()

    def OnTacticalOverlayChange(self):
        self.UpdateButtonState()

    def UpdateButtonState(self):
        isActive = sm.GetService('tactical').IsTacticalOverlayActive()
        if isActive:
            self.busy.state = uiconst.UI_DISABLED
            self.hint = localization.GetByLabel('UI/Inflight/HideTacticalOverview')
        else:
            self.busy.state = uiconst.UI_HIDDEN
            self.hint = localization.GetByLabel('UI/Inflight/ShowTacticalOverlay')


class LeftSideButtonAutopilot(LeftSideButton):
    default_name = 'inFlightAutopilotBtn'
    default_texturePath = 'res:/UI/Texture/Icons/44_32_12.png'
    label = 'UI/Generic/Autopilot'
    cmdName = 'CmdToggleAutopilot'
    __notifyevents__ = ['OnAutoPilotOn', 'OnAutoPilotOff']

    def ApplyAttributes(self, attributes):
        LeftSideButton.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        apActive = sm.GetService('autoPilot').GetState()
        if apActive:
            self.OnAutoPilotOn()
        else:
            self.OnAutoPilotOff()

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        self.AutoPilotOnOff(not sm.GetService('autoPilot').GetState())

    def AutoPilotOnOff(self, onoff, *args):
        if onoff:
            sm.GetService('autoPilot').SetOn()
        else:
            sm.GetService('autoPilot').SetOff('toggled by shipUI')

    def OnAutoPilotOn(self):
        self.busy.state = uiconst.UI_DISABLED
        self.hint = localization.GetByLabel('UI/Inflight/DeactivateAutopilot')
        self.hint += self._GetShortcutForCommand(self.cmdName)

    def OnAutoPilotOff(self):
        self.busy.state = uiconst.UI_HIDDEN
        self.hint = localization.GetByLabel('UI/Inflight/ActivateAutopilot')
        self.hint += self._GetShortcutForCommand(self.cmdName)

    def _GetShortcutForCommand(self, cmdName):
        if cmdName:
            shortcut = uicore.cmd.GetShortcutStringByFuncName(cmdName)
            if shortcut:
                return localization.GetByLabel('UI/Inflight/ShortcutFormatter', shortcut=shortcut)
        return ''


class LeftSideButtonZoomIn(LeftSideButton):
    default_name = 'inFlightZoomInBtn'
    default_texturePath = 'res:/UI/Texture/Icons/44_32_43.png'
    label = 'UI/Inflight/ZoomIn'
    cmdName = 'CmdZoomIn'

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        uicore.cmd.CmdZoomIn()


class LeftSideButtonZoomOut(LeftSideButton):
    default_name = 'inFlightZoomOutBtn'
    default_texturePath = 'res:/UI/Texture/Icons/44_32_44.png'
    label = 'UI/Inflight/ZoomOut'
    cmdName = 'CmdZoomOut'

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        uicore.cmd.CmdZoomOut()


class LeftSideButtonCameraBase(LeftSideButton):
    __notifyevents__ = ['OnActiveCameraChanged']

    def ApplyAttributes(self, attributes):
        LeftSideButton.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.UpdateButtonState()

    def OnActiveCameraChanged(self, cameraID):
        self.UpdateButtonState()

    def UpdateButtonState(self):
        if self.IsActive():
            self.busy.state = uiconst.UI_DISABLED
        else:
            self.busy.state = uiconst.UI_HIDDEN

    def IsActive(self):
        cameraID = sm.GetService('sceneManager').GetActiveCameraMode()
        return cameraID == self.cameraID


class LeftSideButtonCameraPOV(LeftSideButtonCameraBase):
    default_name = 'cameraButtonPOV'
    default_texturePath = 'res:/UI/Texture/classes/ShipUI/iconCameraFirstPerson.png'
    cmdName = 'CmdSetCameraPOV'
    cameraID = evecamera.CAM_SHIPPOV

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        uicore.cmd.CmdSetCameraPOV()


class LeftSideButtonCameraOrbit(LeftSideButtonCameraBase):
    default_name = 'cameraButtonOrbit'
    default_texturePath = 'res:/UI/Texture/classes/ShipUI/iconCameraOrbit.png'
    cmdName = 'CmdSetCameraOrbit'
    cameraID = evecamera.CAM_SHIPORBIT

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        uicore.cmd.CmdSetCameraOrbit()


class LeftSideButtonCameraTactical(LeftSideButtonCameraBase):
    default_name = 'cameraButtonTactical'
    default_texturePath = 'res:/UI/Texture/classes/ShipUI/iconCameraGrid.png'
    cmdName = 'CmdSetCameraTactical'
    cameraID = evecamera.CAM_TACTICAL

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        uicore.cmd.CmdSetCameraTactical()
