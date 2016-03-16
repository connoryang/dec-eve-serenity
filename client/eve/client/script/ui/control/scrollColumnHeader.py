#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\scrollColumnHeader.py
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.themeColored import LineThemeColored
import carbonui.const as uiconst
import uthread
import blue
COLUMNMINSIZE = 24
COLUMNMINDEFAULTSIZE = 80
SETTING_KEY_STATE = 'ScrollColumnHeader_State'
SETTING_KEY_SIZE = 'ScrollColumnHeader_Size'

class ScrollColumnHeader(Container):
    default_name = 'ScrollColumnHeader'
    default_align = uiconst.TOTOP
    default_height = 16
    default_state = uiconst.UI_PICKCHILDREN
    default_clipChildren = True
    default_padBottom = 0

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.settingsID = attributes.settingsID
        self.scroll = attributes.scroll
        self.entryClass = attributes.entryClass
        LineThemeColored(parent=self, align=uiconst.TOBOTTOM, opacity=uiconst.OPACITY_FRAME)
        self.rightAlignedHeaderContainer = Container(parent=self, align=uiconst.TORIGHT)
        self.headerContainer = Container(parent=self, clipChildren=True)
        self.columnIDs = []
        self.fixedColumns = None
        self.defaultColumn = None
        self.minSizeByColumnID = {}
        if self.scroll and self.entryClass:
            self.SetDefaultColumn(*self.entryClass.GetDefaultColumnAndDirection())
            self.SetMinSizeByColumnID(self.entryClass.GetColumnsMinSize())
            self.SetFixedColumns(self.entryClass.GetFixedColumns())
            self.SetRightAlignedColumns(self.entryClass.GetRightAlignedColumns())
            self.SetStretchColumns(self.entryClass.GetStretchColumns())
            self.CreateColumns(self.entryClass.GetColumns())

    def Close(self, *args):
        Container.Close(self, *args)
        self.OnSortingChange = None
        self.OnColumnSizeChange = None
        self.OnColumnSizeReset = None
        self.scroll = None

    def SetDefaultColumn(self, columnID, direction):
        self.defaultColumn = (columnID, direction)

    def SetRightAlignedColumns(self, rightAlignedColumns):
        self.rightAlignedColumns = rightAlignedColumns

    def SetStretchColumns(self, stretchColumns):
        self.stretchColumns = stretchColumns

    def SetMinSizeByColumnID(self, minSizes):
        self.minSizeByColumnID = minSizes

    def SetFixedColumns(self, fixedColumns):
        self.fixedColumns = fixedColumns

    def CreateColumns(self, columns):
        self.headerContainer.Flush()
        self.rightAlignedHeaderContainer.Flush()
        self.rightAlignedHeaderContainer.width = 0
        self.headers = []
        self.columnIDs = columns
        sizes = self.GetColumnSizes()
        for columnID in columns:
            isRigthAligned = True if self.rightAlignedColumns and columnID in self.rightAlignedColumns else False
            isStretchColumn = True if self.stretchColumns and columnID in self.stretchColumns else False
            header = Container(parent=self.rightAlignedHeaderContainer if isRigthAligned else self.headerContainer, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
            header.OnClick = (self.ClickHeader, header)
            header.columnID = columnID
            header.sortTriangle = None
            if not isStretchColumn:
                header.OnDblClick = (self.DblClickHeader, header)
                headerDivider = LineThemeColored(parent=header, align=uiconst.TORIGHT if not isRigthAligned else uiconst.TOLEFT, opacity=uiconst.OPACITY_FRAME)
                if self.fixedColumns and columnID not in self.fixedColumns:
                    scaler = Container(parent=header, align=uiconst.TOPRIGHT, width=4, height=self.height - 1, state=uiconst.UI_NORMAL)
                    scaler.OnMouseDown = (self.StartHeaderScale, header)
                    scaler.cursor = 16
            label = EveLabelSmall(parent=header, text=columnID, align=uiconst.CENTERLEFT, left=6, state=uiconst.UI_DISABLED, maxLines=1)
            header.label = label
            if isStretchColumn:
                header.width = label.width + label.left + 20
            elif self.fixedColumns and columnID in self.fixedColumns:
                header.width = self.fixedColumns[columnID]
                if header.width <= 32:
                    label.Hide()
            elif columnID in sizes:
                header.width = max(self.minSizeByColumnID.get(columnID, COLUMNMINSIZE), sizes[columnID])
            else:
                header.width = max(self.minSizeByColumnID.get(columnID, COLUMNMINSIZE), max(COLUMNMINDEFAULTSIZE, label.textwidth + 24))
            if isRigthAligned:
                self.rightAlignedHeaderContainer.width += header.width
            self.headers.append(header)

        self.UpdateActiveState()

    def UpdateActiveState(self):
        currentActive, currentDirection = self.GetActiveColumnAndDirection()
        for each in self.headers:
            if each.columnID == currentActive:
                if not each.sortTriangle:
                    each.sortTriangle = Sprite(align=uiconst.CENTERRIGHT, pos=(3, -1, 16, 16), parent=each, name='directionIcon', idx=0)
                if currentDirection:
                    each.sortTriangle.texturePath = 'res:/UI/Texture/Icons/1_16_16.png'
                else:
                    each.sortTriangle.texturePath = 'res:/UI/Texture/Icons/1_16_15.png'
                each.sortTriangle.state = uiconst.UI_DISABLED
                rightMargin = 20
            else:
                if each.sortTriangle:
                    each.sortTriangle.Hide()
                rightMargin = 6
            each.label.width = each.width - each.label.left - 4
            if each.sortTriangle and each.sortTriangle.display:
                each.label.SetRightAlphaFade(each.width - rightMargin - each.label.left, uiconst.SCROLL_COLUMN_FADEWIDTH)
            else:
                each.label.SetRightAlphaFade()
            if each.width <= 32 or each.width - each.label.left - rightMargin - 6 < each.label.textwidth:
                each.hint = each.label.text
            else:
                each.hint = None

    def GetColumns(self):
        return self.columnIDs

    def GetActiveColumnAndDirection(self):
        all = settings.char.ui.Get(SETTING_KEY_STATE, {})
        currentActive, currentDirection = None, True
        if self.settingsID in all:
            currentActive, currentDirection = all[self.settingsID]
            if currentActive not in self.columnIDs:
                return (None, True)
            return (currentActive, currentDirection)
        if self.defaultColumn is not None:
            columnID, direction = self.defaultColumn
            if columnID in self.columnIDs:
                return self.defaultColumn
        if self.columnIDs:
            currentActive, currentDirection = self.columnIDs[0], True
        return (currentActive, currentDirection)

    def SetActiveColumn(self, columnID, doCallback = True):
        currentActive, currentDirection = self.GetActiveColumnAndDirection()
        if currentActive == columnID:
            sortDirection = not currentDirection
        else:
            sortDirection = currentDirection
        all = settings.char.ui.Get(SETTING_KEY_STATE, {})
        all[self.settingsID] = (columnID, sortDirection)
        settings.char.ui.Set(SETTING_KEY_STATE, all)
        self.UpdateActiveState()
        if doCallback:
            self.OnSortingChange()

    def DblClickHeader(self, header):
        if not self.ColumnIsFixed(header.columnID):
            self.SetActiveColumn(header.columnID, doCallback=False)
            self.OnColumnSizeReset(header.columnID)

    def ClickHeader(self, header):
        self.SetActiveColumn(header.columnID)

    def StartHeaderScale(self, header, mouseButton, *args):
        if mouseButton == uiconst.MOUSELEFT:
            self.startScaleX = uicore.uilib.x
            self.startScaleWidth = header.width
            uthread.new(self.ScaleHeader, header)

    def ScaleHeader(self, header):
        while not self.destroyed and uicore.uilib.leftbtn:
            diff = self.startScaleX - uicore.uilib.x
            header.width = max(self.minSizeByColumnID.get(header.columnID, COLUMNMINSIZE), self.startScaleWidth - diff)
            self.UpdateActiveState()
            blue.pyos.synchro.Yield()

        currentSizes = self.RegisterCurrentSizes()
        self.UpdateActiveState()
        self.OnColumnSizeChange(header.columnID, header.width, currentSizes)

    def GetColumnSizes(self):
        if self.entryClass:
            defaultSizes = self.entryClass.GetColumnsDefaultSize()
        else:
            defaultSizes = {}
        current = settings.char.ui.Get(SETTING_KEY_SIZE, {}).get(self.settingsID, defaultSizes)
        if self.fixedColumns:
            current.update(self.fixedColumns)
        for each in self.headers:
            if hasattr(each, 'columnID') and each.columnID not in current:
                current[each.columnID] = each.width

        return current

    def GetColumnWidths(self):
        columnWidthsByName = self.GetColumnSizes()
        columnWidths = [ columnWidthsByName[header] for header in self.GetColumns() ]
        return columnWidths

    def ColumnIsFixed(self, columnID):
        return columnID in self.fixedColumns

    def SetColumnSize(self, columnID, size):
        if columnID in self.fixedColumns:
            return
        columnSize = max(self.minSizeByColumnID.get(columnID, COLUMNMINSIZE), size)
        for each in self.headers:
            if hasattr(each, 'columnID') and each.columnID == columnID:
                each.width = columnSize
                break

        self.UpdateActiveState()
        currentSizes = self.RegisterCurrentSizes()
        self.OnColumnSizeChange(columnID, columnSize, currentSizes)

    def RegisterCurrentSizes(self):
        sizes = {}
        for each in self.headers:
            if hasattr(each, 'columnID'):
                sizes[each.columnID] = each.width

        all = settings.char.ui.Get(SETTING_KEY_SIZE, {})
        all[self.settingsID] = sizes
        settings.char.ui.Set(SETTING_KEY_SIZE, all)
        return sizes

    def OnSortingChange(self):
        if self.scroll and self.entryClass:
            columns = self.entryClass.GetColumns()
            activeColumn, columnDirection = self.GetActiveColumnAndDirection()
            activeColumnIndex = columns.index(activeColumn)

            def GetSortValue(_node):
                return _node.sortValues[activeColumnIndex]

            sortedScrollNodes = sorted(self.scroll.GetNodes(), key=GetSortValue, reverse=not columnDirection)
            self.scroll.SetOrderedNodes(sortedScrollNodes)

    def OnColumnSizeChange(self, columnID, newSize, currentSizes):
        if self.scroll and self.entryClass:
            columnWidths = self.GetColumnWidths()
            for node in self.scroll.GetNodes():
                node.columnWidths = columnWidths
                if node.panel:
                    node.panel.OnColumnResize(columnWidths)

    def OnColumnSizeReset(self, columnID):
        if self.scroll and self.entryClass:
            minSize = self.minSizeByColumnID.get(columnID, COLUMNMINSIZE)
            defaultSizes = self.entryClass.GetColumnsDefaultSize()
            if defaultSizes:
                resetSize = defaultSizes.get(columnID, minSize)
            else:
                resetSize = minSize
            self.SetColumnSize(columnID, resetSize)
