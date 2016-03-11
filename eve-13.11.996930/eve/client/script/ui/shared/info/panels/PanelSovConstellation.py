#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\info\panels\PanelSovConstellation.py
from carbon.common.script.util.format import StrFromColor
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control import entries as listentry
from eve.common.script.util.eveFormat import FmtSystemSecStatus
import carbonui.const as uiconst
from inventorycommon.const import typeTerritorialClaimUnit
from localization import GetByLabel
from sovDashboard import GetSovStructureInfoByTypeID
from sovDashboard.sovStatusEntries import SovSystemStatusEntry, SovStructureStatusEntry
from utillib import KeyVal

class PanelSovConstellation(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.constellationID = attributes.constellationID
        self.sovSvc = sm.GetService('sov')
        self.mapSvc = sm.GetService('map')

    def Load(self):
        self.Flush()
        self.scroll = Scroll(name='sovScroll', parent=self, padding=const.defaultPadding)
        systemsList = []
        for solarSystemID in self.mapSvc.GetLocationChildren(self.constellationID):
            systemsList.extend(self.GetSolarSystemInfo(solarSystemID))

        self.scroll.Load(contentList=systemsList)

    def GetSolarSystemInfo(self, solarSystemID):
        contentList = []
        data = KeyVal()
        data.label = self.GetSystemNameText(solarSystemID)
        headerEntry = listentry.Get(decoClass=SystemNameHeader, data=data)
        contentList.append(headerEntry)
        sovStructuresInfo = self.sovSvc.GetSovStructuresInfoForSolarSystem(solarSystemID)
        structureInfosByTypeID = GetSovStructureInfoByTypeID(sovStructuresInfo)
        tcuInfo = structureInfosByTypeID[typeTerritorialClaimUnit]
        isCapital = tcuInfo.get('isCapital', False)
        sovInfo = self.sovSvc.GetSovInfoForSolarsystem(solarSystemID, isCapital)
        multiplierInfo = self.GetMultiplierInfo(sovInfo, isCapital)
        statusEntry = listentry.Get(entryType=None, data=multiplierInfo, decoClass=SovSystemStatusEntry)
        contentList.append(statusEntry)
        if sovStructuresInfo:
            for structureTypeID, structureInfo in structureInfosByTypeID.iteritems():
                if not structureInfo.get('itemID', None):
                    continue
                entryData = KeyVal(structureInfo=structureInfo)
                structureEntry = listentry.Get(entryType=None, data=entryData, decoClass=SovStructureStatusEntry)
                contentList.append(structureEntry)

        return contentList

    def GetMultiplierInfo(self, sovInfo, isCapital):
        if isCapital:
            defenseBonusTexture = 'res:/UI/Texture/classes/Sov/bonusShieldCapital16.png'
        else:
            defenseBonusTexture = 'res:/UI/Texture/classes/Sov/bonusShield16.png'
        defenseBonusInfo = KeyVal(statusNameText=GetByLabel('UI/Sovereignty/ActivityDefenseMultiplier'), texturePath=defenseBonusTexture, currentIndex=None, bonusMultiplier=sovInfo.defenseMultiplier, extraHelpLabelPath='UI/Sovereignty/DefenseBonusExplanation', isCapital=isCapital)
        return defenseBonusInfo

    def GetSystemNameText(self, solarSystemID):
        solarSystemName = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.evelocations.Get(solarSystemID).name, info=('showinfo', const.groupSolarSystem, solarSystemID))
        sec, col = FmtSystemSecStatus(self.mapSvc.GetSecurityStatus(solarSystemID), 1)
        col.a = 1.0
        color = StrFromColor(col)
        text = '<color=%s>%s</color> %s' % (color, sec, solarSystemName)
        return text


class SystemNameHeader(listentry.Header):

    def Startup(self, args):
        listentry.Header.Startup(self, args)
        self.sr.label.state = uiconst.UI_NORMAL
