#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\panels\targetingPanel.py
from dogma import const as dogmaConst
from eve.client.script.ui.shared.fitting.fittingUtil import GetShipAttribute, GetMultiplyColor, GetXtraColor, GetColor, GetSensorStrengthAttribute
from eve.client.script.ui.shared.fitting.panels.attributePanel import AttributePanel
from localization import GetByLabel, GetByMessageID

class TargetingPanel(AttributePanel):
    attributesToShow = [('sensorStrength', dogmaConst.attributeScanResolution), (dogmaConst.attributeSignatureRadius, dogmaConst.attributeMaxLockedTargets)]

    def LoadPanel(self, initialLoad = False):
        AttributePanel.LoadPanel(self, initialLoad)
        activeShip = self.dogmaLocation.GetCurrentShipID()
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
            return self.dogmaLocation.GetSensorStrengthAttribute(shipID)

    def UpdateTargetingPanel(self, shipID, maxLockedTargetsAdd, multiplyMaxTargetRange, sensorStrengthAttrs, sensorStrengthBonus, sensorStrengthBonusAttrs, sensorStrengthPercent, sensorStrengthPercentAttrs, typeAttributesByID):
        self.SetTargetingHeader(shipID, multiplyMaxTargetRange)
        self.SetScanResolutionText(shipID, typeAttributesByID)
        self.SetMaxTargetsText(shipID, maxLockedTargetsAdd)
        self.SetSignatureText(shipID, typeAttributesByID)
        self.SetSensorStrenghtElements(shipID, sensorStrengthAttrs, sensorStrengthBonus, sensorStrengthBonusAttrs, sensorStrengthPercent, sensorStrengthPercentAttrs)

    def SetTargetingHeader(self, shipID, multiplyMaxTargetRange):
        maxTargetRange = GetShipAttribute(shipID, dogmaConst.attributeMaxTargetRange)
        maxRange = maxTargetRange * multiplyMaxTargetRange / 1000.0
        headerText = GetMultiplyColor(multiplyMaxTargetRange)
        headerText += GetByLabel('UI/Fitting/FittingWindow/TargetingHeader', startColorTag='', endColorTag='', maxRange=maxRange)
        headerHint = GetByLabel('UI/Fitting/FittingWindow/TargetingHeaderHint')
        self.SetStatusText(headerText, headerHint)

    def SetScanResolutionText(self, shipID, typeAttributesByID):
        multiplyScanResolution = typeAttributesByID.get(dogmaConst.attributeScanResolutionMultiplier, 1.0)
        if dogmaConst.attributeScanResolutionBonus in typeAttributesByID:
            multiplyScanResolution *= 1 + typeAttributesByID[dogmaConst.attributeScanResolutionBonus] / 100
        scanResolution = GetShipAttribute(shipID, dogmaConst.attributeScanResolution)
        srt = GetMultiplyColor(multiplyScanResolution)
        srt += GetByLabel('UI/Fitting/FittingWindow/ScanResolution', resolution=int(scanResolution * multiplyScanResolution))
        self.SetLabel(dogmaConst.attributeScanResolution, srt)

    def SetMaxTargetsText(self, shipID, maxLockedTargetsAdd):
        maxLockedTargets = GetShipAttribute(shipID, dogmaConst.attributeMaxLockedTargets)
        maxLockedTargetsText = GetXtraColor(maxLockedTargetsAdd)
        maxLockedTargetsText += GetByLabel('UI/Fitting/FittingWindow/MaxLockedTargets', maxTargets=int(maxLockedTargets + maxLockedTargetsAdd))
        self.SetLabel(dogmaConst.attributeMaxLockedTargets, maxLockedTargetsText)

    def SetSignatureText(self, shipID, typeAttributesByID):
        signatureRadius = GetShipAttribute(shipID, dogmaConst.attributeSignatureRadius)
        signatureRadiusAdd = typeAttributesByID.get(dogmaConst.attributeSignatureRadiusAdd, 0.0)
        signatureRadiusText = GetXtraColor(signatureRadiusAdd)
        signatureRadiusText += GetByLabel('UI/Fitting/FittingWindow/TargetingRange', range=signatureRadius + signatureRadiusAdd)
        self.SetLabel(dogmaConst.attributeSignatureRadius, signatureRadiusText)

    def SetSensorStrenghtElements(self, shipID, sensorStrengthAttrs, sensorStrengthBonus, sensorStrengthBonusAttrs, sensorStrengthPercent, sensorStrengthPercentAttrs):
        maxSensor, maxSensorStrength, ssBValue, ssPValue = self.GetSensorStrengthValues(shipID, sensorStrengthAttrs, sensorStrengthBonus, sensorStrengthBonusAttrs, sensorStrengthPercent, sensorStrengthPercentAttrs)
        self.SetSensorText(maxSensorStrength, ssBValue, ssPValue)
        self.LoadIcon('sensorStrength', maxSensor.iconID)
        self.SetSensorTooltip(maxSensor)

    def SetSensorText(self, maxSensorStrength, ssBValue, ssPValue):
        statsText = GetColor(multi=(ssBValue + ssPValue) / 2.0)
        statsText += GetByLabel('UI/Fitting/FittingWindow/SensorStrength', points=maxSensorStrength * ssBValue * ssPValue)
        self.SetLabel('sensorStrength', statsText)

    def SetSensorTooltip(self, maxSensor):
        return
        cont = self.statsContsByIdentifier.get('sensorStrength', None)
        tooltipTitleID = maxSensor.tooltipTitleID
        if tooltipTitleID:
            tooltipTitle = GetByMessageID(tooltipTitleID)
            cont.tooltipPanelClassInfo.headerText = tooltipTitle

    def GetSensorStrengthValues(self, shipID, sensorStrengthAttrs, sensorStrengthBonus, sensorStrengthBonusAttrs, sensorStrengthPercent, sensorStrengthPercentAttrs):
        sensorStrengthAttributeID, maxSensorStrength = GetSensorStrengthAttribute(self.dogmaLocation, shipID)
        maxSensor = cfg.dgmattribs.Get(sensorStrengthAttributeID)
        attrIdx = sensorStrengthAttrs.index(maxSensor.attributeID)
        sensorBonusAttributeID = sensorStrengthBonusAttrs[attrIdx]
        sensorPercentAttributeID = sensorStrengthPercentAttrs[attrIdx]
        ssB = sensorStrengthBonus.get(sensorBonusAttributeID, None)
        ssP = sensorStrengthPercent.get(sensorPercentAttributeID, None)
        ssBValue = 1.0
        ssPValue = 1.0
        if ssB:
            ssBValue = 1.0 + ssB.value / 100.0
        if ssP:
            ssPValue = 1.0 + ssP.value / 100.0
        return (maxSensor,
         maxSensorStrength,
         ssBValue,
         ssPValue)
