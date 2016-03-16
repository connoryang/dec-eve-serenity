#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\cleanShipButton.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.buttons import Button
from carbonui import const as uiconst
from eve.common.script.net import eveMoniker
from localization import GetByLabel

class CleanShipButton(Container):
    default_padLeft = 6
    default_padTop = 6
    default_padRight = 6
    default_padBottom = 6
    default_height = 18

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.AddButton()

    def AddButton(self):
        self.cleanButton = Button(label=GetByLabel('UI/Fitting/FittingWindow/CleanShip'), parent=self, align=uiconst.CENTER, func=self.CleanShip)

    def CleanShip(self, *args):
        shipID = self.controller.GetItemID()
        newDirtTimestamp = eveMoniker.GetShipAccess().ResetDirtTimestamp(shipID)
        print 'Ship cleaned! New dirt timestamp for ship %s is %s' % (shipID, newDirtTimestamp)
