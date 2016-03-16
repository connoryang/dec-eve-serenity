#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\heatGauges.py
from carbon.common.script.util.mathUtil import DegToRad
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from localization import GetByLabel
LOW_HEAT_GAUGE_TEXTURES = ['res:/UI/Texture/classes/ShipUI/lowHeat_0.png',
 'res:/UI/Texture/classes/ShipUI/lowHeat_1.png',
 'res:/UI/Texture/classes/ShipUI/lowHeat_2.png',
 'res:/UI/Texture/classes/ShipUI/lowHeat_3.png',
 'res:/UI/Texture/classes/ShipUI/lowHeat_4.png']
MED_HEAT_GAUGE_TEXTURES = ['res:/UI/Texture/classes/ShipUI/medHeat_0.png',
 'res:/UI/Texture/classes/ShipUI/medHeat_1.png',
 'res:/UI/Texture/classes/ShipUI/medHeat_2.png',
 'res:/UI/Texture/classes/ShipUI/medHeat_3.png',
 'res:/UI/Texture/classes/ShipUI/medHeat_4.png']
HI_HEAT_GAUGE_TEXTURES = ['res:/UI/Texture/classes/ShipUI/hiHeat_0.png',
 'res:/UI/Texture/classes/ShipUI/hiHeat_1.png',
 'res:/UI/Texture/classes/ShipUI/hiHeat_2.png',
 'res:/UI/Texture/classes/ShipUI/hiHeat_3.png',
 'res:/UI/Texture/classes/ShipUI/hiHeat_4.png']
ANGLE_LOW_START = -2.0
ANGLE_MED_START = -62.0
ANGLE_HI_START = -122.0

class HeatGauges(Container):
    default_name = 'HeatGauges'
    default_state = uiconst.UI_NORMAL
    default_width = 160
    default_height = 80

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.lowHeatGauge = self.ConstructHeatGauge(ANGLE_LOW_START)
        self.medHeatGauge = self.ConstructHeatGauge(ANGLE_MED_START)
        self.hiHeatGauge = self.ConstructHeatGauge(ANGLE_HI_START)
        Sprite(parent=self, name='divider', pos=(56, 42, 46, 12), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/heatDivider.png')
        self.heatLowUnderlay = Sprite(parent=self, name='heatLowUnderlay', pos=(36, 42, 27, 38), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/lowHeat_0.png')
        self.heatMedUnderlay = Sprite(parent=self, name='heatMedUnderlay', pos=(57, 36, 45, 18), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/medHeat_0.png')
        self.heatHiUnderlay = Sprite(parent=self, name='heatHiUnderlay', pos=(95, 42, 27, 38), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/hiHeat_0.png')

    def ConstructHeatGauge(self, deg):
        miniGauge = Transform(parent=self, name='heatGauge', pos=(-1, 40, 83, 12), align=uiconst.CENTER, rotation=DegToRad(deg), idx=0)
        Sprite(parent=miniGauge, name='needle', pos=(0, 0, 12, 12), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/heatGaugeNeedle.png')
        return miniGauge

    def Update(self):
        self.UpdateLowHeatGauge(self.controller.GetHeatLowPortion())
        self.UpdateMedHeatGauge(self.controller.GetHeatMedPortion())
        self.UpdateHiHeatGauge(self.controller.GetHeatHiPortion())

    def UpdateLowHeatGauge(self, value, *args):
        rotation = DegToRad(ANGLE_LOW_START - 56.0 * value)
        uicore.animations.MorphScalar(self.lowHeatGauge, 'rotation', self.lowHeatGauge.rotation, rotation, duration=0.5)
        textureIndex = self.GetHeatGaugeTextureIndex(value)
        self.heatLowUnderlay.LoadTexture(LOW_HEAT_GAUGE_TEXTURES[textureIndex])

    def UpdateMedHeatGauge(self, value, *args):
        rotation = DegToRad(ANGLE_MED_START - 56.0 * value)
        uicore.animations.MorphScalar(self.medHeatGauge, 'rotation', self.medHeatGauge.rotation, rotation, duration=0.5)
        textureIndex = self.GetHeatGaugeTextureIndex(value)
        self.heatMedUnderlay.LoadTexture(MED_HEAT_GAUGE_TEXTURES[textureIndex])

    def UpdateHiHeatGauge(self, value, *args):
        rotation = DegToRad(ANGLE_HI_START - 56.0 * value)
        uicore.animations.MorphScalar(self.hiHeatGauge, 'rotation', self.hiHeatGauge.rotation, rotation, duration=0.5)
        textureIndex = self.GetHeatGaugeTextureIndex(value)
        self.heatHiUnderlay.LoadTexture(HI_HEAT_GAUGE_TEXTURES[textureIndex])

    def GetHeatGaugeTextureIndex(self, value):
        if value <= 1 / 8.0:
            textureIndex = 0
        elif value <= 3 / 8.0:
            textureIndex = 1
        elif value <= 5 / 8.0:
            textureIndex = 2
        elif value <= 7 / 8.0:
            textureIndex = 3
        else:
            textureIndex = 4
        return textureIndex

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric3ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=GetByLabel('Tooltips/Hud/HeatStatus'), bold=True, colSpan=tooltipPanel.columns)
        tooltipPanel.lowHeatValue = tooltipPanel.AddLabelMedium(align=uiconst.CENTERRIGHT, cellPadding=(0, 0, 14, 0), bold=True)
        tooltipPanel.mediumHeatValue = tooltipPanel.AddLabelMedium(align=uiconst.CENTERRIGHT, cellPadding=(0, 0, 14, 0), bold=True)
        tooltipPanel.highHeatValue = tooltipPanel.AddLabelMedium(align=uiconst.CENTERRIGHT, bold=True)
        self._UpdateHeatTooltip(tooltipPanel)
        self._heatTooltipUpdate = AutoTimer(10, self._UpdateHeatTooltip, tooltipPanel)

    def _UpdateHeatTooltip(self, tooltipPanel):
        if tooltipPanel.destroyed:
            self._heatTooltipUpdate = None
            return
        if not self.controller.IsLoaded():
            self._heatTooltipUpdate = None
            return
        heatLow = self.controller.GetHeatLowPortion() * 100
        tooltipPanel.lowHeatValue.text = GetByLabel('Tooltips/Hud/HeatStatusLow', percentage=heatLow)
        heatMed = self.controller.GetHeatMedPortion() * 100
        tooltipPanel.mediumHeatValue.text = GetByLabel('Tooltips/Hud/HeatStatusMedium', percentage=heatMed)
        heatHi = self.controller.GetHeatHiPortion() * 100
        tooltipPanel.highHeatValue.text = GetByLabel('Tooltips/Hud/HeatStatusHigh', percentage=heatHi)
