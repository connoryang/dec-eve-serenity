#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\behavior.py
from spacecomponents.common.components.component import Component
import logging
from spacecomponents.server import messages
logger = logging.getLogger(__name__)

class Behavior(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        logger.debug('Adding a behavior to %s of type %s', itemID, typeID)
        self.SubscribeToMessage(messages.MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(messages.MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)

    def OnAddedToSpace(self, ballpark, spaceComponentDB):
        self.UThreadNew(self.TryRegisterBehavior, ballpark.solarsystemID)

    def TryRegisterBehavior(self, solarsystemID):
        try:
            entityLocation = sm.GetService('entity').GetEntityLocation(solarsystemID)
            entityLocation.RegisterBehaviorComponent(self)
            logger.debug('Registered behavior %s for item %s', self.attributes.behaviorName, self.itemID)
        except:
            logger.exception('Failed while trying to register behavior')

    def OnRemovedFromSpace(self, ballpark, spaceComponentDB):
        entityLocation = sm.GetService('entity').GetEntityLocation(ballpark.solarsystemID)
        entityLocation.RemoveBehaviorComponent(self)
