#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\station.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
import evegraphics.utils as gfxutils

class Station(SpaceObject):

    def GetDNA(self):
        materialSetID = self.typeData.get('slimItem').skinMaterialSetID
        return gfxutils.BuildSOFDNAFromGraphicID(self.typeData.get('graphicID'), materialSetID=materialSetID)

    def Assemble(self):
        if hasattr(self.model, 'ChainAnimationEx'):
            self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        self.SetupAmbientAudio()
