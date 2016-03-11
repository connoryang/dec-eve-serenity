#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\industry\mixins.py
import blue
from eve.common.script.sys.eveCfg import IsStation
import evetypes
from industry.const import Reference
from localization.formatters.timeIntervalFormatters import FormatTimeInterval
import util
import const
import copy
import industry
import localization
import invCtrl
import telemetry
import collections
import inventorycommon.typeHelpers
from utillib import KeyVal
from eve.client.script.ui.shared.industry.industryUIConst import ACTIVITY_NAMES, ACTIVITY_ICONS_SMALL
from eve.client.script.ui.shared.inventory.invCommon import CONTAINERGROUPS
from eve.client.script.ui.shared.industry import industryUIConst
from eve.common.script.util import industryCommon
from eve.common.script.util.slimItem import SlimItem
from carbonui.util.color import Color
from utillib import KeyVal

def GetFacilityName(facilityID, typeID = None, solarSystemID = None):
    name = cfg.evelocations.Get(facilityID).name
    if not name and typeID:
        name = evetypes.GetName(typeID)
    if not util.IsStation(facilityID) and solarSystemID:
        if name:
            name = localization.GetByLabel('UI/Industry/LocationAndFacility', locationName=cfg.evelocations.Get(solarSystemID).name, facilityName=name)
        else:
            name = cfg.evelocations.Get(solarSystemID).name
    return name


GROUPORDERINDEXES_BY_NUMGROUPS = ((0,),
 (0, 1),
 (1, 0, 2),
 (0,
  3,
  2,
  1),
 (1,
  3,
  0,
  4,
  2),
 (4,
  2,
  0,
  1,
  3,
  5))

def GetMaterialsByGroups(materialsData):
    groups = collections.defaultdict(list)
    for materialData in materialsData:
        if materialData.IsSelectable():
            invGroupID = industryUIConst.GROUP_SELECTABLEITEM
        elif materialData.IsOptional():
            invGroupID = industryUIConst.GROUP_OPTIONALITEM
        else:
            typeID = materialData.typeID
            groupID = evetypes.GetGroupID(typeID)
            categoryID = evetypes.GetCategoryID(typeID)
            invGroupID = industryUIConst.GetIndustryGroupID(typeID, groupID, categoryID)
        groups[invGroupID].append(materialData)

    if not groups:
        return []
    ret = groups.items()
    ret.sort(key=lambda (_, materials): len(materials), reverse=True)
    numGroups = max(len(ret) - 1, 0)
    groupOrderIndexes = GROUPORDERINDEXES_BY_NUMGROUPS[numGroups]
    return [ ret[index] for index in groupOrderIndexes ]


class BlueprintMixin(object):

    def GetItem(self):
        return SlimItem(itemID=self.blueprintID, typeID=self.blueprintTypeID, ownerID=self.ownerID)

    def GetName(self):
        return evetypes.GetName(self.blueprintTypeID)

    def GetDescription(self):
        return evetypes.GetDescription(self.blueprintTypeID)

    def GetEstimatedUnitPrice(self):
        try:
            return inventorycommon.typeHelpers.GetAveragePrice(self.blueprintTypeID) or 0.0
        except KeyError:
            return 0.0

    def GetLocationName(self):
        return self.location.GetName()

    def GetGroupName(self):
        typeID = self.GetProductOrBlueprintTypeID()
        return evetypes.GetGroupName(typeID)

    def GetProductOrBlueprintTypeID(self):
        if self.productTypeID:
            return self.productTypeID
        else:
            return self.blueprintTypeID

    def GetProductGroupAndCategory(self):
        typeID = self.GetProductOrBlueprintTypeID()
        return KeyVal(groupID=evetypes.GetGroupID(typeID), groupName=evetypes.GetGroupName(typeID), categoryID=evetypes.GetCategoryID(typeID), categoryName=evetypes.GetCategoryName(typeID))

    def GetDistance(self):
        if self.facility:
            return self.facility.distance

    def GetFacilityName(self):
        if self.facility:
            return self.facility.GetName()

    def GetRunsRemainingLabel(self):
        return str(self.runsRemaining)

    def GetLabel(self):
        if self.quantity > 1:
            return '%s x %s' % (self.quantity, self.GetName())
        else:
            return self.GetName()

    def IsInstalled(self):
        return self.jobID is not None

    def IsSameBlueprint(self, bpData):
        if bpData is None:
            return False
        if self.blueprintTypeID != bpData.blueprintTypeID:
            return False
        if self.blueprintID != bpData.blueprintID:
            return False
        if self.locationID != bpData.locationID:
            return False
        if self.flagID != bpData.flagID:
            return False
        if self.ownerID != bpData.ownerID:
            return False
        if self.original != bpData.original:
            return False
        return True

    def IsAncientRelic(self):
        return evetypes.GetCategoryID(self.blueprintTypeID) == const.categoryAncientRelic

    def IsWithinRange(self):
        if IsStation(self.facilityID):
            return self.facilityID == session.stationid2
        if session.solarsystemid:
            bp = sm.GetService('michelle').GetBallpark()
            if bp is None:
                return False
            return bp.GetBall(self.facilityID) is not None
        return False

    def GetCopy(self):
        bpData = sm.GetService('blueprintSvc').GetBlueprintType(self.blueprintTypeID).copy()
        bpData.original = self.original
        bpData.materialEfficiency = self.materialEfficiency
        bpData.timeEfficiency = self.timeEfficiency
        bpData.runsRemaining = self.runsRemaining
        return bpData

    def GetDragData(self):
        dragData = None
        if self.IsWithinRange():
            invController = self.location.GetInvController()
            item = invController.GetItem(self.blueprintID)
            if item:
                return KeyVal(__guid__='xtriui.InvItem', name=self.GetLabel(), item=item, rec=item)
        return KeyVal(__guid__='uicls.GenericDraggableForTypeID', typeID=self.blueprintTypeID, itemID=self.blueprintID, label=self.GetLabel())


class ActivityMixin(object):

    def GetName(self):
        return localization.GetByLabel(ACTIVITY_NAMES.get(self.activityID))

    def GetHint(self):
        return self.GetName()

    def GetIcon(self):
        return ACTIVITY_ICONS_SMALL[self.activityID]

    def GetTime(self, runs = 1):
        return FormatTimeInterval(self.time * runs * const.SEC)

    def GetMaterialsByGroups(self):
        return GetMaterialsByGroups(self.materials)


class FacilityMixin(object):

    def GetName(self):
        return GetFacilityName(self.facilityID, self.typeID, self.solarSystemID)

    def GetTypeName(self):
        categoryID = evetypes.GetCategoryID(self.typeID)
        if categoryID == const.categoryStation:
            return evetypes.GetCategoryNameByCategory(categoryID)
        else:
            return evetypes.GetGroupName(self.typeID)

    def GetOwnerName(self):
        try:
            return cfg.eveowners.Get(self.ownerID).name
        except KeyError:
            return ''

    def GetHint(self):
        return self.GetName()

    def HasFacilityModifiers(self, activityID):
        for modifier in self.modifiers:
            if modifier.reference == industry.Reference.FACILITY and modifier.activity == activityID:
                return True

        return False

    def GetFacilityModifiersByActivityID(self):
        ret = collections.defaultdict(list)
        for modifier in self.modifiers:
            if modifier.reference == industry.Reference.FACILITY and modifier.groupID is None and modifier.categoryID is None:
                ret[modifier.activity].append(modifier)

        return ret

    def GetCostIndexByActivityID(self):
        ret = {}
        for modifier in self.modifiers:
            if modifier.reference == industry.Reference.SYSTEM:
                ret[modifier.activity] = modifier.GetAsSystemCostIndex(modifier.activity)

        return ret

    def GetCostIndex(self, activityID):
        return self.GetCostIndexByActivityID().get(activityID, 0.0)


class SkillMixin(object):

    def GetName(self):
        return evetypes.GetName(self.typeID)

    def GetHint(self):
        return localization.GetByLabel('UI/InfoWindow/SkillAndLevel', skill=self.typeID, skillLevel=self.level)


class MaterialMixin(object):

    def GetName(self):
        return evetypes.GetName(self.typeID)

    def GetDescription(self):
        return evetypes.GetDescription(self.typeID)

    def GetHint(self):
        return localization.GetByLabel('UI/Common/QuantityAndItem', item=self.typeID, quantity=self.quantity)

    def GetEstimatedUnitPrice(self):
        try:
            return inventorycommon.typeHelpers.GetAveragePrice(self.typeID) or 0.0
        except KeyError:
            return 0.0

    def IsOptional(self):
        return bool(self.options)

    def IsSelectable(self):
        if not self.IsOptional():
            return False
        typeIDs = [ material.typeID for material in self.options ]
        return None not in typeIDs

    def IsOptionSelected(self):
        return self.typeID is not None


class JobMixin(object):

    def GetStartDateLabel(self):
        return util.FmtDate(util.DateToBlue(self.startDate), 'ls')

    def GetEndDateLabel(self):
        return util.FmtDate(util.DateToBlue(self.endDate), 'ls')

    def GetJobTimeLeftLabel(self):
        if self.status == industry.STATUS_UNSUBMITTED:
            time = self.time.total_seconds() * const.SEC
        elif self.status == industry.STATUS_INSTALLED:
            time = util.DateToBlue(self.endDate) - blue.os.GetWallclockTime()
        elif self.status == industry.STATUS_PAUSED:
            time = util.DateToBlue(self.endDate) - util.DateToBlue(self.pauseDate)
        elif self.status == industry.STATUS_READY:
            time = 0
        else:
            return '-'
        time = long(max(time, 0L))
        return FormatTimeInterval(time)

    def GetJobStateLabel(self):
        if self.status <= industry.STATUS_READY:
            return self.GetJobTimeLeftLabel()
        elif self.status == industry.STATUS_DELIVERED:
            if self.activityID == industry.INVENTION:
                if self.successfulRuns == 0:
                    return '<color=red>%s' % localization.GetByLabel('UI/Industry/JobFailed')
                else:
                    return localization.GetByLabel('UI/Industry/PartiallySucceeded', numSucceeded=self.successfulRuns, numTotal=self.runs)
            return localization.GetByLabel('UI/Industry/Succeeded')
        elif self.status == industry.STATUS_CANCELLED:
            color = Color.RGBtoHex(*industryUIConst.COLOR_NOTREADY)
            return '<color=%s>%s' % (color, localization.GetByLabel('UI/Industry/Cancelled'))
        elif self.status == industry.STATUS_REVERTED:
            color = Color.RGBtoHex(*industryUIConst.COLOR_NOTREADY)
            return '<color=%s>%s' % (color, localization.GetByLabel('UI/Industry/Reverted'))
        else:
            return ''

    def GetJobProgressRatio(self):
        if self.status == industry.STATUS_INSTALLED:
            timeLeft = blue.os.GetWallclockTime() - util.DateToBlue(self.startDate)
            totalTime = long(self.time.total_seconds()) * const.SEC
            return float(timeLeft) / totalTime
        elif self.status == industry.STATUS_PAUSED:
            timeLeft = blue.os.GetWallclockTime() - util.DateToBlue(self.startDate)
            totalTime = long(self.time.total_seconds()) * const.SEC
            return float(timeLeft) / totalTime
        elif self.status > industry.STATUS_COMPLETED:
            return 1.0
        else:
            return 0.0

    def GetProductTypeID(self):
        product = self.product
        if product:
            return product.typeID

    def GetProductLabel(self):
        if self.activityID == industry.MANUFACTURING:
            return self.product.GetName()
        if self.activityID in (industry.RESEARCH_MATERIAL, industry.RESEARCH_TIME):
            return localization.GetByLabel('UI/Industry/ResearchedBlueprint')
        if self.activityID == industry.COPYING:
            return localization.GetByLabel('UI/Industry/BlueprintCopy')
        if self.activityID == industry.INVENTION:
            if self.product:
                return self.product.GetName()
            else:
                return localization.GetByLabel('UI/Industry/NoOutcomeSelected')

    def GetProductAmountLabel(self):
        if self.activityID in (industry.MANUFACTURING, industry.INVENTION):
            return 'x %s' % self.product.quantity
        if self.activityID == industry.RESEARCH_MATERIAL:
            diff = self.product.materialEfficiency - self.blueprint.materialEfficiency
            return '+%s%%' % diff
        if self.activityID == industry.RESEARCH_TIME:
            diff = self.product.timeEfficiency - self.blueprint.timeEfficiency
            return '+%s%%' % diff
        if self.activityID == industry.COPYING:
            return 'x %s' % self.product.quantity

    def GetProductNewBlueprint(self):
        if isinstance(self.product, industry.Blueprint) and self.product.blueprintID is None:
            return self.product

    def GetRunsRemainingCaption(self):
        if self.activityID in (industry.MANUFACTURING, industry.INVENTION):
            if self.blueprint.original:
                return localization.GetByLabel('UI/Industry/MaximumRuns')
            else:
                return localization.GetByLabel('UI/Industry/RunsRemaining')
        else:
            if self.activityID in (industry.RESEARCH_MATERIAL, industry.RESEARCH_TIME):
                return localization.GetByLabel('UI/Industry/LevelsRemaining')
            if self.activityID == industry.COPYING:
                return localization.GetByLabel('UI/Industry/MaximumRuns')

    def GetRunsRemainingLabel(self):
        if self.activityID in (industry.MANUFACTURING, industry.INVENTION) and not self.blueprint.original:
            return self.blueprint.runsRemaining
        maxRuns = self.maxRuns
        if maxRuns and maxRuns != industry.MAX_RUNS:
            return maxRuns

    def GetStatusColor(self):
        if self.status == industry.STATUS_READY:
            return (1, 1, 1, 1)
        elif self.status == industry.STATUS_INSTALLED:
            return (1, 1, 1, 0.7)
        elif self.status == industry.STATUS_PAUSED:
            return (1, 0, 0, 0.7)
        else:
            return (1, 1, 1, 0.3)

    def GetInstallerName(self):
        return cfg.eveowners.Get(self.installerID).name

    @telemetry.ZONE_METHOD
    def GetLocationsInvControllersAndLocations(self):
        ret = []
        for location in self.locations:
            invController = location.GetInvController()
            ret.append((invController, location))
            ret = sorted(ret, key=self._GetSortKey)

        return ret

    @telemetry.ZONE_METHOD
    def _GetSortKey(self, data):
        invController, location = data
        isContainer = evetypes.GetGroupID(location.typeID) in CONTAINERGROUPS
        return (location.flagID, isContainer, invController.GetName())

    def IsInstalled(self):
        return self.status >= industry.STATUS_INSTALLED

    def HasMultipleProducts(self):
        return len(self.products) > 1

    def IsProductSelectable(self):
        return self.activityID == industry.INVENTION and self.HasMultipleProducts()

    def GetGaugeValue(self):
        maxRuns = self.maxRuns
        if not maxRuns or maxRuns == industry.MAX_RUNS:
            return 0.0
        else:
            return float(self.runs) / maxRuns

    def GetModifierCaption(self, modifierCls):
        if modifierCls == industry.TimeModifier:
            return localization.GetByLabel('UI/Industry/ModifierTimeCaption')
        if modifierCls == industry.CostModifier:
            return localization.GetByLabel('UI/Industry/ModifierCostCaption')
        if modifierCls == industry.MaterialModifier:
            return localization.GetByLabel('UI/Industry/ModifierMaterialCaption')
        if modifierCls == industry.ProbabilityModifier:
            return localization.GetByLabel('UI/Industry/ModifierProbabilityCaption')

    def GetModifiers(self, modifierCls):
        modifiers = {}
        for modifier in self.input_modifiers:
            if self._FilterModifiers(modifier, modifierCls):
                if modifier.reference.value in modifiers:
                    modifiers[modifier.reference.value].amount *= modifier.amount
                else:
                    modifiers[modifier.reference.value] = copy.copy(modifier)

        return [ modifier for ref, modifier in sorted(modifiers.items()) ]

    def _FilterModifiers(self, modifier, modifierCls):
        if isinstance(modifier, industry.CostModifier) and modifier.reference == industry.Reference.SYSTEM:
            return False
        return isinstance(modifier, modifierCls)

    def GetTimeSkillTypes(self):
        skills = []
        if self.activityID == industry.MANUFACTURING:
            skills += [const.typeIndustry, const.typeAdvancedIndustry]
        elif self.activityID == industry.COPYING:
            skills += [const.typeScience, const.typeAdvancedIndustry]
        elif self.activityID == industry.RESEARCH_TIME:
            skills += [const.typeResearch, const.typeAdvancedIndustry]
        elif self.activityID == industry.RESEARCH_MATERIAL:
            skills += [const.typeMetallurgy, const.typeAdvancedIndustry]
        elif self.activityID == industry.INVENTION:
            skills += [const.typeAdvancedIndustry]
        godma = sm.GetService('godma')
        for modifier, attribute, activityID in industryCommon.REQUIRED_SKILL_MODIFIERS:
            if self.activityID == activityID and modifier == industry.TimeModifier:
                for skill in self.required_skills:
                    if godma.GetTypeAttribute(skill.typeID, attribute):
                        skills.append(skill.typeID)

        return skills

    def GetMaterialsByGroups(self):
        if self.IsInstalled():
            return []
        return GetMaterialsByGroups(self.materials)

    def GetFacilityName(self):
        try:
            if self.facility:
                return self.facility.GetName()
            primeFacility = self.status < industry.STATUS_COMPLETED
            return sm.GetService('facilitySvc').GetFacility(self.facilityID, prime=primeFacility).GetName()
        except KeyError:
            return GetFacilityName(self.stationID, None, self.solarSystemID)

    def GetFacilityType(self):
        try:
            if self.facility:
                return self.facility.typeID
            primeFacility = self.status < industry.STATUS_COMPLETED
            return sm.GetService('facilitySvc').GetFacility(self.facilityID, prime=primeFacility).typeID
        except KeyError:
            pass

    def IsPreview(self):
        return self.blueprintID is None

    def HasError(self, errorID):
        for errorID2, args in self.errors:
            if errorID == errorID2:
                return True

        return False


class LocationMixin(object):

    def GetName(self):
        return self.GetInvController().GetName()

    def GetIcon(self):
        return self.GetInvController().GetIconName()

    def GetInvController(self):
        groupID = evetypes.GetGroupID(self.typeID)
        if groupID in CONTAINERGROUPS:
            invController = invCtrl.StationContainer(self.itemID, self.typeID)
        elif self.typeID == const.typeOffice:
            corpFlags = const.corpHangarTakeRolesByFlag.keys()
            divisionNum = corpFlags.index(self.flagID)
            invController = invCtrl.StationCorpHangar(self.itemID, divisionNum)
        elif groupID in (const.groupAssemblyArray, const.groupMobileLaboratory):
            corpFlags = const.corpHangarTakeRolesByFlag.keys()
            divisionNum = corpFlags.index(self.flagID)
            invController = invCtrl.POSCorpHangar(self.itemID, divisionNum)
        else:
            invController = invCtrl.StationItems(self.itemID)
        return invController


class ModifierMixin(object):

    def GetName(self):
        if self.reference == industry.Reference.BLUEPRINT:
            if isinstance(self, industry.TimeModifier):
                return localization.GetByLabel('UI/Industry/BlueprintTimeEfficiency')
            if isinstance(self, industry.MaterialModifier):
                return localization.GetByLabel('UI/Industry/BlueprintMaterialEfficiency')
            if isinstance(self, industry.ProbabilityModifier):
                return localization.GetByLabel('UI/Industry/BlueprintBaseProbability')
            if isinstance(self, industry.CostModifier):
                return localization.GetByLabel('UI/Industry/BlueprintCostModifier')
        else:
            if self.reference == industry.Reference.DECRYPTOR:
                return localization.GetByLabel('UI/Industry/OptionalDecryptor')
            if self.reference == industry.Reference.SYSTEM:
                return localization.GetByLabel('UI/Industry/SystemCostIndex')
            if self.reference == industry.Reference.FACILITY:
                return localization.GetByLabel('UI/Industry/Facility')
            if self.reference == industry.Reference.SKILLS:
                return localization.GetByLabel('UI/Industry/SkillsAndImplants')
            if self.reference == industry.Reference.BASEITEM:
                return localization.GetByLabel('UI/Industry/OptionalBaseItem')
            if self.reference == industry.Reference.DISTRICT:
                return localization.GetByLabel('UI/Industry/DistrictModifier')
            if self.reference == industry.Reference.FACTION:
                return localization.GetByLabel('UI/Industry/FactionModifier')

    def GetAsPercentage(self):
        return self.GetAsBonus() * 100.0

    def GetAsBonus(self):
        return self.amount - 1.0

    def GetAsSystemCostIndex(self, activityID):
        return self.amount

    def GetPercentageLabel(self):
        percent = self.GetAsPercentage()
        if isinstance(self, industry.ProbabilityModifier) and self.reference == Reference.BLUEPRINT:
            return '%.1f%%' % (100.0 + percent)
        else:
            color = self.GetModifierColor()
            if percent > 0:
                return '<color=%s>+%.1f%%</color>' % (Color.RGBtoHex(*color), percent)
            return '<color=%s>%.1f%%</color>' % (Color.RGBtoHex(*color), percent)

    def GetModifierColor(self):
        amount = self.GetAsBonus()
        if isinstance(self, industry.ProbabilityModifier):
            amount = -amount
        if amount < 0.0:
            return Color.GREEN
        elif amount > 0.0:
            return Color.RED
        else:
            return Color.GRAY


industry.Blueprint.extend(BlueprintMixin)
industry.Activity.extend(ActivityMixin)
industry.Facility.extend(FacilityMixin)
industry.Skill.extend(SkillMixin)
industry.Material.extend(MaterialMixin)
industry.Job.extend(JobMixin)
industry.JobData.extend(JobMixin)
industry.Location.extend(LocationMixin)
industry.modifiers.Modifier.extend(ModifierMixin)
