#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\mocks\mockDogmaItem.py
from collections import defaultdict

class MockDogmaItem(object):

    def __init__(self, dogmaLocation, item, attributes = {}):
        dogmaLocation.dogmaItems[item.itemID] = self
        self.invItem = item
        self.itemID = item.itemID
        self.typeID = item.typeID
        self.groupID = item.groupID
        self.ownedItems = set()
        self.ownerID = item.ownerID
        self.owner = None
        self.pilotID = None
        if item.ownerID in dogmaLocation.dogmaItems:
            ownerItem = dogmaLocation.dogmaItems[item.ownerID]
            self.owner = ownerItem
            ownerItem.ownedItems.add(self)
        self.subItems = set()
        self.location = dogmaLocation.dogmaItems[item.locationID]
        self.location.subItems.add(self)
        self.attributes = attributes
        self.locationMods = defaultdict(set)
        self.locationGroupMods = defaultdict(lambda : defaultdict(set))
        self.locationReqSkillMods = defaultdict(lambda : defaultdict(set))
        self.ownerReqSkillMods = defaultdict(lambda : defaultdict(set))
        self.reqSkills = dogmaLocation.dogmaStaticMgr.GetRequiredSkills(item.typeID)

    def SetPilot(self, pilotID):
        self.pilotID = pilotID

    def GetPilot(self):
        return self.pilotID

    def GetLocation(self):
        return self.location
