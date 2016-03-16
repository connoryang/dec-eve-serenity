#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveAssets\assetSearchUtil.py
import re
from collections import namedtuple
import dogma.const as dogmaConst
import eve.common.lib.appConst as appConst
import evetypes
import inventorycommon.const as invConst
REGEX = re.compile("\n    \\b(?P<key>\\w+):\\s*                          # key = a single keyword followed by a : like 'min:'\n    (?P<value>[-+]?\\d+\\.\\d+|[-+]?\\d+|[\\w\\s]+)   # value = decimal number, an integer or any combination of whitespaces and alphanumerical letters\n    (?![\\w+:])                                  # we don't want to include a word that is followed by : since it will mark a new keyword\n    ", re.UNICODE + re.IGNORECASE + re.VERBOSE)
KeywordOption = namedtuple('KeywordOption', 'keyword optionDescription specialOptions matchFunction')

def IsPartOfText(text, value):
    try:
        return text.lower().startswith(value.lower())
    except AttributeError:
        return False


def IsTextMatch(text, value):
    try:
        return text.lower() == value.lower()
    except AttributeError:
        return False


def ParseString(text):
    matches = REGEX.findall(text)
    if matches:
        key, value = matches[0]
        key = key + ':'
        text = text[:text.find(key)]
        matches = [ (k, v.rstrip()) for k, v in matches ]
    return (text.strip(), matches)


class AssetKeywordSearch(object):

    def __init__(self, nameHelper, uiSvc, mapSvc, godma, localization, cfg, *args):
        self.uiSvc = uiSvc
        self.mapSvc = mapSvc
        self.godma = godma
        self.localization = localization
        self.cfg = cfg
        self.nameHelper = nameHelper
        self.getByLabelFunc = localization.GetByLabel
        self.localizationSortFunc = localization.util.Sort
        self.stationNames_lower = {}
        self.solarsystemNamesByStationID_lower = {}
        self.constellationaNamesByStationID_lower = {}
        self.regionNameByStationID_lower = {}
        self.securityClassByStationID_lower = {}
        self.systemSecByStationID = {}
        self.solarsystemIDByStationID = {}
        self.techLevelByTypeID = {}
        self.metaGroupIDsByTypeIDs = {}
        self.metaGroupNamesByMetaGroupID_lower = {}
        self.metaLevelByTypeID = {}
        self.highSecurityText = self.getByLabelFunc('UI/Inventory/AssetSearch/OptionSecurityHigh')
        self.lowSecurityText = self.getByLabelFunc('UI/Inventory/AssetSearch/OptionSecurityLow')
        self.nullSecurityText = self.getByLabelFunc('UI/Inventory/AssetSearch/OptionSecurityNull')
        self.zeroSecurityText = self.getByLabelFunc('UI/Inventory/AssetSearch/OptionSecurityZero')
        self.empireSecurityText = self.getByLabelFunc('UI/Inventory/AssetSearch/OptionSecurityEmpire')
        self.blueprintCopyText = self.getByLabelFunc('UI/Inventory/AssetSearch/OptionBlueprintCopy')
        self.blueprintOriginalText = self.getByLabelFunc('UI/Inventory/AssetSearch/OptionBlueprintOriginal')
        self.ResetPerRunDicts()

    def ResetPerRunDicts(self):
        self.matchResultsTypeNamesByTypeIDs = {}
        self.matchedResultsGroupNameByGroupIDs = {}
        self.matchedResultsCategoryNameByCategoryID = {}
        self.matchedResultsMetaGroupByMetaGroupID = {}
        self.matchedResultsMinSecurityByStationID = {}
        self.matchedResultsMaxSecurityByStationID = {}
        self.matchedSecurityClassByStationID = {}
        self.matchedSolarSystemNameByStationID = {}
        self.matchedConstellationNameByStationID = {}
        self.matchedRegionNameByStationID = {}
        self.matchedStationNameByStationID = {}

    def MatchType(self, conditions, value):
        typeName = value

        def CheckType(item):
            try:
                return self.matchResultsTypeNamesByTypeIDs[item.typeID]
            except KeyError:
                tName = self.nameHelper.GetTypeName(item.typeID)
                matched = tName.find(typeName) > -1
                self.matchResultsTypeNamesByTypeIDs[item.typeID] = matched
                return matched

        conditions.append(CheckType)

    def MatchGroup(self, conditions, value):
        groupName = value

        def CheckGroup(item):
            try:
                return self.matchedResultsGroupNameByGroupIDs[item.groupID]
            except KeyError:
                gName = self.nameHelper.GetGroupName(item.groupID)
                matched = gName.find(groupName) > -1
                self.matchedResultsGroupNameByGroupIDs[item.groupID] = matched
                return matched

        conditions.append(CheckGroup)

    def MatchCategory(self, conditions, value):
        categoryName = value

        def CheckCategory(item):
            try:
                return self.matchedResultsCategoryNameByCategoryID[item.categoryID]
            except KeyError:
                cName = self.nameHelper.GetCategoryName(item.categoryID)
                matched = cName.find(categoryName) > -1
                self.matchedResultsCategoryNameByCategoryID[item.categoryID] = matched
                return matched

        conditions.append(CheckCategory)

    def MatchMinimumQuantity(self, conditions, value):
        try:
            quantity = int(value)
        except ValueError:
            quantity = None

        def CheckMinQuantity(item):
            if not quantity:
                return value == ''
            return item.stacksize >= quantity

        conditions.append(CheckMinQuantity)

    def MatchMaximumQuantity(self, conditions, value):
        try:
            quantity = int(value)
        except ValueError:
            quantity = None

        def CheckMaxQuantity(item):
            if not quantity:
                return value == ''
            return item.stacksize <= quantity

        conditions.append(CheckMaxQuantity)

    def MatchMetalevel(self, conditions, value):
        try:
            level = int(value)
        except ValueError:
            level = None

        def CheckMetaLevel(item):
            if not level:
                return value == ''
            metaLevel = self.GetMetaLevel(item.typeID)
            return level == metaLevel

        conditions.append(CheckMetaLevel)

    def MatchMetagroup(self, conditions, value):
        groupName = value

        def CheckMetaGroup(item):
            metaGroupID = self.GetMetaGroupID(item.typeID)
            try:
                return self.matchedResultsMetaGroupByMetaGroupID[metaGroupID]
            except KeyError:
                matched = False
                if metaGroupID > 0:
                    metaGroupName = self.GetMetaGroupName(metaGroupID)
                    matched = groupName in metaGroupName
                self.matchedResultsMetaGroupByMetaGroupID[metaGroupID] = matched
                return matched

        conditions.append(CheckMetaGroup)

    def MatchTechlevel(self, conditions, value):
        try:
            level = int(value)
        except ValueError:
            level = None

        def CheckTechLevel(item):
            if not level:
                return value == ''
            techLevel = self.GetTechLevel(item.typeID)
            return level == techLevel

        conditions.append(CheckTechLevel)

    def MatchMinSecurity(self, conditions, value):
        try:
            secLevel = float(value)
        except ValueError:
            secLevel = None

        def CheckMinSecurity(item):
            if not secLevel:
                return value == ''
            try:
                return self.matchedResultsMinSecurityByStationID[item.stationID]
            except KeyError:
                systemSec = self.GetSystemSecurity(item.stationID)
                matched = systemSec >= secLevel
                self.matchedResultsMinSecurityByStationID[item.stationID] = matched
                return matched

        conditions.append(CheckMinSecurity)

    def MatchMaxSecurity(self, conditions, value):
        try:
            secLevel = float(value)
        except ValueError:
            secLevel = None

        def CheckMaxSecurity(item):
            if not secLevel:
                return value == ''
            try:
                return self.matchedResultsMaxSecurityByStationID[item.stationID]
            except KeyError:
                systemSec = self.GetSystemSecurity(item.stationID)
                matched = systemSec <= secLevel
                self.matchedResultsMaxSecurityByStationID[item.stationID] = matched
                return matched

        conditions.append(CheckMaxSecurity)

    def MatchSecurityClass(self, conditions, value):
        if IsPartOfText(self.highSecurityText, value):
            secClass = [appConst.securityClassHighSec]
        elif IsPartOfText(self.lowSecurityText, value):
            secClass = [appConst.securityClassLowSec]
        elif IsPartOfText(self.nullSecurityText, value) or IsPartOfText(self.zeroSecurityText, value):
            secClass = [appConst.securityClassZeroSec]
        elif IsPartOfText(self.empireSecurityText, value):
            secClass = [appConst.securityClassHighSec, appConst.securityClassLowSec]
        else:
            secClass = None

        def CheckSecurityClass(item):
            if not secClass:
                return value == ''
            try:
                return self.matchedSecurityClassByStationID[item.stationID]
            except KeyError:
                systemSecClass = self.GetSecurityClass(item.stationID)
                matched = systemSecClass in secClass
                self.matchedSecurityClassByStationID[item.stationID] = matched
                return matched

        conditions.append(CheckSecurityClass)

    def MatchSolarSystem(self, conditions, value):
        name = value

        def CheckSolarSystem(item):
            try:
                return self.matchedSolarSystemNameByStationID[item.stationID]
            except KeyError:
                itemName = self.GetSolarsystemName(item.stationID)
                matched = name in itemName
                self.matchedSolarSystemNameByStationID[item.stationID] = matched
                return matched

        conditions.append(CheckSolarSystem)

    def MatchConstellation(self, conditions, value):
        name = value

        def CheckConstellation(item):
            try:
                return self.matchedConstellationNameByStationID[item.stationID]
            except KeyError:
                constellationName = self.GetConstellationName(item.stationID)
                matched = name in constellationName
                self.matchedConstellationNameByStationID[item.stationID] = matched
                return matched

        conditions.append(CheckConstellation)

    def MatchRegion(self, conditions, value):
        name = value

        def CheckRegion(item):
            try:
                return self.matchedRegionNameByStationID[item.stationID]
            except KeyError:
                regionName = self.GetRegionName(item.stationID)
                matched = name in regionName
                self.matchedRegionNameByStationID[item.stationID] = matched
                return matched

        conditions.append(CheckRegion)

    def MatchStationName(self, conditions, value):
        name = value

        def CheckStation(item):
            try:
                return self.matchedStationNameByStationID[item.stationID]
            except KeyError:
                stationName = self.GetStationName(item.stationID)
                matched = name in stationName
                self.matchedStationNameByStationID[item.stationID] = matched
                return matched

        conditions.append(CheckStation)

    def MatchBlueprint(self, conditions, value):
        if IsPartOfText(self.blueprintCopyText, value):
            isBpo = False
        elif IsPartOfText(self.blueprintOriginalText, value):
            isBpo = True
        else:
            isBpo = None

        def CheckBlueprintType(item):
            if value == '':
                return True
            if isBpo is None:
                return False
            if item.categoryID == invConst.categoryBlueprint:
                if isBpo:
                    return item.singleton != appConst.singletonBlueprintCopy
                else:
                    return item.singleton == appConst.singletonBlueprintCopy
            return False

        conditions.append(CheckBlueprintType)

    def GetSearchKeywords(self):
        keywords = [KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordType'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionType'), None, self.MatchType),
         KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordGroup'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionGroup'), None, self.MatchGroup),
         KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordCategory'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionCategory'), None, self.MatchCategory),
         KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordMinimumQuantity'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionMinimumQuantity'), None, self.MatchMinimumQuantity),
         KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordMaximumQuantity'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionMaximumQuantity'), None, self.MatchMaximumQuantity),
         KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordMetalevel'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionMetalevel'), None, self.MatchMetalevel),
         KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordMetagroup'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionMetagroup'), self.localizationSortFunc([ cfg.invmetagroups.Get(groupID).metaGroupName.lower() for groupID in const.metaGroupsUsed ]), self.MatchMetagroup),
         KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordTechLevel'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionTechLevel'), ['1', '2', '3'], self.MatchTechlevel),
         KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordMinSecurityLevel'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionMinSecurityLevel'), None, self.MatchMinSecurity),
         KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordMaxSecurityLevel'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionMaxSecurityLevel'), None, self.MatchMaxSecurity),
         KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordSecurityClass'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionSecurityClass'), self.localizationSortFunc([self.getByLabelFunc('UI/Inventory/AssetSearch/OptionSecurityHigh'),
          self.getByLabelFunc('UI/Inventory/AssetSearch/OptionSecurityEmpire'),
          self.getByLabelFunc('UI/Inventory/AssetSearch/OptionSecurityLow'),
          self.getByLabelFunc('UI/Inventory/AssetSearch/OptionSecurityNull'),
          self.getByLabelFunc('UI/Inventory/AssetSearch/OptionSecurityZero')]), self.MatchSecurityClass),
         KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordSolarSystem'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionSolarSystem'), None, self.MatchSolarSystem),
         KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordConstellation'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionConstellation'), None, self.MatchConstellation),
         KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordRegion'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionRegion'), None, self.MatchRegion),
         KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordStationName'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionStationName'), None, self.MatchStationName),
         KeywordOption(self.getByLabelFunc('UI/Inventory/AssetSearch/KeywordBlueprint'), self.getByLabelFunc('UI/Inventory/AssetSearch/DescriptionBlueprint'), self.localizationSortFunc([self.getByLabelFunc('UI/Inventory/AssetSearch/OptionBlueprintCopy'), self.getByLabelFunc('UI/Inventory/AssetSearch/OptionBlueprintOriginal')]), self.MatchBlueprint)]
        return self.localizationSortFunc(keywords, key=lambda x: x.keyword)

    def GetMetaLevel(self, typeID):
        try:
            return self.metaLevelByTypeID[typeID]
        except KeyError:
            metaLevel = int(self.godma.GetTypeAttribute(typeID, dogmaConst.attributeMetaLevel, 0))
            self.metaLevelByTypeID[typeID] = metaLevel
            return metaLevel

    def GetMetaGroupName(self, metaGroupID):
        try:
            return self.metaGroupNamesByMetaGroupID_lower[metaGroupID]
        except KeyError:
            metaGroup = self.cfg.invmetagroups.Get(metaGroupID)
            lower = metaGroup.name.lower()
            self.metaGroupNamesByMetaGroupID_lower[metaGroupID] = lower
            return lower

    def GetMetaGroupID(self, typeID):
        try:
            return self.metaGroupIDsByTypeIDs[typeID]
        except KeyError:
            metaGroupID = int(self.godma.GetTypeAttribute(typeID, dogmaConst.attributeMetaGroupID, 0))
            self.metaGroupIDsByTypeIDs[typeID] = metaGroupID
            return metaGroupID

    def GetTechLevel(self, typeID):
        try:
            return self.techLevelByTypeID[typeID]
        except KeyError:
            techLevel = int(self.godma.GetTypeAttribute(typeID, dogmaConst.attributeTechLevel, 1))
            self.techLevelByTypeID[typeID] = techLevel
            return techLevel

    def GetSystemSecurity(self, stationID):
        try:
            return self.systemSecByStationID[stationID]
        except KeyError:
            solarSystemID = self._GetSolarSystemID(stationID)
            systemSec = self.mapSvc.GetSecurityStatus(solarSystemID)
            self.systemSecByStationID[stationID] = systemSec
            return systemSec

    def GetSecurityClass(self, stationID):
        try:
            return self.securityClassByStationID_lower[stationID]
        except KeyError:
            solarSystemID = self._GetSolarSystemID(stationID)
            systemSecClass = self.mapSvc.GetSecurityClass(solarSystemID)
            self.securityClassByStationID_lower[stationID] = systemSecClass
            return systemSecClass

    def GetSolarsystemName(self, stationID):
        try:
            return self.solarsystemNamesByStationID_lower[stationID]
        except KeyError:
            solarSystemID = self._GetSolarSystemID(stationID)
            item = self.mapSvc.GetItem(solarSystemID)
            lower = item.itemName.lower()
            self.solarsystemNamesByStationID_lower[stationID] = lower
            return lower

    def _GetSolarSystemID(self, stationID):
        try:
            return self.solarsystemIDByStationID[stationID]
        except KeyError:
            solarSystemID = self.uiSvc.GetStation(stationID).solarSystemID
            self.solarsystemIDByStationID[stationID] = solarSystemID
            return solarSystemID

    def GetConstellationName(self, stationID):
        try:
            return self.constellationaNamesByStationID_lower[stationID]
        except KeyError:
            solarSystemID = self._GetSolarSystemID(stationID)
            constellationID = self.mapSvc.GetConstellationForSolarSystem(solarSystemID)
            item = self.mapSvc.GetItem(constellationID)
            lower = item.itemName.lower()
            self.constellationaNamesByStationID_lower[stationID] = lower
            return lower

    def GetRegionName(self, stationID):
        try:
            return self.regionNameByStationID_lower[stationID]
        except KeyError:
            solarSystemID = self._GetSolarSystemID(stationID)
            regionID = self.mapSvc.GetRegionForSolarSystem(solarSystemID)
            item = self.mapSvc.GetItem(regionID)
            lower = item.itemName.lower()
            self.regionNameByStationID_lower[stationID] = lower
            return lower

    def GetStationName(self, stationID):
        try:
            return self.stationNames_lower[stationID]
        except KeyError:
            stationName = self.cfg.evelocations.Get(stationID).locationName.lower()
            self.stationNames_lower[stationID] = stationName
            return stationName


class SearchNamesHelper(object):

    def __init__(self, uiSvc, *args):
        self.uiSvc = uiSvc
        self.typeNames_lower = {}
        self.groupNames_lower = {}
        self.categoryNames_lower = {}

    def GetTypeName(self, typeID):
        try:
            return self.typeNames_lower[typeID]
        except KeyError:
            lower = evetypes.GetName(typeID).lower()
            self.typeNames_lower[typeID] = lower
            return lower

    def GetGroupName(self, groupID):
        try:
            return self.groupNames_lower[groupID]
        except KeyError:
            lower = evetypes.GetGroupNameByGroup(groupID).lower()
            self.groupNames_lower[groupID] = lower
            return lower

    def GetCategoryName(self, categoryID):
        try:
            return self.categoryNames_lower[categoryID]
        except KeyError:
            lower = evetypes.GetCategoryNameByCategory(categoryID).lower()
            self.categoryNames_lower[categoryID] = lower
            return lower
