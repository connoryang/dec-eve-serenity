#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\mapViewSearch.py
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.scrollentries import ScrollEntryNode, SE_BaseClassCore
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.util.stringManip import Encode
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall
from eve.client.script.ui.control.searchinput import SearchInput
from eve.client.script.ui.util.searchUtil import Search
import weakref
import evetypes
import uthread
from localization import GetByLabel

class MapViewSearchControl(Container):
    default_align = uiconst.TOPLEFT
    default_width = 160
    default_height = 20
    searchInput = None
    searchResult = None
    searchFor = None
    mapView = None
    scrollListResult = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        if attributes.mapView:
            self.mapView = weakref.ref(attributes.mapView)
        self.icon = ButtonIcon(parent=self, align=uiconst.CENTERRIGHT, texturePath='res:/UI/Texture/Icons/searchMagnifyingGlass.png', pos=(0, 0, 24, 24), state=uiconst.UI_NORMAL, iconSize=24)
        self.icon.OnClick = self.ClickIcon
        self.searchFor = [const.searchResultConstellation,
         const.searchResultSolarSystem,
         const.searchResultRegion,
         const.searchResultStation]
        searchInput = SearchInput(name='MapViewSearchEdit', parent=self, align=uiconst.TOPRIGHT, width=0, maxLength=64, GetSearchEntries=self.GetSearchData, OnSearchEntrySelected=self.OnSearchEntrySelected, OnReturn=self.OnSearchInputConfirm, OnResultMenuClosed=self.OnResultMenuClosed, hinttext=GetByLabel('UI/Common/Buttons/Search'), opacity=0.0, setvalue=settings.char.ui.Get('mapView_searchString', None))
        searchInput.searchResultVisibleEntries = 10
        searchInput.SetHistoryVisibility(False)
        searchInput.OnFocusLost = self.OnSearchFocusLost
        self.searchInput = searchInput

    def ClickIcon(self, *args):
        self.ShowInput()

    def OnSearchFocusLost(self, *args):
        if not self.searchInput.HasResultMenu():
            self.HideInput()

    def OnResultMenuClosed(self, *args):
        if uicore.registry.GetFocus() is not self.searchInput:
            self.HideInput()

    def ShowInput(self):
        uicore.registry.SetFocus(self.searchInput)
        duration = 0.2
        uicore.animations.FadeTo(self.searchInput, startVal=self.searchInput.opacity, endVal=1.0, duration=duration)
        uicore.animations.FadeTo(self.icon, startVal=self.icon.opacity, endVal=0.0, callback=self.icon.Hide, duration=duration)
        uicore.animations.MorphScalar(self.searchInput, 'width', startVal=self.searchInput.width, endVal=self.width, duration=duration, callback=self.OnInputScaleDone)

    def HideInput(self):
        duration = 0.4
        uicore.animations.FadeTo(self.searchInput, startVal=self.searchInput.opacity, endVal=0.0, duration=duration)
        self.icon.Show()
        uicore.animations.FadeTo(self.icon, startVal=self.icon.opacity, endVal=1.0, duration=duration)
        uicore.animations.MorphScalar(self.searchInput, 'width', startVal=self.searchInput.width, endVal=0, duration=duration)

    def OnInputScaleDone(self, *args):
        resultMenu = self.searchInput.GetResultMenu()
        if resultMenu:
            l, t, w, h = self.GetAbsolute()
            resultMenu.left = l
        uthread.new(self.searchInput.SearchForData)

    def GetSearchData(self, searchString):
        self.scrollListResult = []
        searchString = Encode(searchString)
        searchString = searchString.lstrip()
        settings.char.ui.Set('mapView_searchString', searchString)
        if len(searchString) >= 64:
            self.scrollListResult.append(ScrollEntryNode(label=GetByLabel('UI/Common/SearchStringTooLong')))
        elif len(searchString) >= const.searchMinWildcardLength:
            self.searchInput.SetValue(searchString, docallback=False)
            results = Search(searchString, self.searchFor, getWindow=False)
            self.scrollListResult = self.PrepareResultScrollEntries(results)
        return self.scrollListResult

    def PrepareResultScrollEntries(self, results, *args):
        scrollList = []
        if not results:
            scrollList.append(ScrollEntryNode(label=GetByLabel('UI/Search/UniversalSearch/NoResultsReturned')))
        else:
            for groupEntry in results:
                entryType, typeList = groupEntry['groupItems']
                for entryData in typeList:
                    scrollList.append(ScrollEntryNode(decoClass=SearchResultEntry, **entryData))

        return scrollList

    def OnSearchInputConfirm(self, *args, **kwds):
        if self.scrollListResult and len(self.scrollListResult) == 1:
            self.OnSearchEntrySelected(self.scrollListResult)

    def OnSearchEntrySelected(self, selectedDataList, *args, **kwds):
        self.delaySelectionTimer = AutoTimer(500, self._OnSearchEntrySelectedDelayed, selectedDataList)

    def _OnSearchEntrySelectedDelayed(self, selectedDataList, *args, **kwds):
        self.delaySelectionTimer = None
        if self.mapView:
            mapView = self.mapView()
            if mapView:
                mapView.LoadSearchResult(selectedDataList)


class SearchResultEntry(SE_BaseClassCore):

    def Startup(self, *args):
        self.icon = Sprite(parent=self, pos=(2, 1, 16, 16), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        self.label = EveLabelSmall(parent=self, padding=(20, 3, 4, 0), state=uiconst.UI_DISABLED, align=uiconst.TOTOP)

    def Load(self, node):
        data = node
        self.typeID = data.Get('typeID', None)
        self.itemID = data.Get('itemID', None)
        if node.selected:
            self.Select()
        else:
            self.Deselect()
        self.label.text = data.label
        bracketIconPath = sm.GetService('bracket').GetBracketIcon(self.typeID)
        if bracketIconPath:
            self.icon.texturePath = bracketIconPath
        else:
            groupID = evetypes.GetGroupID(self.typeID)
            if groupID == const.groupRegion:
                self.icon.texturePath = 'res:/UI/Texture/Icons/Brackets/region.png'
            if groupID == const.groupConstellation:
                self.icon.texturePath = 'res:/UI/Texture/Icons/Brackets/constellation.png'
            if groupID == const.groupSolarSystem:
                self.icon.texturePath = 'res:/UI/Texture/Icons/Brackets/solarSystem.png'

    def GetHeight(self, *args):
        node, width = args
        return max(20, EveLabelSmall.MeasureTextSize(text=node.label, width=164)[1] + 5)

    def OnMouseEnter(self, *args):
        SE_BaseClassCore.OnMouseEnter(self, *args)
        if self.sr.node:
            eve.Message('ListEntryEnter')

    def OnClick(self, *args):
        if self.sr.node.Get('selectable', 1):
            self.sr.node.scroll.SelectNode(self.sr.node)
        eve.Message('ListEntryClick')
        if self.sr.node.Get('OnClick', None):
            self.sr.node.OnClick(self)

    def OnMouseDown(self, *args):
        SE_BaseClassCore.OnMouseDown(self, *args)
        if self.sr.node and self.sr.node.Get('OnMouseDown', None):
            self.sr.node.OnMouseDown(self)

    def OnMouseUp(self, *args):
        SE_BaseClassCore.OnMouseUp(self, *args)
        if self.sr.node and self.sr.node.Get('OnMouseUp', None):
            self.sr.node.OnMouseUp(self)

    def GetMenu(self):
        return sm.StartService('menu').CelestialMenu(self.sr.node.itemID)

    @classmethod
    def GetCopyData(cls, node):
        return node.label
