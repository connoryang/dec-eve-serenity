#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostFittingPanels\targetingPanel.py
from dogma import const as dogmaConst
from eve.client.script.ui.shared.fitting.panels.attributePanel import AttributePanel
from eve.client.script.ui.shared.fittingGhost.fittingUtilGhost import GetColoredText
from localization import GetByLabel, GetByMessageID

class TargetingPanel(AttributePanel):
    attributesToShow = [('sensorStrength', dogmaConst.attributeScanResolution), (dogmaConst.attributeSignatureRadius, dogmaConst.attributeMaxLockedTargets)]

    def LoadPanel(self, initialLoad = False):
        AttributePanel.LoadPanel(self, initialLoad)
        activeShip = self.dogmaLocation.shipID
        sensorStrengthAttributeID, val = self.GetSensorStrengthAttribute(activeShip)
        parentGrid = self.GetValueParentGrid()
        for eachLine in self.attributesToShow:
            for eachAttributeID in eachLine:
                if eachAttributeID == 'sensorStrength':
                    each = sensorStrengthAttributeID
                else:
                    each = eachAttributeID
                attribute = cfg.dgmattribs.Get(each)
                icon, label, cont = self.AddAttributeCont(attribute, parentGrid, eachAttributeID)

        AttributePanel.FinalizePanelLoading(self, initialLoad)

    def GetSensorStrengthAttribute(self, shipID):
        if session.shipid == shipID:
            return sm.GetService('godma').GetStateManager().GetSensorStrengthAttribute(shipID)
        else:
            dogmaLocation = sm.GetService('fittingSvc').GetCurrentDogmaLocation()
            return dogmaLocation.GetSensorStrengthAttribute(shipID)

    def UpdateTargetingPanel(self):
        self.SetTargetingHeader()
        self.SetScanResolutionText()
        self.SetMaxTargetsText()
        self.SetSignatureText()
        self.SetSensorStrenghtElements()

    def SetTargetingHeader(self):
        maxTargetRangeInfo = self.controller.GetMaxTargetRange()
        maxRange = maxTargetRangeInfo.value / 1000.0
        text = GetByLabel('UI/Fitting/FittingWindow/TargetingHeader', maxRange=maxRange)
        coloredText = GetColoredText(isBetter=maxTargetRangeInfo.isBetterThanBefore, text=text)
        headerHint = GetByLabel('UI/Fitting/FittingWindow/TargetingHeaderHint')
        self.SetStatusText(coloredText, headerHint)

    def SetScanResolutionText(self):
        scanResolutionInfo = self.controller.GetScanResolution()
        text = GetByLabel('UI/Fitting/FittingWindow/ScanResolution', resolution=int(scanResolutionInfo.value))
        coloredText = GetColoredText(isBetter=scanResolutionInfo.isBetterThanBefore, text=text)
        self.SetLabel(scanResolutionInfo.attributeID, coloredText)

    def SetMaxTargetsText(self):
        maxTargetingInfo = self.controller.GetMaxTargets()
        text = GetByLabel('UI/Fitting/FittingWindow/MaxLockedTargets', maxTargets=int(maxTargetingInfo.value))
        coloredText = GetColoredText(isBetter=maxTargetingInfo.isBetterThanBefore, text=text)
        self.SetLabel(maxTargetingInfo.attributeID, coloredText)

    def SetSignatureText(self):
        signatureRadiusInfo = self.controller.GetSignatureRadius()
        text = GetByLabel('UI/Fitting/FittingWindow/TargetingRange', range=signatureRadiusInfo.value)
        coloredText = GetColoredText(isBetter=signatureRadiusInfo.isBetterThanBefore, text=text)
        self.SetLabel(signatureRadiusInfo.attributeID, coloredText)

    def SetSensorStrenghtElements(self):
        sensorStrenghtInfos = {dogmaConst.attributeScanRadarStrength: self.controller.GetScanRadarStrength(),
         dogmaConst.attributeScanMagnetometricStrength: self.controller.GetScanMagnetometricStrength(),
         dogmaConst.attributeScanGravimetricStrength: self.controller.GetScanGravimetricStrength(),
         dogmaConst.attributeScanLadarStrength: self.controller.GetScanLadarStrength()}
        maxSensorStrenghtAttributeID, maxSensorStrengthInfo = (None, None)
        for attributeID, strengthInfo in sensorStrenghtInfos.iteritems():
            if maxSensorStrengthInfo is None or strengthInfo.value > maxSensorStrengthInfo.value:
                maxSensorStrengthInfo = strengthInfo
                maxSensorStrenghtAttributeID = attributeID

        text = GetByLabel('UI/Fitting/FittingWindow/SensorStrength', points=maxSensorStrengthInfo.value)
        coloredText = GetColoredText(isBetter=maxSensorStrengthInfo.isBetterThanBefore, text=text)
        self.SetLabel('sensorStrength', coloredText)
        attributeInfo = cfg.dgmattribs.Get(maxSensorStrenghtAttributeID)
        self.LoadIcon('sensorStrength', attributeInfo.iconID)

    def SetSensorTooltip(self, maxSensor):
        return
        cont = self.statsContsByIdentifier.get('sensorStrength', None)
        tooltipTitleID = maxSensor.tooltipTitleID
        if tooltipTitleID:
            tooltipTitle = GetByMessageID(tooltipTitleID)
            cont.tooltipPanelClassInfo.headerText = tooltipTitle
