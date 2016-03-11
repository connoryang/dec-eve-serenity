#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\panels\attributePanel.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.fitting.panels.basePanel import BaseMenuPanel
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
from localization import GetByMessageID

class AttributePanel(BaseMenuPanel):

    def ApplyAttributes(self, attributes):
        BaseMenuPanel.ApplyAttributes(self, attributes)

    def LoadPanel(self, initialLoad = False):
        self.Flush()
        self.ResetStatsDicts()

    def AddAttributeCont(self, attribute, parentGrid, attributeID = None):
        if attributeID is None:
            attributeID = attribute.attributeID
        iconSize = 32
        attributeCont = self.GetValueCont(iconSize)
        parentGrid.AddCell(cellObject=attributeCont)
        icon = Icon(graphicID=attribute.iconID, pos=(3,
         0,
         iconSize,
         iconSize), hint=attribute.displayName, name=attribute.displayName, ignoreSize=True, state=uiconst.UI_DISABLED)
        attributeCont.AddCell(cellObject=icon)
        label = EveLabelMedium(text='', left=0, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        attributeCont.AddCell(cellObject=label)
        attributeCont.hint = attribute.displayName
        tooltipTitleID = attribute.tooltipTitleID
        if tooltipTitleID:
            tooltipTitle = GetByMessageID(tooltipTitleID)
            tooltipDescr = GetByMessageID(attribute.tooltipDescriptionID)
            SetTooltipHeaderAndDescription(targetObject=attributeCont, headerText=tooltipTitle, descriptionText=tooltipDescr)
        self.statsLabelsByIdentifier[attributeID] = label
        self.statsIconsByIdentifier[attributeID] = icon
        self.statsContsByIdentifier[attributeID] = attributeCont
        return (icon, label, attributeCont)
