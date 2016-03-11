#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\login\charcreation\charCreationButtons.py
import carbonui.const as uiconst
import uiprimitives
import charactercreator.const as ccConst

class BaseCCButton(uiprimitives.Container):
    __guid__ = 'uicls.BaseCCButton'
    default_state = uiconst.UI_NORMAL
    default_left = 0
    default_top = 0
    default_width = 128
    default_height = 128
    default_align = uiconst.CENTER
    mouseoverSound = 'wise:/ui_icc_button_mouse_over_play'
    selectSound = 'wise:/ui_icc_button_select_play'

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.normalSprite = uiprimitives.Sprite(name='normalSprite', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='', width=self.default_width, height=self.default_height)
        self.hiliteSprite = uiprimitives.Sprite(name='hiliteSprite', parent=self, align=uiconst.CENTER, state=uiconst.UI_HIDDEN, texturePath='', width=self.default_width, height=self.default_height)
        self.normalSprite.SetAlpha(0.3)

    def OnMouseEnter(self, *args):
        sm.StartService('audio').SendUIEvent(unicode(self.mouseoverSound))
        self.normalSprite.SetAlpha(0.6)

    def OnMouseExit(self, *args):
        self.normalSprite.SetAlpha(0.3)

    def Deselect(self):
        self.hiliteSprite.state = uiconst.UI_HIDDEN
        self.normalSprite.state = uiconst.UI_DISABLED
        self.normalSprite.SetAlpha(0.3)

    def Select(self):
        sm.StartService('audio').SendUIEvent(unicode(self.selectSound))
        self.hiliteSprite.state = uiconst.UI_DISABLED
        self.normalSprite.state = uiconst.UI_HIDDEN

    def OnClick(self, *args):
        pass


class RaceButton(BaseCCButton):
    __guid__ = 'uicls.RaceButton'
    default_left = 0
    default_top = 0
    default_width = 256
    default_height = 256

    def ApplyAttributes(self, attributes):
        BaseCCButton.ApplyAttributes(self, attributes)
        self.raceID = attributes.raceID
        self.mouseExitCallback = attributes.mouseExitCallback
        self.normalSprite.texture.resPath = 'res:/UI/Texture/CharacterCreation/raceButtons/RaceButtonNormal_%s.dds' % self.raceID
        self.hiliteSprite.texture.resPath = 'res:/UI/Texture/CharacterCreation/raceButtons/RaceButtonDown_%s.dds' % self.raceID

    def OnMouseEnter(self, *args):
        BaseCCButton.OnMouseEnter(self, *args)
        info = uicore.layer.charactercreation.GetInfo()
        if not info.raceID:
            uicore.layer.charactercreation.UpdateBackdropLite(raceID=self.raceID, mouseEnter=True)

    def OnMouseExit(self, *args):
        BaseCCButton.OnMouseExit(self, *args)
        info = uicore.layer.charactercreation.GetInfo()
        if not info.raceID:
            uicore.layer.charactercreation.UpdateBackdropLite(raceID=None, mouseEnter=True)
        if self.mouseExitCallback is not None:
            self.mouseExitCallback()

    def OnClick(self, *args):
        if uicore.layer.charactercreation.raceID != self.raceID:
            uicore.layer.charactercreation.SelectRace(self.raceID)

    def OnDblClick(self, *args):
        uicore.layer.charactercreation.Approve()


class BloodlineButton(BaseCCButton):
    __guid__ = 'uicls.BloodlineButton'
    default_width = 185
    default_height = 140

    def ApplyAttributes(self, attributes):
        BaseCCButton.ApplyAttributes(self, attributes)
        self.bloodlineID = attributes.bloodlineID
        self.mouseEnterCallback = attributes.mouseEnterCallback
        self.mouseExitCallback = attributes.mouseExitCallback
        self.normalSprite.texture.resPath = 'res:/UI/Texture/CharacterCreation/bloodlineButtons/Bloodline_Normal_%d.png' % self.bloodlineID
        self.normalSprite.top = 6
        self.hiliteSprite.texture.resPath = 'res:/UI/Texture/CharacterCreation/bloodlineButtons/Bloodline_Down_%d.png' % self.bloodlineID
        self.hiliteSprite.top = 6

    def OnClick(self, *args):
        if uicore.layer.charactercreation.bloodlineID != self.bloodlineID:
            uicore.layer.charactercreation.SelectBloodline(self.bloodlineID)

    def OnMouseEnter(self, *args):
        if self.mouseEnterCallback is not None:
            self.mouseEnterCallback(self.bloodlineID)

    def OnMouseEnterAppearanceChange(self, *args):
        BaseCCButton.OnMouseEnter(self, *args)

    def OnMouseExit(self, *args):
        BaseCCButton.OnMouseExit(self, *args)
        if self.mouseExitCallback is not None:
            self.mouseExitCallback()


class GenderButton(BaseCCButton):
    __guid__ = 'uicls.GenderButton'
    default_left = 0
    default_top = 0
    default_width = 64
    default_height = 64
    selectSound = 'wise:/ui_icc_button_select_gender_play'

    def ApplyAttributes(self, attributes):
        BaseCCButton.ApplyAttributes(self, attributes)
        self.raceID = attributes.raceID
        self.genderID = attributes.genderID
        if self.genderID == ccConst.GENDERID_FEMALE:
            gender = 'Female'
        else:
            gender = 'Male'
        self.normalSprite.texture.resPath = 'res:/UI/Texture/CharacterCreation/bloodlineButtons/Gender_%s_Normal.dds' % gender
        self.hiliteSprite.texture.resPath = 'res:/UI/Texture/CharacterCreation/bloodlineButtons/Gender_%s_%d.dds' % (gender, self.raceID)

    def OnClick(self, *args):
        if uicore.layer.charactercreation.genderID != self.genderID:
            uicore.layer.charactercreation.SelectGender(self.genderID)

    def OnDblClick(self, *args):
        uicore.layer.charactercreation.Approve()
