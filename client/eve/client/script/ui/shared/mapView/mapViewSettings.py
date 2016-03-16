#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\mapViewSettings.py
from carbon.common.script.sys.service import ROLE_GML
from carbonui.control.scrollentries import ScrollEntryNode, SE_BaseClassCore
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.fill import Fill
from carbonui.primitives.layoutGrid import LayoutGrid, LayoutGridRow
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.buttons import ButtonIcon, Button
from eve.client.script.ui.control.checkbox import Checkbox, RadioButtonUnderlay
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.themeColored import FillThemeColored, LineThemeColored
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.mapViewColorHandler import GetFormatFunction, GetFormatFunctionLabel
from eve.client.script.ui.shared.mapView.mapViewConst import VIEWMODE_COLOR_SETTINGS, VIEWMODE_LAYOUT_REGIONS, VIEWMODE_LAYOUT_CONSTELLATIONS, VIEWMODE_LAYOUT_DEFAULT, VIEWMODE_LAYOUT_SETTINGS, DEFAULT_MAPVIEW_SETTINGS, VIEWMODE_LAYOUT_SHOW_ABSTRACT_SETTINGS, VIEWMODE_LINES_ALL, VIEWMODE_LINES_SELECTION_REGION_NEIGHBOURS, VIEWMODE_LINES_SELECTION_REGION, VIEWMODE_LINES_SELECTION, VIEWMODE_LINES_NONE, VIEWMODE_LINES_SETTINGS, VIEWMODE_LAYOUT_SHOW_ABSTRACT_DEFAULT, VIEWMODE_LAYOUT_SOLARSYSTEM, VIEWMODE_MARKERS_SETTINGS, VIEWMODE_MARKERS_OPTIONS, VIEWMODE_FOCUS_SELF, VIEWMODE_MARKERS_OPTIONS_CUSTOM, VIEWMODE_MARKERS_CUSTOM_LABELS, VIEWMODE_COLOR_RECENT, VIEWMODE_COLOR_RECENT_MAX
from eve.client.script.ui.shared.maps.mapcommon import *
from eve.client.script.ui.tooltips.tooltipUtil import RefreshTooltipForOwner
import evetypes
import localization
import service
import blue
import eve.client.script.ui.shared.maps.maputils as maputils
from utillib import KeyVal
import uthread
ICON_ROOT = 'res:/UI/Texture/classes/MapView/'
ICON_MAP_BY_ID = {VIEWMODE_LINES_ALL: ICON_ROOT + 'icon_all_lines.png',
 VIEWMODE_LINES_SELECTION: ICON_ROOT + 'icon_selectiononly_lines.png',
 VIEWMODE_LINES_SELECTION_REGION: ICON_ROOT + 'icon_region_lines.png',
 VIEWMODE_LAYOUT_SOLARSYSTEM: ICON_ROOT + 'icon_no_group.png',
 VIEWMODE_LAYOUT_CONSTELLATIONS: ICON_ROOT + 'icon_const_group.png',
 VIEWMODE_LAYOUT_REGIONS: ICON_ROOT + 'icon_reg_group.png'}
LABEL_MAP_BY_ID = {VIEWMODE_LINES_ALL: localization.GetByLabel('UI/Map/MapPallet/cbAllLinesOnly'),
 VIEWMODE_LINES_SELECTION: localization.GetByLabel('UI/Map/MapPallet/cbSelectionLinesOnly'),
 VIEWMODE_LINES_SELECTION_REGION: localization.GetByLabel('UI/Map/MapPallet/cbSelectionRegionLinesOnly'),
 VIEWMODE_LAYOUT_SOLARSYSTEM: localization.GetByLabel('UI/Map/Layout/NoGrouping'),
 VIEWMODE_LAYOUT_CONSTELLATIONS: localization.GetByLabel('UI/Map/Layout/GroupByConstellations'),
 VIEWMODE_LAYOUT_REGIONS: localization.GetByLabel('UI/Map/Layout/GroupByRegions'),
 VIEWMODE_LAYOUT_SHOW_ABSTRACT_SETTINGS: localization.GetByLabel('UI/Map/Layout/AbstractLayout')}
MV_GROUPS_BY_ID = {VIEWMODE_LAYOUT_SETTINGS: [VIEWMODE_LAYOUT_SOLARSYSTEM, VIEWMODE_LAYOUT_CONSTELLATIONS, VIEWMODE_LAYOUT_REGIONS],
 VIEWMODE_LINES_SETTINGS: [VIEWMODE_LINES_ALL, VIEWMODE_LINES_SELECTION_REGION, VIEWMODE_LINES_SELECTION]}

def GetMapViewSetting(settingGroupKey, mapViewID):
    return settings.char.ui.Get('%s_%s' % (settingGroupKey, mapViewID), DEFAULT_MAPVIEW_SETTINGS[settingGroupKey])


def SetMapViewSetting(settingGroupKey, settingValue, mapViewID):
    settings.char.ui.Set('%s_%s' % (settingGroupKey, mapViewID), settingValue)


def IsMarkerGroupEnabled(markerGroupID, mapViewID):
    markerGroups = GetMapViewSetting(VIEWMODE_MARKERS_SETTINGS, mapViewID)
    return markerGroupID in markerGroups


class MapViewSettingButtons(LayoutGrid):
    onSettingsChangedCallback = None

    def ApplyAttributes(self, attributes):
        LayoutGrid.ApplyAttributes(self, attributes)
        self.columns = 4
        self.buttonIconByGroupKey = {}
        self.onSettingsChangedCallback = attributes.onSettingsChangedCallback
        self.mapViewID = attributes.mapViewID
        MapViewCheckboxOptionButton(parent=self, settingGroupKeys=(VIEWMODE_LAYOUT_SETTINGS, VIEWMODE_LINES_SETTINGS, VIEWMODE_LAYOUT_SHOW_ABSTRACT_SETTINGS), callback=self.OnSettingsChanged, mapViewID=self.mapViewID)
        MapViewColorModeSettingButton(parent=self, settingGroupKey=VIEWMODE_COLOR_SETTINGS, callback=self.OnSettingsChanged, mapViewID=self.mapViewID)
        MapViewMarkersSettingButton(parent=self, callback=self.OnSettingsChanged, mapViewID=self.mapViewID)
        focusSelf = ButtonIcon(parent=self, width=26, height=26, iconSize=16, func=self.FocusSelf, hint=localization.GetByLabel('UI/Map/FocusCurrentLocation'), texturePath='res:/UI/Texture/classes/MapView/focusIcon.png')
        focusSelf.tooltipPointer = uiconst.POINT_TOP_1

    def Close(self, *args):
        LayoutGrid.Close(self, *args)
        self.buttonIconByGroupKey = None
        self.onSettingsChangedCallback = None

    def FocusSelf(self, *args):
        if self.onSettingsChangedCallback:
            self.onSettingsChangedCallback(VIEWMODE_FOCUS_SELF, session.charid)

    def OnSettingsChanged(self, settingGroupKey, settingValue, mapViewID = None):
        button = self.buttonIconByGroupKey.get(settingGroupKey, None)
        if button:
            button.ReloadSettingValue()
        if self.onSettingsChangedCallback:
            self.onSettingsChangedCallback(settingGroupKey, settingValue)

    def UpdateButtons(self):
        for groupID, button in self.buttonIconByGroupKey.iteritems():
            button.ReloadSettingValue()


class MapViewSettingButton(ButtonIcon):
    default_iconSize = 24
    default_width = 26
    default_height = 26
    settingGroupKey = None
    callback = None
    mapViewID = None

    def ApplyAttributes(self, attributes):
        ButtonIcon.ApplyAttributes(self, attributes)
        self.settingGroupKey = attributes.settingGroupKey
        self.mapViewID = attributes.mapViewID
        self.callback = attributes.callback
        self.ReloadSettingValue()

    def ReloadSettingValue(self):
        currentActive = GetMapViewSetting(self.settingGroupKey, self.mapViewID)
        self.SetTexturePath(ICON_MAP_BY_ID[currentActive])
        uicore.animations.BlinkOut(self.icon, startVal=1.0, endVal=0.0, duration=0.2, loops=2, curveType=uiconst.ANIM_BOUNCE)

    def Close(self, *args):
        ButtonIcon.Close(self, *args)
        self.callback = None

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if uicore.uilib.leftbtn:
            return
        tooltipPanel.columns = 2
        tooltipPanel.margin = 2
        for settingsID in MV_GROUPS_BY_ID[self.settingGroupKey]:
            tooltipPanel.AddRow(rowClass=ButtonTooltipRow, settingValue=settingsID, settingGroupKey=self.settingGroupKey, callback=self.callback, mapViewID=self.mapViewID)

        tooltipPanel.state = uiconst.UI_NORMAL

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_1


class MapViewMarkersSettingButton(ButtonIcon):
    default_iconSize = 24
    default_width = 26
    default_height = 26
    settingGroupKey = None
    mapViewID = None
    callback = None

    def ApplyAttributes(self, attributes):
        ButtonIcon.ApplyAttributes(self, attributes)
        self.settingGroupKey = VIEWMODE_MARKERS_SETTINGS
        self.mapViewID = attributes.Get('mapViewID', mapViewConst.MAPVIEW_PRIMARY_ID)
        self.callback = attributes.callback
        self.SetTexturePath(ICON_ROOT + 'markersIcon.png')

    def Close(self, *args):
        ButtonIcon.Close(self, *args)
        self.callback = None

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if uicore.uilib.leftbtn:
            return
        tooltipPanel.columns = 2
        tooltipPanel.AddLabelSmall(text=localization.GetByLabel('UI/Map/Markers'), bold=True, cellPadding=(8, 4, 4, 2), colSpan=tooltipPanel.columns)
        divider = LineThemeColored(align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=1, padding=(1, 1, 1, 0), opacity=0.3)
        tooltipPanel.AddCell(divider, cellPadding=(0, 0, 0, 2), colSpan=tooltipPanel.columns)
        currentActive = GetMapViewSetting(self.settingGroupKey, self.mapViewID)
        sortList = []
        for groupID in VIEWMODE_MARKERS_OPTIONS:
            sortList.append((evetypes.GetGroupNameByGroup(groupID), groupID))

        for customID in VIEWMODE_MARKERS_OPTIONS_CUSTOM:
            sortList.append((localization.GetByLabel(VIEWMODE_MARKERS_CUSTOM_LABELS[customID]), customID))

        for optionName, optionID in sorted(sortList):
            checkBox = Checkbox(align=uiconst.TOPLEFT, text=optionName, checked=optionID in currentActive, wrapLabel=False, callback=self.OnSettingButtonCheckBoxChange, retval=optionID, prefstype=None)
            tooltipPanel.AddCell(cellObject=checkBox, colSpan=tooltipPanel.columns, cellPadding=(5, 0, 5, 0))

        tooltipPanel.AddSpacer(width=2, height=2, colSpan=tooltipPanel.columns)
        tooltipPanel.state = uiconst.UI_NORMAL

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_1

    def GetTooltipDelay(self):
        return 5

    def OnSettingButtonCheckBoxChange(self, checkbox, *args, **kwds):
        currentActive = set(GetMapViewSetting(self.settingGroupKey, self.mapViewID))
        active = checkbox.GetValue()
        if active:
            currentActive.add(checkbox.data['value'])
        else:
            try:
                currentActive.remove(checkbox.data['value'])
            except KeyError:
                pass

        SetMapViewSetting(self.settingGroupKey, list(currentActive), self.mapViewID)
        if self.callback:
            self.callback(self.settingGroupKey, list(currentActive))


class ButtonTooltipRow(LayoutGridRow):
    default_state = uiconst.UI_NORMAL
    callback = None
    settingValue = None
    settingGroupKey = None
    mapViewID = None

    def ApplyAttributes(self, attributes):
        LayoutGridRow.ApplyAttributes(self, attributes)
        self.callback = attributes.callback
        self.settingValue = attributes.settingValue
        self.settingGroupKey = attributes.settingGroupKey
        self.mapViewID = attributes.mapViewID
        checkbox = RadioButtonUnderlay(pos=(0, 0, 16, 16))
        currentSetting = GetMapViewSetting(self.settingGroupKey, self.mapViewID)
        if currentSetting == self.settingValue:
            checkMark = Sprite(parent=checkbox, pos=(0, 0, 16, 16), texturePath='res:/UI/Texture/Shared/checkboxCheckedOval.png', idx=0)
        self.AddCell(cellObject=checkbox, cellPadding=(0, 0, 3, 0))
        label = EveLabelMedium(text=LABEL_MAP_BY_ID[attributes.settingValue], align=uiconst.CENTERLEFT)
        self.AddCell(cellObject=label, cellPadding=(0, 0, 6, 0))
        self.highLight = Fill(bgParent=self, color=(1, 1, 1, 0.1), state=uiconst.UI_HIDDEN)

    def Close(self, *args):
        LayoutGridRow.Close(self, *args)
        self.callback = None

    def OnMouseEnter(self, *args):
        self.highLight.display = True

    def OnMouseExit(self, *args):
        self.highLight.display = False

    def OnClick(self, *args):
        SetMapViewSetting(self.settingGroupKey, self.settingValue, self.mapViewID)
        if self.callback:
            self.callback(self.settingGroupKey, self.settingValue)


class MapViewCheckboxOptionButton(ButtonIcon):
    default_iconSize = 24
    default_width = 26
    default_height = 26
    settingGroupKeys = None
    callback = None

    def ApplyAttributes(self, attributes):
        ButtonIcon.ApplyAttributes(self, attributes)
        self.settingGroupKeys = attributes.settingGroupKeys
        self.mapViewID = attributes.mapViewID
        self.callback = attributes.callback
        self.SetTexturePath(ICON_ROOT + 'icon_const_group.png')

    def Close(self, *args):
        ButtonIcon.Close(self, *args)
        self.callback = None

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if uicore.uilib.leftbtn:
            return
        tooltipPanel.columns = 2
        tooltipPanel.AddLabelSmall(text=localization.GetByLabel('UI/Map/Layout'), bold=True, cellPadding=(8, 4, 4, 2), colSpan=tooltipPanel.columns)
        for settingsGroupKey in self.settingGroupKeys:
            if len(tooltipPanel.children):
                divider = LineThemeColored(align=uiconst.TOTOP, height=1, padding=(1, 1, 1, 0), opacity=0.3)
                tooltipPanel.AddCell(cellObject=divider, colSpan=tooltipPanel.columns)
            if settingsGroupKey in MV_GROUPS_BY_ID:
                for settingsID in MV_GROUPS_BY_ID[settingsGroupKey]:
                    checked = settingsID == GetMapViewSetting(settingsGroupKey, self.mapViewID)
                    checkBox = Checkbox(align=uiconst.TOPLEFT, text=LABEL_MAP_BY_ID[settingsID], groupname=settingsGroupKey, checked=checked, wrapLabel=False, callback=self.OnCheckBoxChange, configName=settingsGroupKey, retval=settingsID, prefstype=None)
                    tooltipPanel.AddCell(cellObject=checkBox, colSpan=tooltipPanel.columns, cellPadding=(5, 0, 5, 0))

            else:
                checked = bool(GetMapViewSetting(settingsGroupKey, self.mapViewID))
                checkBox = Checkbox(align=uiconst.TOPLEFT, text=LABEL_MAP_BY_ID[settingsGroupKey], checked=checked, wrapLabel=False, callback=self.OnCheckBoxChange, configName=settingsGroupKey, prefstype=None)
                tooltipPanel.AddCell(cellObject=checkBox, colSpan=tooltipPanel.columns, cellPadding=(5, 0, 5, 0))

        tooltipPanel.state = uiconst.UI_NORMAL

    def OnCheckBoxChange(self, checkbox):
        key = checkbox.data['config']
        val = checkbox.data['value']
        if val is None:
            val = checkbox.checked
        SetMapViewSetting(key, val, self.mapViewID)
        if self.callback:
            self.callback(key, val)

    def _LocalCallback(self, *args, **kwds):
        if self.callback:
            self.callback(*args, **kwds)

    def GetTooltipDelay(self):
        return 5

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_1

    def GetTooltipPositionFallbacks(self):
        return [uiconst.POINT_TOP_2,
         uiconst.POINT_TOP_1,
         uiconst.POINT_TOP_3,
         uiconst.POINT_BOTTOM_2,
         uiconst.POINT_BOTTOM_1,
         uiconst.POINT_BOTTOM_3]


COLORMODE_MENU_WIDTH = 200
COLORMODE_MENU_HEIGHT = 220

class MapViewColorModeSettingButton(MapViewSettingButton):

    def ReloadSettingValue(self):
        self.SetTexturePath(ICON_ROOT + 'spectrumIcon.png')

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if uicore.uilib.leftbtn:
            return
        tooltipPanel.columns = 1
        tooltipPanel.cellPadding = 2
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.AddLabelSmall(text=localization.GetByLabel('UI/Map/ColorMapBy'), bold=True, cellPadding=(8, 4, 4, 2))
        divider = LineThemeColored(align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=1, padding=(1, 1, 1, 0), opacity=0.3)
        tooltipPanel.AddCell(divider, cellPadding=(0, 0, 0, 0))
        if eve.session.role & service.ROLE_GML:
            Button(parent=tooltipPanel, label='Debug Run All', func=self.DebugRunAll, align=uiconst.CENTER)
        tooltipPanel.AddLabelSmall(text=localization.GetByLabel('UI/Map/RecentColorBy'), cellPadding=(8, 4, 4, 2))
        self.recentLayoutGrid = LayoutGrid(columns=1, parent=tooltipPanel)
        self.LoadRecentColorModes()
        divider = LineThemeColored(align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=1, padding=(1, 1, 1, 0), opacity=0.3)
        tooltipPanel.AddCell(divider, cellPadding=(0, 0, 0, 0))
        self.scroll = Scroll(parent=tooltipPanel, align=uiconst.TOPLEFT, width=COLORMODE_MENU_WIDTH, height=COLORMODE_MENU_HEIGHT)
        self.scroll.OnUpdatePosition = self.OnScrollPositionChanged
        self.LoadColorModes()

    def DebugRunAll(self, *args):
        print 'DebugRunAll'
        for groupLabel, groupID, loadFunction in self.GetColorModeGroups():
            colorModes = loadFunction()
            for colorMode in colorModes:
                print ' -', colorMode, GetFormatFunctionLabel(colorMode)
                SetMapViewSetting(VIEWMODE_COLOR_SETTINGS, colorMode, self.mapViewID)
                if self.callback:
                    self.callback(self.settingGroupKey, colorMode)
                blue.synchro.Sleep(500)

    def Close(self, *args):
        MapViewSettingButton.Close(self, *args)

    def OnScrollPositionChanged(self, *args, **kwargs):
        settings.char.ui.Set('mapViewColorModeScrollPosition_%s' % self.mapViewID, self.scroll.GetScrollProportion())

    def GetScrollEntries(self, options, settingsKey = None, sublevel = 0):
        currentActive = GetMapViewSetting(self.settingGroupKey, self.mapViewID)
        scrollList = []
        for colorMode in options:
            label = GetFormatFunctionLabel(colorMode)
            if not label:
                continue
            config = [self.settingGroupKey,
             colorMode,
             label,
             currentActive == colorMode]
            entry = self.AddCheckBox(config, None, self.settingGroupKey, sublevel=sublevel)
            scrollList.append(entry)

        return scrollList

    def GetGroupScrollEntry(self, groupID, groupLabel, groupData):
        import listentry
        id = ('mapviewsettings', groupID)
        data = {'GetSubContent': self.GetSubContent,
         'label': groupLabel,
         'id': id,
         'groupItems': groupData,
         'iconMargin': 32,
         'showlen': 0,
         'state': 'locked',
         'BlockOpenWindow': 1,
         'key': groupID,
         'showicon': 'hide'}
        return listentry.Get('Group', data)

    def GetSubContent(self, data, newitems = 0):
        for entry in self.scroll.GetNodes():
            if entry.__guid__ != 'listentry.Group' or entry.id == data.id:
                continue
            if entry.open:
                if entry.panel:
                    entry.panel.Toggle()
                else:
                    uicore.registry.SetListGroupOpenState(entry.id, 0)
                    entry.scroll.PrepareSubContent(entry)

        return self.GetScrollEntries(data.groupItems)

    def AddCheckBox(self, config, scrolllist, group = None, sublevel = 0):
        cfgname, retval, desc, default = config
        data = {}
        data['label'] = desc
        data['checked'] = default
        data['cfgname'] = cfgname
        data['retval'] = retval
        data['group'] = group
        data['OnChange'] = self.OnColorModeScrollCheckBoxChange
        data['entryWidth'] = COLORMODE_MENU_WIDTH
        data['decoClass'] = MapViewCheckbox
        scrollNode = ScrollEntryNode(**data)
        if scrolllist is not None:
            scrolllist.append(scrollNode)
        else:
            return scrollNode

    def OnColorModeScrollCheckBoxChange(self, checkbox):
        key = checkbox.data['key']
        val = checkbox.data['retval']
        if val is None:
            val = checkbox.checked
        self._SetColorMode(key, val)
        self.RegisterRecentColorMode(val)
        self.LoadRecentColorModes()

    def OnColorModeCheckBoxChange(self, checkbox):
        key = checkbox.data['config']
        val = checkbox.data['value']
        if val is None:
            val = checkbox.checked
        self._SetColorMode(key, val)
        self.LoadColorModes()

    def _SetColorMode(self, key, val):
        SetMapViewSetting(key, val, self.mapViewID)
        if self.callback:
            self.callback(self.settingGroupKey, val)

    def GetColorModeOptions(self):
        scrollEntries = []
        for groupLabel, groupID, loadFunction in self.GetColorModeGroups():
            groupEntry = self.GetGroupScrollEntry(groupID, groupLabel, loadFunction())
            scrollEntries.append((groupLabel.lower(), groupEntry))

        return [ entry for sortLabel, entry in sorted(scrollEntries) ]

    def RegisterRecentColorMode(self, colorMode):
        current = GetMapViewSetting(VIEWMODE_COLOR_RECENT, self.mapViewID)
        if colorMode in current:
            return
        current.insert(0, colorMode)
        current = current[:VIEWMODE_COLOR_RECENT_MAX]
        SetMapViewSetting(VIEWMODE_COLOR_RECENT, current, self.mapViewID)

    def GetRecentColorModes(self):
        return GetMapViewSetting(VIEWMODE_COLOR_RECENT, self.mapViewID)

    def LoadColorModes(self):
        scrollPosition = settings.char.ui.Get('mapViewColorModeScrollPosition_%s' % self.mapViewID, 0.0)
        scrollEntries = self.GetColorModeOptions()
        self.scroll.Load(contentList=scrollEntries, scrollTo=scrollPosition)

    def LoadRecentColorModes(self):
        if self.destroyed:
            return
        self.recentLayoutGrid.Flush()
        ret = self.GetRecentColorModes()
        currentActive = GetMapViewSetting(VIEWMODE_COLOR_SETTINGS, self.mapViewID)
        for colorMode in ret:
            label = GetFormatFunctionLabel(colorMode)
            if not label:
                continue
            checkBox = Checkbox(align=uiconst.TOPLEFT, text=label, checked=colorMode == currentActive, wrapLabel=True, callback=self.OnColorModeCheckBoxChange, configName=VIEWMODE_COLOR_SETTINGS, groupname=VIEWMODE_COLOR_SETTINGS, retval=colorMode, prefstype=None, width=COLORMODE_MENU_WIDTH - 10)
            self.recentLayoutGrid.AddCell(cellObject=checkBox, cellPadding=(5, 0, 5, 0))

    def GetNPCOptions(self):
        ret = [STARMODE_DUNGEONS, STARMODE_DUNGEONSAGENTS, STARMODE_INCURSION]
        if eve.session.role & ROLE_GML:
            ret.append(STARMODE_INCURSIONGM)
        return ret

    def GetCorporationOptions(self):
        ret = [STARMODE_FRIENDS_CORP]
        if (const.corpRoleAccountant | const.corpRoleJuniorAccountant) & eve.session.corprole != 0:
            ret += [STARMODE_CORPOFFICES,
             STARMODE_CORPIMPOUNDED,
             STARMODE_CORPPROPERTY,
             STARMODE_CORPDELIVERIES]
        return ret

    def GetPersonalColorModeOptions(self):
        ret = [STARMODE_ASSETS,
         STARMODE_VISITED,
         STARMODE_CARGOILLEGALITY,
         STARMODE_PISCANRANGE,
         STARMODE_FRIENDS_FLEET,
         STARMODE_FRIENDS_AGENT,
         STARMODE_MYCOLONIES,
         STARMODE_AVOIDANCE]
        return ret

    def GetPlanetsOptions(self):
        ret = []
        for planetTypeID in maputils.PLANET_TYPES:
            ret.append((STARMODE_PLANETTYPE, planetTypeID))

        return ret

    def GetIndustryOptions(self):
        ret = [STARMODE_JOBS24HOUR,
         STARMODE_MANUFACTURING_JOBS24HOUR,
         STARMODE_RESEARCHTIME_JOBS24HOUR,
         STARMODE_RESEARCHMATERIAL_JOBS24HOUR,
         STARMODE_COPY_JOBS24HOUR,
         STARMODE_INVENTION_JOBS24HOUR,
         STARMODE_INDUSTRY_MANUFACTURING_COST_INDEX,
         STARMODE_INDUSTRY_RESEARCHTIME_COST_INDEX,
         STARMODE_INDUSTRY_RESEARCHMATERIAL_COST_INDEX,
         STARMODE_INDUSTRY_COPY_COST_INDEX,
         STARMODE_INDUSTRY_INVENTION_COST_INDEX]
        return ret

    def GetServicesOptions(self):
        ret = [STARMODE_STATION_SERVICE_CLONING,
         STARMODE_STATION_SERVICE_FACTORY,
         STARMODE_STATION_SERVICE_FITTING,
         STARMODE_STATION_SERVICE_INSURANCE,
         STARMODE_STATION_SERVICE_LABORATORY,
         STARMODE_STATION_SERVICE_REPAIRFACILITIES,
         STARMODE_STATION_SERVICE_NAVYOFFICES,
         STARMODE_STATION_SERVICE_REPROCESSINGPLANT,
         STARMODE_STATION_SERVICE_SECURITYOFFICE]
        return ret

    def GetStatisticsOptions(self):
        ret = [STARMODE_REAL,
         STARMODE_SECURITY,
         STARMODE_REGION,
         STARMODE_PLAYERCOUNT,
         STARMODE_PLAYERDOCKED,
         STARMODE_JUMPS1HR,
         STARMODE_SHIPKILLS1HR,
         STARMODE_SHIPKILLS24HR,
         STARMODE_PODKILLS1HR,
         STARMODE_PODKILLS24HR,
         STARMODE_FACTIONKILLS1HR,
         STARMODE_STATIONCOUNT,
         STARMODE_CYNOSURALFIELDS]
        return ret

    def GetFactionalWarfareOptions(self):
        ret = [(STARMODE_MILITIA, STARMODE_FILTER_FACWAR_ENEMY)]
        for factionID in sm.StartService('facwar').GetWarFactions():
            ret.append((STARMODE_MILITIA, factionID))

        ret.append(STARMODE_MILITIAKILLS1HR)
        ret.append(STARMODE_MILITIAKILLS24HR)
        return ret

    def GetSovereigntyDevelopmentIndicesOptions(self):
        ret = [STARMODE_INDEX_STRATEGIC, STARMODE_INDEX_MILITARY, STARMODE_INDEX_INDUSTRY]
        return ret

    def GetSovereigntyOptions(self):
        ret = [STARMODE_FACTION,
         STARMODE_SOV_STANDINGS,
         (STARMODE_FACTIONEMPIRE, STARMODE_FILTER_EMPIRE),
         STARMODE_INDEX_STRATEGIC,
         STARMODE_INDEX_MILITARY,
         STARMODE_INDEX_INDUSTRY,
         STARMODE_SOV_CHANGE,
         STARMODE_SOV_GAIN,
         STARMODE_SOV_LOSS,
         STARMODE_OUTPOST_GAIN,
         STARMODE_OUTPOST_LOSS,
         STARMODE_STATION_FREEPORT]
        return ret

    def GetColorModeGroups(self):
        colorModeGroups = [(localization.GetByLabel('UI/Map/MapColorPersonal'), 'Personal', self.GetPersonalColorModeOptions),
         (localization.GetByLabel('UI/Map/MapPallet/hdrStarsServices'), 'Services', self.GetServicesOptions),
         (localization.GetByLabel('UI/Map/MapColorGeography'), 'Statistics', self.GetStatisticsOptions),
         (localization.GetByLabel('UI/Map/MapColorNPC'), 'NPCActivity', self.GetNPCOptions),
         (localization.GetByLabel('UI/Map/MapColorCorporation'), 'Corporation', self.GetCorporationOptions),
         (localization.GetByLabel('UI/Map/MapPallet/hdrStarsPlanets'), 'Planets', self.GetPlanetsOptions),
         (localization.GetByLabel('UI/Map/MapPallet/hdrStarsIndustry'), 'Industry', self.GetIndustryOptions),
         (localization.GetByLabel('UI/Map/MapPallet/hdrStarsSovereigntyFacWar'), 'FactionalWarfare', self.GetFactionalWarfareOptions),
         (localization.GetByLabel('UI/Map/MapPallet/hdrStarsSovereignty'), 'Sovereignty', self.GetSovereigntyOptions)]
        return colorModeGroups


class MapViewCheckbox(SE_BaseClassCore):
    TEXTLEFT = 20
    TEXTRIGHT = 12
    TEXTTOPBOTTOM = 4

    def Startup(self, *args):
        self.label = EveLabelSmall(parent=self, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT, left=self.TEXTLEFT, top=self.TEXTTOPBOTTOM)
        cbox = Checkbox(align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, parent=self, idx=0)
        cbox.left = 4
        cbox.top = 1
        cbox.width = 16
        cbox.height = 16
        cbox.data = {}
        cbox.OnChange = self.CheckBoxChange
        self.checkbox = cbox

    def Load(self, data):
        self.checkbox.SetGroup(data.Get('group', None))
        self.checkbox.SetChecked(data.checked, 0)
        self.checkbox.data.update({'key': data.cfgname,
         'retval': data.retval})
        self.label.width = data.entryWidth - self.TEXTLEFT - self.TEXTRIGHT
        self.label.text = data.label

    def CheckBoxChange(self, *args):
        self.sr.node.checked = self.checkbox.checked
        self.sr.node.OnChange(*args)

    def OnClick(self, *args):
        if not self or self.destroyed:
            return
        if self.checkbox.checked:
            eve.Message('DiodeDeselect')
        else:
            eve.Message('DiodeClick')
        if self.checkbox.groupName is None:
            self.checkbox.SetChecked(not self.checkbox.checked)
            return
        for node in self.sr.node.scroll.GetNodes():
            if issubclass(node.decoClass, MapViewCheckbox) and node.Get('group', None) == self.checkbox.groupName:
                if node.panel:
                    node.panel.checkbox.SetChecked(0, 0)
                    node.checked = 0
                else:
                    node.checked = 0

        if not self.destroyed:
            self.checkbox.SetChecked(1)

    def GetHeight(_self, node, width):
        textWidth, textHeight = EveLabelSmall.MeasureTextSize(node.label, width=node.entryWidth - MapViewCheckbox.TEXTLEFT - MapViewCheckbox.TEXTRIGHT)
        return max(20, textHeight + MapViewCheckbox.TEXTTOPBOTTOM * 2)

    def OnCharSpace(self, enteredChar, *args):
        uthread.pool('checkbox::OnChar', self.OnClick, self)
        return 1

    def OnMouseEnter(self, *args):
        SE_BaseClassCore.OnMouseEnter(self, *args)
        self.checkbox.OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        SE_BaseClassCore.OnMouseExit(self, *args)
        self.checkbox.OnMouseExit(*args)

    def OnMouseDown(self, *args):
        self.checkbox.OnMouseDown(*args)

    def OnMouseUp(self, *args):
        self.checkbox.OnMouseUp(*args)
