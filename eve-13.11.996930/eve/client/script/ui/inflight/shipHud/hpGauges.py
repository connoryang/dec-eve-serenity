#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\hpGauges.py
import math
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
import carbonui.const as uiconst
from localization import GetByLabel
from localization.formatters.numericFormatters import FormatNumeric
import trinity
OPACITY_BARS = 1.8

class HPGauges(Container):
    default_name = 'HPGauges'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.lastStructure = None
        self.lastArmor = None
        self.lastShield = None
        self.structureGauge = ShipHudSpriteGauge(parent=self, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/gauge3.png', spriteEffect=trinity.TR2_SFX_MODULATE, pickRadius=54, name='structureGauge')
        self.armorGauge = ShipHudSpriteGauge(parent=self, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/gauge2.png', spriteEffect=trinity.TR2_SFX_MODULATE, pickRadius=64, name='armorGauge')
        self.shieldGauge = ShipHudSpriteGauge(parent=self, texturePath='res:/UI/Texture/classes/ShipUI/gauge1.png', spriteEffect=trinity.TR2_SFX_MODULATE, pickRadius=74, name='shieldGauge')
        self.shieldGauge.LoadTooltipPanel = self.LoadDamageTooltip

    def Update(self):
        if self.destroyed:
            return
        self.shieldGauge.UpdateValue(self.controller.GetShieldHPPortion())
        self.armorGauge.UpdateValue(self.controller.GetArmorHPPortion())
        self.structureGauge.UpdateValue(self.controller.GetStructureHPPortion())

    def LoadDamageTooltip(self, tooltipPanel, *args):
        self._LoadDamageTooltip(tooltipPanel)

    def _LoadDamageTooltip(self, tooltipPanel):
        tooltipPanel.LoadGeneric3ColumnTemplate()
        tooltipPanel.margin = (6, 4, 8, 4)
        for key, iconNo, labelText in (('Shield', 'res:/UI/Texture/Icons/1_64_13.png', GetByLabel('Tooltips/Hud/Shield')), ('Armor', 'res:/UI/Texture/Icons/1_64_9.png', GetByLabel('Tooltips/Hud/Armor')), ('Structure', 'res:/UI/Texture/Icons/2_64_12.png', GetByLabel('Tooltips/Hud/Structure'))):
            iconObj, labelObj, valueObj = tooltipPanel.AddIconLabelValue(iconNo, labelText, '', iconSize=36)
            valueObj.fontsize = 16
            valueObj.bold = True
            valueObj.top = -2
            labelObj.bold = False
            setattr(tooltipPanel, 'label' + key, labelObj)
            setattr(tooltipPanel, 'valueLabel' + key, valueObj)

        tooltipPanel.AddCell()
        f = Container(align=uiconst.TOPLEFT, width=100, height=1)
        tooltipPanel.AddCell(f, colSpan=2)
        self._UpdateDamageTooltip(tooltipPanel)
        self._damageTooltipUpdate = AutoTimer(10, self._UpdateDamageTooltip, tooltipPanel)

    def _UpdateDamageTooltip(self, tooltipPanel):
        if tooltipPanel.destroyed:
            self._damageTooltipUpdate = None
            return
        if not self.controller.IsLoaded():
            self._damageTooltipUpdate = None
            return
        structure = self.controller.GetStructureHPPortion()
        armor = self.controller.GetArmorHPPortion()
        shield = self.controller.GetShieldHPPortion()
        shieldString = '<b>' + GetByLabel('Tooltips/Hud/Shield')
        shieldString += '</b><br>'
        shieldString += '%s / %s' % (FormatNumeric(self.controller.GetShieldHP(), useGrouping=True, decimalPlaces=0), FormatNumeric(self.controller.GetShieldHPMax(), useGrouping=True, decimalPlaces=0))
        tooltipPanel.labelShield.text = shieldString
        tooltipPanel.valueLabelShield.text = GetByLabel('UI/Common/Formatting/Percentage', percentage=shield * 100)
        armorString = '<b>' + GetByLabel('Tooltips/Hud/Armor')
        armorString += '</b><br>'
        armorString += '%s / %s' % (FormatNumeric(self.controller.GetArmorHP(), useGrouping=True, decimalPlaces=0), FormatNumeric(self.controller.GetArmorHPMax(), useGrouping=True, decimalPlaces=0))
        tooltipPanel.labelArmor.text = armorString
        tooltipPanel.valueLabelArmor.text = GetByLabel('UI/Common/Formatting/Percentage', percentage=armor * 100)
        structureString = '<b>' + GetByLabel('Tooltips/Hud/Structure')
        structureString += '</b><br>'
        structureString += '%s / %s' % (FormatNumeric(self.controller.GetStructureHP(), useGrouping=True, decimalPlaces=0), FormatNumeric(self.controller.GetStructureHPMax(), useGrouping=True, decimalPlaces=0))
        tooltipPanel.labelStructure.text = structureString
        tooltipPanel.valueLabelStructure.text = GetByLabel('UI/Common/Formatting/Percentage', percentage=structure * 100)


class ShipHudSpriteGauge(Sprite):
    default_opacity = OPACITY_BARS
    default_width = 148
    default_height = 148
    default_textureSecondaryPath = 'res:/UI/Texture/classes/ShipUI/gaugeFill.png'
    default_shadowOffset = (0, 1)

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        self.textureSecondary.useTransform = True
        self.textureSecondary.rotation = 0.0
        self._lastValue = None

    @property
    def value(self):
        return self._lastValue

    @value.setter
    def value(self, value):
        rotation = math.pi * (1.0 - value)
        self.textureSecondary.rotation = rotation

    def UpdateValue(self, value):
        if self._lastValue is None:
            self.StopAnimations()
            self.value = value
        else:
            self.AnimGauge(value)
        self._lastValue = value

    def AnimGauge(self, value):
        uicore.animations.MorphScalar(self, 'value', self._lastValue, value, duration=0.5)
