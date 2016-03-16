#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\gamma.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.buttonGroup import ButtonGroup
from eve.client.script.ui.control.eveWindow import Window
from carbonui.control.slider import Slider
import evegraphics.settings as gfxsettings
import carbonui.const as uiconst
import localization
import trinity

class GammaSliderWindow(Window):
    default_topParentHeight = 0
    default_isCollapseable = False
    default_isKillable = False
    default_isMinimizable = False
    default_fixedWidth = 300
    default_fixedHeight = 100
    default_windowID = 'GammaSliderWindow'
    default_isPinable = False
    default_caption = localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Brightness')

    def ConvertValue(self, value):
        return 2.0 - value

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        uicore.layer.systemmenu.FadeBGOut()
        uicore.layer.systemmenu.Hide()
        uicore.layer.inflight.Disable()
        mainCont = Container(name='mainCont', parent=self.sr.main, align=uiconst.CENTER, state=uiconst.UI_NORMAL, width=200, height=60)
        self.savedValue = gfxsettings.Get(gfxsettings.GFX_BRIGHTNESS)
        self.currentValue = self.savedValue
        self.gammaSlider = Slider(name='gammaSlider', parent=mainCont, minValue=0.5, maxValue=1.5, startValue=1.0, onsetvaluefunc=self.OnMySliderMoved, setlabelfunc=self.UpdateSliderLabel)
        self.gammaSlider.SetValue(self.ConvertValue(self.currentValue), True)
        buttonGroup = ButtonGroup(name='buttonGroup', parent=mainCont, align=uiconst.CENTERBOTTOM, buttonPadding=10)
        buttonGroup.AddButton(localization.GetByLabel('UI/Common/Buttons/Save'), self.Save)
        buttonGroup.AddButton(localization.GetByLabel('UI/SystemMenu/ResetSettings/Reset'), self.Reset)
        buttonGroup.AddButton(localization.GetByLabel('UI/Common/Buttons/Cancel'), self.Cancel)

    def UpdateSliderLabel(self, label, *_):
        label.text = ''

    def OnMySliderMoved(self, slider):
        self.currentValue = self.ConvertValue(slider.GetValue())
        trinity.settings.SetValue('eveSpaceSceneGammaBrightness', self.currentValue)

    def Reset(self, *_):
        self.gammaSlider.SetValue(1.0, True)

    def Close(self, *args, **kwds):
        Window.Close(self, *args, **kwds)
        uicore.layer.systemmenu.Show()
        uicore.layer.systemmenu.FadeBGIn()
        uicore.layer.inflight.Enable()

    def Save(self, *_):
        self.savedValue = self.currentValue
        gfxsettings.Set(gfxsettings.GFX_BRIGHTNESS, self.savedValue, pending=False)
        self.Close()

    def Cancel(self, *_):
        trinity.settings.SetValue('eveSpaceSceneGammaBrightness', self.savedValue)
        self.Close()


def GammaSlider():
    GammaSliderWindow.CloseIfOpen()
    wnd = GammaSliderWindow.Open()
    wnd.SetParent(uicore.layer.modal)
    return wnd
