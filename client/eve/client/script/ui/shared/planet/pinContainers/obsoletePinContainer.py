#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\planet\pinContainers\obsoletePinContainer.py
import evetypes
import util
import localization
from .BasePinContainer import BasePinContainer
from .. import planetCommon

class ObsoletePinContainer(BasePinContainer):
    __guid__ = 'planet.ui.ObsoletePinContainer'

    def _GetActionButtons(self):
        btns = [util.KeyVal(id=planetCommon.PANEL_DECOMMISSION, panelCallback=self.PanelDecommissionPin, hint=localization.GetByLabel('UI/PI/Common/ObsoletePinReimbursementHint', pinName=evetypes.GetName(self.pin.typeID), iskAmount=util.FmtISK(evetypes.GetBasePrice(self.pin.typeID))))]
        return btns
