#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\sovSvc.py
import blue
from collections import defaultdict
from brennivin.threadutils import expiring_memoize
from dogma.const import attributeSovBillSystemCost
from entosis.entosisConst import STRUCTURES_UPDATED
from eve.client.script.ui.shared.infoPanels.infoPanelConst import PANEL_LOCATION_INFO
from appConst import IHUB_BILLING_DURATION_DAYS
from eveexceptions.const import UE_AMT3
import evetypes
from entosis.occupancyCalculator import GetOccupancyMultiplier
from inventorycommon.const import typeTerritorialClaimUnit, typeInfrastructureHub, typeOutpostConstructionPlatform
from inventorycommon.util import IsWormholeSystem
import service
import form
import util
import moniker
import localization
from utillib import KeyVal
import carbonui.const as uiconst
CLAIM_DAYS_TO_SECONDS = 86400

class SovService(service.Service):
    __guid__ = 'svc.sov'
    __dependencies__ = ['audio']
    __startupdependencies__ = ['facwar']
    __notifyevents__ = ['ProcessSovStatusChanged',
     'OnSessionChanged',
     'OnSovereigntyAudioEvent',
     'OnSolarSystemSovStructuresUpdated',
     'OnSolarSystemDevIndexChanged']

    def __init__(self):
        service.Service.__init__(self)
        self.sovInfoBySystemID = {}
        self.devIndexMgr = None
        self.outpostData = None

    def Run(self, *args):
        service.Service.Run(self, *args)
        self.indexLevels = []
        for level in util.GetDevIndexLevels()[const.attributeDevIndexMilitary].itervalues():
            self.indexLevels.append(level.maxLevel)

        self.indexLevels.sort()
        self.holdTimeLevels = util.GetTimeIndexLevels()

    def GetInfrastructureHubWnd(self, hubID = None):
        form.InfrastructureHubWnd.CloseIfOpen()
        wnd = form.InfrastructureHubWnd.Open(hubID=hubID)
        return wnd

    def GetTimeIndexValuesInDays(self):
        return [ t / CLAIM_DAYS_TO_SECONDS for t in self.holdTimeLevels ]

    def ProcessSovStatusChanged(self, *args):
        solarSystemID, newStatus = args
        if newStatus is None and solarSystemID in self.sovInfoBySystemID:
            del self.sovInfoBySystemID[solarSystemID]
        else:
            self.sovInfoBySystemID[solarSystemID] = newStatus
        if solarSystemID == session.solarsystemid2:
            sm.ScatterEvent('OnSystemStatusChanged')

    def GetSystemSovereigntyInfo(self, solarSystemID, forceUpdate = False):
        if self.facwar.IsFacWarSystem(solarSystemID):
            return util.KeyVal(allianceID=self.facwar.GetSystemOccupier(solarSystemID), corporationID=None, claimStructureID=None, contested=0)
        if not forceUpdate and solarSystemID in self.sovInfoBySystemID:
            self.LogInfo('GetSystemSovereigntyInfo: Returning cached sov info', self.sovInfoBySystemID[solarSystemID])
            return self.sovInfoBySystemID[solarSystemID]
        status = sm.RemoteSvc('sovMgr').GetSystemSovereigntyInfo(solarSystemID)
        self.sovInfoBySystemID[solarSystemID] = status
        self.LogInfo('GetSystemSovereigntyInfo: Returning sov status from server:', status)
        return status

    def GetInfrastructureHubInfo(self, solarSystemID):
        return sm.RemoteSvc('sovMgr').GetInfrastructureHubInfo(solarSystemID)

    @expiring_memoize(15)
    def GetSovStructuresInfoForSolarSystem(self, solarsystemID):
        sovMgr = sm.RemoteSvc('sovMgr')
        if solarsystemID == session.solarsystemid2:
            solarSystemStructuresInfo = sovMgr.GetSovStructuresInfoForLocalSolarSystem()
        else:
            solarSystemStructuresInfo = sovMgr.GetSovStructuresInfoForSolarSystem(solarsystemID)
        self.ModifyStructureInfoIfNeeded(solarSystemStructuresInfo, solarsystemID)
        return solarSystemStructuresInfo

    def GetSpecificSovStructuresInfoInSolarSystem(self, solarsystemID, itemID):
        solarsystemStructureInfo = self.GetSovStructuresInfoForSolarSystem(solarsystemID)
        for structureInfo in solarsystemStructureInfo:
            if structureInfo.itemID == itemID:
                return structureInfo

    def ModifyStructureInfoIfNeeded(self, solarSystemStructuresInfo, solarsystemID):
        if solarSystemStructuresInfo is None:
            return
        for structureInfo in solarSystemStructuresInfo:
            structureInfo['solarSystemID'] = solarsystemID
            structureInfo['constellationID'] = cfg.mapSystemCache.Get(solarsystemID).constellationID

    def OnSolarSystemSovStructuresUpdated(self, solarsystemID, solarSystemStructuresInfo, changes = None):
        self.LogInfo('OnSolarSystemSovStructuresUpdated', solarsystemID, solarSystemStructuresInfo)
        self.ModifyStructureInfoIfNeeded(solarSystemStructuresInfo, solarsystemID)
        self.GetSovStructuresInfoForSolarSystem.prime_cache_result((self, solarsystemID), solarSystemStructuresInfo)
        if changes:
            for sourceItemID, whatChanged in changes.iteritems():
                sm.ScatterEvent('OnSolarsystemSovStructureChanged', solarsystemID, whatChanged, sourceItemID)

        else:
            sm.ScatterEvent('OnSolarsystemSovStructureChanged', solarsystemID, whatChanged=set([STRUCTURES_UPDATED]))

    def OnSolarSystemDevIndexChanged(self, solarsystemID):
        if solarsystemID == session.solarsystemid2:
            self.InvalidateCacheForGetDevelopmentIndicesForSystem(solarsystemID)
            locationPanel = self.GetLocationPanel()
            locationPanel.Update()

    def GetLocationPanel(self):
        infoPanelSvc = sm.GetService('infoPanel')
        locationPanel = infoPanelSvc.GetPanelByTypeID(PANEL_LOCATION_INFO)
        return locationPanel

    def GetContestedState(self, solarSystemID):
        return localization.GetByLabel('UI/Inflight/Brackets/SystemContested')

    def AddInfrastructureHubUpgrade(self, hubID, upgradeItemID, upgradeTypeID, sourceLocationID):
        godma = sm.GetService('godma')
        activationCost = IHUB_BILLING_DURATION_DAYS * godma.GetTypeAttribute(upgradeTypeID, attributeSovBillSystemCost, 0)
        if activationCost > 0:
            confirmationLabelName = 'SovConfirmUpgradeDropWithCharge'
            confirmationArgs = {'amount': (UE_AMT3, activationCost)}
        else:
            confirmationLabelName = 'SovConfirmUpgradeDrop'
            confirmationArgs = {}
        if eve.Message(confirmationLabelName, confirmationArgs, uiconst.YESNO) != uiconst.ID_YES:
            return
        inv = sm.GetService('invCache').GetInventoryFromId(hubID)
        inv.Add(upgradeItemID, sourceLocationID)

    def SetInfrastructureHubUpgradeOnline(self, hubID, upgradeItemID, upgradeTypeID):
        godma = sm.GetService('godma')
        activationCost = IHUB_BILLING_DURATION_DAYS * godma.GetTypeAttribute(upgradeTypeID, attributeSovBillSystemCost, 0)
        if activationCost > 0:
            confirmationLabelName = 'IHubConfirmOnlineUpgradeWithCharge'
            confirmationArgs = {'amount': (UE_AMT3, activationCost)}
            if eve.Message(confirmationLabelName, confirmationArgs, uiconst.YESNO) != uiconst.ID_YES:
                return
        iHubInv = sm.GetService('invCache').GetInventoryFromId(hubID)
        iHubInv.SetUpgradeOnline(upgradeItemID)

    def SetInfrastructureHubUpgradeOffline(self, hubID, upgradeItemID, upgradeTypeID):
        if eve.Message('IHubConfirmOfflineUpgrade', {}, uiconst.YESNO) != uiconst.ID_YES:
            return
        iHubInv = sm.GetService('invCache').GetInventoryFromId(hubID)
        iHubInv.SetUpgradeOffline(upgradeItemID)

    def GetKillLast24H(self, itemID):
        historyDB = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatKills, 24)
        systems = set(sm.GetService('map').IterateSolarSystemIDs(itemID))
        totalKills = 0
        totalPods = 0
        for stats in historyDB:
            if stats.solarSystemID in systems:
                kills = stats.value1 - stats.value2
                totalKills += kills
                totalPods += stats.value3

        return (totalKills, totalPods)

    def GetSovOwnerID(self):
        systemItem = sm.GetService('map').GetItem(session.solarsystemid2)
        solSovOwner = None
        if systemItem:
            solSovOwner = systemItem.factionID
            if solSovOwner is None:
                sovInfo = self.GetSystemSovereigntyInfo(session.solarsystemid2)
                if sovInfo is not None:
                    solSovOwner = sovInfo.allianceID
        return solSovOwner

    def AddToBucket(self, buckets, systemOwners, systemID):
        self.counter += 1
        sovID = systemOwners.get(systemID, None)
        if sovID is None:
            sovID = sm.GetService('map').GetItem(systemID).factionID
        if sovID is not None:
            count = buckets.get(sovID, 0)
            buckets[sovID] = count + 1

    def GetIdFromScope(self, scope):
        if scope == 'world':
            itemID = None
        elif scope == 'region':
            itemID = session.regionid
        elif scope == 'constellation':
            itemID = session.constellationid
        else:
            itemID = session.solarsystemid2
        return itemID

    def GetPrerequisite(self, typeID):
        reqTypeID = sm.GetService('godma').GetTypeAttribute(typeID, const.attributeSovUpgradeRequiredUpgradeID)
        reqTypeName = None
        if reqTypeID != 0 and reqTypeID is not None:
            reqTypeName = evetypes.GetName(reqTypeID)
        return reqTypeName

    def CanInstallUpgrade(self, typeID, hubID, devIndices = None):
        if devIndices is None:
            devIndices = self.GetDevelopmentIndicesForSystem(session.solarsystemid2)
        godma = sm.GetService('godma')
        for attributeID, data in devIndices.iteritems():
            value = godma.GetTypeAttribute(typeID, attributeID)
            level = self.GetDevIndexLevel(data.points)
            if value > 0 and value > level:
                return False

        requiredSovereigntyLevel = int(godma.GetTypeAttribute(typeID, const.attributeDevIndexSovereignty, 0))
        if requiredSovereigntyLevel:
            iHubInfo = self.GetInfrastructureHubInfo(session.solarsystemid)
            if iHubInfo is None:
                return False
            sovHeldFor = (blue.os.GetWallclockTime() - iHubInfo.claimTime) / const.DAY
            if util.GetTimeIndexLevelForDays(sovHeldFor) < requiredSovereigntyLevel:
                return False
        requiredUpgradeID = int(godma.GetTypeAttribute(typeID, const.attributeSovUpgradeRequiredUpgradeID, 0))
        blockingUpgradeID = int(godma.GetTypeAttribute(typeID, const.attributeSovUpgradeBlockingUpgradeID, 0))
        if requiredUpgradeID > 0 or blockingUpgradeID > 0:
            inv = sm.GetService('invCache').GetInventoryFromId(hubID)
            found = False
            for upgrade in inv.List():
                if requiredUpgradeID > 0 and upgrade.typeID == requiredUpgradeID and upgrade.flagID == const.flagStructureActive:
                    found = True
                if blockingUpgradeID > 0 and upgrade.typeID == blockingUpgradeID:
                    return False

            if not found:
                return False
        return True

    def GetDevIndexMgr(self):
        if self.devIndexMgr is None:
            self.devIndexMgr = sm.RemoteSvc('devIndexManager')
        return self.devIndexMgr

    def GetOutpostData(self, outpostID):
        if self.outpostData is not None and blue.os.TimeDiffInMs(self.outpostData.updateTime, blue.os.GetWallclockTime()) > 3600000:
            return self.outpostData
        else:
            allianceSvc = sm.GetService('alliance')
            corpMgr = moniker.GetCorpStationManagerEx(outpostID)
            self.outpostData = util.KeyVal(allianceCorpList=set([ corporationID for corporationID in allianceSvc.GetMembers() ]), updateTime=blue.os.GetWallclockTime(), upgradeLevel=corpMgr.GetStationDetails(outpostID).upgradeLevel)
            return self.outpostData

    def GetUpgradeLevel(self, typeID):
        for indexID in const.developmentIndices:
            value = int(sm.GetService('godma').GetTypeAttribute(typeID, indexID, -1))
            if value >= 0:
                levelInfo = self.GetIndexLevel(value, typeID, True)
                levelInfo.indexID = indexID
                return levelInfo

    def GetIHubOwnerAllianceID(self, hubID):
        try:
            hubItem = sm.GetService('invCache').GetInventoryFromId(hubID).GetItem()
            corpID = hubItem.ownerID
            allianceID = sm.GetService('corp').GetCorporation(corpID).allianceID
        except:
            return None

        return allianceID

    def GetInfrastructureHubItemData(self, hubID):
        inv = sm.GetService('invCache').GetInventoryFromId(hubID)
        itemData = {}
        for item in inv.List():
            itemData[item.typeID] = util.KeyVal(itemID=item.itemID, typeID=item.typeID, groupID=item.groupID, flagID=item.flagID)

        return itemData

    def GetIndexLevel(self, value, indexID, isUpgrade = False):
        if indexID == const.attributeDevIndexUpgrade:
            indexLevels = const.facwarSolarSystemUpgradeThresholds
        elif indexID == const.attributeDevIndexSovereignty:
            indexLevels = self.holdTimeLevels
        else:
            indexLevels = self.indexLevels
        if value >= indexLevels[-1]:
            return util.KeyVal(level=5, remainder=0.0)
        for level, maxValue in enumerate(indexLevels):
            if value < maxValue:
                if level == 0:
                    minValue = 0.0
                else:
                    minValue = float(indexLevels[level - 1])
                if value < 0:
                    remainder = 0
                remainder = value - minValue
                remainder = remainder / (maxValue - minValue)
                if isUpgrade:
                    level = value
                return util.KeyVal(level=level, remainder=remainder)

    def GetLevelInfoForIndex(self, indexID, devIndex = None, solarsystemID = None):
        if solarsystemID is None:
            solarsystemID = session.solarsystemid2
        increasing = False
        if indexID == const.attributeDevIndexSovereignty:
            iHubInfo = self.GetInfrastructureHubInfo(solarsystemID)
            if iHubInfo:
                currentTime = blue.os.GetWallclockTime()
                timeDiff = currentTime - iHubInfo.claimTime
                value = timeDiff / const.SEC
                increasing = True
            else:
                value = 0
        else:
            if devIndex is None:
                devIndex = self.GetDevelopmentIndicesForSystem(solarsystemID).get(indexID, None)
            if devIndex is None:
                self.LogError('The index', indexID, 'does not exist')
                value = 0
                increasing = True
            else:
                increasing = devIndex.increasing
                value = devIndex.points
        ret = self.GetIndexLevel(value, indexID)
        ret.increasing = increasing
        return ret

    def GetAllDevelopmentIndicesMapped(self):
        systemToIndexMap = {}
        for indexInfo in sm.RemoteSvc('devIndexManager').GetAllDevelopmentIndices():
            systemToIndexMap[indexInfo.solarSystemID] = {const.attributeDevIndexMilitary: indexInfo.militaryPoints,
             const.attributeDevIndexIndustrial: indexInfo.industrialPoints,
             const.attributeDevIndexSovereignty: indexInfo.claimedFor * CLAIM_DAYS_TO_SECONDS}

        return systemToIndexMap

    def OnSessionChanged(self, isRemote, sess, change):
        if 'solarsystemid2' in change:
            self.devIndexMgr = None
            self.outpostData = None
            oldSolarSystemID2, newSolarSystemID2 = change['solarsystemid2']
            self.GetSovStructuresInfoForSolarSystem.remove_from_cache((self, newSolarSystemID2))

    def GetCurrentData(self, locationID):
        fwData = {}
        if util.IsSolarSystem(locationID) and not util.IsWormholeSystem(locationID):
            constellationID = sm.GetService('map').GetParent(locationID)
            data = sm.RemoteSvc('map').GetCurrentSovData(constellationID)
            indexedData = data.Index('locationID')
            sovData = [indexedData[locationID]]
            fwData = sm.RemoteSvc('map').GetConstellationLPData(constellationID).Index('solarSystemID')
        else:
            if util.IsConstellation(locationID):
                fwData = sm.RemoteSvc('map').GetConstellationLPData(locationID).Index('solarSystemID')
            sovData = sm.RemoteSvc('map').GetCurrentSovData(locationID)
        return (sovData, fwData)

    def GetRecentActivity(self):
        data = sm.RemoteSvc('map').GetRecentSovActivity()
        return data

    def GetFreeportStations(self):
        data = sm.RemoteSvc('map').GetFreeportStations()
        return data

    def GetDevIndexLevel(self, points):
        ret = 0
        for level, value in enumerate(self.indexLevels):
            if value < points:
                ret = level + 1
            else:
                break

        return ret

    def OnSovereigntyAudioEvent(self, eventID, textParams):
        if eventID in const.sovAudioEventFiles:
            self.audio.SendUIEvent(unicode(const.sovAudioEventFiles[eventID][0]))
            if const.sovAudioEventFiles[eventID][1] is not None:
                eve.Message(const.sovAudioEventFiles[eventID][1], textParams)

    def InvalidateCacheForGetDevelopmentIndicesForSystem(self, solarsystemID):
        self.GetDevelopmentIndicesForSystem.remove_from_cache((self, solarsystemID))
        sm.GetService('objectCaching').InvalidateCachedMethodCall('devIndexManager', 'GetDevelopmentIndicesForSystem', solarsystemID)

    @expiring_memoize(120)
    def GetDevelopmentIndicesForSystem(self, solarsystemID):
        return self.GetDevIndexMgr().GetDevelopmentIndicesForSystem(solarsystemID)

    def GetIndexInfoForSolarsystem(self, solarsystemID):
        devIndices = self.GetDevelopmentIndicesForSystem(solarsystemID)
        militaryIndex = devIndices.get(const.attributeDevIndexMilitary, None)
        industrialIndex = devIndices.get(const.attributeDevIndexIndustrial, None)
        strategicIndex = devIndices.get(const.attributeDevIndexSovereignty, None)
        militaryIndexInfo = self.GetLevelInfoForIndex(const.attributeDevIndexMilitary, devIndex=militaryIndex, solarsystemID=solarsystemID)
        industrialIndexInfo = self.GetLevelInfoForIndex(const.attributeDevIndexIndustrial, devIndex=industrialIndex, solarsystemID=solarsystemID)
        strategicIndexInfo = self.GetLevelInfoForIndex(const.attributeDevIndexSovereignty, devIndex=strategicIndex, solarsystemID=solarsystemID)
        ret = util.KeyVal(militaryIndexLevel=militaryIndexInfo.level, industrialIndexLevel=industrialIndexInfo.level, strategicIndexLevel=strategicIndexInfo.level, militaryIndexRemainder=militaryIndexInfo.remainder, industrialIndexRemainder=industrialIndexInfo.remainder, strategicIndexRemainder=strategicIndexInfo.remainder)
        return ret

    def GetSovInfoForSolarsystem(self, solarsystemID, isCapital):
        indexInfo = self.GetIndexInfoForSolarsystem(solarsystemID)
        multiplier = 1 / GetOccupancyMultiplier(indexInfo.industrialIndexLevel, indexInfo.militaryIndexLevel, indexInfo.strategicIndexLevel, isCapital)
        sovInfo = self.GetSystemSovereigntyInfo(solarsystemID)
        if sovInfo:
            solSovOwnerID = sovInfo.allianceID
        else:
            solSovOwnerID = None
        indexInfo.defenseMultiplier = multiplier
        indexInfo.sovHolderID = solSovOwnerID
        return indexInfo

    def IsSystemConquarable(self, solarsystemID):
        if sm.GetService('map').GetSecurityClass(solarsystemID) != const.securityClassZeroSec:
            return False
        if IsWormholeSystem(solarsystemID):
            return False
        solarSystem = cfg.mapSystemCache.get(solarsystemID, None)
        factionID = getattr(solarSystem, 'factionID', None)
        if factionID:
            return False
        return True

    def GetSovereigntyStructuresInfoForAlliance(self):
        if session.allianceid is None:
            return
        allianceSvc = sm.GetService('alliance')
        alliance = allianceSvc.GetMoniker()
        tcuRows, iHubRows, stationRows, campaignScores = alliance.GetAllianceSovereigntyStructuresInfo()
        scoresPerStructure = defaultdict(dict)
        for campaignScore in campaignScores:
            scoresPerStructure[campaignScore.sourceItemID][campaignScore.teamID] = campaignScore.score

        structuresPerSolarsystem = defaultdict(list)
        rowsPerType = [(tcuRows, typeTerritorialClaimUnit), (iHubRows, typeInfrastructureHub), (stationRows, typeOutpostConstructionPlatform)]
        for structureRows, structureType in rowsPerType:
            for structureRow in structureRows:
                structureInfo = KeyVal({'itemID': structureRow.structureID,
                 'typeID': structureType,
                 'campaignState': None,
                 'vulnerabilityState': None,
                 'defenseMultiplier': 1.0})
                if structureRow.campaignStartTime and structureRow.campaignEventType:
                    structureInfo.campaignState = (structureRow.campaignEventType,
                     session.allianceid,
                     structureRow.campaignStartTime,
                     scoresPerStructure[structureRow.structureID])
                    structureInfo.defenseMultiplier = structureRow.campaignOccupancyLevel
                elif structureRow.vulnerableStartTime and structureRow.vulnerableEndTime:
                    structureInfo.vulnerabilityState = (structureRow.vulnerableStartTime, structureRow.vulnerableEndTime)
                    structureInfo.defenseMultiplier = structureRow.vulnerabilityOccupancyLevel
                structuresPerSolarsystem[structureRow.solarSystemID].append(structureInfo)

        return structuresPerSolarsystem

    def GetMyCapitalSystem(self):
        if session.allianceid:
            capitalSystemInfo = sm.GetService('alliance').GetCapitalSystemInfo()
            if capitalSystemInfo:
                return capitalSystemInfo.currentCapitalSystem
