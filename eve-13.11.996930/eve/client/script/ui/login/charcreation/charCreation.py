#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\login\charcreation\charCreation.py
import uicontrols
import carbonui.const as uiconst
import uicls
import uiprimitives
import uthread
import uiutil
import log
import localization
import charactercreator.const as ccConst
import blue
import base
import eve.common.lib.appConst as const
FILL_SELECTION = 0.2
TEXT_NORMAL = 0.8
MINSIDESIZE = 280
MAXMENUSIZE = 380
LEFTSIZE = 200
ZONEMAP = {-1: uiconst.UICURSOR_DEFAULT,
 0: uiconst.UICURSOR_CCALLDIRECTIONS,
 1: uiconst.UICURSOR_CCALLDIRECTIONS,
 2: uiconst.UICURSOR_CCALLDIRECTIONS,
 3: uiconst.UICURSOR_CCALLDIRECTIONS,
 4: uiconst.UICURSOR_CCALLDIRECTIONS,
 5: uiconst.UICURSOR_CCALLDIRECTIONS,
 6: uiconst.UICURSOR_CCALLDIRECTIONS,
 7: uiconst.UICURSOR_CCALLDIRECTIONS,
 8: uiconst.UICURSOR_CCALLDIRECTIONS,
 9: uiconst.UICURSOR_CCALLDIRECTIONS,
 10: uiconst.UICURSOR_CCALLDIRECTIONS,
 11: uiconst.UICURSOR_CCALLDIRECTIONS,
 12: uiconst.UICURSOR_CCALLDIRECTIONS,
 13: uiconst.UICURSOR_CCALLDIRECTIONS,
 14: uiconst.UICURSOR_CCUPDOWN,
 15: uiconst.UICURSOR_CCALLDIRECTIONS,
 16: uiconst.UICURSOR_CCALLDIRECTIONS,
 17: uiconst.UICURSOR_CCLEFTRIGHT}
ZONEMAP_SIDE = {-1: uiconst.UICURSOR_DEFAULT,
 0: uiconst.UICURSOR_CCALLDIRECTIONS,
 1: uiconst.UICURSOR_CCALLDIRECTIONS,
 2: uiconst.UICURSOR_CCALLDIRECTIONS,
 3: uiconst.UICURSOR_CCALLDIRECTIONS,
 4: uiconst.UICURSOR_CCALLDIRECTIONS,
 5: uiconst.UICURSOR_CCALLDIRECTIONS,
 6: uiconst.UICURSOR_CCALLDIRECTIONS,
 7: uiconst.UICURSOR_CCALLDIRECTIONS,
 8: uiconst.UICURSOR_CCALLDIRECTIONS,
 9: uiconst.UICURSOR_CCALLDIRECTIONS,
 10: uiconst.UICURSOR_CCALLDIRECTIONS,
 11: uiconst.UICURSOR_CCALLDIRECTIONS,
 12: uiconst.UICURSOR_CCALLDIRECTIONS,
 13: uiconst.UICURSOR_CCALLDIRECTIONS,
 14: uiconst.UICURSOR_CCUPDOWN,
 15: uiconst.UICURSOR_CCALLDIRECTIONS,
 16: uiconst.UICURSOR_CCALLDIRECTIONS,
 17: uiconst.UICURSOR_DEFAULT}
ZONEMAP_ANIM = {-1: uiconst.UICURSOR_DEFAULT,
 0: uiconst.UICURSOR_CCHEADALL,
 1: uiconst.UICURSOR_CCHEADALL,
 2: uiconst.UICURSOR_CCHEADALL,
 3: uiconst.UICURSOR_CCALLDIRECTIONS,
 4: uiconst.UICURSOR_CCHEADTILT,
 5: uiconst.UICURSOR_CCALLDIRECTIONS,
 6: uiconst.UICURSOR_CCALLDIRECTIONS,
 7: uiconst.UICURSOR_CCHEADALL,
 8: uiconst.UICURSOR_CCHEADALL,
 9: uiconst.UICURSOR_CCALLDIRECTIONS,
 10: uiconst.UICURSOR_CCALLDIRECTIONS,
 11: uiconst.UICURSOR_CCHEADTILT,
 12: uiconst.UICURSOR_CCHEADALL,
 13: uiconst.UICURSOR_CCHEADALL,
 14: uiconst.UICURSOR_CCHEADALL,
 15: uiconst.UICURSOR_CCALLDIRECTIONS,
 16: uiconst.UICURSOR_CCALLDIRECTIONS,
 17: uiconst.UICURSOR_CCALLDIRECTIONS}
ZONEMAP_ANIMBODY = {-1: uiconst.UICURSOR_DEFAULT,
 3: uiconst.UICURSOR_CCSHOULDERTWIST,
 4: uiconst.UICURSOR_CCSHOULDERTWIST,
 5: uiconst.UICURSOR_CCSHOULDERTWIST,
 6: uiconst.UICURSOR_CCSHOULDERTWIST}

class BaseCharacterCreationStep(uiprimitives.Container):
    __guid__ = 'uicls.BaseCharacterCreationStep'
    __notifyevents__ = ['OnHideUI', 'OnShowUI', 'OnUIScalingChange']
    default_align = uiconst.TOALL
    default_state = uiconst.UI_NORMAL
    racialHeader = {const.raceCaldari: 384,
     const.raceMinmatar: 128,
     const.raceAmarr: 256,
     const.raceGallente: 0}
    raceHeaderPath = 'res:/UI/Texture/CharacterCreation/RACE_Titletext.dds'
    raceFontColor = {const.raceCaldari: (0.93, 0.94, 0.99, 1.0),
     const.raceMinmatar: (0.99, 0.95, 0.95, 1.0),
     const.raceAmarr: (0.99, 0.95, 0.92, 1.0),
     const.raceGallente: (0.99, 0.99, 0.92, 1.0)}

    def UpdateLayout(self):
        self.UpdateSideContainerWidth()

    def ApplyAttributes(self, attributes):
        sm.RegisterNotify(self)
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.charSvc = sm.GetService('character')
        self._cameraActive = False
        self._activeSculptZone = None
        self._didSculptMotion = False
        self._latestPickTime = None
        self.sr.uiContainer = uiprimitives.Container(name='uiContainer', parent=self, align=uiconst.TOALL)
        self.sr.leftSide = uiprimitives.Container(name='leftSide', parent=self.sr.uiContainer, align=uiconst.TOLEFT, pos=(0, 0, 0, 0))
        self.sr.rightSide = uiprimitives.Container(name='rightSide', parent=self.sr.uiContainer, align=uiconst.TORIGHT, pos=(0, 0, 0, 0))
        self.UpdateSideContainerWidth()
        settings.user.ui.Get('assetMenuState', {ccConst.BODYGROUP: True})

    def UpdateSideContainerWidth(self):
        mainCenterSize = min(uicore.desktop.width, uicore.desktop.height)
        sideSize = max(MINSIDESIZE, (uicore.desktop.width - mainCenterSize) / 2)
        self.sr.leftSide.width = LEFTSIZE
        self.sr.rightSide.width = sideSize

    def GetInfo(self):
        return uicore.layer.charactercreation.GetInfo()

    def ValidateStepComplete(self):
        return True

    def GetPickInfo(self, pos):
        layer = uicore.layer.charactercreation
        layer.StartEditMode(mode='makeup', skipPickSceneReset=True, useThread=0)
        pickedMakeup = layer.PassMouseEventToSculpt('LeftDown', *pos)
        layer.StartEditMode(mode='hair', skipPickSceneReset=True, useThread=0)
        pickedHair = layer.PassMouseEventToSculpt('LeftDown', *pos)
        layer.StartEditMode(mode='bodyselect', skipPickSceneReset=True, useThread=0)
        pickedBody = layer.PassMouseEventToSculpt('LeftDown', *pos)
        layer.StartEditMode(mode='sculpt', skipPickSceneReset=True, useThread=0)
        pickedSculpt = layer.PassMouseEventToSculpt('LeftDown', *pos)
        reset = layer.PassMouseEventToSculpt('LeftUp', *pos)
        return (pickedMakeup,
         pickedHair,
         pickedBody,
         pickedSculpt)

    def OnDblClick(self, *args):
        if self.stepID == ccConst.BLOODLINESTEP:
            pos = (uicore.uilib.x, uicore.uilib.y)
            layer = uicore.layer.charactercreation
            if getattr(layer, 'bloodlineSelector', None) is not None:
                picked = layer.PickObject(pos)
                bloodlineID, genderID = uicore.layer.charactercreation.bloodlineSelector.GetBloodlineAndGender(picked)
                if bloodlineID is not None:
                    if genderID is not None:
                        layer.Approve()

    def OnMouseDown(self, btn, *args):
        if self.stepID not in (ccConst.CUSTOMIZATIONSTEP,
         ccConst.PORTRAITSTEP,
         ccConst.RACESTEP,
         ccConst.BLOODLINESTEP):
            return
        self.storedMousePos = None
        pos = (int(uicore.uilib.x * uicore.desktop.dpiScaling), int(uicore.uilib.y * uicore.desktop.dpiScaling))
        layer = uicore.layer.charactercreation
        if btn == uiconst.MOUSELEFT and self.stepID == ccConst.BLOODLINESTEP:
            if getattr(layer, 'bloodlineSelector', None) is not None:
                picked = layer.PickObject(pos)
                bloodlineID, genderID = uicore.layer.charactercreation.bloodlineSelector.GetBloodlineAndGender(picked)
                if bloodlineID is not None:
                    uthread.new(layer.SelectBloodline, bloodlineID)
                if genderID is not None:
                    uthread.new(layer.SelectGender, genderID)
            return
        if btn == uiconst.MOUSERIGHT and self.stepID not in (ccConst.RACESTEP, ccConst.BLOODLINESTEP):
            self._cameraActive = True
            self._activeSculptZone = None
        elif btn == uiconst.MOUSELEFT and not self._cameraActive and self.charSvc.IsSculptingReady():
            self._didSculptMotion = False
            self._latestPickTime = blue.os.GetWallclockTime()
            if self.CanSculpt():
                layer.StartEditMode(mode='sculpt', callback=self.ChangeSculptingCursor)
                pickedSculpt = layer.PassMouseEventToSculpt('LeftDown', *pos)
                if pickedSculpt >= 0:
                    uicore.layer.charactercreation.TryFreezeAnimation()
                    self.storedMousePos = (uicore.uilib.x, uicore.uilib.y)
                    self.cursor = uiconst.UICURSOR_NONE
                    self._cameraActive = False
                    self._activeSculptZone = pickedSculpt
                else:
                    self._cameraActive = True
                    self._activeSculptZone = None
            elif self.stepID == ccConst.PORTRAITSTEP:
                info = self.GetInfo()
                self.charSvc.StartPosing(info.charID, callback=self.ChangeSculptingCursor)
                pickedSculpt = layer.PassMouseEventToSculpt('LeftDown', *pos)
                if pickedSculpt >= 0:
                    self._cameraActive = False
                    self._activeSculptZone = pickedSculpt
                else:
                    self._cameraActive = True
                    self._activeSculptZone = None
            else:
                self._cameraActive = True
                self._activeSculptZone = None
        elif btn == uiconst.MOUSELEFT and self.stepID == ccConst.CUSTOMIZATIONSTEP and not layer.CanChangeBaseAppearance():
            self._cameraActive = True
        else:
            return
        uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
        uicore.uilib.SetCapture(self)

    def OnMouseUp(self, btn, *args):
        if self.stepID not in (ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP):
            return
        uicore.layer.charactercreation.UnfreezeAnimationIfNeeded()
        if getattr(self, 'storedMousePos', None) is not None:
            uicore.uilib.SetCursorPos(*self.storedMousePos)
            self.storedMousePos = None
        if btn == uiconst.MOUSELEFT:
            uicore.layer.charactercreation.PassMouseEventToSculpt('LeftUp', uicore.uilib.x, uicore.uilib.y)
            if self.CanSculpt():
                if self._activeSculptZone is not None and self._didSculptMotion:
                    uicore.layer.charactercreation.TryStoreDna(False, 'Sculpting', sculpting=True)
                    charID = uicore.layer.charactercreation.GetInfo().charID
                    sm.ScatterEvent('OnDollUpdated', charID, False, 'sculpting')
                    self.charSvc.UpdateTattoos(charID)
                elif self._latestPickTime:
                    if blue.os.TimeDiffInMs(self._latestPickTime, blue.os.GetWallclockTime()) < 250.0:
                        pickedMakeup, pickedHair, pickedBody, pickedSculpt = self.GetPickInfo((uicore.uilib.x, uicore.uilib.y))
                        log.LogInfo('Pickinfo: makeup, hair, bodyselect, sculpt = ', pickedMakeup, pickedHair, pickedBody, pickedSculpt)
                        for each in (('hair', pickedHair),
                         ('makeup', pickedMakeup),
                         ('clothes', pickedBody),
                         ('sculpt', pickedSculpt)):
                            if each in ccConst.PICKMAPPING:
                                pickedModifier = ccConst.PICKMAPPING[each]
                                self.ExpandMenuByModifier(pickedModifier)
                                break

            self._activeSculptZone = None
        if not uicore.uilib.rightbtn and not uicore.uilib.leftbtn:
            uicore.layer.charactercreation.PassMouseEventToSculpt('Motion', uicore.uilib.x, uicore.uilib.y)
            self._cameraActive = False
            self._activeSculptZone = None
            self.cursor = uiconst.UICURSOR_DEFAULT
            uicore.uilib.UnclipCursor()
            if uicore.uilib.GetCapture() is self:
                uicore.uilib.ReleaseCapture()

    def OnMouseMove(self, *args):
        if self.stepID not in (ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP):
            return
        pos = (int(uicore.uilib.x * uicore.desktop.dpiScaling), int(uicore.uilib.y * uicore.desktop.dpiScaling))
        if self._cameraActive:
            if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
                modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
                uicore.layer.charactercreation.camera.Dolly(modifier * uicore.uilib.dy)
            if uicore.uilib.leftbtn:
                uicore.layer.charactercreation.camera.AdjustYaw(uicore.uilib.dx)
                if not uicore.uilib.rightbtn:
                    uicore.layer.charactercreation.camera.AdjustPitch(uicore.uilib.dy)
            elif uicore.uilib.rightbtn:
                uicore.layer.charactercreation.camera.Pan(uicore.uilib.dx, uicore.uilib.dy)
        else:
            if self._activeSculptZone is not None and self.stepID == ccConst.CUSTOMIZATIONSTEP:
                uicore.layer.charactercreation.CheckDnaLog('OnMouseMove')
                self._didSculptMotion = True
            uicore.layer.charactercreation.PassMouseEventToSculpt('Motion', *pos)

    def OnMouseWheel(self, *args):
        if not uicore.layer.charactercreation.camera:
            return
        modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
        uicore.layer.charactercreation.camera.Dolly(modifier * -uicore.uilib.dz)

    def ChangeSculptingCursor(self, zone, isFront, isHead):
        if self.destroyed:
            return
        if self.stepID == ccConst.CUSTOMIZATIONSTEP:
            if isFront:
                cursor = ZONEMAP.get(zone, uiconst.UICURSOR_DEFAULT)
            else:
                cursor = ZONEMAP_SIDE.get(zone, uiconst.UICURSOR_DEFAULT)
            self.cursor = cursor
        elif self.stepID == ccConst.PORTRAITSTEP:
            if isHead:
                cursor = ZONEMAP_ANIM.get(zone, uiconst.UICURSOR_DEFAULT)
            else:
                cursor = ZONEMAP_ANIMBODY.get(zone, uiconst.UICURSOR_DEFAULT)
            self.cursor = cursor
        lastZone = getattr(self, '_lastZone', None)
        if lastZone != zone:
            sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_sculpting_mouse_over_loop_play'))
            self._lastZone = zone
            if self._lastZone == -1:
                sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_sculpting_mouse_over_loop_stop'))

    def ExpandMenuByModifier(self, modifier):
        if not self.sr.assetMenu:
            return
        lastParentGroup = None
        allMenus = [ each for each in self.sr.assetMenu.sr.mainCont.children if isinstance(each, uicls.CharCreationAssetPicker) ]
        for menu in allMenus:
            if not menu.isSubmenu:
                lastParentGroup = menu
            if getattr(menu, 'modifier', None) == modifier:
                if lastParentGroup and not lastParentGroup.IsExpanded():
                    uthread.new(lastParentGroup.Expand)
                uthread.new(menu.Expand)

    def OnHideUI(self, *args):
        self.sr.uiContainer.state = uiconst.UI_HIDDEN

    def OnShowUI(self, *args):
        self.sr.uiContainer.state = uiconst.UI_PICKCHILDREN

    def CanSculpt(self, *args):
        return self.stepID == ccConst.CUSTOMIZATIONSTEP and uicore.layer.charactercreation.CanChangeBaseAppearance() and getattr(self, 'menuMode', None) != getattr(self, 'TATTOOMENU', None)

    def IsDollReady(self, *args):
        if uicore.layer.charactercreation.doll is None:
            return False
        return not uicore.layer.charactercreation.doll.busyUpdating

    def OnUIScalingChange(self, *args):
        self.UpdateLayout()


class CharCreationButton(uicontrols.ButtonCore):
    __guid__ = 'uicls.CharCreationButton'
    default_align = uiconst.TOPLEFT

    def Prepare_(self):
        self.sr.label = uicontrols.Label(parent=self, state=uiconst.UI_DISABLED, align=uiconst.CENTER, bold=1, uppercase=0, idx=0, fontsize=self.default_fontsize, color=ccConst.COLOR + (TEXT_NORMAL,), letterspace=1)
        self.sr.hilite = uicontrols.Frame(parent=self, name='hilite', state=uiconst.UI_HIDDEN, color=ccConst.COLOR + (0.2,), frameConst=ccConst.FILL_BEVEL)
        self.sr.hilite.padLeft = self.sr.hilite.padTop = self.sr.hilite.padRight = self.sr.hilite.padBottom = 3
        fill = uiprimitives.Fill(parent=self, name='fill', state=uiconst.UI_DISABLED, color=(0.35, 0.35, 0.35, 0.3), padding=(2, 2, 2, 2))
        self.sr.activeframe = uiprimitives.Fill(parent=self, name='activeframe', state=uiconst.UI_HIDDEN, color=ccConst.COLOR + (FILL_SELECTION,), padding=(2, 2, 2, 2))
        hiliteFrame = uicontrols.Frame(name='hiliteFrame', parent=self, frameConst=('ui_105_32_10', 8, -2), color=(1.0, 1.0, 1.0, 0.4))
        shadow = uicontrols.Frame(name='shadow', parent=self, frameConst=ccConst.FRAME_SOFTSHADE)
        shadow.padding = (-9, -6, -9, -11)

    def Update_Size_(self):
        uicontrols.ButtonCore.Update_Size_(self)
        self.height = 25

    def OnSetFocus(self, *args):
        uicontrols.ButtonCore.OnSetFocus(self, *args)
        self.sr.label.SetAlpha(1.0)

    def OnKillFocus(self, *args):
        uicontrols.ButtonCore.OnKillFocus(self, *args)
        self.sr.label.SetAlpha(TEXT_NORMAL)

    def OnMouseEnter(self, *args):
        uicontrols.ButtonCore.OnMouseEnter(self, *args)
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_over_play'))

    def OnMouseExit(self, *args):
        uicontrols.ButtonCore.OnMouseExit(self, *args)
        if self.sr and self.sr.activeframe:
            self.sr.activeframe.display = False

    def OnMouseDown(self, *args):
        uicontrols.ButtonCore.OnMouseDown(self, *args)
        if self.sr and self.sr.activeframe:
            self.sr.activeframe.display = True

    def OnClick(self, *blah):
        if not self or self.destroyed:
            return
        if not self.func:
            return
        if type(self.args) == tuple:
            self.func(*self.args)
        else:
            self.func(self.args or self)
        if self.sr and self.sr.activeframe:
            self.sr.activeframe.display = False
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_down_play'))


class CCLabel(uicontrols.Label):
    __guid__ = 'uicls.CCLabel'
    default_bold = 1
    default_color = ccConst.COLOR
    default_letterspace = 1
    default_state = uiconst.UI_DISABLED


class CCHeadBodyPicker(uiprimitives.Container):
    __guid__ = 'uicls.CCHeadBodyPicker'

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.headCallback = attributes.headCallback
        self.bodyCallback = attributes.bodyCallback
        self.Setup()

    def Setup(self, *args):
        self.width = 130
        self.height = 130
        self.SetOpacity(0.0)
        hex = uicls.CCHexButtonHead(name='headHex', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, pos=(0, 0, 64, 64), pickRadius=21, info=None, id=0, hexName=localization.GetByLabel('UI/CharacterCreation/ZoomIn'), func=self.HeadClicked, iconNum=0, showIcon=False)
        self.sr.headSolid = hex.selection
        hex.selection.state = uiconst.UI_DISABLED
        self.sr.headFrame = hex.frame
        self.sr.headHex = hex
        hex = uicls.CCHexButtonBody(name='bodyHex', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, pos=(0, 16, 128, 128), pickRadius=42, info=None, id=0, hexName=localization.GetByLabel('UI/CharacterCreation/ZoomOut'), func=self.BodyClicked, iconNum=0, showIcon=False)
        self.sr.bodySolid = hex.selection
        hex.selection.state = uiconst.UI_DISABLED
        self.sr.bodyFrame = hex.frame
        self.sr.bodyHex = hex
        texturePath = 'res:/UI/Texture/CharacterCreation/silhuette_ghost.dds'
        sprite = uiprimitives.Sprite(name='ghost', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, pos=(0, 7, 128, 128), idx=0, texturePath=texturePath)
        sprite.rectLeft, sprite.rectTop, sprite.rectWidth, sprite.rectHeight = (0, 0, 0, 0)
        self.sr.updateTimer = base.AutoTimer(33, self.UpdatePosition)
        uthread.new(uicore.effect.CombineEffects, self, opacity=1.0, time=250.0)

    def UpdatePosition(self, *args):
        if self.destroyed:
            return
        camera = getattr(uicore.layer.charactercreation, 'camera', None)
        if camera is not None:
            portion = camera.GetPortionFromDistance()
            self.sr.headSolid.SetOpacity(max(0.2, 1.0 - portion))
            self.sr.bodySolid.SetOpacity(max(0.2, portion))
            for hex in (self.sr.headHex, self.sr.bodyHex):
                if hex.selection.opacity >= 0.5 and len(self.children) and hex == self.children[-1]:
                    toSwap = self.children[-2]
                    self.children.remove(toSwap)
                    self.children.append(toSwap)
                    break

    def MouseOverPart(self, frameName, *args):
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_over_play'))
        frame = self.sr.get(frameName, None)
        if frame:
            frame.state = uiconst.UI_DISABLED

    def MouseExitPart(self, frameName, *args):
        frame = self.sr.get(frameName, None)
        if frame:
            frame.state = uiconst.UI_HIDDEN

    def HeadClicked(self, *args):
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_down_play'))
        self.sr.headFrame.state = uiconst.UI_HIDDEN
        self.sr.bodyFrame.state = uiconst.UI_HIDDEN
        if self.headCallback:
            self.headCallback()

    def BodyClicked(self, *args):
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_down_play'))
        self.sr.headFrame.state = uiconst.UI_HIDDEN
        self.sr.bodyFrame.state = uiconst.UI_HIDDEN
        if self.bodyCallback:
            self.bodyCallback()


class BitSlider(uiprimitives.Container):
    __guid__ = 'uicls.BitSlider'
    default_name = 'BitSlider'
    default_align = uiconst.RELATIVE
    default_bitWidth = 3
    default_bitHeight = 8
    default_bitGap = 1
    default_state = uiconst.UI_NORMAL
    default_left = 0
    default_top = 0
    default_width = 128
    default_height = 12
    cursor = uiconst.UICURSOR_SELECT

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.onSetValueCallback = None
        targetWidth = attributes.get('sliderWidth', 100)
        bitGap = attributes.get('bitGap', self.default_bitGap)
        bitAmount = attributes.bitAmount
        self.bitHeight = attributes.bitHeight or self.default_bitHeight
        self.height = self.bitHeight + 4
        if bitAmount:
            self.bitWidth = int(targetWidth / float(bitAmount))
        else:
            self.bitWidth = attributes.bitWidth or self.default_bitWidth
        self._value = 0.0
        self.bitParent = uiprimitives.Container(parent=self, pos=(0,
         0,
         targetWidth,
         self.height), align=uiconst.TOPLEFT)
        self.sr.handle = uiprimitives.Container(parent=self.bitParent, align=uiconst.RELATIVE, state=uiconst.UI_DISABLED, pos=(0,
         0,
         3,
         self.height), bgColor=ccConst.COLOR + (1.0,))
        i = 0
        while True:
            if bitAmount is None and i >= 3 and i * (self.bitWidth + bitGap) + self.bitWidth > targetWidth:
                break
            bit = uiprimitives.Container(parent=self.bitParent, pos=(i * (self.bitWidth + bitGap),
             2,
             self.bitWidth,
             self.bitHeight), align=uiconst.RELATIVE, state=uiconst.UI_DISABLED, bgColor=ccConst.COLOR + (1.0,))
            bit.isBit = True
            i += 1
            if bitAmount is not None and i == bitAmount:
                break

        self._numBits = i
        if targetWidth != bit.left + bit.width:
            diff = targetWidth - (bit.left + bit.width)
            bit.width += diff
        self.bitParent.width = targetWidth
        if attributes.setvalue is not None:
            self.SetValue(attributes.setvalue)
        self.onSetValueCallback = attributes.OnSetValue

    def OnMouseDown(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return
        self.sr.softSlideTimer = None
        self.sr.slideTimer = base.AutoTimer(33, self.UpdateSliderPortion)

    def OnMouseEnter(self, *args):
        self.sr.softSlideTimer = base.AutoTimer(33, self.UpdateSoftSliderPortion)

    def OnMouseExit(self, *args):
        pass

    def OnMouseWheel(self, *args):
        if uicore.uilib.dz > 0:
            self.SetValue(self.GetValue() + 1.0 / self._numBits)
        else:
            self.SetValue(self.GetValue() - 1.0 / self._numBits)

    def UpdateSoftSliderPortion(self, *args):
        if uicore.uilib.mouseOver is self or uiutil.IsUnder(uicore.uilib.mouseOver, self):
            l, t, w, h = self.bitParent.GetAbsolute()
            portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
            self.ShowSoftLit(portion)
        else:
            self.sr.softSlideTimer = None
            self.ShowSoftLit(0.0)

    def UpdateSliderPortion(self, *args):
        l, t, w, h = self.bitParent.GetAbsolute()
        portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
        self.sr.handle.left = int((w - self.bitWidth) * portion)
        self.ShowLit(portion)

    def OnMouseUp(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return
        self.sr.slideTimer = None
        l, t, w, h = self.bitParent.GetAbsolute()
        portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
        self.sr.handle.left = int((w - self.sr.handle.width) * portion)
        self.SetValue(portion)

    def ShowLit(self, portion):
        l, t, w, h = self.bitParent.GetAbsolute()
        if not w:
            return
        self.sr.handle.left = int((w - self.sr.handle.width) * portion)
        for each in self.bitParent.children:
            if not hasattr(each, 'isBit'):
                continue
            mportion = max(0.0, min(1.0, (each.left + each.width / 2) / float(w)))
            if portion > mportion:
                each.SetOpacity(1.0)
            else:
                each.SetOpacity(0.333)

    def ShowSoftLit(self, portion):
        l, t, w, h = self.bitParent.GetAbsolute()
        for each in self.bitParent.children:
            if not hasattr(each, 'isBit'):
                continue
            if each.opacity == 1.0:
                continue
            mportion = max(0.0, min(1.0, (each.left + each.width / 2) / float(w)))
            if portion > mportion:
                each.SetOpacity(0.5)
            else:
                each.SetOpacity(0.333)

    def SetValue(self, value, doCallback = True):
        callback = value != self._value
        self._value = max(0.0, min(1.0, value))
        self.ShowLit(self._value)
        if callback and doCallback and self.onSetValueCallback:
            self.onSetValueCallback(self)

    def GetValue(self):
        return self._value


class GradientSlider(uiprimitives.Container):
    __guid__ = 'uicls.GradientSlider'
    default_name = 'GradientSlider'
    default_align = uiconst.RELATIVE
    default_bitWidth = 3
    default_bitHeight = 8
    default_bitGap = 1
    default_state = uiconst.UI_NORMAL
    default_left = 0
    default_top = 0
    default_width = 128
    default_height = 12
    cursor = uiconst.UICURSOR_SELECT

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.onSetValueCallback = None
        targetWidth = attributes.get('sliderWidth', 100)
        bitHeight = attributes.bitHeight or self.default_bitHeight
        self.height = bitHeight + 4
        self._value = 0.0
        self.sr.handle = uiprimitives.Container(parent=self, align=uiconst.RELATIVE, state=uiconst.UI_DISABLED, pos=(0,
         -2,
         3,
         self.height + 4), bgColor=ccConst.COLOR + (1.0,))
        if attributes.get('alphaValues'):
            alphaValues = attributes.get('alphaValues')
            rgbValues = [(0, (0, 0, 0))]
        else:
            alphaValues = (1, 1)
            rgbValues = [(0, (0, 0, 0)), (1.0, (1, 1, 1))]
        self.gradientSprite = uicontrols.GradientSprite(parent=self, pos=(0,
         0,
         targetWidth,
         self.height), rgbData=rgbValues, alphaData=[alphaValues, (1.0, 1.0)], alphaInterp=uicls.GradientConst.INTERP_LINEAR, colorInterp=uicls.GradientConst.INTERP_LINEAR, state=uiconst.UI_DISABLED)
        self.gradientSprite.width = targetWidth
        if attributes.setvalue is not None:
            self.SetValue(attributes.setvalue)
        self.onSetValueCallback = attributes.OnSetValue
        self.ChangeGradientColor(secondColor=(1.0, (1, 1, 0)))

    def OnMouseDown(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return
        self.sr.slideTimer = base.AutoTimer(33, self.UpdateSliderPortion)

    def UpdateSliderPortion(self, *args):
        l, t, w, h = self.gradientSprite.GetAbsolute()
        portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
        self.sr.handle.left = int(w * portion)

    def OnMouseUp(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return
        self.sr.slideTimer = None
        l, t, w, h = self.gradientSprite.GetAbsolute()
        portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
        self.sr.handle.left = int(w * portion)
        self.SetValue(portion)

    def SetValue(self, value, doCallback = True):
        callback = value != self._value
        self._value = max(0.0, min(1.0, value))
        self.SetHandle(self._value)
        if callback and doCallback and self.onSetValueCallback:
            self.onSetValueCallback(self)

    def SetHandle(self, portion):
        l, t, w, h = self.gradientSprite.GetAbsolute()
        if not w:
            return
        self.sr.handle.left = int((w - self.sr.handle.width) * portion)

    def GetValue(self):
        return self._value

    def ChangeGradientColor(self, firstColor = None, secondColor = None):
        colorData = self.gradientSprite.colorData
        if len(colorData) < 2:
            firstColor = secondColor
        if firstColor is not None:
            colorData[0] = firstColor
        if secondColor is not None and len(colorData) > 1:
            colorData[1] = secondColor
        self.gradientSprite.SetGradient()
