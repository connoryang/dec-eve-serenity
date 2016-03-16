#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\switch.py
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
import carbonui.const as uiconst
from eve.client.script.ui.control.themeColored import FillThemeColored, FrameThemeColored
COLOR_GREEN = (0.0, 1.0, 0.0, 0.5)
COLOR_RED = (1.0, 0.0, 0.0, 0.5)

class Switch(Container):
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_width = 30
    default_height = 10

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isEnabled = attributes.get('isEnabled', True)
        self.disabled = False
        FrameThemeColored(parent=self)
        btnCont = Container(parent=self)
        self.onBtn = Container(parent=self, align=uiconst.TOLEFT_PROP, width=0.5, bgColor=COLOR_GREEN, state=uiconst.UI_DISABLED)
        self.offBtn = Container(parent=self, align=uiconst.TORIGHT_PROP, width=0.5, bgColor=COLOR_RED, state=uiconst.UI_DISABLED)
        self.knob = FillThemeColored(parent=btnCont, align=uiconst.TOLEFT_PROP, width=0.5, state=uiconst.UI_DISABLED, colorType=uiconst.COLORTYPE_UIHEADER, opacity=1.0)
        self.SetStateNotAnimated()

    def SetStateNotAnimated(self):
        if self.isEnabled:
            self.knob.left = self.width / 2
        else:
            self.knob.left = 0

    def OnClick(self, *args):
        if self.disabled:
            return
        self.isEnabled = not self.isEnabled
        self.UpdateKnob()

    def UpdateKnob(self):
        if self.isEnabled:
            self.knob.StopAnimations()
            animations.MorphScalar(self.knob, 'left', startVal=self.knob.left, endVal=self.width / 2, duration=0.1)
        else:
            animations.MorphScalar(self.knob, 'left', startVal=self.knob.left, endVal=0, duration=0.1)

    def SetOnline(self):
        self.isEnabled = True
        self.UpdateKnob()

    def SetOffline(self):
        self.isEnabled = False
        self.UpdateKnob()

    def Close(self):
        super(Switch, self).Close()

    def Disable(self):
        self.disabled = True
        self.opacity = 0.5
        if self.isEnabled:
            self.offBtn.opacity = 0.0
        else:
            self.onBtn.opacity = 0.0

    def Enable(self):
        self.disabled = False
        self.opacity = 1.0
