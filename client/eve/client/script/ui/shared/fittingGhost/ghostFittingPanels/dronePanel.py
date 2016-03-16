#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostFittingPanels\dronePanel.py
from carbonui import const as uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.fitting.panels.basePanel import BaseMenuPanel
from shipfitting.fittingDogmaLocationUtil import GetDroneRanges, GetDroneBandwidth
from localization import GetByLabel

class DronePanel(BaseMenuPanel):
    droneStats = (('bandwidth', 'res:/UI/Texture/Icons/56_64_5.png'),
     ('droneDps', 'res:/UI/Texture/Icons/drones.png'),
     ('droneRange', 'res:/UI/Texture/Icons/22_32_15.png'),
     ('controlRange', 'res:/UI/Texture/Icons/22_32_15.png'))

    def ApplyAttributes(self, attributes):
        BaseMenuPanel.ApplyAttributes(self, attributes)

    def LoadPanel(self, initialLoad = False):
        self.Flush()
        self.ResetStatsDicts()
        self.display = True
        parentGrid = self.GetValueParentGrid()
        iconSize = 32
        for configName, texturePath in self.droneStats:
            valueCont = self.GetValueCont(iconSize)
            parentGrid.AddCell(cellObject=valueCont)
            icon = Sprite(texturePath=texturePath, parent=valueCont, align=uiconst.CENTERLEFT, pos=(0,
             0,
             iconSize,
             iconSize), state=uiconst.UI_DISABLED)
            valueCont.hint = configName
            label = EveLabelMedium(text='', parent=valueCont, left=0, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
            self.statsLabelsByIdentifier[configName] = label
            self.statsIconsByIdentifier[configName] = icon
            self.statsContsByIdentifier[configName] = valueCont

        BaseMenuPanel.FinalizePanelLoading(self, initialLoad)

    def UpdateDroneStats(self):
        shipID = self.controller.GetItemID()
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        activeDrones = ghostFittingSvc.GetActiveDrones()
        bandwidthUsed, shipBandwidth = GetDroneBandwidth(shipID, self.dogmaLocation, activeDrones)
        bandwidthText = '%s/%s' % (bandwidthUsed, shipBandwidth)
        self.SetLabel('bandwidth', bandwidthText)
        minDroneRange, maxDroneRange = GetDroneRanges(shipID, self.dogmaLocation, activeDrones)
        if minDroneRange == maxDroneRange:
            droneRangeText = '%sm' % minDroneRange
        else:
            droneRangeText = '%sm<br>%sm' % (minDroneRange, maxDroneRange)
        self.SetLabel('droneRange', droneRangeText)
        droneDps, drones = self.dogmaLocation.GetOptimalDroneDamage(shipID, activeDrones)
        droneText = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=droneDps)
        self.SetLabel('droneDps', droneText)
        droneControlRange = self.dogmaLocation.GetAttributeValue(session.charid, const.attributeDroneControlDistance)
        controlRangeText = '%sm' % droneControlRange
        self.SetLabel('controlRange', controlRangeText)
