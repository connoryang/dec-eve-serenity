#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\eveTabgroupUtil.py
import localization

def FixedTabName(tabNamePath):
    enText = localization.GetByLabel(tabNamePath, localization.const.LOCALE_SHORT_ENGLISH)
    text = localization.GetByLabel(tabNamePath)
    return (enText, text)


exports = {'uiutil.FixedTabName': FixedTabName}
