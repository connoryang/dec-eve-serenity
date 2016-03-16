#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\monetization\multiTrainingOverlay.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import CONTENT_ALIGN_CENTER, FlowContainer
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelLargeBold, EveLabelMedium
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.shared.monetization.events import LogMultiPilotTrainingOpenAurOffer, LogMultiPilotTrainingOpenIskOffer
from eve.client.script.ui.shared.vgs.button import BuyButtonAur, BuyButtonIsk
from eve.common.script.util.eveFormat import RoundISK
import evetypes
from inventorycommon.const import typeMultiTrainingToken
from inventorycommon.typeHelpers import GetAveragePrice
import localization

class MultiTrainingOverlay(Container):
    SUPPRESS_KEY = 'suppress.MultiplePilotTrainingPromotion'
    CONTENT_LEFT = 140
    CHARACTERS_LEFT = -180
    default_align = uiconst.TOALL
    default_clipChildren = True
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        super(MultiTrainingOverlay, self).ApplyAttributes(attributes)
        self.Layout()

    def Layout(self):
        self.compactMode = False
        Frame(bgParent=self, texturePath='res:/UI/Texture/classes/Monetization/vignette.png', cornerSize=150)
        self.characters = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, left=self.CHARACTERS_LEFT, top=10, texturePath='res:/UI/Texture/classes/Monetization/characters.png', width=299, height=355)
        self.content = ContainerAutoSize(parent=self, align=uiconst.CENTER, left=self.CONTENT_LEFT, width=340)
        EveCaptionLarge(parent=self.content, align=uiconst.TOTOP, text=localization.GetByLabel('UI/SkillQueue/MultiTrainingOverlay/MultiplePilotTraining'))
        EveLabelMedium(parent=self.content, align=uiconst.TOTOP, top=4, text=localization.GetByLabel('UI/SkillQueue/MultiTrainingOverlay/MultiTrainingMessageTop'))
        itemCont = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, top=12)
        Frame(bgParent=itemCont, texturePath='res:/UI/Texture/classes/Monetization/item_well_frame.png', cornerSize=2)
        itemIconCont = ContainerAutoSize(parent=itemCont, align=uiconst.TOLEFT, padding=(8, 8, 0, 8))
        Icon(parent=itemIconCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, size=64, typeID=typeMultiTrainingToken)
        Sprite(parent=itemIconCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/InvItem/bgNormal.png', width=64, height=64)
        EveLabelLargeBold(parent=itemCont, align=uiconst.TOTOP, padding=(8, 8, 24, 0), text=evetypes.GetName(typeMultiTrainingToken))
        InfoIcon(parent=itemCont, align=uiconst.TOPRIGHT, top=8, left=8, typeID=typeMultiTrainingToken)
        self.estimatePriceLabel = EveLabelMedium(parent=itemCont, align=uiconst.TOTOP, padding=(8, 0, 8, 6), color=Color.GRAY5)
        buyButtonCont = FlowContainer(parent=itemCont, align=uiconst.TOTOP, padding=(8, 0, 8, 8), contentSpacing=(8, 0))
        MultiTrainingBuyButtonIsk(parent=buyButtonCont, align=uiconst.NOALIGN, typeID=typeMultiTrainingToken)
        MultiTrainingBuyButtonAur(parent=buyButtonCont, align=uiconst.NOALIGN, types=[typeMultiTrainingToken])
        EveLabelMedium(parent=self.content, align=uiconst.TOTOP, top=12, text=localization.GetByLabel('UI/SkillQueue/MultiTrainingOverlay/MultiTrainingMessageBottom'))
        dismissCont = FlowContainer(parent=self.content, align=uiconst.TOTOP, padding=(8, 24, 8, 0), contentAlignment=CONTENT_ALIGN_CENTER, contentSpacing=(8, 4))
        Button(parent=dismissCont, align=uiconst.NOALIGN, label=localization.GetByLabel('UI/SkillQueue/MultiTrainingOverlay/Dismiss'), func=lambda *args: self.Dismiss())
        self.suppressCheckbox = Checkbox(parent=dismissCont, align=uiconst.NOALIGN, width=200, text=localization.GetByLabel('UI/Common/SuppressionShowMessage'), checked=self.suppressed, callback=self.OnSuppressChanged)

    def OnSuppressChanged(self, checkbox):
        self.suppressed = self.suppressCheckbox.GetValue()

    @property
    def suppressed(self):
        return settings.user.suppress.Get(self.SUPPRESS_KEY, False)

    @suppressed.setter
    def suppressed(self, suppressed):
        if suppressed:
            settings.user.suppress.Set(self.SUPPRESS_KEY, suppressed)
        else:
            settings.user.suppress.Delete(self.SUPPRESS_KEY)
        sm.GetService('settings').SaveSettings()

    def ShouldDisplay(self):
        if self.suppressed:
            return False
        if sm.GetService('skillqueue').SkillInTraining() is not None:
            return False
        queues = sm.GetService('skillqueue').GetMultipleCharacterTraining().items()
        characterData = sm.GetService('cc').GetCharacterSelectionData()
        activeQueues = 1 + len(queues)
        usedQueues = 0
        for characterDetails in characterData.details.values():
            isTraining = characterDetails.GetSkillInTrainingInfo()['currentSkill'] is not None
            if characterDetails.charID != session.charid and isTraining:
                usedQueues += 1

        return usedQueues == activeQueues

    def Display(self):
        self.Load()
        self.Enable()
        self.AnimShow()

    def Load(self):
        self.UpdateEstimatedPrice()
        self.suppressCheckbox.SetValue(self.suppressed)

    def UpdateEstimatedPrice(self):
        try:
            tokenAveragePrice = GetAveragePrice(typeMultiTrainingToken)
        except KeyError:
            tokenAveragePrice = None

        if not tokenAveragePrice:
            text = localization.GetByLabel('UI/SkillQueue/MultiTrainingOverlay/EstimatedPriceUnknown')
        else:
            amount = RoundISK(tokenAveragePrice)
            text = localization.GetByLabel('UI/SkillQueue/MultiTrainingOverlay/EstimatedPrice', amount=amount)
        self.estimatePriceLabel.SetText(text)

    def Dismiss(self):
        self.Disable()
        self.AnimHide()

    def AnimShow(self):
        self.Show()
        animations.FadeTo(self, duration=0.4)
        if not self.compactMode:
            animations.FadeTo(self.characters, timeOffset=0.3)
        animations.FadeTo(self.content, timeOffset=0.3)

    def AnimHide(self):
        animations.FadeOut(self, duration=0.4)

    def EnterCompactMode(self):
        if self.compactMode:
            return
        self.compactMode = True
        animations.FadeOut(self.characters, duration=0.2)
        animations.MorphScalar(self.characters, 'left', startVal=self.characters.left, endVal=self.CHARACTERS_LEFT - 60, duration=0.3)
        animations.MorphScalar(self.content, 'left', startVal=self.content.left, endVal=0, duration=0.3)

    def ExitCompactMode(self):
        if not self.compactMode:
            return
        self.compactMode = False
        animations.FadeIn(self.characters, duration=0.2)
        animations.MorphScalar(self.characters, 'left', startVal=self.characters.left, endVal=self.CHARACTERS_LEFT, duration=0.3)
        animations.MorphScalar(self.content, 'left', startVal=self.content.left, endVal=self.CONTENT_LEFT, duration=0.3)

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        if budgetWidth < 640:
            self.EnterCompactMode()
        else:
            self.ExitCompactMode()
        return super(MultiTrainingOverlay, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)


class MultiTrainingBuyButtonIsk(BuyButtonIsk):

    def OpenMarketWindow(self):
        super(MultiTrainingBuyButtonIsk, self).OpenMarketWindow()
        LogMultiPilotTrainingOpenIskOffer()


class MultiTrainingBuyButtonAur(BuyButtonAur):

    def OpenOfferWindow(self):
        super(MultiTrainingBuyButtonAur, self).OpenOfferWindow()
        LogMultiPilotTrainingOpenAurOffer()
