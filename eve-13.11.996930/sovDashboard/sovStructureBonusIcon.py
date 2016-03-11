#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sovDashboard\sovStructureBonusIcon.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium
from localization import GetByLabel

class StructureBonusIcon(Container):
    minOffset = -0.23
    maxOffset = 0.21
    offsetRange = maxOffset - minOffset
    iconSize = 16
    default_width = iconSize
    default_height = iconSize
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.shieldSprite = Sprite(name='shieldSprite', parent=self, texturePath='res:/UI/Texture/classes/Sov/defenseBonusStructure.png', state=uiconst.UI_DISABLED, pos=(0,
         0,
         self.iconSize,
         self.iconSize))
        self.structureBonusLabel = EveLabelMedium(parent=self, align=uiconst.CENTERLEFT, left=self.iconSize + 2)
        self.SetStructureBonus(attributes.defenceMultiplier)

    def SetStructureBonus(self, defenceMultiplier):
        self.defenceMultiplier = defenceMultiplier
        text = GetByLabel('UI/Sovereignty/DefenseMultiplierDisplayNumber', bonusMultiplier=defenceMultiplier)
        self.structureBonusLabel.text = text
        self.width = self.structureBonusLabel.textwidth + self.iconSize + 4

    def LoadTooltipPanel(self, *args, **kwds):
        pass
