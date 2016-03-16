#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\satellite.py
import uthread
import eve.common.lib.appConst as const
from eve.client.script.environment.spaceObject.LargeCollidableStructure import LargeCollidableStructure

class Satellite(LargeCollidableStructure):

    def Assemble(self):
        LargeCollidableStructure.Assemble(self)
        slimItem = self.typeData.get('slimItem')
        self.districtID = slimItem.districtID
        direction = self.FindClosestPlanetDir()
        self.AlignToDirection(direction)
        proximity = self.sm.GetService('godma').GetTypeAttribute(slimItem.typeID, const.attributeProximityRange)
        self.AddProximitySensor(proximity, 2, 0, False)

    def Release(self):
        LargeCollidableStructure.Release(self)
        uthread.new(self.sm.GetService('district').DisableDistrict, self.districtID)

    def DoProximity(self, violator, entered):
        if violator == session.shipid and getattr(self, 'districtID', None) is not None:
            if entered:
                uthread.new(self.sm.GetService('district').EnableDistrict, self.districtID)
            else:
                uthread.new(self.sm.GetService('district').DisableDistrict, self.districtID)
