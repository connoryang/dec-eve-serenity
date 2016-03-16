#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sovDashboard\__init__.py
from collections import OrderedDict
from carbon.common.lib.const import DAY
from carbon.common.script.util.format import FmtDate, FmtTime
import gametime
from inventorycommon.const import typeTerritorialClaimUnit, typeInfrastructureHub, typeOutpostConstructionPlatform
from localization import GetByLabel
from sovDashboard.dashboardConst import STATUS_INVULNERABLE, STATUS_REINFORCED, STATUS_NODEFIGHT, STATUS_VULNERABLE, STATUS_VULNERABLE_OVERTIME
from utillib import KeyVal

def CalculateStructureStatusFromStructureInfo(structureInfo):
    campaignState = structureInfo.get('campaignState', None)
    vulnerabilityState = structureInfo.get('vulnerabilityState', None)
    if campaignState:
        eventType, defenderID, startTime, scoreByTeamID = campaignState
        if gametime.GetWallclockTime() < startTime:
            structureStatus = STATUS_REINFORCED
        else:
            structureStatus = STATUS_NODEFIGHT
    elif vulnerabilityState is None:
        structureStatus = STATUS_INVULNERABLE
    else:
        startTime, endTime = vulnerabilityState
        now = gametime.GetWallclockTime()
        if now < startTime:
            structureStatus = STATUS_INVULNERABLE
        elif now > endTime:
            structureStatus = STATUS_VULNERABLE_OVERTIME
        else:
            structureStatus = STATUS_VULNERABLE
    return structureStatus


def GetStartTimeFromStructureInfo(structureInfo):
    campaignState = structureInfo.get('campaignState', None)
    vulnerabilityState = structureInfo.get('vulnerabilityState', None)
    if campaignState:
        eventType, defenderID, startTime, scoreByTeamID = campaignState
        return startTime
    if vulnerabilityState:
        startTime, endTime = vulnerabilityState
    else:
        startTime = None
    return startTime


def FormatCountDownTime(targetTime):
    now = gametime.GetWallclockTime()
    if targetTime > now:
        diff = targetTime - now
        timeText = FmtTime(diff)
        timeText += '<br>%s' % FmtDate(targetTime, 'ls')
    else:
        timeText = GetByLabel('UI/Sovereignty/Status/Overtime')
    return timeText


def GetStructureStatusString(structureInfo, getTimeString = False):
    structureTypeID = structureInfo['typeID']
    typeString = dashboardConst.STRUCTURELABEL_BY_TYPEID[structureTypeID]
    typeLabel = GetByLabel(typeString)
    timeText = None
    structureStatus = CalculateStructureStatusFromStructureInfo(structureInfo)
    if structureStatus == dashboardConst.STATUS_VULNERABLE:
        text = GetByLabel('UI/Sovereignty/Status/VulnerableNowType', typeName=typeLabel)
        vulnerabilityState = structureInfo.get('vulnerabilityState', None)
        startTime, endTime = vulnerabilityState
        timeText = FormatCountDownTime(endTime)
    elif structureStatus == dashboardConst.STATUS_VULNERABLE_OVERTIME:
        text = GetByLabel('UI/Sovereignty/Status/VulnerableType', typeName=typeLabel)
        timeText = GetByLabel('UI/Sovereignty/Status/Overtime')
    elif structureStatus == dashboardConst.STATUS_REINFORCED:
        text = GetByLabel('UI/Sovereignty/Status/ReinforcedType', typeName=typeLabel)
        campaignState = structureInfo.get('campaignState', None)
        eventType, defenderID, startTime, scoreByTeamID = campaignState
        timeText = FormatCountDownTime(startTime)
    elif structureStatus == dashboardConst.STATUS_INVULNERABLE:
        text = GetByLabel('UI/Sovereignty/Status/InvulnerableType', typeName=typeLabel)
        vulnerabilityState = structureInfo.get('vulnerabilityState', None)
        if vulnerabilityState is None:
            timeText = GetByLabel('UI/Sovereignty/Status/Unknown')
        else:
            startTime, endTime = vulnerabilityState
            if startTime - gametime.GetWallclockTime() > DAY:
                startDateFormat = 'ls'
            else:
                startDateFormat = 'ns'
            startTimeText = FmtDate(startTime, startDateFormat)
            endTimeText = FmtDate(endTime, 'ns')
            timeText = '%s<br>%s-%s' % (GetByLabel('UI/Sovereignty/Status/VulnerabilityWindow'), startTimeText, endTimeText)
    elif structureStatus == dashboardConst.STATUS_NODEFIGHT:
        text = GetByLabel('UI/Sovereignty/Status/ContestedType', typeName=typeLabel)
        timeText = GetByLabel('UI/Sovereignty/StatusOngoing')
    else:
        text = ''
    if getTimeString:
        return (text, timeText)
    return text


def ShouldUpdateStructureInfo(structureInfo, sourceItemID):
    itemID = getattr(structureInfo, 'itemID', None)
    if itemID is None or itemID != sourceItemID:
        return False
    solarSystemID = getattr(structureInfo, 'solarSystemID', None)
    if solarSystemID is None:
        return False
    return True


def GetSovStructureInfoByTypeID(solarsystemStructureInfo):
    structureInfosByTypeID = OrderedDict([(typeTerritorialClaimUnit, KeyVal(typeID=typeTerritorialClaimUnit)), (typeInfrastructureHub, KeyVal(typeID=typeInfrastructureHub)), (typeOutpostConstructionPlatform, KeyVal(typeID=typeOutpostConstructionPlatform))])
    for structureInfo in solarsystemStructureInfo:
        structureInfosByTypeID[structureInfo.typeID] = structureInfo

    return structureInfosByTypeID
