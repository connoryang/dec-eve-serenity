#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\info\panels\panelSov.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control import entries as listentry
from inventorycommon.const import typeTerritorialClaimUnit
from localization import GetByLabel
from sovDashboard import GetSovStructureInfoByTypeID
from sovDashboard.devIndexHints import SetNormalBoxHint, SetStrategyHint
from sovDashboard.sovStatusEntries import SovSystemStatusEntry, SovStructureStatusEntry, SovAllianceEntry
from utillib import KeyVal

class PanelSov(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.solarsystemID = attributes.solarsystemID
        self.sovSvc = sm.GetService('sov')

    def Load(self):
        self.Flush()
        self.scroll = Scroll(name='sovScroll', parent=self, padding=const.defaultPadding)
        contentList = []
        sovStructuresInfo = self.sovSvc.GetSovStructuresInfoForSolarSystem(self.solarsystemID)
        structureInfosByTypeID = GetSovStructureInfoByTypeID(sovStructuresInfo)
        tcuInfo = structureInfosByTypeID[typeTerritorialClaimUnit]
        isCapital = tcuInfo.get('isCapital', False)
        sovInfo = self.sovSvc.GetSovInfoForSolarsystem(self.solarsystemID, isCapital)
        entryData = KeyVal(sovHolderID=sovInfo.sovHolderID)
        sovAllianceEntry = listentry.Get(entryType=None, data=entryData, decoClass=SovAllianceEntry)
        contentList.append(sovAllianceEntry)
        headerEntry = listentry.Get('Header', {'label': GetByLabel('UI/Sovereignty/SystemSovStatus')})
        contentList.append(headerEntry)
        indexAndMultiplierInfo = self.GetIndexAndMultiplierInfo(sovInfo, isCapital)
        for entryData in indexAndMultiplierInfo:
            statusEntry = listentry.Get(entryType=None, data=entryData, decoClass=SovSystemStatusEntry)
            contentList.append(statusEntry)

        if sovStructuresInfo:
            headerEntry2 = listentry.Get('Header', {'label': GetByLabel('UI/Sovereignty/StructureSovStatus')})
            contentList.append(headerEntry2)
            for structureTypeID, structureInfo in structureInfosByTypeID.iteritems():
                if not structureInfo.get('itemID', None):
                    continue
                entryData = KeyVal(structureInfo=structureInfo)
                structureEntry = listentry.Get(entryType=None, data=entryData, decoClass=SovStructureStatusEntry)
                contentList.append(structureEntry)

        self.scroll.Load(contentList=contentList)

    def GetIndexAndMultiplierInfo(self, sovInfo, isCapital):
        if isCapital:
            defenseBonusTexture = 'res:/UI/Texture/classes/Sov/bonusShieldCapital16.png'
        else:
            defenseBonusTexture = 'res:/UI/Texture/classes/Sov/bonusShield16.png'
        defenseBonusInfo = KeyVal(indexID=None, statusNameText=GetByLabel('UI/Sovereignty/ActivityDefenseMultiplier'), texturePath=defenseBonusTexture, currentIndex=None, bonusMultiplier=sovInfo.defenseMultiplier, extraHelpLabelPath='UI/Sovereignty/DefenseBonusExplanation', isCapital=isCapital)
        strategicInfo = KeyVal(indexID=const.attributeDevIndexSovereignty, statusNameText=GetByLabel('UI/Sovereignty/StrategicIndex'), texturePath='res:/UI/Texture/classes/Sov/strategicIndex.png', currentIndex=sovInfo.strategicIndexLevel, bonusMultiplier=None, boxTooltipFunc=SetStrategyHint, extraHelpLabelPath='UI/Sovereignty/StrategicIndexExplanation', partialValue=sovInfo.strategicIndexRemainder)
        militaryInfo = KeyVal(indexID=const.attributeDevIndexMilitary, statusNameText=GetByLabel('UI/Sovereignty/MilitaryIndex'), texturePath='res:/UI/Texture/classes/Sov/militaryIndex.png', currentIndex=sovInfo.militaryIndexLevel, bonusMultiplier=None, boxTooltipFunc=SetNormalBoxHint, extraHelpLabelPath='UI/Sovereignty/MilitaryIndexExplanation', partialValue=sovInfo.militaryIndexRemainder)
        industryInfo = KeyVal(indexID=const.attributeDevIndexIndustrial, statusNameText=GetByLabel('UI/Sovereignty/IndustryIndex'), texturePath='res:/UI/Texture/classes/Sov/industryIndex.png', currentIndex=sovInfo.industrialIndexLevel, bonusMultiplier=None, boxTooltipFunc=SetNormalBoxHint, extraHelpLabelPath='UI/Sovereignty/IndustryIndexExplanation', partialValue=sovInfo.industrialIndexRemainder)
        return [defenseBonusInfo,
         strategicInfo,
         militaryInfo,
         industryInfo]
