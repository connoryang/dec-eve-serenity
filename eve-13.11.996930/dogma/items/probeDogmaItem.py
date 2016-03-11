#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\probeDogmaItem.py
from baseDogmaItem import BaseDogmaItem
from ccpProfile import TimedFunction
from eve.common.script.sys.idCheckers import IsSolarSystem

class ProbeDogmaItem(BaseDogmaItem):

    @TimedFunction('ProbeDogmaItem::Load')
    def Load(self, item, instanceRow):
        super(ProbeDogmaItem, self).Load(item, instanceRow)
        self.ownerID = item.ownerID

    def IsOwnerModifiable(self, locationID = None):
        if boot.role == 'client':
            return True
        if not locationID:
            locationID = self.locationID
        if IsSolarSystem(locationID):
            return True
        return False
