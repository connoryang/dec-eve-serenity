#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\world\worldSpaceScene.py
from carbon.common.script.world.worldSpaceCommon import WorldSpace

class WorldSpaceScene(WorldSpace):
    __guid__ = 'world.CoreWorldSpaceScene'

    def __init__(self, worldSpaceID = None, instanceID = None):
        WorldSpace.__init__(self, worldSpaceID, instanceID)
        self.properties = {}

    def LoadProperties(self):
        pass
