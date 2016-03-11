#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sovDashboard\sovStatusEntries.py
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
import carbonui.const as uiconst
from entosis.entosisConst import STRUCTURE_SCORE_UPDATED
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.inflight.infrastructureHub import SetDeltaSprite
import inventorycommon.const as invConst
from localization import GetByLabel
from sovDashboard import ShouldUpdateStructureInfo
from sovDashboard.dashboardSovHolderIcon import SovHolderIcon
from sovDashboard.indexBars import IndexBars
import uiprimitives
import blue
import uthread
from sovDashboard.sovUIControls import SovStructureStatusHorizontal, SovStatusTimeLabel
LEFT_PADDING = 10
RIGHT_PADDING = 10
STRUCTURE_STATUS_WIDTH = 200

class MouseInsideScrollEntry(SE_BaseClassCore):
    onMouseEntyerThread = None

    def OnMouseEnter(self, *args):
        if self.onMouseEntyerThread is None:
            SE_BaseClassCore.OnMouseEnter(self, *args)
            self.onMouseEntyerThread = AutoTimer(10, self.MonitorMouseOver)

    def OnMouseExit(self, *args):
        if not self.IsMouseInsideEntry():
            self.KillHilite()

    def KillHilite(self):
        SE_BaseClassCore.OnMouseExit(self)
        self.onMouseEntyerThread = None

    def MonitorMouseOver(self):
        if self.destroyed:
            self.onMouseEntyerThread = None
        elif not self.IsMouseInsideEntry():
            self.KillHilite()


class SovSystemStatusEntry(MouseInsideScrollEntry):
    ENTRYHEIGHT = 32

    def ApplyAttributes(self, attributes):
        MouseInsideScrollEntry.ApplyAttributes(self, attributes)
        self.node = attributes.node
        statusNameText = self.node.statusNameText
        texturePath = self.node.get('texturePath', None)
        currentIndex = self.node.get('currentIndex', None)
        partialValue = self.node.get('partialValue', 0)
        bonusMultiplier = self.node.get('bonusMultiplier', None)
        isCapital = self.node.get('isCapital', None)
        boxTooltipFunc = self.node.get('boxTooltipFunc', None)
        extraHelpLabelPath = self.node.get('extraHelpLabelPath', None)
        indexID = self.node.get('indexID', None)
        statusIcon = Sprite(parent=self, name='icon', texturePath=texturePath, pos=(LEFT_PADDING,
         0,
         16,
         16), align=uiconst.CENTERLEFT, opacity=0.75)
        self.statusNamelabel = EveLabelMedium(parent=self, text=statusNameText, align=uiconst.CENTERLEFT, left=statusIcon.width + statusIcon.left + 6, state=uiconst.UI_NORMAL)
        if extraHelpLabelPath:
            helpText = GetByLabel(extraHelpLabelPath)
            helpIcon = MoreInfoIcon(parent=self, align=uiconst.CENTERRIGHT, hint=helpText, left=2)
            rightPadding = helpIcon.left + helpIcon.width + 4
        else:
            rightPadding = RIGHT_PADDING
        self.indexBars = IndexBars(parent=self, boxTooltipFunc=boxTooltipFunc, align=uiconst.CENTERRIGHT, left=rightPadding)
        self.indexBars.display = False
        self.bonusMultiplierLabel = EveLabelMedium(parent=self, align=uiconst.CENTERRIGHT, left=rightPadding)
        self.bonusMultiplierLabel.display = False
        if currentIndex is not None:
            self.indexBars.SetIndexStatus(currentIndex, partialValue)
            self.indexBars.display = True
            if indexID != const.attributeDevIndexSovereignty:
                self.AddDeltaSprite(indexID)
        elif bonusMultiplier is not None:
            text = GetByLabel('UI/Sovereignty/DefenseMultiplierDisplayNumber', bonusMultiplier=bonusMultiplier)
            self.bonusMultiplierLabel.text = text
            self.bonusMultiplierLabel.display = True

    def AddDeltaSprite(self, indexID):
        self.devIndices = sm.GetService('sov').GetDevelopmentIndicesForSystem(session.solarsystemid2)
        devIndex = self.devIndices.get(indexID, None)
        indexInfo = sm.GetService('sov').GetLevelInfoForIndex(indexID, devIndex=devIndex)
        changeSprite = uiprimitives.Sprite(parent=self, align=uiconst.CENTERRIGHT, pos=(0, 0, 16, 16))
        SetDeltaSprite(changeSprite, indexInfo)
        changeSprite.left = self.indexBars.left + self.indexBars.width + 4

    def Load(self, *args):
        pass


class SovStructureStatusEntry(MouseInsideScrollEntry):
    ENTRYHEIGHT = 46
    structureStatusBar = None
    __notifyevents__ = ['OnSolarsystemSovStructureChanged']

    def ApplyAttributes(self, attributes):
        MouseInsideScrollEntry.ApplyAttributes(self, attributes)
        self.node = attributes.node
        self.AddStructureIcon()
        self.AddAllianceIcon()
        self.AddTimeLabel()
        uthread.new(self.AddStatusCont)
        sm.RegisterNotify(self)

    def AddStructureIcon(self):
        texturePath = SovHolderIcon.GetTexturePaths(self.node.structureInfo['typeID'])
        self.sovHolderIcon = Sprite(name='sovHolderIcon', parent=self, texturePath=texturePath, pos=(LEFT_PADDING,
         0,
         32,
         32), align=uiconst.CENTERLEFT, state=uiconst.UI_PICKCHILDREN)

    def AddAllianceIcon(self):
        allianceID = self.node.structureInfo['allianceID']
        if not allianceID:
            self.allianceIcon = None
            return
        allianceName = cfg.eveowners.Get(allianceID).name
        self.allianceIcon = GetLogoIcon(itemID=allianceID, parent=self, acceptNone=False, align=uiconst.CENTERRIGHT, pos=(RIGHT_PADDING,
         0,
         32,
         32), state=uiconst.UI_NORMAL, hint=allianceName)
        self.allianceIcon.OnClick = lambda *args: sm.GetService('info').ShowInfo(typeID=invConst.typeAlliance, itemID=allianceID)

    def AddStatusCont(self):
        if self.destroyed:
            return
        self.structureStatusBar = SovStructureStatusHorizontal(parent=self, left=self.sovHolderIcon.left + self.sovHolderIcon.width + 10, structureInfo=self.node.structureInfo, align=uiconst.CENTERLEFT, width=STRUCTURE_STATUS_WIDTH, autoHeight=True)

    def AddTimeLabel(self):
        if self.allianceIcon:
            padRight = self.allianceIcon.left + self.allianceIcon.width + 6
        else:
            padRight = RIGHT_PADDING
        timeCont = Container(name='timeCont', parent=self, align=uiconst.TOALL, padRight=padRight, padLeft=self.sovHolderIcon.left + self.sovHolderIcon.width + 10 + STRUCTURE_STATUS_WIDTH)
        self.timeLabel = SovStatusTimeLabel(parent=timeCont, align=uiconst.CENTERLEFT, left=6, state=uiconst.UI_NORMAL, structureInfo=self.node.structureInfo, autoFadeSides=True)

    def Load(self, *args):
        pass

    def GetMenu(self):
        m = sm.GetService('menu').GetMenuFormItemIDTypeID(itemID=self.node.structureInfo.get('itemID', None), typeID=self.node.structureInfo.get('typeID', None))
        return m

    def OnSolarsystemSovStructureChanged(self, solarsystemID, whatChanged, sourceItemID = None):
        if STRUCTURE_SCORE_UPDATED in whatChanged:
            if ShouldUpdateStructureInfo(self.node.structureInfo, sourceItemID):
                newStructureInfo = sm.GetService('sov').GetSpecificSovStructuresInfoInSolarSystem(solarsystemID, sourceItemID)
                self.node.structureInfo = newStructureInfo
                self.UpdateScore()

    def UpdateScore(self):
        if self.structureStatusBar and not self.structureStatusBar.destroyed:
            self.structureStatusBar.UpdateStructureInfo(self.node.structureInfo)
            uicore.animations.MorphScalar(self.structureStatusBar, 'opacity', startVal=self.structureStatusBar.opacity, endVal=0.5, curveType=uiconst.ANIM_WAVE, duration=0.2, loops=3)


class SovAllianceEntry(MouseInsideScrollEntry):
    texturePath = 'res:/UI/Texture/WindowIcons/sovereignty.png'
    ENTRYHEIGHT = 46

    def ApplyAttributes(self, attributes):
        MouseInsideScrollEntry.ApplyAttributes(self, attributes)
        self.node = attributes.node
        self.AddAlliance()
        self.AddFlagIcon()
        self.AddText()

    def AddAlliance(self):
        sovHolderID = self.node.sovHolderID
        self.allianceIcon = GetLogoIcon(itemID=sovHolderID, parent=self, acceptNone=False, align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL, pos=(RIGHT_PADDING,
         0,
         32,
         32))
        self.allianceIcon.OnClick = lambda *args: sm.GetService('info').ShowInfo(typeID=invConst.typeAlliance, itemID=sovHolderID)
        self.allianceIcon.display = False
        if sovHolderID:
            sovText = cfg.eveowners.Get(sovHolderID).name
            textLeft = self.allianceIcon.width + self.allianceIcon.left + 6
            self.allianceIcon.hint = sovText
            self.allianceIcon.display = True
        else:
            sovText = GetByLabel('UI/Neocom/Unclaimed')
            textLeft = RIGHT_PADDING
        cont = ContainerAutoSize(parent=self, align=uiconst.TORIGHT, left=textLeft)
        EveLabelMedium(parent=cont, text=sovText, align=uiconst.CENTER, state=uiconst.UI_NORMAL)

    def AddFlagIcon(self):
        self.flagSprite = Sprite(parent=self, name='icon', texturePath=self.texturePath, pos=(LEFT_PADDING - 4,
         0,
         24,
         24), align=uiconst.CENTERLEFT, opacity=0.75)

    def AddText(self):
        cont = Container(name='textCont', parent=self, align=uiconst.TOALL, padRight=6)
        EveLabelMedium(parent=cont, text=GetByLabel('UI/Sovereignty/SovereignAlliance'), align=uiconst.CENTERLEFT, left=self.flagSprite.width + self.flagSprite.left + 2, state=uiconst.UI_NORMAL, autoFadeSides=True)

    def Load(self, node):
        pass
