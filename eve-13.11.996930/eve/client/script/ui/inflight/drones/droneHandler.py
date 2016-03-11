#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\drones\droneHandler.py
import uthread
import blue

class DroneHandler(object):
    __notifyevents__ = ['OnItemChange',
     'OnRepairDone',
     'OnDamageStateChange',
     'OnDroneControlLost']

    def __init__(self):
        self.droneDamageStatesByDroneIDs = {}
        sm.RegisterNotify(self)
        self.fetchingInfoForDrones = set()
        self.clearTimestamp = None
        self.dogmaLM = sm.GetService('godma').GetDogmaLM()

    def FetchInBayDroneDamageToServer(self, droneIDs):
        droneIDsMissingDamage = self.FindDronesMissingDamageState(droneIDs)
        if not droneIDsMissingDamage:
            return
        self.fetchingInfoForDrones.update(droneIDsMissingDamage)
        callMadeTime = blue.os.GetSimTime()
        damageStateForDrones = self.dogmaLM.GetDamageStateItems(droneIDsMissingDamage)
        if not self.HasDictBeenClearedAfterCall(callMadeTime):
            damageStateDict = ConvertDroneStateToCorrectFormat(damageStateForDrones)
            self.droneDamageStatesByDroneIDs.update(damageStateDict)
        self.fetchingInfoForDrones.difference_update(droneIDsMissingDamage)

    def FindDronesMissingDamageState(self, droneIDs):
        droneIDsMissingDamage = {x for x in droneIDs if x not in self.droneDamageStatesByDroneIDs}
        return droneIDsMissingDamage - self.fetchingInfoForDrones

    def HasDictBeenClearedAfterCall(self, callMadeTime):
        if self.clearTimestamp and self.clearTimestamp > callMadeTime:
            return True
        else:
            return False

    def GetDamageStateForDrone(self, droneID):
        if self.IsDroneDamageReady(droneID):
            return self.droneDamageStatesByDroneIDs.get(droneID, None)
        droneIDsMissingDamage = self.FindDronesMissingDamageState([droneID])
        if droneIDsMissingDamage:
            uthread.new(self.FetchInBayDroneDamageToServer, droneIDsMissingDamage)
        return -1

    def IsDroneDamageReady(self, droneID):
        return droneID in self.droneDamageStatesByDroneIDs

    def OnItemChange(self, change, *args):
        if change.itemID not in self.droneDamageStatesByDroneIDs:
            return
        if change.flagID not in (const.flagDroneBay, const.flagNone):
            del self.droneDamageStatesByDroneIDs[change.itemID]

    def OnDroneControlLost(self, droneID):
        self.droneDamageStatesByDroneIDs.pop(droneID, None)

    def OnRepairDone(self, itemIDs, *args):
        for itemID in itemIDs:
            self.droneDamageStatesByDroneIDs.pop(itemID, None)

    def OnDamageStateChange(self, itemID, damageState):
        droneDamageInfo = self.droneDamageStatesByDroneIDs.get(itemID, None)
        if droneDamageInfo is None:
            return
        timestamp = blue.os.GetSimTime()
        droneDamageInfo.UpdateInfo(timestamp, damageState)


def ConvertDroneStateToCorrectFormat(damageStateForDrones):
    newDroneDamageDict = {}
    for itemID, ds in damageStateForDrones.iteritems():
        shieldInfo = ds[0]
        shieldDamage = shieldInfo[0]
        shieldHp = shieldInfo[1]
        timestamp = shieldInfo[2]
        d = DroneDamageClass(itemID, shieldHp, timestamp, shieldDamage, ds[1], ds[2])
        newDroneDamageDict[itemID] = d

    return newDroneDamageDict


class DroneDamageClass:

    def __init__(self, itemID, shieldHp, timestamp, shieldDamage, armorDamage, hullDamage):
        self.itemID = itemID
        self.shieldHp = shieldHp
        self.timestamp = timestamp
        self.shieldDamage = shieldDamage
        self.armorDamage = armorDamage
        self.hullDamage = hullDamage

    def UpdateInfo(self, timestamp, damageValues):
        self.timestamp = timestamp
        self.shieldDamage = damageValues[0]
        self.armorDamage = damageValues[1]
        self.hullDamage = damageValues[2]

    def GetInfoInMichelleFormat(self):
        return [(self.shieldDamage, self.shieldHp, self.timestamp), self.armorDamage, self.hullDamage]
