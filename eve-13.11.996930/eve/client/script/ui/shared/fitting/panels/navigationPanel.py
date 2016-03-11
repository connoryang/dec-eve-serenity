#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\panels\navigationPanel.py
from carbon.common.script.util.format import FmtDist
from dogma import const as dogmaConst
from eve.client.script.ui.shared.fitting.fittingUtil import GetShipAttribute, GetXtraColor, GetColor2
from eve.client.script.ui.shared.fitting.panels.attributePanel import AttributePanel
from eve.common.lib import appConst
from localization import GetByLabel
__author__ = 'bara'

class NavigationPanel(AttributePanel):
    attributesToShow = ((dogmaConst.attributeMass, dogmaConst.attributeAgility), (dogmaConst.attributeBaseWarpSpeed,))

    def LoadPanel(self, initialLoad = False):
        AttributePanel.LoadPanel(self, initialLoad)
        parentGrid = self.GetValueParentGrid()
        for eachLine in self.attributesToShow:
            for eachAttributeID in eachLine:
                attribute = cfg.dgmattribs.Get(eachAttributeID)
                icon, label, cont = self.AddAttributeCont(attribute, parentGrid)

        AttributePanel.FinalizePanelLoading(self, initialLoad)

    def UpdateNavigationPanel(self, shipID, multiplySpeed, typeAttributesByID):
        self.SetMassText(shipID, typeAttributesByID)
        self.SetMaxVelocityText(shipID, multiplySpeed, typeAttributesByID)
        self.SetAgilityText(shipID)

    def SetMassText(self, shipID, typeAttributesByID):
        massAddition = typeAttributesByID.get(dogmaConst.attributeMassAddition, 0.0)
        mass = GetShipAttribute(shipID, dogmaConst.attributeMass)
        value = int(mass + massAddition)
        color = GetXtraColor(massAddition)
        if value > 10000.0:
            value = value / 1000.0
            massText = color + GetByLabel('UI/Fitting/FittingWindow/MassTonnes', mass=value)
        else:
            massText = color + GetByLabel('UI/Fitting/FittingWindow/MassKg', mass=value)
        self.SetLabel(dogmaConst.attributeMass, massText)

    def SetMaxVelocityText(self, shipID, multiplySpeed, typeAttributesByID):
        xtraSpeed = typeAttributesByID.get(dogmaConst.attributeSpeedBonus, 0.0) + typeAttributesByID.get(dogmaConst.attributeMaxVelocity, 0.0)
        multiplyVelocity = typeAttributesByID.get(dogmaConst.attributeVelocityModifier, None)
        if multiplyVelocity is not None:
            multiplyVelocity = 1 + multiplyVelocity / 100 * multiplySpeed
        else:
            multiplyVelocity = 1.0 * multiplySpeed
        maxVelocity = GetShipAttribute(shipID, dogmaConst.attributeMaxVelocity)
        maxVelocityText = '<color=%s>' % hex(GetColor2(xtraSpeed, multiplyVelocity))
        maxVelocityText += GetByLabel('UI/Fitting/FittingWindow/ColoredMaxVelocity', maxVelocity=(maxVelocity + xtraSpeed) * multiplyVelocity)
        maxVelocityText += '</color>'
        self.SetStatusText(maxVelocityText)

    def SetAgilityText(self, shipID):
        agility = GetShipAttribute(shipID, dogmaConst.attributeAgility)
        agilityText = GetByLabel('UI/Fitting/FittingWindow/InertiaModifier', value=agility)
        self.SetLabel(dogmaConst.attributeAgility, agilityText)
        baseWarpSpeed = GetShipAttribute(shipID, dogmaConst.attributeBaseWarpSpeed)
        warpSpeedMultiplier = GetShipAttribute(shipID, dogmaConst.attributeWarpSpeedMultiplier)
        baseWarpSpeedText = GetByLabel('UI/Fitting/FittingWindow/WarpSpeed', distText=FmtDist(baseWarpSpeed * warpSpeedMultiplier * appConst.AU, 2))
        self.SetLabel(dogmaConst.attributeBaseWarpSpeed, baseWarpSpeedText)
