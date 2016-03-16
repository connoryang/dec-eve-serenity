#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostFittingPanels\navigationPanel.py
from carbon.common.script.util.format import FmtDist
from dogma import const as dogmaConst
from eve.client.script.ui.shared.fitting.panels.attributePanel import AttributePanel
from eve.client.script.ui.shared.fittingGhost.fittingUtilGhost import GetColoredText
from eve.common.lib import appConst
from localization import GetByLabel

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

    def UpdateNavigationPanel(self):
        self.SetMassText()
        self.SetMaxVelocityText()
        self.SetAgilityText()
        self.SetWarpSpeedText()

    def SetMassText(self):
        massInfo = self.controller.GetMass()
        if massInfo.value > 10000.0:
            value = massInfo.value / 1000.0
            massText = GetByLabel('UI/Fitting/FittingWindow/MassTonnes', mass=value)
        else:
            massText = GetByLabel('UI/Fitting/FittingWindow/MassKg', mass=massInfo.value)
        coloredText = GetColoredText(isBetter=massInfo.isBetterThanBefore, text=massText)
        self.SetLabel(dogmaConst.attributeMass, coloredText)

    def SetMaxVelocityText(self):
        maxVelocityInfo = self.controller.GetMaxVelocity()
        text = GetByLabel('UI/Fitting/FittingWindow/ColoredMaxVelocity', maxVelocity=maxVelocityInfo.value)
        coloredText = GetColoredText(isBetter=maxVelocityInfo.isBetterThanBefore, text=text)
        self.SetStatusText(coloredText)

    def SetAgilityText(self):
        agilityInfo = self.controller.GetAgility()
        text = GetByLabel('UI/Fitting/FittingWindow/InertiaModifier', value=agilityInfo.value)
        coloredText = GetColoredText(isBetter=agilityInfo.isBetterThanBefore, text=text)
        self.SetLabel(dogmaConst.attributeAgility, coloredText)

    def SetWarpSpeedText(self):
        baseWarpSpeedInfo = self.controller.GetBaseWarpSpeed()
        warpSpeedMultiplierInfo = self.controller.GetWarpSpeedMultiplier()
        distValue = baseWarpSpeedInfo.value * warpSpeedMultiplierInfo.value * appConst.AU
        text = GetByLabel('UI/Fitting/FittingWindow/WarpSpeed', distText=FmtDist(distValue, 2))
        coloredText = GetColoredText(isBetter=warpSpeedMultiplierInfo.isBetterThanBefore, text=text)
        self.SetLabel(dogmaConst.attributeBaseWarpSpeed, coloredText)
