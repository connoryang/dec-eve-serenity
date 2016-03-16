#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sovDashboard\claimedSystems.py
from entosis.occupancyCalculator import GetOccupancyMultiplier
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.control.utilButtons.showInMapButton import ShowInMapButton
from inventorycommon.const import typeTerritorialClaimUnit
from sovDashboard.dashboard import SovDashboard
from sovDashboard.dashboardEntry import DashboardEntry
from sovDashboard.defenseMultiplierIcon import DefenseMultiplierIcon
import carbonui.const as uiconst
from sovDashboard.indexBars import IndexBars
from utillib import KeyVal
import listentry
from eve.client.script.ui.control.glowSprite import GlowSprite
from localization import GetByLabel
import uthread
import blue

class ClaimedSystemEntry(DashboardEntry):

    def AddExtraColumns(self):
        multiplier = self.node.multiplier
        devIndexes = self.node.devIndexes
        defenseMultiplierIcon = DefenseMultiplierIcon(parent=self.contentContainer, align=uiconst.CENTERLEFT, iconSize=32, currentMultiplier=multiplier, devIndexes=devIndexes, isCapital=self.node.isCapital, state=uiconst.UI_DISABLED, showValue=True)
        self.defenseMultiplierIcon = defenseMultiplierIcon
        self.centerAlignedColumns.append((self.defenseMultiplierIcon, 4))
        columnIndex = 5
        for indexValue in (devIndexes[2], devIndexes[0], devIndexes[1]):
            indexBars = IndexBars(parent=self.contentContainer, currentIndex=indexValue, align=uiconst.CENTERLEFT)
            self.centerAlignedColumns.append((indexBars, columnIndex))
            columnIndex += 1

    def AddButtons(self):
        ShowInMapButton(parent=self, align=uiconst.CENTERRIGHT, itemID=self.node['solarSystemID'], left=30)
        CapitalButton(parent=self, align=uiconst.CENTERRIGHT, isCapital=self.node['isCapital'], solarSystemID=self.node['solarSystemID'], left=6)
        self.contentContainer.padRight = 54

    @staticmethod
    def GetColumnsMinSize():
        return {GetByLabel('UI/Common/LocationTypes/System'): 100,
         GetByLabel('UI/Common/LocationTypes/Constellation'): 100,
         GetByLabel('UI/Common/LocationTypes/Region'): 100,
         GetByLabel('UI/Common/Jumps'): 60,
         GetByLabel('UI/Sovereignty/StrategicIndex'): 110,
         GetByLabel('UI/Sovereignty/MilitaryIndex'): 110,
         GetByLabel('UI/Sovereignty/IndustryIndex'): 110}

    @staticmethod
    def GetFixedColumns():
        return {GetByLabel('UI/Sovereignty/DefenseMultiplierBonus'): 100}

    @staticmethod
    def GetHeaders():
        ret = [GetByLabel('UI/Common/LocationTypes/System'),
         GetByLabel('UI/Common/LocationTypes/Constellation'),
         GetByLabel('UI/Common/LocationTypes/Region'),
         GetByLabel('UI/Common/Jumps'),
         GetByLabel('UI/Sovereignty/DefenseMultiplierBonus'),
         GetByLabel('UI/Sovereignty/StrategicIndex'),
         GetByLabel('UI/Sovereignty/MilitaryIndex'),
         GetByLabel('UI/Sovereignty/IndustryIndex')]
        return ret

    def UpdateCapitalSystem(self, *args):
        if eve.Message('CustomQuestion', {'header': GetByLabel('UI/Sovereignty/SetNewCapital'),
         'question': GetByLabel('UI/Sovereignty/SetNewCapitalDetails')}, uiconst.YESNO) != uiconst.ID_YES:
            return
        sm.GetService('alliance').SetCapitalSystem(self.node.solarSystemID)

    def GetMenu(self):
        return sm.GetService('menu').CelestialMenu(self.node.solarSystemID)


class ClaimedSystemsDashboard(SovDashboard):
    __notifyevents__ = SovDashboard.__notifyevents__ + ['OnCapitalSystemChanged']
    searchSettingKey = 'claimedSystemsDashboard_searchString'
    scrollID = 'claimedSystemsDashboard'
    entryClass = ClaimedSystemEntry
    emptyHintLabel = 'UI/Sovereignty/ClaimedListNoSystems'

    def ApplyAttributes(self, attributes):
        SovDashboard.ApplyAttributes(self, attributes)
        self.searchInput.left += const.defaultPadding
        self.reloadBtn.display = False
        EveLabelMedium(parent=self.topSection, text=GetByLabel('UI/Corporations/CorporationWindow/Alliances/Systems'), align=uiconst.CENTERLEFT, left=const.defaultPadding * 2)
        FillThemeColored(parent=self.topSection, colorType=uiconst.COLORTYPE_UIHEADER, opacity=0.15, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         1))

    def IncludesTCU(self, structures):
        for eachStructure in structures:
            if eachStructure.typeID == typeTerritorialClaimUnit:
                return True

        return False

    def ReloadDashboard(self):
        self.scroll.Clear()
        self.sortedScrollNodes = []
        structuresPerSolarsystem = self.sovSvc.GetSovereigntyStructuresInfoForAlliance()
        indexData = self.sovSvc.GetAllDevelopmentIndicesMapped()
        cfg.evelocations.Prime(structuresPerSolarsystem.keys())
        cfg.evelocations.Prime({cfg.mapSystemCache.Get(solarsystemID).constellationID for solarsystemID in structuresPerSolarsystem})
        cfg.evelocations.Prime({cfg.mapSystemCache.Get(solarsystemID).regionID for solarsystemID in structuresPerSolarsystem})
        myCapitalSystemID = self.sovSvc.GetMyCapitalSystem()
        GetAutopilotJumpCount = sm.GetService('clientPathfinderService').GetAutopilotJumpCount
        GetIndexLevel = self.sovSvc.GetIndexLevel
        GetLocation = cfg.evelocations.Get
        batchSize = 5
        batchList = []
        for solarsystemID, structures in structuresPerSolarsystem.iteritems():
            if not self.IncludesTCU(structures):
                continue
            systemIndexInfo = indexData.get(solarsystemID, None)
            if systemIndexInfo:
                militaryIndexLevel = GetIndexLevel(systemIndexInfo[const.attributeDevIndexMilitary], const.attributeDevIndexMilitary).level
                industrialIndexLevel = GetIndexLevel(systemIndexInfo[const.attributeDevIndexIndustrial], const.attributeDevIndexIndustrial).level
                strategicIndexLevel = GetIndexLevel(systemIndexInfo[const.attributeDevIndexSovereignty], const.attributeDevIndexSovereignty).level
            else:
                militaryIndexLevel = 0
                industrialIndexLevel = 0
                strategicIndexLevel = 0
            solarSystemMapSystemCache = cfg.mapSystemCache.Get(solarsystemID)
            constellationID = solarSystemMapSystemCache.constellationID
            regionID = solarSystemMapSystemCache.regionID
            jumpCount = GetAutopilotJumpCount(session.solarsystemid2, solarsystemID)
            solarsystemSortingString = GetLocation(solarsystemID).name.lower()
            constellationSortingString = GetLocation(constellationID).name.lower()
            regionSortingString = cfg.evelocations.Get(regionID).name.lower()
            isCapital = myCapitalSystemID == solarsystemID
            multiplier = 1 / GetOccupancyMultiplier(militaryIndexLevel, industrialIndexLevel, strategicIndexLevel, isCapital)
            sortValues = [solarsystemSortingString,
             constellationSortingString,
             regionSortingString,
             jumpCount,
             multiplier,
             strategicIndexLevel,
             militaryIndexLevel,
             industrialIndexLevel]
            searchValue = '%s %s %s' % (solarsystemSortingString, constellationSortingString, regionSortingString)
            if isCapital:
                searchValue += ' %s' % GetByLabel('UI/Sovereignty/CurrentCapital').lower()
            entryData = KeyVal(isCapital=isCapital, devIndexes=(militaryIndexLevel, industrialIndexLevel, strategicIndexLevel), multiplier=multiplier, jumpCount=jumpCount, solarSystemID=solarsystemID, constellationID=constellationID, regionID=regionID, columnWidths=self.columnWidths, sortValues=sortValues, height=self.entryClass.ENTRYHEIGHT, fixedHeight=self.entryClass.ENTRYHEIGHT, searchValue=searchValue)
            entry = listentry.Get(data=entryData, decoClass=self.entryClass)
            batchList.append(entry)
            if len(batchList) == batchSize:
                self.AddBatchToScroll(batchList)
                batchList = []
                blue.pyos.BeNice(100)
                if self.destroyed:
                    return

        if batchList:
            self.AddBatchToScroll(batchList)
        else:
            self.UpdateScrollList()

    def OnCapitalSystemChanged(self, *args, **kwds):
        uthread.new(self.ReloadDashboard)


class CapitalButton(GlowSprite):
    default_texturePath = 'res:/ui/Texture/classes/Sov/CapitalStarSelection.png'
    default_width = 20
    default_height = 20

    def ApplyAttributes(self, attributes):
        if attributes.isCapital:
            attributes.texturePath = 'res:/ui/Texture/classes/Sov/CapitalStarSelection20.png'
            attributes.hint = GetByLabel('UI/Sovereignty/CurrentCapital')
        else:
            attributes.texturePath = 'res:/UI/Texture/classes/Sov/selectCapitalButton20.png'
            attributes.hint = GetByLabel('UI/Sovereignty/SetAsCapital')
        GlowSprite.ApplyAttributes(self, attributes)
        self.isCapital = attributes.isCapital
        self.solarSystemID = attributes.solarSystemID

    def OnClick(self, *args):
        if not self.isCapital:
            if eve.Message('CustomQuestion', {'header': GetByLabel('UI/Sovereignty/SetNewCapital'),
             'question': GetByLabel('UI/Sovereignty/SetNewCapitalDetails')}, uiconst.YESNO) != uiconst.ID_YES:
                return
            sm.GetService('alliance').SetCapitalSystem(self.solarSystemID)
