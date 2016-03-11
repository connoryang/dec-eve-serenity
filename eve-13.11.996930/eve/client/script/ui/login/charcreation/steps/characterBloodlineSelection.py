#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\login\charcreation\steps\characterBloodlineSelection.py
from carbonui import const as uiconst
from charactercreator import const as ccConst
from eve.client.script.ui.login.charcreation.charCreation import BaseCharacterCreationStep
from eve.client.script.ui.login.charcreation.charCreationButtons import GenderButton, BloodlineButton
import localization
import log
import uicls
import uiprimitives
import uthread
import blue

class CharacterBloodlineSelection(BaseCharacterCreationStep):
    __guid__ = 'uicls.CharacterBloodlineSelection'
    stepID = ccConst.BLOODLINESTEP

    def ApplyAttributes(self, attributes):
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        self.bloodlineInfo = {}
        self.bloodlineIDs = []
        self.bloodlineBtns = []
        info = self.GetInfo()
        self.raceID = info.raceID
        self.bloodlineID = info.bloodlineID
        self.hoveredBloodlineID = None
        self.isFemaleLeft = False
        self.sr.rightSide.width = self.sr.leftSide.width
        bloodlines = sm.GetService('cc').GetBloodlineDataByRaceID().get(self.raceID, [])[:]
        for bloodline in bloodlines:
            self.bloodlineIDs.append(bloodline.bloodlineID)

        self.sr.raceInfoCont = uiprimitives.Container(name='raceInfoCont', parent=self.sr.uiContainer, align=uiconst.CENTERTOP, width=600, height=uicore.desktop.height, state=uiconst.UI_PICKCHILDREN)
        self.sr.textCont = uiprimitives.Container(name='raceCont', parent=self.sr.raceInfoCont, align=uiconst.TOTOP, pos=(0, 38, 0, 20), state=uiconst.UI_DISABLED)
        self.sr.header = uicls.CCLabel(text=localization.GetByLabel('UI/CharacterCreation/BloodlineSelection'), name='header', parent=self.sr.textCont, align=uiconst.CENTERTOP, uppercase=1, letterspace=2, color=(0.9, 0.9, 0.9, 0.8), fontsize=22, bold=False)
        if uicore.desktop.height <= 900:
            top = 20
        else:
            top = 40
        self.sr.raceCont = uiprimitives.Container(name='raceCont', parent=self.sr.raceInfoCont, align=uiconst.TOTOP, pos=(0,
         top,
         0,
         80), state=uiconst.UI_DISABLED)
        self.raceSprite = uiprimitives.Sprite(name='raceSprite', parent=self.sr.raceCont, align=uiconst.CENTER, state=uiconst.UI_HIDDEN, texturePath=self.raceHeaderPath, pos=(0, 0, 512, 128))
        self.raceSprite.state = uiconst.UI_DISABLED
        height = 128
        top = self.racialHeader.get(self.raceID, None)
        self.raceSprite.rectTop, self.raceSprite.rectHeight = top, height
        for bloodlineID in self.bloodlineIDs:
            cont = uiprimitives.Container(name='cont', parent=self.sr.uiContainer, align=uiconst.TOPLEFT, pos=(0, 0, 300, 200), state=uiconst.UI_HIDDEN)
            contName = 'cont_%d' % bloodlineID
            setattr(self.sr, contName, cont)
            contGender = uiprimitives.Container(name='contGender', parent=cont, align=uiconst.CENTERBOTTOM, pos=(0, 4, 255, 64))
            contGenderName = 'contGender_%d' % bloodlineID
            setattr(self.sr, contGenderName, contGender)
            genderBtnFemale = GenderButton(name='GenderButton', parent=contGender, align=uiconst.BOTTOMLEFT, pos=(0, 0, 64, 64), genderID=0, raceID=self.raceID, state=uiconst.UI_HIDDEN)
            btnName = 'genderBtn_%d_%d' % (bloodlineID, 0)
            setattr(self.sr, btnName, genderBtnFemale)
            genderBtnMale = GenderButton(name='GenderButton', parent=contGender, align=uiconst.BOTTOMRIGHT, pos=(0, 0, 64, 64), genderID=1, raceID=self.raceID, state=uiconst.UI_HIDDEN)
            btnName = 'genderBtn_%d_%d' % (bloodlineID, 1)
            setattr(self.sr, btnName, genderBtnMale)
            btn = BloodlineButton(name='BloodlineButton', parent=cont, align=uiconst.CENTER, pos=(0, 0, 128, 128), bloodlineID=bloodlineID, mouseExitCallback=self.ResetHoverRaceID, mouseEnterCallback=self.HiliteCorrectBloodlines)
            btnName = 'bloodlineBtn_%d' % bloodlineID
            setattr(self.sr, btnName, btn)
            self.bloodlineBtns.append(btn)
            if info.bloodlineID and info.bloodlineID == bloodlineID:
                btn.Select()
                genderBtnFemale.state = uiconst.UI_NORMAL
                genderBtnMale.state = uiconst.UI_NORMAL
                if info.genderID is not None:
                    canChangeGender = uicore.layer.charactercreation.CanChangeGender()
                    if info.genderID == ccConst.GENDERID_FEMALE:
                        genderBtnFemale.Select()
                        if not canChangeGender:
                            genderBtnMale.state = uiconst.UI_HIDDEN
                    else:
                        genderBtnMale.Select()
                        if not canChangeGender:
                            genderBtnFemale.state = uiconst.UI_HIDDEN

        self.sr.bloodlineTextCont = uiprimitives.Container(name='bloodlineTextCont', parent=self.sr.uiContainer, align=uiconst.TOBOTTOM, height=80, top=64, state=uiconst.UI_NORMAL)
        self.sr.bloodlineText = uicls.CCLabel(parent=self.sr.bloodlineTextCont, fontsize=12, align=uiconst.BOTTOMLEFT, width=600, text='', letterspace=0, top=0, bold=0)
        if info.bloodlineID:
            self.GetBloodlineText()

    def UpdateLayout(self):
        if uicore.desktop.height <= 900:
            self.sr.raceCont.top = 20
        else:
            self.sr.raceCont.top = 40
        self.MakeUI()
        uthread.new(self.GetTextWidth)

    def ResetHoverRaceID(self, *args):
        self.hoveredBloodlineID = None
        info = self.GetInfo()
        if info.bloodlineID:
            hilited = [info.bloodlineID]
        else:
            hilited = []
        uicore.layer.charactercreation.bloodlineSelector.HiliteBloodline(hilited)

    def GetTextWidth(self):
        blue.pyos.synchro.Yield()
        left, top, width, height = self.sr.bloodlineTextCont.GetAbsolute()
        self.sr.bloodlineText.width = width

    def OnBloodlineSelected(self, bloodlineID, *args):
        info = uicore.layer.charactercreation.GetInfo()
        if uicore.layer.charactercreation.CanChangeGender():
            uicore.layer.charactercreation.genderID = None
        self.sr.header.text = localization.GetByLabel('UI/CharacterCreation/GenderSelection')
        self.bloodlineID = bloodlineID
        for i in self.bloodlineIDs:
            bloodlineBtn = self.sr.Get('bloodlineBtn_%d' % i)
            bloodlineBtn.Deselect()
            genderBtnFemale = self.sr.Get('genderBtn_%d_%d' % (i, 0))
            genderBtnFemale.state = uiconst.UI_HIDDEN
            genderBtnMale = self.sr.Get('genderBtn_%d_%d' % (i, 1))
            genderBtnMale.state = uiconst.UI_HIDDEN
            btnContainer = self.sr.Get('contGender_%d' % i)
            btnContainer.width = 140

        btn = self.sr.Get('bloodlineBtn_%d' % bloodlineID)
        btn.Select()
        btnContainer = self.sr.Get('contGender_%d' % bloodlineID)
        uicore.effect.MorphUI(btnContainer, 'width', 255, 350.0, ifWidthConstrain=0)
        uicore.animations.FadeIn(btnContainer, duration=0.15)
        if not uicore.layer.charactercreation.CanChangeGender() and info.genderID:
            genderBtn = self.sr.Get('genderBtn_%d_%d' % (bloodlineID, info.genderID))
            genderBtn.state = uiconst.UI_NORMAL
            genderBtn.Select()
        else:
            genderBtnFemale = self.sr.Get('genderBtn_%d_%d' % (bloodlineID, 0))
            genderBtnFemale.state = uiconst.UI_NORMAL
            genderBtnFemale.Deselect()
            genderBtnMale = self.sr.Get('genderBtn_%d_%d' % (bloodlineID, 1))
            genderBtnMale.state = uiconst.UI_NORMAL
            genderBtnMale.Deselect()
        self.GetBloodlineText()

    def OnGenderSelected(self, genderID, *args):
        genderBtnFemale = self.sr.Get('genderBtn_%d_%d' % (self.bloodlineID, 0))
        genderBtnMale = self.sr.Get('genderBtn_%d_%d' % (self.bloodlineID, 1))
        if genderID == 0:
            genderBtnFemale.Select()
            genderBtnMale.Deselect()
        else:
            genderBtnFemale.Deselect()
            genderBtnMale.Select()

    def GetBloodlineText(self):
        info = self.GetInfo()
        if info.bloodlineID is None:
            return
        if not len(self.bloodlineInfo):
            self.bloodlineInfo = sm.GetService('cc').GetBloodlineDataByID()
        color = self.raceFontColor.get(info.raceID, (1.0, 1.0, 1.0, 0.75))
        blinfo = self.bloodlineInfo[info.bloodlineID]
        bloodlineText = localization.GetByMessageID(blinfo.descriptionID)
        self.sr.bloodlineText.color.SetRGB(*color)
        self.sr.bloodlineText.text = bloodlineText
        uthread.new(self.GetTextWidth)

    def MakeUI(self):
        for bloodlineID in self.bloodlineIDs:
            uthread.new(self.GetBloodlinePos, bloodlineID)

    def GetBloodlinePos(self, bloodlineID):
        blue.resMan.Wait()
        camera = uicore.layer.charactercreation.camera
        left = top = 0
        if getattr(uicore.layer.charactercreation, 'bloodlineSelector', None) is not None:
            pos = uicore.layer.charactercreation.bloodlineSelector.GetProjectedPosition(bloodlineID, None, camera)
            self.isFemaleLeft = uicore.layer.charactercreation.bloodlineSelector.GetGenderOrder(bloodlineID)
        else:
            log.LogError('Trying to place bloodline UI, but bloodlineSelector is None!')
            pos = (0.0, 0.0)
        if pos:
            left = int(pos[0] / uicore.desktop.dpiScaling)
            top = int(pos[1] / uicore.desktop.dpiScaling)
        cont = self.sr.Get('cont_%d' % bloodlineID)
        cont.left = left - cont.width / 2
        cont.top = top - cont.height / 2 - 35
        cont.state = uiconst.UI_PICKCHILDREN
        if not self.isFemaleLeft:
            cont = self.sr.Get('cont_%d' % bloodlineID)
            genderBtnFemale = self.sr.Get('genderBtn_%d_%d' % (bloodlineID, 0))
            genderBtnMale = self.sr.Get('genderBtn_%d_%d' % (bloodlineID, 1))
            genderBtnMale.SetAlign(uiconst.BOTTOMLEFT)
            genderBtnFemale.SetAlign(uiconst.BOTTOMRIGHT)

    def OnMouseMove(self, *args):
        uicls.BaseCharacterCreationStep.OnMouseMove(self, *args)
        pos = (int(uicore.uilib.x * uicore.desktop.dpiScaling), int(uicore.uilib.y * uicore.desktop.dpiScaling))
        layer = uicore.layer.charactercreation
        if getattr(layer, 'bloodlineSelector', None) is not None:
            picked = layer.PickObject(pos)
            bloodlineID, genderID = uicore.layer.charactercreation.bloodlineSelector.GetBloodlineAndGender(picked)
            if uicore.layer.charactercreation.bloodlineSelector is not None:
                self.HiliteCorrectBloodlines(bloodlineID)

    def HiliteCorrectBloodlines(self, bloodlineID, *args):
        info = self.GetInfo()
        hilited = []
        if bloodlineID not in (self.hoveredBloodlineID, info.bloodlineID):
            for eachBtn in self.bloodlineBtns:
                if eachBtn.bloodlineID != bloodlineID and eachBtn.bloodlineID != info.bloodlineID:
                    eachBtn.Deselect()
                else:
                    eachBtn.OnMouseEnterAppearanceChange()
                    hilited.append(eachBtn.bloodlineID)

            uicore.layer.charactercreation.bloodlineSelector.HiliteBloodline(hilited)
        elif bloodlineID is None and bloodlineID != self.hoveredBloodlineID:
            if info.bloodlineID:
                hilited = [info.bloodlineID]
            else:
                hilited = []
            uicore.layer.charactercreation.bloodlineSelector.HiliteBloodline(hilited)
        self.hoveredBloodlineID = bloodlineID
