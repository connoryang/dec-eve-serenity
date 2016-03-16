#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\login\charcreation\steps\characterNamingMinimal.py
from charactercreator import const as ccConst
from eve.client.script.ui.login.charcreation.steps.characterNaming import CharacterNaming
import uicls
import uiprimitives
from carbonui import const as uiconst
import blue
import localization

class CharacterNamingMinimal(CharacterNaming):
    __guid__ = 'uicls.CharacterNamingMinimal'
    stepID = ccConst.MINIMALNAMINGSTEP

    def SetPhoto(self, photo):
        if photo is not None:
            self.sr.facePortrait.texture.atlasTexture = photo
            self.sr.facePortrait.texture.atlasTexture.Reload()

    def ApplyAttributes(self, attributes):
        CharacterNaming.ApplyAttributes(self, attributes)
        self.sr.customizeTextCont = uiprimitives.Container(name='customizeLater', parent=self.sr.uiContainer, align=uiconst.TOBOTTOM, height=80, top=64, state=uiconst.UI_NORMAL)
        self.sr.customizeText = uicls.CCLabel(parent=self.sr.customizeTextCont, fontsize=14, align=uiconst.BOTTOMLEFT, width=600, text='', letterspace=0, top=0, bold=0)
        self.sr.customizeText.text = localization.GetByLabel('UI/CharacterCreation/CustomizeLater')
        self.UpdateLayout()

    def UpdateLayout(self):
        CharacterNaming.UpdateLayout(self)
        self.AdjustTextWidth()

    def AdjustTextWidth(self):
        blue.pyos.synchro.Yield()
        if self.sr.customizeTextCont:
            left, top, width, height = self.sr.customizeTextCont.GetAbsolute()
            self.sr.customizeText.width = width
