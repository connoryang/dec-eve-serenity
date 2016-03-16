#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\info\infoUtil.py
import localization

def GetAttributeTooltipTitleAndDescription(attributeID):
    if attributeID:
        attributeInfo = cfg.dgmattribs.Get(attributeID)
        tooltipTitleID = attributeInfo.tooltipTitleID
        if tooltipTitleID:
            tooltipDescriptionID = attributeInfo.tooltipDescriptionID
            return (localization.GetByMessageID(tooltipTitleID), localization.GetByMessageID(tooltipDescriptionID))
    return (None, None)
