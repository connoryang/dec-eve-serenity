#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\cynoInhibitor.py
from spacecomponents.server.messages import MSG_ON_ADDED_TO_SPACE
from spacecomponents.common.componentConst import CYNO_INHIBITOR_CLASS

class CynoInhibitor(object):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        self.itemID = itemID
        self.typeID = typeID
        self.attributes = attributes
        self.componentRegistry = componentRegistry
        self.componentRegistry.SubscribeToItemMessage(itemID, MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.bubbleID = None

    def OnAddedToSpace(self, ballpark, spaceComponentDB):
        self.bubbleID = ballpark.GetBall(self.itemID).newBubbleId

    def IsBallWithinCynoInhibitorRange(self, ballID, ballpark):
        if self.bubbleID is not None and self.bubbleID == ballpark.GetBall(ballID).newBubbleId:
            return ballpark.GetSurfaceDist(ballID, self.itemID) < self.attributes.range
        return False

    @staticmethod
    def GetEspTypeInfo(typeID, spaceComponentStaticData):
        attributes = spaceComponentStaticData.GetAttributes(typeID, CYNO_INHIBITOR_CLASS)
        attributeStrings = []
        attributeStrings.append('Range: %d m' % attributes.range)
        infoString = '<br>'.join(attributeStrings)
        return infoString
