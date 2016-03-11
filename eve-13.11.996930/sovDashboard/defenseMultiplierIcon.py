#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sovDashboard\defenseMultiplierIcon.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.control.themeColored import LineThemeColored
from localization import GetByLabel
from sovDashboard.indexBars import IndexBars
import trinity

class DefenseMultiplierIcon(Container):
    default_align = uiconst.CENTER
    default_iconSize = 64
    default_showValue = False
    shieldTexturePath_big = 'res:/UI/Texture/classes/Sov/bonusShieldBase.png'
    shieldTexturePath_medium = 'res:/UI/Texture/classes/Sov/bonusShieldBase_32.png'
    shieldTexturePath_small = 'res:/UI/Texture/classes/Sov/bonusShieldBase_24.png'
    shieldFillTexturePath_big = 'res:/UI/Texture/classes/Sov/bonusShieldFill.png'
    shieldFillTexturePath_small = 'res:/UI/Texture/classes/Sov/bonusShieldFill24.png'
    shieldCapitalFillTexturePath_big = 'res:/UI/Texture/classes/Sov/bonusShieldFillCapital.png'
    shieldCapitalFillTexturePath_small = 'res:/UI/Texture/classes/Sov/bonusShieldFillCapital24.png'
    capitalStarTexturePath_big = 'res:/UI/Texture/classes/Sov/captitalStar64.png'
    capitalStarTexturePath_small = 'res:/UI/Texture/classes/Sov/captitalStar24.png'
    minOffset = -0.23
    maxOffset = 0.21
    numSteps = 6
    offsetRange = maxOffset - minOffset
    labelPadding = 3

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.currentMultiplier = attributes.get('currentMultiplier', 1.0)
        self.devIndexes = attributes.get('devIndexes', (0, 0, 0))
        self.showValue = attributes.get('showValue', self.default_showValue)
        self.iconSize = attributes.get('iconSize', self.default_iconSize)
        self.isCapital = attributes.get('isCapital', False)
        self.capitalOwnerID = attributes.get('capitalOwnerID', None)
        self.height = self.iconSize
        self.width = self.iconSize
        self.valueLabel = None
        self.capitalStar = None
        self.shieldCont = Container(name='shieldCont', parent=self, pos=(0,
         0,
         self.iconSize,
         self.iconSize), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        shieldTexturePath, shieldFillTexturePath, _ = self.GetTexturePathsToUse()
        self.shieldSprite = Sprite(name='shieldSprite', parent=self.shieldCont, texturePath=shieldFillTexturePath, textureSecondaryPath=shieldTexturePath, align=uiconst.TOALL, spriteEffect=trinity.TR2_SFX_MODULATE, state=uiconst.UI_DISABLED)
        self.shieldSprite.scale = (1.0, 0.5)
        self.shieldCont.LoadTooltipPanel = self.LoadTooltipPanel
        self.shieldCont.GetTooltipPointer = self.GetTooltipPointer
        self.SetStatusFromMultiplier(self.currentMultiplier, self.devIndexes)
        self.ChangeCapitalState(self.isCapital)

    def GetTexturePathsToUse(self):
        if self.iconSize > 32:
            shieldTexturePath = self.shieldTexturePath_big
            starTexturePath = self.capitalStarTexturePath_big
        elif self.iconSize > 24:
            shieldTexturePath = self.shieldTexturePath_medium
            starTexturePath = self.capitalStarTexturePath_big
        else:
            shieldTexturePath = self.shieldTexturePath_small
            starTexturePath = self.capitalStarTexturePath_small
        if self.isCapital:
            if self.iconSize > 24:
                shieldFillTexturePath = self.shieldCapitalFillTexturePath_big
            else:
                shieldFillTexturePath = self.shieldCapitalFillTexturePath_small
        elif self.iconSize > 24:
            shieldFillTexturePath = self.shieldFillTexturePath_big
        else:
            shieldFillTexturePath = self.shieldFillTexturePath_small
        return (shieldTexturePath, shieldFillTexturePath, starTexturePath)

    def GetCapitalStar(self, create = True):
        if create and (not self.capitalStar or self.capitalStar.destroyed):
            _, _, starTexturePath = self.GetTexturePathsToUse()
            self.capitalStar = Sprite(name='capitalStar', parent=self.shieldCont, texturePath=starTexturePath, align=uiconst.TOPLEFT, pos=(0,
             0,
             self.iconSize,
             self.iconSize), idx=0, state=uiconst.UI_DISABLED)
        return self.capitalStar

    def GetValueLabel(self):
        if self.valueLabel is None:
            self.valueLabel = EveLabelMedium(parent=self, align=uiconst.CENTERLEFT, left=self.iconSize + self.labelPadding, state=uiconst.UI_NORMAL)
        return self.valueLabel

    def SetStatusFromMultiplier(self, multiplierValue, devIndexes):
        newValue = multiplierValue / self.numSteps
        self.SetStatus(newValue, devIndexes)

    def SetStatus(self, value, devIndexes, animate = False):
        self.devIndexes = devIndexes
        newOffset = self.offsetRange * value
        newShieldValue = self.minOffset + newOffset
        self.currentMultiplier = value * self.numSteps
        self.shieldSprite.StopAnimations()
        if animate:
            currentTranslation = self.shieldSprite.translationPrimary
            uicore.animations.MorphVector2(self.shieldSprite, 'translationPrimary', startVal=currentTranslation, endVal=(currentTranslation[0], newShieldValue), duration=0.75)
        else:
            self.shieldSprite.translationPrimary = (0, newShieldValue)
        if self.showValue:
            valueLabel = self.GetValueLabel()
            text = GetByLabel('UI/Sovereignty/DefenseMultiplierDisplayNumber', bonusMultiplier=self.currentMultiplier)
            valueLabel.text = text
            self.width = self.iconSize + valueLabel.textwidth + self.labelPadding

    def ChangeCapitalState(self, isCapital):
        self.isCapital = isCapital
        capitalStar = self.GetCapitalStar(create=isCapital)
        if capitalStar:
            capitalStar.display = isCapital
        _, shieldFillTexturePath, _ = self.GetTexturePathsToUse()
        self.shieldSprite.SetTexturePath(shieldFillTexturePath)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.columns = 5
        tooltipPanel.margin = 6
        tooltipPanel.cellPadding = 3
        tooltipPanel.cellSpacing = 0
        text = GetByLabel('UI/Sovereignty/ActivityDefenseMultiplier')
        label = EveLabelMedium(text=text, align=uiconst.TOTOP, padTop=1, bold=True)
        tooltipPanel.AddCell(cellObject=label, colSpan=4)
        text = GetByLabel('UI/Sovereignty/DefenseMultiplierDisplayNumber', bonusMultiplier=self.currentMultiplier)
        label = EveLabelLarge(text=text, align=uiconst.TOPRIGHT, bold=True)
        tooltipPanel.AddCell(cellObject=label)
        valueAndTextures = [(self.devIndexes[2], 'res:/UI/Texture/classes/Sov/strategicIndex.png', 'UI/Sovereignty/StrategicIndex'), (self.devIndexes[0], 'res:/UI/Texture/classes/Sov/militaryIndex.png', 'UI/Sovereignty/MilitaryIndex'), (self.devIndexes[1], 'res:/UI/Texture/classes/Sov/industryIndex.png', 'UI/Sovereignty/IndustryIndex')]
        for indexValue, texturePath, labelPath in valueAndTextures:
            indexSprite = Sprite(name='indexSprite', parent=tooltipPanel, pos=(0, 0, 16, 16), align=uiconst.CENTERLEFT, texturePath=texturePath)
            label = EveLabelMedium(text=GetByLabel(labelPath))
            tooltipPanel.AddCell(cellObject=label)
            indexBars = IndexBars(currentIndex=indexValue, align=uiconst.CENTERRIGHT)
            tooltipPanel.AddCell(cellObject=indexBars, cellPadding=(16, 0, 3, 0), colSpan=3)

        if self.isCapital:
            tooltipPanel.state = uiconst.UI_NORMAL
            l = LineThemeColored(height=1, align=uiconst.TOTOP, opacity=0.3)
            tooltipPanel.AddCell(l, colSpan=5, cellPadding=(1, 1, 1, 3))
            capitalSprite = Sprite(name='capitalSprite', parent=tooltipPanel, pos=(0, 0, 16, 16), align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/classes/Sov/bonusShieldCapital16.png')
            capitalLabel = EveLabelMedium(text=GetByLabel('UI/Sovereignty/Capital'), align=uiconst.CENTERLEFT)
            tooltipPanel.AddCell(cellObject=capitalLabel)
            infoLabel = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(self.capitalOwnerID).name, info=('showinfo', const.typeAlliance, self.capitalOwnerID))
            tooltipPanel.AddLabelMedium(text=infoLabel, colSpan=3, wrapWidth=160, align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL)

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_1
