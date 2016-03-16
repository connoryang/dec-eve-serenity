#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\colorModes\colorModeInfoBase.py
from carbonui.control.scrollentries import ScrollEntryNode
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium
from eve.client.script.ui.control.searchinput import SearchInput
from eve.client.script.ui.util.searchUtil import Search
import eve.client.script.ui.control.entries as listentry
from localization import GetByLabel
import weakref

class ColorModeInfoBase(Container):
    default_align = uiconst.TOLEFT_NOPUSH
    default_width = 220
    default_padLeft = 8
    default_padTop = 8
    searchHandler = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.headerLabel = EveLabelLarge(parent=self, align=uiconst.TOTOP, bold=True)
        self.resultLabel = EveLabelMedium(parent=self, align=uiconst.TOTOP)
        self.mapView = weakref.ref(attributes.mapView)

    def LoadColorModeInfo(self, colorMode, colorModeInfo, colorData, *args):
        if not self.mapView:
            return
        mapView = self.mapView()
        if not mapView:
            return
        if callable(colorModeInfo.header):
            label = colorModeInfo.header(colorMode)
        else:
            label = colorModeInfo.header
        self.headerLabel.text = label
        if self.searchHandler:
            if colorModeInfo.searchHandler and isinstance(self.searchHandler, colorModeInfo.searchHandler):
                return
            self.searchHandler.Close()
            self.searchHandler = None
        if colorModeInfo.searchHandler:
            self.searchHandler = colorModeInfo.searchHandler(parent=self, mapView=mapView)


class ColorModeInfoSearchBase(Container):
    default_align = uiconst.TOTOP
    default_height = 32
    settingsKey = None
    searchFor = None
    searchString = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.mapView = weakref.ref(attributes.mapView)
        searchInput = SearchInput(name=self.settingsKey, parent=self, align=uiconst.TOTOP, width=0, maxLength=64, GetSearchEntries=self.GetSearchData, OnSearchEntrySelected=self.OnSearchEntrySelected, OnReturn=self.OnSearchInputConfirm, hinttext=GetByLabel('UI/Common/Buttons/Search'))
        searchInput.searchResultVisibleEntries = 10
        searchInput.SetHistoryVisibility(False)
        searchInput.ShowClearButton()
        searchInput.SetValue(settings.char.ui.Get('%s_searchString' % self.settingsKey, None))
        self.searchInput = searchInput

    def GetSearchData(self, searchString):
        searchString = searchString.lstrip()
        settings.char.ui.Set('%s_searchString' % self.settingsKey, searchString)
        if searchString == self.searchString:
            return self.scrollListResult
        self.searchString = searchString
        if len(searchString) >= 3:
            self.searchInput.SetValue(searchString, docallback=False)
            results = Search(searchString, self.searchFor, getWindow=False)
            self.scrollListResult = self.PrepareResultScrollEntries(results)
        else:
            self.scrollListResult = []
            self.OnSearchCleared()
        return self.scrollListResult

    def PrepareResultScrollEntries(self, results, *args):
        scrollList = []
        if not results:
            scrollList.append(ScrollEntryNode(label=GetByLabel('UI/Search/UniversalSearch/NoResultsReturned')))
        else:
            for groupEntry in results:
                entryType, typeList = groupEntry['groupItems']
                for entryData in typeList:
                    scrollList.append(listentry.Get(entryType, entryData))

        return scrollList

    def OnSearchInputConfirm(self, *args, **kwds):
        if self.scrollListResult and len(self.scrollListResult) == 1:
            self.OnSearchEntrySelected(self.scrollListResult)

    def OnSearchEntrySelected(self, *args, **kwds):
        pass
