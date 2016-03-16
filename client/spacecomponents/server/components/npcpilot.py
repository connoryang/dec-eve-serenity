#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\npcpilot.py
from spacecomponents.common.components.component import Component
import logging
from spacecomponents.server import messages
import random
logger = logging.getLogger(__name__)

class NpcPilot(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(messages.MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)

    def OnAddedToSpace(self, ballpark, _):
        charID = random.choice(self.attributes.characterIds.keys())
        ballpark.UpdateSlimItemField(self.itemID, 'charID', charID)
