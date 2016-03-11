#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\common\components\component.py


class Component(object):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        self.itemID = itemID
        self.typeID = typeID
        self.attributes = attributes
        self.componentRegistry = componentRegistry
        self.GetSimTime = componentRegistry.asyncFuncs.GetSimTime
        self.SleepSim = componentRegistry.asyncFuncs.SleepSim
        self.GetWallclockTime = componentRegistry.asyncFuncs.GetWallclockTime
        self.SleepWallclock = componentRegistry.asyncFuncs.SleepWallclock
        self.TimeDiffInMs = componentRegistry.asyncFuncs.TimeDiffInMs
        self.UThreadNew = componentRegistry.asyncFuncs.UThreadNew

    def SubscribeToMessage(self, messageName, messageHandler):
        self.componentRegistry.SubscribeToItemMessage(self.itemID, messageName, messageHandler)

    def UnsubscribeFromMessage(self, messageName, messageHandler):
        self.componentRegistry.UnsubscribeFromItemMessage(self.itemID, messageName, messageHandler)

    def SendMessage(self, messageName, *args, **kwargs):
        self.componentRegistry.SendMessageToItem(self.itemID, messageName, *args, **kwargs)
