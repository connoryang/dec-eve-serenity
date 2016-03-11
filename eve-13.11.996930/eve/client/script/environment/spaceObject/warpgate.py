#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\warpgate.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject

class WarpGate(SpaceObject):

    def Assemble(self):
        self.SetStaticDirection()
        self.SetupAmbientAudio()
