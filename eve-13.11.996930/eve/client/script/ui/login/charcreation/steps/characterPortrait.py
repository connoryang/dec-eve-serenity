#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\login\charcreation\steps\characterPortrait.py
import base
from carbonui import const as uiconst
from charactercreator import const as ccConst
from eve.client.script.ui.login.charcreation.charCreation import BaseCharacterCreationStep, MAXMENUSIZE
from evegraphics import settings as gfxsettings
import localization
import uicls
import uicontrols
import uiprimitives
import uiutil

class CharacterPortrait(BaseCharacterCreationStep):
    __guid__ = 'uicls.CharacterPortrait'
    __notifyevents__ = BaseCharacterCreationStep.__notifyevents__
    __notifyevents__ += ['OnGraphicSettingsChanged']
    stepID = ccConst.PORTRAITSTEP

    def ApplyAttributes(self, attributes):
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        self.colorPaletteWidth = uicls.CCColorPalette.COLORPALETTEWIDTH
        self.portraitSize = 128
        self.selectedPortrait = 0
        self.sr.assetMenuPar = uiprimitives.Container(parent=self.sr.rightSide, pos=(0,
         0,
         MAXMENUSIZE,
         uicore.desktop.height), state=uiconst.UI_PICKCHILDREN, align=uiconst.CENTERTOP)
        self.sr.hintBox = uiprimitives.Container(parent=self.sr.assetMenuPar, pos=(MAXMENUSIZE,
         20,
         200,
         150), align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED)
        self.sr.hintText = uicontrols.EveLabelMedium(text='', parent=self.sr.hintBox, align=uiconst.TOTOP)
        self.UpdateLayout()

    def UpdateLayout(self):
        BaseCharacterCreationStep.UpdateLayout(self)
        self.sr.rightSide.width += uicls.CCColorPalette.COLORPALETTEWIDTH
        self.ReloadPortraitAssetMenu()
        self.ReloadPortraits()
        self.sr.hintBox.left = self.assetMenuMainWidth + 20

    def ReloadPortraitAssetMenu(self):
        sm.GetService('cc').LogInfo('CharacterPortrait::ReloadPortraitAssetMenu')
        if self.sr.portraitAssetMenu:
            self.sr.portraitAssetMenu.Close()
        groups = [(ccConst.BACKGROUNDGROUP, ()), (ccConst.POSESGROUP, ()), (ccConst.LIGHTSGROUP, ())]
        assetMenuWidth = min(MAXMENUSIZE + uicls.CCColorPalette.COLORPALETTEWIDTH, self.sr.rightSide.width - 32)
        self.assetMenuMainWidth = assetMenuWidth - uicls.CCColorPalette.COLORPALETTEWIDTH
        self.sr.portraitAssetMenu = uicls.CharCreationAssetMenu(parent=self.sr.assetMenuPar, groups=groups, align=uiconst.CENTERTOP, width=assetMenuWidth, height=uicore.desktop.height, top=16)
        self.sr.assetMenuPar.width = assetMenuWidth

    def SetHintText(self, modifier, hintText = ''):
        text = hintText
        if modifier in ccConst.HELPTEXTS:
            labelPath = ccConst.HELPTEXTS[modifier]
            text = localization.GetByLabel(labelPath)
        if text != self.sr.hintText.text:
            self.sr.hintText.text = text

    def ReloadPortraits(self):
        if self.sr.portraitCont:
            self.sr.portraitCont.Close()
        self.sr.portraitCont = uiprimitives.Container(name='portraitCont', parent=self.sr.leftSide, align=uiconst.CENTERTOP, pos=(0,
         128,
         128,
         134 * ccConst.NUM_PORTRAITS - 6 + 44))
        self.sr.facePortraits = [None] * ccConst.NUM_PORTRAITS
        for i in xrange(ccConst.NUM_PORTRAITS):
            if i == 0:
                frameAlpha = 0.8
            else:
                frameAlpha = 0.2
            portraitCont = uiprimitives.Container(name='portraitCont1', parent=self.sr.portraitCont, align=uiconst.TOTOP, pos=(0,
             0,
             0,
             self.portraitSize), padBottom=6, state=uiconst.UI_NORMAL)
            portraitCont.OnClick = (self.PickPortrait, i)
            portraitCont.OnDblClick = self.OnPortraitDblClick
            portraitCont.OnMouseEnter = (self.OnPortraitEnter, portraitCont)
            button = uicontrols.Icon(parent=portraitCont, icon=ccConst.ICON_CAM_IDLE, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT, color=ccConst.COLOR75, left=6, top=6)
            button._idleIcon = ccConst.ICON_CAM_IDLE
            button._pressedIcon = ccConst.ICON_CAM_PRESSED
            button._imageIndex = i
            button.OnClick = (self.CameraButtonClick, button)
            button.OnMouseEnter = (self.GenericButtonEnter, button)
            button.OnMouseExit = (self.GenericButtonExit, button)
            button.OnMouseDown = (self.GenericButtonDown, button)
            button.OnMouseUp = (self.GenericButtonUp, button)
            frame = uicontrols.Frame(parent=portraitCont, color=ccConst.COLOR + (frameAlpha,))
            facePortrait = uicontrols.Icon(parent=portraitCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
            uiprimitives.Fill(parent=portraitCont, color=(0.0, 0.0, 0.0, 0.35))
            portraitCont.sr.button = button
            portraitCont.sr.frame = frame
            portraitCont.sr.facePortrait = facePortrait
            portraitCont.hasPhoto = False
            self.sr.facePortraits[i] = portraitCont

        for i in xrange(ccConst.NUM_PORTRAITS):
            if uicore.layer.charactercreation.facePortraits[i] is not None:
                photo = uicore.layer.charactercreation.facePortraits[i]
                cont = self.sr.facePortraits[i]
                cont.sr.facePortrait.texture.atlasTexture = photo
                cont.sr.facePortrait.texture.atlasTexture.Reload()
                cont.hasPhoto = True
                cont.sr.button.state = uiconst.UI_HIDDEN
                if photo == uicore.layer.charactercreation.activePortrait:
                    self.SetPortraitFocus(i)

        btn = uicls.CharCreationButton(parent=self.sr.portraitCont, label=localization.GetByLabel('UI/CharacterCreation/ResetExpression'), pos=(0, 0, 0, 0), fixedwidth=128, align=uiconst.CENTERBOTTOM, func=self.ResetFacePose)

    def ResetFacePose(self, *args):
        info = self.GetInfo()
        self.charSvc.ResetFacePose(info.charID)

    def OnPortraitDblClick(self, *args):
        uicore.layer.charactercreation.Approve()

    def PickPortrait(self, selectedNo):
        uicore.layer.charactercreation.AnimateToStoredPortrait(selectedNo)
        self.SetPortraitFocus(selectedNo)

    def SetPortraitFocus(self, selectedNo, *args):
        self.selectedPortrait = selectedNo
        for portraitContainer in self.sr.facePortraits:
            portraitContainer.sr.frame.SetAlpha(0.2)
            portraitContainer.sr.facePortrait.SetAlpha(0.3)

        frame = self.sr.facePortraits[selectedNo].sr.frame
        frame.SetAlpha(0.8)
        portrait = self.sr.facePortraits[selectedNo].sr.facePortrait
        portrait.SetAlpha(1.0)
        uicore.layer.charactercreation.SetActivePortrait(selectedNo)

    def ValidateStepComplete(self):
        if not self.IsDollReady:
            return False
        if uicore.layer.charactercreation.GetPortraitInfo(self.selectedPortrait) is None:
            self.CapturePortrait(self.selectedPortrait)
        return True

    def CapturePortrait(self, idx, *args):
        photo = uicore.layer.charactercreation.CapturePortrait(idx)
        if photo:
            self.SetPortrait(photo)
            uicore.layer.charactercreation.SetFacePortrait(photo, idx)

    def SetPortrait(self, photo, *args):
        if self.destroyed:
            return
        facePortraitCont = self.sr.facePortraits[self.selectedPortrait]
        facePortraitCont.sr.facePortrait.texture.atlasTexture = photo
        facePortraitCont.sr.facePortrait.texture.atlasTexture.Reload()
        facePortraitCont.hasPhoto = True

    def OnPortraitEnter(self, portrait, *args):
        portrait.sr.button.state = uiconst.UI_NORMAL
        portrait.sr.mouseOverTimer = base.AutoTimer(33.0, self.CheckPortraitMouseOver, portrait)

    def CheckPortraitMouseOver(self, portrait, *args):
        if uicore.uilib.mouseOver is portrait or uiutil.IsUnder(uicore.uilib.mouseOver, portrait):
            return
        portrait.sr.mouseOverTimer = None
        if portrait.hasPhoto:
            portrait.sr.button.state = uiconst.UI_HIDDEN

    def CameraButtonClick(self, button, *args):
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_portrait_snapshot_play'))
        self.SetPortraitFocus(button._imageIndex)
        self.CapturePortrait(button._imageIndex)

    def GenericButtonDown(self, button, mouseBtn, *args):
        if mouseBtn == uiconst.MOUSELEFT:
            uiutil.MapIcon(button, button._pressedIcon)

    def GenericButtonUp(self, button, *args):
        uiutil.MapIcon(button, button._idleIcon)

    def GenericButtonEnter(self, button, *args):
        uiutil.MapIcon(button, button._idleIcon)

    def GenericButtonExit(self, button, *args):
        uiutil.MapIcon(button, button._idleIcon)

    def OnGraphicSettingsChanged(self, changes):
        if gfxsettings.UI_NCC_GREEN_SCREEN in changes:
            self.UpdateLayout()
        self.ReloadPortraitAssetMenu()
