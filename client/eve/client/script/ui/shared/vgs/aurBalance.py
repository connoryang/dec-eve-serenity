#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\vgs\aurBalance.py
from carbon.common.script.util.format import FmtAmt
from carbonui import const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui.shared.vgs.button import VgsBuyAurButton
from eve.client.script.ui.shared.vgs.label import VgsHeaderMedium, VgsLabelSmall
import localization

class AurBalance(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(AurBalance, self).ApplyAttributes(attributes)
        account = attributes.account
        onClick = attributes.get('onClick', None)
        button = VgsBuyAurButton(parent=self, align=uiconst.TOPLEFT, onClick=onClick)
        walletLabel = VgsLabelSmall(parent=self, align=uiconst.TOPLEFT, top=-3, left=button.width + 4, text=localization.GetByLabel('UI/VirtualGoodsStore/AurBalance'), color=(1, 1, 1, 0.5))
        self.label = VgsHeaderMedium(parent=self, align=uiconst.TOPLEFT, top=walletLabel.height - 6, left=button.width + 4)
        self.balance = account.GetAurumBalance()
        account.SubscribeToAurumBalanceChanged(self.OnBalanceChange)

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        self._balance = value
        self.label.SetText(FmtAmt(self._balance))

    def OnBalanceChange(self, balance):

        def callback():
            self.balance = balance

        animations.MorphScalar(self, 'balance', startVal=self.balance, endVal=balance, curveType=uiconst.ANIM_SMOOTH, duration=1.5, callback=callback)
