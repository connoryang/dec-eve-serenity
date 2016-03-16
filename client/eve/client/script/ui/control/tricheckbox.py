#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\tricheckbox.py
from carbonui.primitives.base import Base
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
import carbonui.const as uiconst
from carbonui.const import NOT_CHECKED, HALF_CHECKED, FULL_CHECKED
from eve.client.script.ui.control.themeColored import SpriteThemeColored
import trinity

class TriCheckbox(Container):
    __guid__ = 'uicontrols.TriCheckbox'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.OnChange = attributes.get('callback', None)
        self.checked = False
        self.checkMark = Sprite(parent=self, pos=(0, 0, 16, 16), name='self_ok', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/checkboxChecked.png')
        self.underlay = SpriteThemeColored(name='frame', bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT, blendMode=trinity.TR2_SBM_ADD, texturePath='res:/UI/Texture/Shared/checkbox_comp.png', opacity=0.2, padding=2)

    def SetChecked(self, checkState):
        checkState = checkState or NOT_CHECKED
        self.checked = checkState
        if self.checked == NOT_CHECKED:
            self.checkMark.display = False
        elif self.checked == HALF_CHECKED:
            self.checkMark.texturePath = 'res:/UI/Texture/Shared/checkboxHalfChecked.png'
            self.checkMark.display = True
        elif self.checked == FULL_CHECKED:
            self.checkMark.texturePath = 'res:/UI/Texture/Shared/checkboxChecked.png'
            self.checkMark.display = True
        if self.OnChange:
            self.OnChange(self)

    def GetValue(self):
        return self.checked

    def OnClick(self, *args):
        if self.checked == NOT_CHECKED:
            self.SetChecked(HALF_CHECKED)
            uicore.Message('DiodeClick')
        elif self.checked == HALF_CHECKED:
            self.SetChecked(FULL_CHECKED)
            uicore.Message('DiodeClick')
        elif self.checked == FULL_CHECKED:
            self.SetChecked(NOT_CHECKED)
            uicore.Message('DiodeDeselect')

    def Enable(self):
        Base.Enable(self)
        self.opacity = 1.0

    def Disable(self):
        Base.Disable(self)
        self.opacity = 0.3
