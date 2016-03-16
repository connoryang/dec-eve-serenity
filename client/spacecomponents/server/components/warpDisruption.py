#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\warpDisruption.py
from spacecomponents.common.components.component import Component
from spacecomponents.server.messages import MSG_ON_ACTIVE, MSG_ON_REMOVED_FROM_SPACE
from spacecomponents.common.componentConst import WARP_DISRUPTION_CLASS

class WarpDisruption(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.warpDisruptionRange = attributes.warpDisruptionRange
        self.SubscribeToMessage(MSG_ON_ACTIVE, self.OnActive)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)
        self.addedWarpDisruptor = False

    def OnActive(self, ballpark):
        ballpark.warpDisruptProbeTracker.AddWarpDisruptProbe(self.itemID)
        self.addedWarpDisruptor = True

    def OnRemovedFromSpace(self, ballpark, dbspacecomponent):
        if self.addedWarpDisruptor:
            ballpark.warpDisruptProbeTracker.RemoveWarpDisruptProbe(self.itemID)

    @staticmethod
    def GetEspTypeInfo(typeID, spaceComponentStaticData):
        attributes = spaceComponentStaticData.GetAttributes(typeID, WARP_DISRUPTION_CLASS)
        attributeStrings = []
        attributeStrings.append('Warp Disruption Range: %d meters' % attributes.warpDisruptionRange)
        infoString = '<br>'.join(attributeStrings)
        return infoString
