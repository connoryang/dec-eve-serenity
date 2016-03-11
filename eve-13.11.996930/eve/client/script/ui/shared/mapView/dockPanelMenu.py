#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\dockPanelMenu.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.themeColored import FillThemeColored, LineThemeColored, SpriteThemeColored
from eve.client.script.ui.shared.infoPanels.infoPanelControls import InfoPanelHeaderBackground
from eve.client.script.ui.control.divider import Divider
import uthread
import math
MIN_MENU_HEIGHT = 100

class DockPanelMenuContainer(Container):
    menus = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.menus = []

    def Close(self, *args):
        Container.Close(self, *args)
        self.menus = None

    def CreateMenu(self, settingsID, headerLabel = None, resizeable = True, fixedHeight = None, minExpandedHeight = MIN_MENU_HEIGHT, fillParent = False, expandedByDefault = False):
        menu = DockPanelMenu(parent=self, headerLabel=headerLabel, settingsID=settingsID, align=uiconst.TOTOP, resizeable=resizeable, fixedHeight=fixedHeight, minExpandedHeight=minExpandedHeight, fillParent=fillParent, expandedByDefault=expandedByDefault, OnMenuResizeStartingCallback=self.OnMenuResizeStarting, OnMenuResizeCallback=self.OnMenuResize, OnMenuExpandCallback=self.OnMenuExpand, OnMenuCollapseCallback=self.OnMenuCollapse, GetMenuMaxHeight=self.GetMenuMaxHeight, GetFreeSpaceForMenu=self.GetFreeSpaceForMenu)
        self.menus.append(menu)
        return menu

    def _OnSizeChange_NoBlock(self, width, height, *args):
        if not self.menus:
            return
        modifyMenus = [ each for each in self.menus if each.IsExpanded() ]
        allTotal = sum([ each.height for each in self.menus ])
        if allTotal > height:
            self._CompressMenus(modifyMenus, allTotal - height)
        if allTotal < height:
            self._ExpandMenus(modifyMenus, height - allTotal)

    def GetFreeSpaceForMenu(self, menu):
        width, height = self.GetAbsoluteSize()
        totalHeight = 0
        for each in self.menus:
            if each is menu:
                continue
            totalHeight += each.setHeight

        return height - totalHeight

    def GetMenuMaxHeight(self, menu):
        if menu.fixedHeight:
            return menu.fixedHeight
        width, height = self.GetAbsoluteSize()
        totalHeight = 0
        for each in self.menus:
            if each is menu:
                continue
            if each.IsExpanded():
                totalHeight += each.GetMinHeight()
            else:
                totalHeight += each.height

        maxHeight = max(menu.minExpandedHeight, height - totalHeight)
        return maxHeight

    def OnMenuResizeStarting(self, menu):
        width, height = self.GetAbsoluteSize()
        foundSelf = False
        totalAbove = 0
        totalBelow = 0
        for each in self.menus:
            if each is menu:
                foundSelf = True
                continue
            if isinstance(each, DockPanelMenu):
                if foundSelf:
                    if each.IsExpanded():
                        totalBelow += each.GetMinHeight()
                    else:
                        totalBelow += each.height
                else:
                    totalAbove += each.height

        menu.SetMinMaxResizeValues(menu.minExpandedHeight, height - totalAbove - totalBelow)

    def OnMenuResize(self, menu):
        self._CompressMenusBelow(menu)
        self._ExpandMenusBelow(menu)
        menu.RegisterSettings()

    def OnMenuExpand(self, menu):
        self._CompressMenusAbove(menu)
        self._CompressMenusBelow(menu)

    def OnMenuCollapse(self, menu):
        self._ExpandMenusAbove(menu)
        self._ExpandMenusBelow(menu)

    def _CompressMenusAbove(self, menu):
        width, height = self.GetAbsoluteSize()
        allTotal = sum([ each.height for each in self.menus ])
        if allTotal > height:
            menusAbove = []
            for each in self.menus:
                if each is menu:
                    break
                if each.IsExpanded():
                    menusAbove.append(each)

            self._CompressMenus(menusAbove, allTotal - height)

    def _CompressMenusBelow(self, menu):
        width, height = self.GetAbsoluteSize()
        allTotal = sum([ each.height for each in self.menus ])
        if allTotal > height:
            foundSelf = False
            menusBelow = []
            for each in self.menus:
                if each is menu:
                    foundSelf = True
                    continue
                if foundSelf and each.IsExpanded():
                    menusBelow.append(each)

            self._CompressMenus(menusBelow, allTotal - height)

    def _CompressMenus(self, menus, compressNeed):
        while compressNeed and menus:
            for each in menus[:]:
                if each.height > each.GetMinHeight():
                    each.height -= 1
                    compressNeed -= 1
                    if not compressNeed:
                        break
                else:
                    menus.remove(each)

    def _ExpandMenusAbove(self, menu):
        width, height = self.GetAbsoluteSize()
        allTotal = sum([ each.height for each in self.menus ])
        if allTotal < height:
            menusAbove = []
            for each in self.menus:
                if each is menu:
                    break
                if each.IsExpanded():
                    menusAbove.append(each)

            if menusAbove:
                self._ExpandMenus(menusAbove, height - allTotal)

    def _ExpandMenusBelow(self, menu):
        width, height = self.GetAbsoluteSize()
        allTotal = sum([ each.height for each in self.menus ])
        if allTotal < height:
            foundSelf = False
            menusBelow = []
            for each in self.menus:
                if each is menu:
                    foundSelf = True
                    continue
                if foundSelf and each.IsExpanded():
                    menusBelow.append(each)

            self._ExpandMenus(menusBelow, height - allTotal)

    def _ExpandMenus(self, menus, availableSpace):
        while availableSpace and menus:
            for each in menus[:]:
                if each.height < each.GetExpandedHeight():
                    each.height += 1
                    availableSpace -= 1
                    if not availableSpace:
                        break
                else:
                    menus.remove(each)


class DockPanelMenu(Container):
    default_clipChildren = True
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    _expanded = False
    _collapsedHeight = 0
    resizeDivider = None
    resizeable = False
    fixedHeight = None
    fillParent = False
    minExpandedHeight = MIN_MENU_HEIGHT
    setHeight = 0

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.minExpandedHeight = attributes.Get('minExpandedHeight', self.minExpandedHeight)
        self.resizeable = attributes.Get('resizeable', self.resizeable)
        self.fillParent = attributes.Get('fillParent', self.fillParent)
        self.settingsID = attributes.settingsID
        self.OnMenuResizeStartingCallback = attributes.OnMenuResizeStartingCallback
        self.OnMenuResizeCallback = attributes.OnMenuResizeCallback
        self.OnMenuExpandCallback = attributes.OnMenuExpandCallback
        self.OnMenuCollapseCallback = attributes.OnMenuCollapseCallback
        self.GetMenuMaxHeight = attributes.GetMenuMaxHeight
        self.GetFreeSpaceForMenu = attributes.GetFreeSpaceForMenu
        self.fixedHeight = attributes.fixedHeight
        self.headerParent = Container(parent=self, name='headerParent', align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, height=24)
        FillThemeColored(bgParent=self.headerParent, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.5)
        InfoPanelHeaderBackground(bgParent=self.headerParent)
        self.expanderSprite = Sprite(parent=self.headerParent, texturePath='res:/UI/Texture/classes/Neocom/arrowDown.png', rotation=math.pi / 2, pos=(6, 6, 7, 7), state=uiconst.UI_DISABLED)
        self.headerLabel = EveLabelMedium(text=attributes.headerLabel, parent=self.headerParent, bold=True, state=uiconst.UI_DISABLED, padding=(22, 2, 6, 0), align=uiconst.TOLEFT)
        self.content = Container(parent=self, name='contentParent', align=uiconst.TOALL, state=uiconst.UI_NORMAL, opacity=0.0)
        self.headerParent.height = max(20, self.headerLabel.textheight + 2)
        if self.resizeable and not self.fixedHeight:
            if self.align == uiconst.TOBOTTOM:
                divAlign = uiconst.TOTOP
            else:
                divAlign = uiconst.TOBOTTOM
            divider = Divider(name='resizeDivider', align=divAlign, pos=(0,
             0,
             0,
             const.defaultPadding), parent=self, state=uiconst.UI_NORMAL, opacity=0.0, idx=0)
            divider.OnSizeChangeStarting = self.OnMenuResizeStarting
            divider.OnSizeChanging = self.OnMenuResize
            divider.Startup(self, 'height', 'y', 100, 300)
            self.resizeDivider = divider
            LineThemeColored(parent=divider, align=uiconst.TOTOP, height=1, opacity=0.3)
            SpriteThemeColored(parent=divider, texturePath='res:/UI/Texture/Classes/DockPanel/menuResizeHandle.png', pos=(0, 0, 30, 5), align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, opacity=0.6)
        self._collapsedHeight = self.headerParent.height + const.defaultPadding
        current = settings.user.ui.Get('DockPanelMenuPrefs', {})
        if self.settingsID in current:
            if current[self.settingsID]['isExpanded']:
                uthread.new(self.Expand)
                return
        elif attributes.expandedByDefault:
            uthread.new(self.Expand)
            return
        self.Collapse(startup=True)

    def Close(self, *args):
        Container.Close(self, *args)
        self.OnMenuResizeStartingCallback = None
        self.OnMenuResizeCallback = None
        self.OnMenuExpandCallback = None
        self.OnMenuCollapseCallback = None
        self.GetMenuMaxHeight = None
        self.GetFreeSpaceForMenu = None

    def OnMenuResizeStarting(self, *args):
        if self.OnMenuResizeStartingCallback:
            self.OnMenuResizeStartingCallback(self)

    def OnMenuResize(self, *args):
        self.setHeight = self.height
        if self.OnMenuResizeCallback:
            self.OnMenuResizeCallback(self)

    def SetMinMaxResizeValues(self, minValue, maxValue):
        self.resizeDivider.SetMinMax(minValue, maxValue)

    def SetHeader(self, text, hint = None):
        self.headerLabel.text = text
        if hint:
            self.headerLabel.state = uiconst.UI_NORMAL
            self.headerLabel.hint = hint
            self.headerLabel.OnClick = self.OnClick
        else:
            self.headerLabel.state = uiconst.UI_DISABLED

    def OnClick(self, *args):
        if self._expanded:
            self.Collapse()
        else:
            self.Expand()

    def Expand(self, *args):
        if self.GetMenuMaxHeight:
            maxHeight = self.GetMenuMaxHeight(self)
        else:
            maxHeight = self.GetMinHeight()
        endHeight = min(maxHeight, self.GetExpandedHeight())
        uicore.animations.Tr2DRotateTo(self.expanderSprite, self.expanderSprite.rotation, 0.0, duration=0.25)
        self._expanded = True
        self.setHeight = endHeight
        if self.resizeDivider:
            self.resizeDivider.state = uiconst.UI_NORMAL
            uicore.animations.MorphScalar(self.resizeDivider, 'opacity', startVal=self.resizeDivider.opacity, endVal=1.0, duration=0.25)
        self.content.state = uiconst.UI_NORMAL
        uicore.animations.MorphScalar(self, '_expandfunc', startVal=self.height, endVal=endHeight, duration=0.25)
        uicore.animations.MorphScalar(self.content, 'opacity', startVal=self.content.opacity, endVal=1.0, duration=0.25, sleep=True)
        if self.destroyed:
            return
        if self._expanded is True:
            self.RegisterSettings()

    def Collapse(self, startup = False):
        endHeight = self._collapsedHeight
        self.setHeight = endHeight
        self._expanded = False
        if not startup:
            uicore.animations.Tr2DRotateTo(self.expanderSprite, self.expanderSprite.rotation, math.pi / 2, duration=0.25)
            if self.resizeDivider:
                self.resizeDivider.state = uiconst.UI_DISABLED
                uicore.animations.MorphScalar(self.resizeDivider, 'opacity', startVal=self.resizeDivider.opacity, endVal=0.0, duration=0.25)
            uicore.animations.MorphScalar(self, '_collapsefunc', startVal=self.height, endVal=endHeight, duration=0.25)
            uicore.animations.MorphScalar(self.content, 'opacity', startVal=self.content.opacity, endVal=0.0, duration=0.25, sleep=True)
            if self.destroyed:
                return
        else:
            self.expanderSprite.rotation = math.pi / 2
            if self.resizeDivider:
                self.resizeDivider.state = uiconst.UI_DISABLED
                self.resizeDivider.opacity = 0.0
            self.height = endHeight
            self.content.opacity = 0.0
        if self._expanded is False:
            self.content.state = uiconst.UI_HIDDEN
            self.RegisterSettings()

    @apply
    def _expandfunc():

        def fget(self):
            return self.height

        def fset(self, value):
            self.height = value
            if self.OnMenuExpandCallback:
                self.OnMenuExpandCallback(self)

        return property(**locals())

    @apply
    def _collapsefunc():

        def fget(self):
            return self.height

        def fset(self, value):
            self.height = value
            if self.OnMenuCollapseCallback:
                self.OnMenuCollapseCallback(self)

        return property(**locals())

    def RegisterSettings(self):
        if self.settingsID:
            current = settings.user.ui.Get('DockPanelMenuPrefs', {})
            if self._expanded:
                current[self.settingsID] = {'expandedHeight': self.height,
                 'isExpanded': self._expanded}
            elif self.settingsID in current:
                current[self.settingsID]['isExpanded'] = self._expanded
            else:
                return
            settings.user.ui.Set('DockPanelMenuPrefs', current)

    def GetExpandedHeight(self):
        if self.fixedHeight:
            return self.fixedHeight
        if self.fillParent and self.GetFreeSpaceForMenu:
            expandedHeight = self.GetFreeSpaceForMenu(self)
        else:
            current = settings.user.ui.Get('DockPanelMenuPrefs', {})
            if self.settingsID in current:
                expandedHeight = current[self.settingsID]['expandedHeight']
            else:
                expandedHeight = None
        return max(self.minExpandedHeight, expandedHeight)

    def GetMinHeight(self):
        if self.fixedHeight:
            return self.fixedHeight
        else:
            return self.minExpandedHeight

    def IsExpanded(self):
        return self._expanded
