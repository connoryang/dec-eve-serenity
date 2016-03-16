#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\industry\blueprintSvc.py
import blue
import evetypes
import util
import const
import service
import telemetry
import industry
from eve.common.script.util import industryCommon
import eve.client.script.industry.mixins

class BlueprintService(service.Service):
    __guid__ = 'svc.blueprintSvc'
    __servicename__ = 'Blueprint'
    __displayname__ = 'Blueprint Service'
    __notifyevents__ = ['OnBlueprintsUpdated', 'OnSessionChanged', 'OnIndustryJob']

    def Run(self, *args, **kwargs):
        service.Service.Run(self, *args, **kwargs)
        self.blueprintManager = sm.RemoteSvc('blueprintManager')

    def OnBlueprintsUpdated(self, ownerID):
        objectCaching = sm.GetService('objectCaching')
        keys = [ key for key in objectCaching.cachedMethodCalls if key[:3] == ('blueprintManager', 'GetBlueprintDataByOwner', ownerID) ]
        objectCaching.InvalidateCachedObjects(keys)
        sm.ScatterEvent('OnBlueprintReload', ownerID)

    def OnIndustryJob(self, jobID, ownerID, blueprintID, installerID, status, successfulRuns):
        objectCaching = sm.GetService('objectCaching')
        keys = [ key for key in objectCaching.cachedMethodCalls if key[:3] == ('blueprintManager', 'GetBlueprintDataByOwner', ownerID) ]
        for key in keys:
            blueprints, facilities = objectCaching.cachedMethodCalls[key]['lret']
            for blueprint in blueprints:
                if blueprint.itemID == blueprintID:
                    if status < industry.STATUS_COMPLETED:
                        blueprint.jobID = jobID
                    else:
                        blueprint.jobID = None

    def OnSessionChanged(self, isRemote, session, change):
        if 'corprole' in change:
            self.OnBlueprintsUpdated(session.corpid)

    @telemetry.ZONE_METHOD
    def GetBlueprintType(self, blueprintTypeID, isCopy = False):
        try:
            ret = cfg.blueprints[blueprintTypeID]
            if isCopy or evetypes.GetCategoryID(blueprintTypeID) == const.categoryAncientRelic:
                ret = ret.copy()
                ret.original = False
            return ret
        except KeyError:
            raise UserError('IndustryBlueprintNotFound')

    def GetBlueprintTypeCopy(self, typeID, original = True, runsRemaining = None, materialEfficiency = None, timeEfficiency = None):
        bpData = self.GetBlueprintType(typeID).copy()
        bpData.original = original and evetypes.GetCategoryID(typeID) != const.categoryAncientRelic
        if runsRemaining is not None:
            bpData.runsRemaining = runsRemaining
        if materialEfficiency is not None:
            bpData.materialEfficiency = materialEfficiency
        if timeEfficiency is not None:
            bpData.timeEfficiency = timeEfficiency
        return bpData

    @telemetry.ZONE_METHOD
    def GetBlueprintItem(self, blueprintID):
        return industryCommon.BlueprintInstance(self.blueprintManager.GetBlueprintData(blueprintID))

    def GetBlueprint(self, blueprintID, blueprintTypeID, isCopy = False):
        try:
            return self.GetBlueprintItem(blueprintID)
        except UserError:
            return self.GetBlueprintType(blueprintTypeID, isCopy=isCopy)

    def GetBlueprintByProduct(self, productTypeID):
        try:
            return cfg.blueprints.index('productTypeID', productTypeID)
        except KeyError:
            return None

    @telemetry.ZONE_METHOD
    def GetOwnerBlueprints(self, ownerID, facilityID = None):
        blueprints = []
        locations = set()
        rows, facilities = self.blueprintManager.GetBlueprintDataByOwner(ownerID, facilityID)
        for data in rows:
            try:
                blueprint = industryCommon.BlueprintInstance(data)
                blueprints.append(blueprint)
                locations.add(blueprint.locationID)
                locations.add(blueprint.facilityID)
                blue.pyos.BeNice()
            except KeyError:
                self.LogError('Unable to load blueprint instance: ', data)

        cfg.evelocations.Prime(locations)
        facilitySvc = sm.GetService('facilitySvc')
        for blueprint in blueprints:
            try:
                blueprint.facility = facilitySvc.GetFacility(blueprint.facilityID)
                blue.pyos.BeNice()
            except KeyError:
                pass

        return (blueprints, facilities)

    def GetCharacterBlueprints(self, facilityID = None):
        return self.GetOwnerBlueprints(session.charid, facilityID)

    def GetCorporationBlueprints(self, facilityID = None):
        return self.GetOwnerBlueprints(session.corpid, facilityID)

    def CanSeeCorpBlueprints(self):
        if util.IsNPC(session.corpid):
            return False
        return session.corprole & (const.corpRoleCanRentResearchSlot | const.corpRoleFactoryManager | const.corpRoleCanRentFactorySlot) > 0
