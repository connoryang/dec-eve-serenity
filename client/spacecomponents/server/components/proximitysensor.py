#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\proximitysensor.py
from ballpark.messenger.const import MESSAGE_ON_PROXIMITY
from ccpProfile import TimedFunction
from spacecomponents.common.components.component import Component
from spacecomponents.server.messages import MSG_ON_ADDED_TO_SPACE

class ProximitySensor(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        super(ProximitySensor, self).__init__(itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)

    def OnAddedToSpace(self, ballpark, _):
        self.SetBallpark(ballpark)
        ballpark.proximityRegistry.RegisterForProximity(self.itemID, self.attributes.detectionRange, self.OnProximity)

    def OnProximity(self, ballId, isEntering):
        self.ballpark.eventMessenger.SendMessage(self.itemID, MESSAGE_ON_PROXIMITY, ballId, isEntering)

    @TimedFunction('ProximitySensor::GetBallIdsInRange')
    def GetBallIdsInRange(self):
        ballIds = []
        for ballId in self.ballpark.GetBallIdsInRange(self.itemID, self.attributes.detectionRange):
            if ballId <= 0:
                continue
            ballIds.append(ballId)

        return ballIds

    def GetBubbleId(self):
        return self.ballpark.GetBall(self.itemID).newBubbleId

    def SetBallpark(self, ballpark):
        self.ballpark = ballpark
