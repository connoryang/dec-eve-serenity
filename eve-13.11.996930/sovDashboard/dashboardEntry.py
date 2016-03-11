#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sovDashboard\dashboardEntry.py
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.util.color import Color
from entosis.entosisConst import STRUCTURE_SCORE_UPDATED, STRUCTURES_UPDATED
from eve.client.script.ui.control.eveLabel import EveLabelMedium
import carbonui.const as uiconst
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.control.utilButtons.showInMapButton import ShowInMapButton
import inventorycommon.const as invConst
from localization import GetByLabel
import blue
from sovDashboard import CalculateStructureStatusFromStructureInfo
from sovDashboard.dashboardSovHolderIcon import SovHolderIcon
import sovDashboard.dashboardConst as dashboardConst
from sovDashboard.sovStatusEntries import MouseInsideScrollEntry
from sovDashboard.sovStructureBonusIcon import StructureBonusIcon
from sovDashboard.sovUIControls import SovStructureStatusHorizontal, SovStatusTimeLabel
import sys
COL_SYSTEM = 0
COL_CONSTELLATION = 1
COL_REGION = 2
COL_JUMPS = 3
COL_STRUCTUREBONUS = 4
COL_STRUCTURE = 5
COL_STATUS = 6
COL_TIMER = 7

class DashboardEntry(MouseInsideScrollEntry):
    default_name = 'DashboardEntry'
    entryLoaded = False
    entryThreadLoaded = False
    ENTRYHEIGHT = 46
    COLUMN_PADLEFT = 6
    COLUMN_PADRIGHT = 4

    def Load(self, node):
        if self.entryLoaded:
            return
        self.sovSvc = sm.GetService('sov')
        self.contentContainer = Container(parent=self, padRight=28, clipChildren=True)
        self.labelColumns = []
        self.centerAlignedColumns = []
        self.filledColumns = []
        self.node = node
        self.entryLoaded = True
        self.AddSystemLabel()
        self.AddConstellationLabel()
        self.AddRegionLabel()
        self.AddJumpLabel()
        self.AddExtraColumns()
        self.AddButtons()
        self.UpdateLabelColumns()
        self.UpdateCenterAlignedColumns()
        self.UpdateFilledColumns()

    def AddExtraColumns(self):
        self.AddTimeLabel()
        self.AddBonusCont()
        self.AddStructureCont()
        self.AddStatusCont()

    def AddButtons(self):
        self.AddMapButton()

    def ConstructHiliteFill(self):
        if not self._hiliteFill:
            self._hiliteFill = ListEntryUnderlay(bgParent=self, padding=0)

    def OnColumnResize(self, newCols):
        self.node.columnWidths = newCols
        self.UpdateLabelColumns()
        self.UpdateCenterAlignedColumns()
        self.UpdateFilledColumns()

    def UpdateLabelColumns(self):
        columnWidths = self.node.columnWidths
        for columnLabel, columnIndex in self.labelColumns:
            columnLabel.left = sum(columnWidths[:columnIndex]) + self.COLUMN_PADLEFT
            columnLabel.clipWidth = columnWidths[columnIndex] - (self.COLUMN_PADLEFT + self.COLUMN_PADRIGHT)

    def UpdateCenterAlignedColumns(self):
        columnWidths = self.node.columnWidths
        for columnObject, columnIndex in self.centerAlignedColumns:
            width = columnWidths[columnIndex]
            left = sum(columnWidths[:columnIndex])
            columnObject.left = left + (width - columnObject.width) / 2

    def UpdateFilledColumns(self):
        columnWidths = self.node.columnWidths
        for columnObject, columnIndex in self.filledColumns:
            columnObject.left = sum(columnWidths[:columnIndex]) + self.COLUMN_PADLEFT
            columnObject.width = columnWidths[columnIndex] - (self.COLUMN_PADLEFT + self.COLUMN_PADRIGHT)

    def AddSystemLabel(self):
        text = self.GetSolarSystemText(self.node)
        self.systemNameLabel = self.AddColumnLabel(text=text)
        self.labelColumns.append((self.systemNameLabel, COL_SYSTEM))

    def AddConstellationLabel(self):
        text = self.GetConstellationText(self.node)
        self.constellationNameLabel = self.AddColumnLabel(text=text)
        self.labelColumns.append((self.constellationNameLabel, COL_CONSTELLATION))

    def AddRegionLabel(self):
        text = self.GetRegionText(self.node)
        self.regionNameLabel = self.AddColumnLabel(text=text)
        self.labelColumns.append((self.regionNameLabel, COL_REGION))

    def AddJumpLabel(self):
        text = self.GetJumpText(self.node)
        self.jumpLabel = self.AddColumnLabel(text=text)
        self.labelColumns.append((self.jumpLabel, COL_JUMPS))

    def AddTimeLabel(self):
        self.timeLabel = SovStatusTimeLabel(parent=self.contentContainer, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, structureInfo=self.node.structureInfo, autoFadeSides=32)
        self.labelColumns.append((self.timeLabel, COL_TIMER))

    def AddBonusCont(self):
        multiplierIcon = StructureBonusIcon(parent=self.contentContainer, defenceMultiplier=self.node.structureInfo.defenseMultiplier, align=uiconst.CENTERLEFT)
        self.multiplierIcon = multiplierIcon
        self.centerAlignedColumns.append((self.multiplierIcon, COL_STRUCTUREBONUS))

    def AddStructureCont(self):
        self.sovHolderIcon = SovHolderIcon(parent=self.contentContainer, structureInfo=self.node.structureInfo, pos=(0, 0, 32, 32), align=uiconst.CENTERLEFT)
        self.centerAlignedColumns.append((self.sovHolderIcon, COL_STRUCTURE))

    def AddStatusCont(self):
        self.structureStatus = SovStructureStatusHorizontal(parent=self.contentContainer, structureInfo=self.node.structureInfo, align=uiconst.CENTERLEFT, width=100, autoHeight=True)
        self.filledColumns.append((self.structureStatus, COL_STATUS))

    def AddMapButton(self):
        ShowInMapButton(parent=self, align=uiconst.CENTERRIGHT, itemID=self.node['solarSystemID'], left=6)

    def AddColumnLabel(self, text, color = None):
        if color is None:
            color = dashboardConst.PRIMARYCOLOR_DEFAULT
        label = EveLabelMedium(parent=self.contentContainer, text=text, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, color=color, autoFadeSides=32)
        return label

    def GetMenu(self):
        m = sm.GetService('menu').GetMenuFormItemIDTypeID(itemID=self.node.structureInfo['itemID'], typeID=self.node.structureInfo['typeID'])
        return m

    def ChangeStructureInfoAndUpdate(self, structureInfo, whatChanged = set([STRUCTURES_UPDATED])):
        self.node.structureInfo = structureInfo
        if 'all' in whatChanged:
            return
        if STRUCTURE_SCORE_UPDATED in whatChanged:
            self.UpdateScore()

    def UpdateScore(self, animate = True):
        if self.structureStatus is None or self.structureStatus.destroyed:
            return
        self.structureStatus.UpdateStructureInfo(self.node.structureInfo, animate=animate)
        if animate:
            uicore.animations.MorphScalar(self.structureStatus, 'opacity', startVal=self.structureStatus.opacity, endVal=0.5, curveType=uiconst.ANIM_WAVE, duration=0.2, loops=3)

    @staticmethod
    def GetSolarSystemText(node):
        solarSystemID = node['solarSystemID']
        solarsystemName = cfg.evelocations.Get(solarSystemID).name
        linkInfo = ('showinfo', invConst.groupSolarSystem, solarSystemID)
        solarsystemLink = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=solarsystemName, info=linkInfo)
        securityStatus, color = sm.GetService('map').GetSecurityStatus(solarSystemID, getColor=True)
        text = '%s <color=%s>%s</color>' % (solarsystemLink, Color.RGBtoHex(color.r, color.g, color.b), securityStatus)
        return text

    @staticmethod
    def GetConstellationText(node):
        constellationID = node['constellationID']
        constellationName = cfg.evelocations.Get(constellationID).name
        linkInfo = ('showinfo', invConst.groupConstellation, constellationID)
        constellationLink = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=constellationName, info=linkInfo)
        return constellationLink

    @staticmethod
    def GetRegionText(node):
        regionID = node['regionID']
        regionName = cfg.evelocations.Get(regionID).name
        linkInfo = ('showinfo', invConst.groupRegion, regionID)
        regionLink = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=regionName, info=linkInfo)
        return regionLink

    @staticmethod
    def GetJumpText(node):
        if node.jumpCount == sys.maxint:
            return '-'
        else:
            return str(node.jumpCount)

    @staticmethod
    def GetColumnsMinSize():
        return {GetByLabel('UI/Common/LocationTypes/System'): 100,
         GetByLabel('UI/Common/LocationTypes/Constellation'): 100,
         GetByLabel('UI/Common/LocationTypes/Region'): 100,
         GetByLabel('UI/Common/Jumps'): 60,
         GetByLabel('UI/Generic/Status'): 150,
         GetByLabel('UI/Sovereignty/Timer'): 70}

    @staticmethod
    def GetFixedColumns():
        return {GetByLabel('UI/Sovereignty/StructureBonus'): 100,
         GetByLabel('UI/Inflight/Scanner/Structure'): 80}

    @staticmethod
    def GetHeaders():
        ret = [GetByLabel('UI/Common/LocationTypes/System'),
         GetByLabel('UI/Common/LocationTypes/Constellation'),
         GetByLabel('UI/Common/LocationTypes/Region'),
         GetByLabel('UI/Common/Jumps'),
         GetByLabel('UI/Sovereignty/StructureBonus'),
         GetByLabel('UI/Inflight/Scanner/Structure'),
         GetByLabel('UI/Generic/Status'),
         GetByLabel('UI/Sovereignty/Timer')]
        return ret

    @classmethod
    def GetColumnMinSize(cls, node, columnID):
        fixed = cls.GetFixedColumns()
        if columnID in fixed:
            return fixed[columnID]
        minSizes = cls.GetColumnsMinSize()
        minSize = minSizes[columnID]
        text = None
        if columnID == GetByLabel('UI/Common/LocationTypes/System'):
            text = cls.GetSolarSystemText(node)
        elif columnID == GetByLabel('UI/Common/LocationTypes/Constellation'):
            text = cls.GetConstellationText(node)
        elif columnID == GetByLabel('UI/Common/LocationTypes/Region'):
            text = cls.GetRegionText(node)
        elif columnID == GetByLabel('UI/Common/Jumps'):
            text = cls.GetJumpText(node)
        if text:
            textWidth, textHeight = EveLabelMedium.MeasureTextSize(text)
            width = textWidth + cls.COLUMN_PADLEFT + cls.COLUMN_PADRIGHT
            return max(minSize, width)
        return minSize
