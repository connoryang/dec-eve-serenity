#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\dogma\clientDogmaIM.py
import service
import util
import uthread
from clientDogmaLocation import DogmaLocation

class ClientDogmaInstanceManager(service.Service):
    __guid__ = 'svc.clientDogmaIM'
    __startupdependencies__ = ['clientEffectCompiler', 'invCache', 'godma']
    __notifyevents__ = ['ProcessSessionChange']

    def Run(self, *args):
        service.Service.Run(self, *args)
        self.dogmaLocation = None
        self.fittingDogmaLocation = None
        self.nextKey = 0
        self.shipIDBeingActivated = None

    def GetDogmaLocation(self, charBrain = None, *args):
        uthread.Lock('GetDogmaLocation')
        try:
            if self.dogmaLocation is None:
                self.dogmaLocation = DogmaLocation(self, charBrain)
                self.LogInfo('Created client dogmaLocation', id(self.dogmaLocation))
        finally:
            uthread.UnLock('GetDogmaLocation')

        return self.dogmaLocation

    def GetFittingDogmaLocation(self, force = False, *args):
        uthread.Lock('GetFittingDogmaLocation')
        try:
            if self.fittingDogmaLocation is None or force:
                from eve.client.script.ui.shared.fittingGhost.fittingDogmaLocation import FittingDogmaLocation
                self.fittingDogmaLocation = FittingDogmaLocation(self)
                self.LogInfo('Created client fittingDogmaLocation', id(self.fittingDogmaLocation))
        finally:
            uthread.UnLock('GetFittingDogmaLocation')

        return self.fittingDogmaLocation

    def GodmaItemChanged(self, item, change):
        if item.itemID == session.charid:
            return
        if self.dogmaLocation is not None:
            shipID = self.dogmaLocation.GetCurrentShipID()
            disembarkingID = self.dogmaLocation.shipIDBeingDisembarked
            if item.locationID == shipID:
                self.dogmaLocation.OnItemChange(item, change)
            elif change.get(const.ixLocationID, None) == shipID:
                self.dogmaLocation.OnItemChange(item, change)
            elif item.itemID == shipID and session.stationid2 is not None and item.itemID != disembarkingID:
                if item.locationID != session.stationid or item.flagID != const.flagHangar:
                    if util.IsWorldSpace(item.locationID) or util.IsSolarSystem(item.locationID):
                        self.LogInfo('ActiveShip moved as we are undocking. Ignoring')
                    elif util.IsStation(item.locationID) and item.flagID == const.flagHangar and item.ownerID == session.charid:
                        self.LogInfo("Active ship moved stations but is still in it's hangar", item, change, session.stationid)
                    else:
                        sm.GetService('station').TryLeaveShip(item)
                        self.dogmaLocation.UnboardShip(session.charid)
                        self.LogError('Our active ship got moved', item, change)

    def ProcessSessionChange(self, isRemote, session, change):
        if self.dogmaLocation is None:
            return
        if 'stationid2' in change or 'solarsystemid' in change:
            self.dogmaLocation.UpdateRemoteDogmaLocation()

    def GetCapacityForItem(self, itemID, attributeID):
        if self.dogmaLocation is None:
            return
        if not self.dogmaLocation.IsItemLoaded(itemID):
            return
        return self.dogmaLocation.GetAttributeValue(itemID, attributeID)
