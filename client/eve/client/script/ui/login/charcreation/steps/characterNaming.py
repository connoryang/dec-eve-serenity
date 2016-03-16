#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\login\charcreation\steps\characterNaming.py
import random
from carbonui import const as uiconst
from charactercreator import const as ccConst
from eve.client.script.ui.login.charcreation.charCreation import BaseCharacterCreationStep
from eve.common.lib import appConst as const
import localization
import uicls
import uicontrols
import uiprimitives
import util
import blue

class CharacterNaming(BaseCharacterCreationStep):
    __guid__ = 'uicls.CharacterNaming'
    __notifyevents__ = ['OnHideUI', 'OnShowUI']
    stepID = ccConst.NAMINGSTEP

    def ApplyAttributes(self, attributes):
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        self.isSerenity = boot.region == 'optic'
        self.namesChecked = {}
        self.schoolInfo = {}
        self.ancestryInfo = {}
        self.ancestryConts = {}
        self.schoolConts = {}
        self.checkingName = 0
        self.startAncestryHeight = 180
        self.startEducationHeight = 180
        self.padValue = 16
        self.SetupAncestrySection()
        self.SetupEducationSection()
        self.SetupNameSection()
        self.sr.portraitCont = uiprimitives.Container(name='portraitCont', parent=self.sr.leftSide, align=uiconst.CENTERTOP, pos=(0, 128, 128, 128))
        uicontrols.Frame(parent=self.sr.portraitCont, color=ccConst.COLOR + (0.3,))
        self.sr.facePortrait = uicontrols.Icon(parent=self.sr.portraitCont, idx=1, align=uiconst.TOALL)
        photo = uicore.layer.charactercreation.GetActivePortrait()
        if photo is not None:
            self.sr.facePortrait.texture.atlasTexture = photo
            self.sr.facePortrait.texture.atlasTexture.Reload()
        self.UpdateLayout()

    def UpdateLayout(self):
        BaseCharacterCreationStep.UpdateLayout(self)
        info = self.GetInfo()
        self.sr.rightSide.width = min(self.sr.rightSide, 380)
        picker = uicls.CCRacePicker(parent=self.sr.leftSide, align=uiconst.BOTTOMLEFT, owner=self, raceID=info.raceID, bloodlineID=info.bloodlineID, genderID=info.genderID, padding=(30, 0, 0, 0), clickable=False, showText=True)
        self.AdjustHeightAndWidth(doMorph=0)
        try:
            self.SetAncestryFromID(info.ancestryID, doMorph=0)
            self.SetSchoolFromID(info.schoolID, doMorph=0)
        except Exception:
            if self and not self.destroyed:
                raise

    def SetupAncestrySection(self, *args):
        info = self.GetInfo()
        padding = self.padValue
        if self.sr.ancestyCont:
            self.sr.ancestyCont.Close()
        self.sr.ancestyCont = uiprimitives.Container(name='ancestryCont', parent=self.sr.rightSide, align=uiconst.TOTOP, height=self.startAncestryHeight, padding=(padding,
         padding,
         padding,
         0))
        sub = uiprimitives.Container(name='sub', parent=self.sr.ancestyCont, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, padding=(padding,
         padding,
         padding,
         padding))
        topCont = uiprimitives.Container(name='topCont', parent=sub, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, pos=(0, 30, 0, 78))
        text = uicls.CCLabel(parent=sub, text=localization.GetByLabel('UI/CharacterCreation/AncestrySelection'), fontsize=20, align=uiconst.TOPLEFT, letterspace=1, idx=1, pos=(0, -6, 0, 0), uppercase=1, color=ccConst.COLOR50)
        self.ancestryTextCont = textCont = uiprimitives.Container(name='textCont', parent=sub, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.sr.ancestryNameText = uicls.CCLabel(parent=textCont, text='', fontsize=14, align=uiconst.TOPLEFT, letterspace=1, idx=1, pos=(0, 0, 0, 0), color=ccConst.COLOR50)
        self.sr.ancestryDescrText = uicls.CCLabel(parent=textCont, text='', fontsize=10, align=uiconst.TOTOP, letterspace=0, idx=1, padTop=20, shadowOffset=(0, 0), bold=0, color=ccConst.COLOR50)
        hiliteFrame = uicontrols.Frame(name='hiliteFrame', parent=self.sr.ancestyCont, frameConst=ccConst.MAINFRAME_INV)
        uiprimitives.Fill(name='fill', parent=self.sr.ancestyCont, color=(0.0, 0.0, 0.0, 0.5))
        if not self.ancestryInfo:
            ancestries = sm.GetService('cc').GetData('ancestries', ['bloodlineID', info.bloodlineID], 1)
            for each in ancestries:
                self.ancestryInfo[each.ancestryID] = each

        self.ancestryConts = {}
        left = 0
        for i, (ancestryID, info) in enumerate(self.ancestryInfo.iteritems()):
            c = uiprimitives.Container(name='c', parent=topCont, align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, pos=(left,
             0,
             100,
             80))
            hexName = localization.GetByMessageID(info.ancestryNameID)
            label = uicls.CCLabel(parent=c, text='<center>%s' % hexName, fontsize=12, align=uiconst.CENTERTOP, letterspace=0, idx=1, pos=(0,
             46,
             c.width,
             0), shadowOffset=(0, 0), bold=0, color=ccConst.COLOR50)
            hex = uicls.CCHexButtonAncestry(name='ancestryHex', parent=c, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, pos=(0, -10, 64, 64), pickRadius=32, info=info, id=ancestryID, hexName=hexName, func=self.SetAncestry, iconNum=ancestryID - 1)
            left += 110
            self.ancestryConts[ancestryID] = hex

    def SetAncestryFromID(self, ancestryID, doMorph = 1, *args):
        selected = self.ancestryConts.get(ancestryID, None)
        self.SetAncestry(selected, doMorph=doMorph)

    def SetAncestry(self, selected = None, doMorph = 1, *args):
        if selected is None:
            i = random.randint(0, 2)
            selected = self.ancestryConts.values()[i]
        uicore.layer.charactercreation.SelectAncestry(selected.id)
        selected.SelectHex(self.ancestryConts.values())
        ancestryInfo = self.ancestryInfo.get(selected.id)
        self.sr.ancestryNameText.text = localization.GetByMessageID(ancestryInfo.ancestryNameID)
        self.sr.ancestryDescrText.text = localization.GetByMessageID(ancestryInfo.descriptionID)
        selected.frame.state = uiconst.UI_DISABLED
        self.AdjustHeightAndWidth(doMorph=doMorph)

    def SetupEducationSection(self, *args):
        info = self.GetInfo()
        padding = self.padValue
        if self.sr.educationCont:
            self.sr.educationCont.Close()
        self.sr.educationCont = uiprimitives.Container(name='educationCont', parent=self.sr.rightSide, align=uiconst.TOTOP, height=self.startEducationHeight, padding=(padding,
         padding,
         padding,
         0))
        sub = uiprimitives.Container(name='sub', parent=self.sr.educationCont, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, padding=(padding,
         padding,
         padding,
         padding))
        topCont = uiprimitives.Container(name='topCont', parent=sub, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, pos=(0, 30, 0, 78))
        text = uicls.CCLabel(parent=sub, text=localization.GetByLabel('UI/CharacterCreation/EducationSelection'), fontsize=20, align=uiconst.TOPLEFT, letterspace=1, idx=1, pos=(0, -6, 0, 0), uppercase=1, color=ccConst.COLOR50)
        self.schoolTextCont = textCont = uiprimitives.Container(name='textCont', parent=sub, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.sr.schoolNameText = uicls.CCLabel(parent=textCont, text='', fontsize=14, align=uiconst.TOPLEFT, letterspace=1, idx=1, pos=(0, 0, 0, 0), color=ccConst.COLOR50)
        self.sr.schoolDescrText = uicls.CCLabel(parent=textCont, text='', fontsize=10, align=uiconst.TOTOP, letterspace=0, idx=1, padTop=20, shadowOffset=(0, 0), bold=0, color=ccConst.COLOR50)
        hiliteFrame = uicontrols.Frame(name='hiliteFrame', parent=self.sr.educationCont, frameConst=ccConst.MAINFRAME_INV)
        uiprimitives.Fill(name='fill', parent=self.sr.educationCont, color=(0.0, 0.0, 0.0, 0.5))
        if not self.schoolInfo:
            schools = sm.GetService('cc').GetData('schools', ['raceID', info.raceID], 1)
            for each in schools:
                info = sm.GetService('cc').GetData('schools', ['schoolID', each.schoolID])
                self.schoolInfo[each.schoolID] = info

        left = 0
        offsetByRace = {const.raceCaldari: 17,
         const.raceMinmatar: 14,
         const.raceAmarr: 11,
         const.raceGallente: 20}
        iconNumOffset = offsetByRace.get(info.raceID)
        for schoolID, info in self.schoolInfo.iteritems():
            c = uiprimitives.Container(name='c', parent=topCont, align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, pos=(left,
             0,
             100,
             80))
            hexName = localization.GetByMessageID(info.schoolNameID)
            label = uicls.CCLabel(parent=c, text='<center>%s' % hexName, fontsize=12, align=uiconst.CENTERTOP, letterspace=0, idx=1, pos=(0,
             46,
             c.width,
             0), shadowOffset=(0, 0), bold=0, color=ccConst.COLOR50)
            hex = uicls.CCHexButtonSchool(name='schoolHex', parent=c, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, pos=(0, -10, 64, 64), pickRadius=32, info=info, id=schoolID, hexName=hexName, func=self.SetSchool, iconNum=schoolID - iconNumOffset)
            left += 110
            self.schoolConts[schoolID] = hex

    def SetSchoolFromID(self, schoolID, doMorph = 1, *args):
        selected = self.schoolConts.get(schoolID, None)
        self.SetSchool(selected, doMorph=doMorph)

    def SetSchool(self, selected = None, doMorph = 1, *args):
        if selected is None:
            i = random.randint(0, 2)
            selected = self.schoolConts.values()[i]
        uicore.layer.charactercreation.SelectSchool(selected.id)
        selected.SelectHex(self.schoolConts.values())
        schoolInfo = self.schoolInfo.get(selected.id)
        self.sr.schoolNameText.text = selected.hexName
        self.sr.schoolDescrText.text = localization.GetByMessageID(schoolInfo.descriptionID)
        selected.frame.state = uiconst.UI_DISABLED
        self.AdjustHeightAndWidth(doMorph=doMorph)

    def SetupNameSection(self, *args):
        info = self.GetInfo()
        padding = self.padValue
        if self.sr.nameCont:
            self.sr.nameCont.Close()
        if self.isSerenity:
            maxFirstNameChars = 37
            contHeight = 120
        else:
            maxFirstNameChars = 24
            contHeight = 160
        self.sr.nameCont = uiprimitives.Container(name='nameCont', parent=self.sr.rightSide, align=uiconst.TOTOP, pos=(0,
         0,
         0,
         contHeight), padding=(padding,
         padding,
         padding,
         0))
        if not uicore.layer.charactercreation.CanChangeName():
            self.sr.nameCont.height = 0
            return
        sub = uiprimitives.Container(name='sub', parent=self.sr.nameCont, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, padding=(padding,
         padding,
         padding,
         padding))
        hiliteFrame = uicontrols.Frame(name='hiliteFrame', parent=self.sr.nameCont, frameConst=ccConst.MAINFRAME_INV)
        uiprimitives.Fill(name='fill', parent=self.sr.nameCont, color=(0.0, 0.0, 0.0, 0.5))
        text = uicls.CCLabel(parent=sub, text=localization.GetByLabel('UI/CharacterCreation/NameSelection'), fontsize=20, align=uiconst.TOPLEFT, letterspace=1, idx=1, pos=(0, -6, 0, 0), uppercase=1, color=ccConst.COLOR50)
        text.SetRGB(1.0, 1.0, 1.0)
        text.SetAlpha(1.0)
        top = 30
        firstName = info.charFirstName or ''
        self.sr.firstNameEdit = edit = uicontrols.SinglelineEdit(name='firstNameEdit', setvalue=firstName, parent=sub, pos=(0,
         top,
         150,
         0), maxLength=maxFirstNameChars, align=uiconst.TOTOP, OnChange=self.EnteringName, color=(1.0, 1.0, 1.0, 1.0), hinttext=localization.GetByLabel('UI/CharacterCreation/FirstName'))
        edit.OnReturn = self.CheckAvailability
        edit.OnAnyChar = self.OnCharInFirstName
        offset = 20
        if not self.isSerenity:
            btnTop = edit.top + edit.height + offset - 2
            btn = uicls.CharCreationButton(parent=sub, label=localization.GetByLabel('UI/CharacterCreation/Randomize'), pos=(0,
             btnTop,
             0,
             0), align=uiconst.TOPRIGHT, func=self.RandomizeLastName)
            rightPadding = btn.width + 10
            lastNameEditCont = uiprimitives.Container(name='lastNameEditCont', parent=sub, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, pos=(0,
             offset - 10,
             0,
             29), padding=(0,
             0,
             rightPadding,
             0))
            lastNameEditCont.isTabOrderGroup = 1
            lastName = info.charLastName or ''
            self.sr.lastNameEdit = edit = uicontrols.SinglelineEdit(name='lastNameEdit', parent=lastNameEditCont, setvalue=lastName, pos=(0, 10, 0, 0), maxLength=12, align=uiconst.TOTOP, OnChange=self.EnteringName, color=(1.0, 1.0, 1.0, 1.0), hinttext=localization.GetByLabel('UI/CharacterCreation/LastName'))
            edit.OnReturn = self.CheckAvailability
            edit.OnAnyChar = self.OnCharInLastName
            self.sr.firstNameEdit.padRight = rightPadding
        availCont = uiprimitives.Container(name='availCont', parent=sub, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, pos=(0,
         offset,
         0,
         0))
        availBtn = uicls.CharCreationButton(parent=availCont, label=localization.GetByLabel('UI/CharacterCreation/CheckNameAvailability'), pos=(0, 0, 0, 0), align=uiconst.TOPLEFT, func=self.CheckAvailability)
        availCont.height = availBtn.height
        left = availBtn.width + 4
        self.sr.availabilityLabel = uicontrols.EveLabelMedium(parent=availCont, align=uiconst.CENTERLEFT, left=left + 16, state=uiconst.UI_DISABLED)
        self.sr.availableIcon = uicontrols.Icon(parent=availCont, align=uiconst.CENTERLEFT, pos=(left,
         0,
         16,
         16), state=uiconst.UI_HIDDEN)
        self.sr.availableIcon.LoadIcon('ui_38_16_193')

    def RandomizeLastName(self, *args):
        info = self.GetInfo()
        self.sr.lastNameEdit.SetValue(uicore.layer.charactercreation.GetRandomLastName(info.bloodlineID))

    def EnteringName(self, *args):
        self.sr.availabilityLabel.state = uiconst.UI_HIDDEN
        self.sr.availableIcon.state = uiconst.UI_HIDDEN

    def OnCharInFirstName(self, char, *args):
        if char == uiconst.VK_SPACE:
            if self.isSerenity:
                allowedNumSpaces = 2
            else:
                allowedNumSpaces = 1
            numSpaces = self.sr.firstNameEdit.text.count(' ')
            if numSpaces >= allowedNumSpaces:
                uicore.Message('uiwarning03')
                return False
        return True

    def OnCharInLastName(self, char, *args):
        if char == uiconst.VK_SPACE:
            uicore.Message('uiwarning03')
            return False
        return True

    def NotifyCCLayerOfAvailabilityCheck(self, name):
        uicore.layer.charactercreation.OnAvailabilityCheck(name)

    def CheckAvailability(self, *args):
        if self.checkingName:
            return
        else:
            self.checkingName = 1
            charFirstName = self.sr.firstNameEdit.GetValue()
            if self.isSerenity:
                charLastName = ''
            else:
                charLastName = self.sr.lastNameEdit.GetValue()
                self.sr.lastNameEdit.CloseHistoryMenu()
            self.sr.firstNameEdit.CloseHistoryMenu()
            charName = charFirstName.strip()
            if charLastName:
                charName += ' %s' % charLastName
            self.NotifyCCLayerOfAvailabilityCheck(charName)
            if charName in self.namesChecked:
                valid = self.namesChecked[charName]
            else:
                valid = sm.RemoteSvc('charUnboundMgr').ValidateNameEx(charName, len(self.namesChecked))
                self.namesChecked[charName] = valid
            self.sr.availableIcon.state = uiconst.UI_DISABLED
            self.sr.availabilityLabel.state = uiconst.UI_DISABLED
            isAvailable = util.KeyVal()
            self.checkingName = 0
            if valid == 1:
                self.sr.availableIcon.LoadIcon('ui_38_16_193')
                self.sr.availabilityLabel.text = ''
                isAvailable.charName = charName
                isAvailable.reason = ''
                uicore.layer.charactercreation.setFirstLastNameCallback(charFirstName, charLastName)
                return isAvailable
            validStates = {-1: localization.GetByLabel('UI/CharacterCreation/InvalidName/TooShort'),
             -2: localization.GetByLabel('UI/CharacterCreation/InvalidName/TooLong'),
             -5: localization.GetByLabel('UI/CharacterCreation/InvalidName/IllegalCharacter'),
             -6: localization.GetByLabel('UI/CharacterCreation/InvalidName/TooManySpaces'),
             -7: localization.GetByLabel('UI/CharacterCreation/InvalidName/ConsecutiveSpaces'),
             -101: localization.GetByLabel('UI/CharacterCreation/InvalidName/Unavailable'),
             -102: localization.GetByLabel('UI/CharacterCreation/InvalidName/Unavailable')}
            reason = validStates.get(valid, localization.GetByLabel('UI/CharacterCreation/InvalidName/IllegalCharacter'))
            self.sr.availableIcon.LoadIcon('ui_38_16_194')
            self.sr.availabilityLabel.text = reason
            if not self.isSerenity:
                self.sr.lastNameEdit.SelectAll()
                uicore.registry.SetFocus(self.sr.lastNameEdit)
            isAvailable.charName = None
            isAvailable.reason = reason
            return isAvailable

    def AdjustHeightAndWidth(self, doMorph = 1, *args):
        schoolTextContHeight = self.sr.educationCont.height - 130
        textHeight = self.sr.schoolDescrText.textheight + self.sr.schoolDescrText.padTop
        missingSchoolHeight = textHeight - schoolTextContHeight
        ancestryTextContHeight = self.sr.ancestyCont.height - 130
        textHeight = self.sr.ancestryDescrText.textheight + self.sr.ancestryDescrText.padTop
        missingAncestryHeight = textHeight - ancestryTextContHeight
        totalMissing = max(missingSchoolHeight, 0) + max(missingAncestryHeight, 0)
        if totalMissing > 0:
            for missingHeight, cont in [(missingSchoolHeight, self.sr.educationCont), (missingAncestryHeight, self.sr.ancestyCont)]:
                if missingHeight < -10:
                    cont.height -= 5
                    blue.synchro.Yield()
                    if self and not self.destroyed:
                        self.AdjustHeightAndWidth(doMorph=doMorph)
                    return

            availableHeight = uicore.desktop.height - self.sr.ancestyCont.height - self.sr.educationCont.height - self.sr.nameCont.height - 80 - 4 * self.padValue
            if availableHeight >= totalMissing:
                if missingSchoolHeight > 0:
                    self.sr.educationCont.height += missingSchoolHeight + 2
                if missingAncestryHeight > 0:
                    self.sr.ancestyCont.height += missingAncestryHeight + 2
            elif self.sr.rightSide.width < uicore.desktop.width * 0.6:
                if doMorph:
                    uicore.effect.CombineEffects(self.sr.rightSide, width=self.sr.rightSide.width + 50, time=25)
                else:
                    self.sr.rightSide.width += 50
                    blue.synchro.Yield()
                self.AdjustHeightAndWidth(doMorph=doMorph)
