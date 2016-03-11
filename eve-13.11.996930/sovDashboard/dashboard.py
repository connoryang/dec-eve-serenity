#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sovDashboard\dashboard.py
from carbonui.primitives.container import Container
from carbonui.control.basicDynamicScroll import BasicDynamicScroll
from entosis.entosisConst import STRUCTURE_SCORE_UPDATED
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.searchinput import SearchInput
from eve.client.script.ui.inflight.overViewLabel import SortHeaders
from eve.client.script.ui.control import entries as listentry
from localization import GetByLabel
from sovDashboard import GetStructureStatusString, GetStartTimeFromStructureInfo, ShouldUpdateStructureInfo
from sovDashboard.dashboardEntry import DashboardEntry
import carbonui.const as uiconst
import uthread
import blue
import bisect
from utillib import KeyVal

class SovDashboard(Container):
    __notifyevents__ = ['OnSolarsystemSovStructureChanged']
    searchSettingKey = 'sovDashboard_searchString'
    scrollID = 'sovDashboard'
    entryClass = DashboardEntry
    emptyHintLabel = 'UI/Sovereignty/DashboardNoStructures'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sovSvc = sm.GetService('sov')
        self.sortedScrollNodes = []
        self.topSection = Container(parent=self, align=uiconst.TOTOP)
        self.searchString = settings.char.ui.Get(self.searchSettingKey, None)
        searchInput = SearchInput(name=self.searchSettingKey, parent=self.topSection, align=uiconst.TOPRIGHT, width=120, left=const.defaultPadding, top=const.defaultPadding, maxLength=64, GetSearchEntries=self.GetSearchData, hinttext=GetByLabel('UI/Common/Buttons/Search'), setvalue=self.searchString)
        searchInput.ShowClearButton()
        searchInput.searchResultVisibleEntries = 10
        searchInput.SetHistoryVisibility(False)
        self.searchInput = searchInput
        self.reloadBtn = Button(parent=self.topSection, label=GetByLabel('UI/Commands/Refresh'), align=uiconst.TOPLEFT, left=const.defaultPadding, top=const.defaultPadding, func=self.ReloadDashboard)
        self.topSection.height = searchInput.height + searchInput.top * 2
        self.scroll = BasicDynamicScroll(parent=self, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         const.defaultPadding), id=self.scrollID)
        sortHeaders = SortHeaders(parent=self.scroll.sr.maincontainer, settingsID=self.scrollID, idx=0)
        sortHeaders.SetMinSizeByColumnID(self.entryClass.GetColumnsMinSize())
        sortHeaders.OnColumnSizeChange = self.OnColumnSizeChanged
        sortHeaders.OnSortingChange = self.OnSortingChange
        sortHeaders.OnColumnSizeReset = self.OnColumnSizeReset
        self.sortHeaders = sortHeaders
        self.sortHeaders.CreateColumns(self.entryClass.GetHeaders(), fixedColumns=self.entryClass.GetFixedColumns())
        columnWidthsByName = self.sortHeaders.GetCurrentSizes()
        self.columnWidths = [ columnWidthsByName[header] for header in self.entryClass.GetHeaders() ]
        sm.RegisterNotify(self)

    def CreateWindow(self):
        uthread.new(self.ReloadDashboard)

    def ReloadDashboard(self, *args):
        self.scroll.Clear()
        self.sortedScrollNodes = []
        structuresPerSolarsystem = sm.GetService('sov').GetSovereigntyStructuresInfoForAlliance()
        cfg.evelocations.Prime(structuresPerSolarsystem.keys())
        cfg.evelocations.Prime({cfg.mapSystemCache.Get(solarsystemID).constellationID for solarsystemID in structuresPerSolarsystem})
        cfg.evelocations.Prime({cfg.mapSystemCache.Get(solarsystemID).regionID for solarsystemID in structuresPerSolarsystem})
        GetAutopilotJumpCount = sm.GetService('clientPathfinderService').GetAutopilotJumpCount
        batchSize = 5
        batchList = []
        for solarsystemID, structures in structuresPerSolarsystem.iteritems():
            solarSystemMapSystemCache = cfg.mapSystemCache.Get(solarsystemID)
            constellationID = solarSystemMapSystemCache.constellationID
            regionID = solarSystemMapSystemCache.regionID
            jumpCount = GetAutopilotJumpCount(session.solarsystemid2, solarsystemID)
            solarsystemSortingString = cfg.evelocations.Get(solarsystemID).name.lower()
            constellationSortingString = cfg.evelocations.Get(constellationID).name.lower()
            regionSortingString = cfg.evelocations.Get(regionID).name.lower()
            for structureInfo in structures:
                structureStatusString, timeString = GetStructureStatusString(structureInfo, getTimeString=True)
                structureStatusString = structureStatusString.lower()
                sortValues = [solarsystemSortingString,
                 constellationSortingString,
                 regionSortingString,
                 jumpCount,
                 structureInfo.defenseMultiplier,
                 structureInfo.typeID,
                 structureStatusString,
                 timeString]
                structureInfo.solarSystemID = solarsystemID
                structureInfo.constellationID = constellationID
                structureInfo.regionID = regionID
                entryData = KeyVal(jumpCount=jumpCount, structureInfo=structureInfo, solarSystemID=solarsystemID, constellationID=constellationID, regionID=regionID, columnWidths=self.columnWidths, sortValues=sortValues, height=self.entryClass.ENTRYHEIGHT, fixedHeight=self.entryClass.ENTRYHEIGHT, searchValue='%s %s %s %s %s' % (solarsystemSortingString,
                 constellationSortingString,
                 regionSortingString,
                 structureStatusString,
                 timeString.lower()))
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

    def AddBatchToScroll(self, batch):
        columns = self.entryClass.GetHeaders()
        activeColumn, columnDirection = self.sortHeaders.GetCurrentActive()
        activeColumnIndex = columns.index(activeColumn)

        def GetSortValue(_node):
            return _node.sortValues[activeColumnIndex]

        sortValues = [ GetSortValue(node) for node in self.sortedScrollNodes ]
        for entry in batch:
            entrySortValue = GetSortValue(entry)
            insertionIndex = bisect.bisect_right(sortValues, entrySortValue)
            sortValues.insert(insertionIndex, entrySortValue)
            self.sortedScrollNodes.insert(insertionIndex, entry)

        self.UpdateScrollList()

    def UpdateScrollList(self):
        activeColumn, columnDirection = self.sortHeaders.GetCurrentActive()
        if not columnDirection:
            scrollNodes = self.sortedScrollNodes[:]
            scrollNodes.reverse()
        else:
            scrollNodes = self.sortedScrollNodes
        if self.searchString:
            lSearchString = self.searchString.lower()
            filterNodes = []
            for scrollNode in scrollNodes:
                if scrollNode.searchValue.find(lSearchString) != -1:
                    filterNodes.append(scrollNode)

            scrollNodes = filterNodes
            emptyListHint = GetByLabel('UI/Common/NothingFound')
        else:
            emptyListHint = GetByLabel(self.emptyHintLabel, allianceName=cfg.eveowners.Get(session.allianceid).name)
        self.scroll.SetFilteredNodes(scrollNodes)
        if scrollNodes:
            self.scroll.ShowHint(None)
        else:
            self.scroll.ShowHint(emptyListHint)

    def OnColumnSizeChanged(self, *args):
        columnWidthsByName = self.sortHeaders.GetCurrentSizes()
        self.columnWidths = [ columnWidthsByName[header] for header in self.entryClass.GetHeaders() ]
        self.UpdateScrollEntriesColumns()

    def OnSortingChange(self, *args):
        columns = self.entryClass.GetHeaders()
        activeColumn, columnDirection = self.sortHeaders.GetCurrentActive()
        activeColumnIndex = columns.index(activeColumn)

        def GetSortValue(_node):
            return _node.sortValues[activeColumnIndex]

        self.sortedScrollNodes = sorted(self.sortedScrollNodes, key=GetSortValue)
        self.UpdateScrollList()

    def OnColumnSizeReset(self, columnID, *args):
        minSize = 0
        for node in self.scroll.GetNodes():
            minSize = max(minSize, self.entryClass.GetColumnMinSize(node, columnID))

        self.sortHeaders.SetColumnSize(columnID, minSize)

    def UpdateScrollEntriesColumns(self):
        for node in self.scroll.GetNodes():
            if node.panel:
                node.panel.OnColumnResize(self.columnWidths)
            else:
                node.columnWidths = self.columnWidths

    def GetSearchData(self, searchString):
        settings.char.ui.Set(self.searchSettingKey, searchString)
        self.searchString = searchString
        self.UpdateScrollList()

    def OnSolarsystemSovStructureChanged(self, solarsystemID, whatChanged, sourceItemID = None):
        if STRUCTURE_SCORE_UPDATED not in whatChanged:
            return
        for node in self.scroll.GetNodes():
            if not ShouldUpdateStructureInfo(node.structureInfo, sourceItemID):
                continue
            newStructureInfo = self.sovSvc.GetSpecificSovStructuresInfoInSolarSystem(solarsystemID, sourceItemID)
            if node.panel and not node.panel.destroyed:
                node.panel.ChangeStructureInfoAndUpdate(newStructureInfo, whatChanged=whatChanged)
            else:
                node.structureInfo = newStructureInfo
            break
