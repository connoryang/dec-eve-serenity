#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\skilltrading\banner.py
from carbonui import const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveWindowUnderlay import RaisedUnderlay
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.utilButtons.marketDetailsButton import ShowMarketDetailsButton
from eve.common.script.util.eveFormat import FmtISKAndRound
import evetypes
from inventorycommon import const as invconst
import inventorycommon.typeHelpers
import localization
import uthread

class SkillInjectorBanner(ContainerAutoSize):
    __notifyevents__ = ['OnFreeSkillPointsChanged_Local']
    PAD_TOP = 4
    PAD_BOTTOM = 4
    default_height = 30
    default_showHilite = False

    def ApplyAttributes(self, attributes):
        super(SkillInjectorBanner, self).ApplyAttributes(attributes)
        self.Layout()
        self.Load()
        sm.RegisterNotify(self)

    def Close(self):
        super(SkillInjectorBanner, self).Close()
        sm.UnregisterNotify(self)

    def Layout(self):
        RaisedUnderlay(bgParent=self)
        topCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT, top=4)
        Icon(parent=topCont, align=uiconst.TOPLEFT, top=4, left=4, typeID=invconst.typeSkillInjector, size=32, state=uiconst.UI_DISABLED)
        EveLabelMedium(parent=topCont, align=uiconst.TOPLEFT, top=4, left=40, text=evetypes.GetName(invconst.typeSkillInjector))
        self.priceLabel = EveLabelMedium(parent=topCont, align=uiconst.TOPLEFT, top=18, left=40, color=Color.GRAY4)
        InfoIcon(parent=topCont, align=uiconst.CENTERRIGHT, left=4, typeID=invconst.typeSkillInjector)
        ShowMarketDetailsButton(parent=topCont, align=uiconst.CENTERRIGHT, left=24, width=16, height=16, typeID=invconst.typeSkillInjector)
        textCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(8, 4, 8, 4))
        self.mainLabel = EveLabelMedium(parent=textCont, align=uiconst.TOTOP)
        bottomCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, padding=(0, 0, 4, 4))
        Button(parent=bottomCont, align=uiconst.TOPRIGHT, label=localization.GetByLabel('UI/SkillTrading/Dismiss'), func=self.Dismiss)

    def Load(self):
        freePoints = sm.GetService('skills').GetFreeSkillPoints()
        if freePoints:
            self.HideImmediately()
        else:
            self._UpdateEstimatedInjectorPrice()
            self._UpdateMainText()

    def Update(self):
        freePoints = sm.GetService('skills').GetFreeSkillPoints()
        if freePoints:
            uthread.new(self.AnimHide)
        else:
            self._UpdateEstimatedInjectorPrice()
            self._UpdateMainText()
            uthread.new(self.AnimShow)

    def _UpdateEstimatedInjectorPrice(self):
        price = inventorycommon.typeHelpers.GetAveragePrice(invconst.typeSkillInjector)
        if price is None or price <= 0:
            price = localization.GetByLabel('UI/Common/Unknown')
        else:
            price = FmtISKAndRound(price, False)
        text = localization.GetByLabel('UI/SkillTrading/EstimatedPrice', price=price)
        self.priceLabel.SetText(text)

    def _UpdateMainText(self):
        injector = invconst.typeSkillInjector
        points = sm.GetService('skills').GetSkillPointAmountFromInjectors(quantity=1)
        color = Color.RGBtoHex(1.0, 0.8, 0.0, 1.0)
        text = localization.GetByLabel('UI/SkillTrading/InjectorBannerMainText', injector=injector, points=points, color=color)
        self.mainLabel.SetText(text)

    def Dismiss(self, button):
        button.Disable()
        SetSkillInjectorBannerDismissed()
        self.AnimHide()

    def AnimHide(self):
        for child in self.children:
            animations.FadeOut(child, duration=0.3)

        self.DisableAutoSize()
        animations.MorphScalar(self, 'height', startVal=self.height, endVal=0, timeOffset=0.1, duration=0.3)
        animations.MorphScalar(self, 'padTop', startVal=self.padTop, endVal=0, timeOffset=0.1, duration=0.3)
        animations.MorphScalar(self, 'padBottom', startVal=self.padBottom, endVal=0, timeOffset=0.1, duration=0.3)

    def AnimShow(self):
        for child in self.children:
            animations.FadeIn(child, duration=0.3, timeOffset=0.1)

        self.EnableAutoSize()
        self.DisableAutoSize()
        animations.MorphScalar(self, 'height', startVal=0, endVal=self.height, duration=0.3)
        animations.MorphScalar(self, 'padTop', startVal=0, endVal=self.PAD_TOP, duration=0.3)
        animations.MorphScalar(self, 'padBottom', startVal=0, endVal=self.PAD_BOTTOM, duration=0.3, sleep=True)
        self.EnableAutoSize()

    def HideImmediately(self):
        for child in self.children:
            child.opacity = 0.0

        self.DisableAutoSize()
        self.height = 0
        self.padTop = 0
        self.padBottom = 0

    def OnFreeSkillPointsChanged_Local(self):
        self.Update()


BANNER_DISMISSED_KEY = 'skillInjectorBanner_dismissed'
BANNER_DISMISSED_DEFAULT = False

def IsSkillInjectorBannerDismissed():
    return settings.user.ui.Get(BANNER_DISMISSED_KEY, BANNER_DISMISSED_DEFAULT)


def SetSkillInjectorBannerDismissed(dismissed = True):
    settings.user.ui.Set(BANNER_DISMISSED_KEY, dismissed)
