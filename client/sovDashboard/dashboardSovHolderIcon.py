#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sovDashboard\dashboardSovHolderIcon.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.util.bunch import Bunch
from entosis.entosisConst import STRUCTURE_SCORE_UPDATED
from eve.client.script.ui.control.eveIcon import LogoIcon, GetLogoIcon
from eve.client.script.ui.control.themeColored import LineThemeColored
from eve.client.script.ui.control.utilButtons.marketDetailsButton import ShowMarketDetailsButton
from eve.client.script.ui.control.utilButtons.showInfoButton import ShowInfoButton
from eve.common.script.sys.eveCfg import IsAlliance, IsFaction, IsCorporation
import evetypes
from localization import GetByLabel
from sovDashboard import ShouldUpdateStructureInfo, GetStructureStatusString
import sovDashboard.dashboardConst as dashboardConst
from sovDashboard.sovUIControls import SovStructureStatusHorizontal, SovStructureStatusCircular, SovStatusTimeLabel

class SovHolderIcon(Container):
    default_width = 40
    default_height = 40
    default_align = uiconst.TOPLEFT
    showStructureStatusBar = False
    structureStatusBar = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.showStructureStatusBar = attributes.Get('showStructureStatusBar', self.showStructureStatusBar)
        self.structureInfo = attributes.structureInfo
        self.facwarSvc = sm.GetService('facwar')
        self.sovSvc = sm.GetService('sov')
        self.corpSvc = sm.GetService('corp')
        self.sovHolderIcon = Sprite(name='sovHolderIcon', parent=self, pos=(0, 0, 32, 32), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)
        if self.showStructureStatusBar:
            self.structureStatusBar = SovStructureStatusCircular(parent=self, align=uiconst.CENTER, width=40, height=40, structureInfo=self.structureInfo)
            backgroundShape = Sprite(parent=self, texturePath='res:/ui/Texture/classes/Sov/structureIconBackground.png', color=(0, 0, 0, 0.3), align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=-1)
        self.UpdateStructureState()

    def LoadTooltipPanel(self, *args, **kwds):
        structureID = self.structureInfo.get('itemID', None)
        if not structureID:
            return self.LoadTooltipPanelNoStructure(*args, **kwds)
        ownerID = self.structureInfo.get('ownerID', None)
        allianceID = self.structureInfo.get('allianceID', None)
        if allianceID:
            return self.LoadTooltipWithOwner(*args, **kwds)
        return self.LoadTooltipPanelNoOwner(*args, **kwds)

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_2

    def UpdateStructureState(self, updateGauge = False):
        texturePath = self.GetTexturePaths(self.structureInfo['typeID'])
        ownerID = self.structureInfo.get('ownerID', None)
        allianceID = self.structureInfo.get('allianceID', None)
        self.sovHolderIcon.texturePath = texturePath
        if ownerID == dashboardConst.UNCLAIMABLE:
            self.sovHolderIcon.texturePath = None
        elif ownerID:
            if allianceID:
                sm.GetService('photo').GetAllianceLogo(allianceID, 32, self.sovHolderIcon)
            elif IsFaction(ownerID):
                texturePath = LogoIcon.GetFactionIconTexturePath(ownerID, isSmall=True)
                self.sovHolderIcon.texturePath = texturePath
        structureID = self.structureInfo.get('itemID', None)
        if not structureID and not IsFaction(ownerID):
            self.sovHolderIcon.SetAlpha(dashboardConst.NO_STRUCTURE_ALPHA)
        if updateGauge:
            self.UpdateScore()

    def UpdateScore(self, animate = True):
        if self.structureStatusBar is None or self.structureStatusBar.destroyed:
            return
        self.structureStatusBar.UpdateStructureInfo(self.structureInfo, animate=animate)
        if animate:
            uicore.animations.MorphScalar(self.structureStatusBar, 'opacity', startVal=self.structureStatusBar.opacity, endVal=0.5, curveType=uiconst.ANIM_WAVE, duration=0.2, loops=3)

    @staticmethod
    def GetTexturePaths(structureTypeID, large = False):
        if structureTypeID == const.typeOutpostConstructionPlatform:
            texturePath = 'res:/ui/Texture/classes/Sov/station.png'
            if large:
                texturePath = 'res:/ui/Texture/classes/Sov/station_64.png'
        elif structureTypeID == const.typeInfrastructureHub:
            texturePath = 'res:/ui/Texture/classes/Sov/ihub.png'
            if large:
                texturePath = 'res:/ui/Texture/classes/Sov/ihub_64.png'
        elif structureTypeID == const.typeTerritorialClaimUnit:
            texturePath = 'res:/ui/Texture/classes/Sov/tcu.png'
            if large:
                texturePath = 'res:/ui/Texture/classes/Sov/tcu_64.png'
        else:
            raise NotImplementedError
        return texturePath

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_1

    def LoadTooltipWithOwner(self, tooltipPanel, *args):
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.columns = 2
        tooltipPanel.margin = 2
        tooltipPanel.cellPadding = 1
        structureOwnerID = self.structureInfo.get('allianceID', None)
        ownerIcon = GetLogoIcon(itemID=structureOwnerID, parent=tooltipPanel, width=48, height=48, ignoreSize=True, state=uiconst.UI_NORMAL, align=uiconst.CENTER)
        ownerIcon.GetDragData = self.GetAllianceDragData
        infoLabel = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(structureOwnerID).name, info=('showinfo', const.typeAlliance, structureOwnerID))
        tooltipPanel.AddLabelLarge(text=infoLabel, width=160, align=uiconst.CENTERLEFT, bold=True, state=uiconst.UI_NORMAL)
        statusContainer = SovStructureStatusHorizontal(structureInfo=self.structureInfo, align=uiconst.CENTER, width=214, centerLabel=True, barBgColor=(0.2, 0.2, 0.2, 0.3), autoHeight=True)
        tooltipPanel.AddCell(cellObject=statusContainer, colSpan=2)
        timeLabel = SovStatusTimeLabel(align=uiconst.CENTER, state=uiconst.UI_NORMAL, structureInfo=self.structureInfo, width=190)
        tooltipPanel.AddCell(cellObject=timeLabel, colSpan=2)

    def LoadTooltipPanelNoStructure(self, tooltipPanel, *args):
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.columns = 2
        tooltipPanel.margin = 2
        tooltipPanel.cellPadding = 1
        texturePath = self.GetTexturePaths(self.structureInfo['typeID'], large=True)
        icon = Sprite(width=48, height=48, state=uiconst.UI_DISABLED, texturePath=texturePath, opacity=dashboardConst.NO_STRUCTURE_ALPHA)
        tooltipPanel.AddCell(icon)
        structureTypeID = self.structureInfo['typeID']
        if structureTypeID == const.typeTerritorialClaimUnit:
            headerText = GetByLabel('UI/Sovereignty/Unclaimed')
        else:
            headerText = GetByLabel('UI/Sovereignty/Uninstalled')
        if structureTypeID == const.typeOutpostConstructionPlatform:
            structureName = GetByLabel('UI/Common/LocationTypes/Station')
        else:
            structureName = evetypes.GetName(structureTypeID)
        tooltipPanel.AddLabelLarge(text=headerText, width=150, bold=True, align=uiconst.CENTERLEFT)
        l = LineThemeColored(width=200, height=1, align=uiconst.CENTER, opacity=0.3)
        tooltipPanel.AddCell(l, colSpan=2, cellPadding=(1, 1, 1, 3))
        deployText = GetByLabel('UI/Sovereignty/StructureMayBeDeployed', structureName=structureName)
        tooltipPanel.AddLabelMedium(text='<center>%s</center>' % deployText, align=uiconst.CENTER, width=190, colSpan=2)
        buttonGrid = LayoutGrid(columns=2, align=uiconst.CENTER, cellPadding=2)
        showInfoBtn = ShowInfoButton(parent=buttonGrid, typeID=structureTypeID)
        showMarketDetailsBtn = ShowMarketDetailsButton(parent=buttonGrid, typeID=structureTypeID)
        tooltipPanel.AddCell(cellObject=buttonGrid, colSpan=2, cellPadding=3)

    def LoadTooltipPanelNoOwner(self, tooltipPanel, *args):
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.columns = 2
        tooltipPanel.margin = 2
        tooltipPanel.cellPadding = 1
        texturePath = self.GetTexturePaths(self.structureInfo['typeID'], large=True)
        icon = Sprite(width=48, height=48, state=uiconst.UI_DISABLED, texturePath=texturePath)
        tooltipPanel.AddCell(icon)
        structureTypeID = self.structureInfo['typeID']
        if structureTypeID == const.typeOutpostConstructionPlatform:
            headerText = GetByLabel('UI/Sovereignty/Freeport')
            unclaimedText = GetByLabel('UI/Sovereignty/StationOpen')
        else:
            headerText = GetByLabel('UI/Sovereignty/Neutral')
            structureName = evetypes.GetName(structureTypeID)
            unclaimedText = GetByLabel('UI/Sovereignty/StructureUnclaimed', structureName=structureName)
        tooltipPanel.AddLabelLarge(text=headerText, width=150, bold=True, align=uiconst.CENTERLEFT)
        l = LineThemeColored(width=200, height=1, align=uiconst.CENTER, opacity=0.3)
        tooltipPanel.AddCell(l, colSpan=2, cellPadding=(1, 1, 1, 3))
        tooltipPanel.AddLabelMedium(text='<center>%s</center>' % unclaimedText, align=uiconst.CENTER, width=190, colSpan=2)
        statusContainer = SovStructureStatusHorizontal(structureInfo=self.structureInfo, width=200, align=uiconst.CENTER, centerLabel=True, barBgColor=(0.2, 0.2, 0.2, 0.3), autoHeight=True)
        tooltipPanel.AddCell(cellObject=statusContainer, colSpan=2)
        timeLabel = SovStatusTimeLabel(align=uiconst.CENTER, state=uiconst.UI_NORMAL, structureInfo=self.structureInfo, width=190)
        tooltipPanel.AddCell(cellObject=timeLabel, colSpan=2)

    def GetAllianceDragData(self, *args, **kwds):
        allianceID = self.structureInfo['allianceID']
        typeID = cfg.eveowners.Get(allianceID).typeID
        fakeNode = Bunch()
        fakeNode.__guid__ = 'listentry.User'
        fakeNode.charID = allianceID
        fakeNode.info = cfg.eveowners.Get(allianceID)
        fakeNode.itemID = allianceID
        fakeNode.typeID = typeID
        return [fakeNode]

    def GetMenu(self):
        m = sm.GetService('menu').GetMenuFormItemIDTypeID(itemID=self.structureInfo.get('itemID', None), typeID=self.structureInfo['typeID'])
        return m

    def SolarsystemSovStructureChanged(self, sourceItemID, structureInfo, whatChanged):
        if not self.showStructureStatusBar or STRUCTURE_SCORE_UPDATED not in whatChanged:
            return
        if ShouldUpdateStructureInfo(self.structureInfo, sourceItemID):
            self.structureInfo = structureInfo
            self.UpdateStructureState(updateGauge=True)
