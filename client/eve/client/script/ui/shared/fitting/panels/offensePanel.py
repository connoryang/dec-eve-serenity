#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\panels\offensePanel.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from eve.client.script.ui.shared.fitting.panels.basePanel import BaseMenuPanel
from localization import GetByLabel
import uthread

class OffensePanel(BaseMenuPanel):
    damageStats = (('turretDps', 'res:/UI/Texture/Icons/26_64_1.png', 'UI/Fitting/FittingWindow/TurretDpsTooltip', 'DamagePerSecondTurrets'), ('droneDps', 'res:/UI/Texture/Icons/drones.png', 'UI/Fitting/FittingWindow/DroneDpsTooltip', 'DamagePerSecondDrones'), ('missileDps', 'res:/UI/Texture/Icons/81_64_16.png', 'UI/Fitting/FittingWindow/MissileDpsTooltip', 'DamagePerSecondMissiles'))
    iconSize = 26

    def ApplyAttributes(self, attributes):
        BaseMenuPanel.ApplyAttributes(self, attributes)

    def LoadPanel(self, initialLoad = False):
        self.Flush()
        self.ResetStatsDicts()
        self.display = True
        parentGrid = self.GetValueParentGrid(columns=len(self.damageStats))
        for dps, texturePath, hintPath, tooltipName in self.damageStats:
            hint = GetByLabel(hintPath)
            c = self.GetValueCont(self.iconSize)
            parentGrid.AddCell(cellObject=c)
            icon = Sprite(texturePath=texturePath, parent=c, align=uiconst.CENTERLEFT, pos=(0,
             0,
             self.iconSize,
             self.iconSize), state=uiconst.UI_DISABLED)
            SetFittingTooltipInfo(targetObject=c, tooltipName=tooltipName)
            c.hint = hint
            label = EveLabelMedium(text='', parent=c, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
            self.statsLabelsByIdentifier[dps] = label
            self.statsIconsByIdentifier[dps] = icon
            self.statsContsByIdentifier[dps] = c

        BaseMenuPanel.FinalizePanelLoading(self, initialLoad)

    def UpdateOffenseStats(self):
        uthread.new(self._UpdateOffenseStats)

    def _UpdateOffenseStats(self):
        itemID = self.controller.GetItemID()
        turretDps, missileDps = self.dogmaLocation.GetTurretAndMissileDps(itemID)
        dpsText = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=turretDps)
        self.SetLabel('turretDps', dpsText)
        missileText = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=missileDps)
        self.SetLabel('missileDps', missileText)
        droneDps, drones = self.dogmaLocation.GetOptimalDroneDamage(itemID)
        droneText = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=droneDps)
        self.SetLabel('droneDps', droneText)
        totalDps = turretDps + missileDps + droneDps
        totalDpsText = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=totalDps)
        self.SetStatusText(totalDpsText)
