#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\fitting.py
import logging
from spacecomponents.common.componentConst import REINFORCE_CLASS, FITTING_CLASS
from spacecomponents.common import helper
from spacecomponents.common.components.component import Component
logger = logging.getLogger(__name__)

class Fitting(Component):

    def CanUseFittingService(self, ballpark, shipID):
        if not self.CheckCorrectOwner(ballpark, shipID):
            return False
        if not self.CheckWithinRange(ballpark, shipID):
            return False
        if not helper.IsActiveComponent(self.componentRegistry, self.typeID, self.itemID):
            return False
        if not self.CheckReinforceComponent():
            return False
        return True

    def CheckCorrectOwner(self, ballpark, shipID):
        ownerID = ballpark.inventory2.GetItem(self.itemID).ownerID
        shipOwnerID = ballpark.inventory2.GetItem(shipID).ownerID
        return ownerID == shipOwnerID

    def CheckWithinRange(self, ballpark, shipID):
        fittingRange = self.attributes.range
        shipDistance = ballpark.GetSurfaceDist(shipID, self.itemID)
        return shipDistance <= fittingRange

    def CheckReinforceComponent(self):
        if helper.HasReinforceComponent(self.typeID):
            reinforceComponent = self.componentRegistry.GetComponentForItem(self.itemID, REINFORCE_CLASS)
            if reinforceComponent.isReinforced:
                return False
        return True

    @staticmethod
    def GetEspTypeInfo(typeID, spaceComponentStaticData):
        attributes = spaceComponentStaticData.GetAttributes(typeID, FITTING_CLASS)
        attributeStrings = []
        attributeStrings.append('Fitting range: %d m' % attributes.range)
        infoString = '<br>'.join(attributeStrings)
        return infoString
