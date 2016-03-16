#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\inventory\containerContentWindow.py
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveWindow import Window
from eve.common.script.sys.eveCfg import GetShipFlagLocationName
import evetypes
from eve.client.script.ui.control import entries as listentry
from localization import GetByLabel
import carbonui.const as uiconst

class ContainerContentWindow(Window):
    __guid__ = 'ContainerContentWindow'
    default_width = 500
    default_height = 400
    default_minSize = (500, 256)
    default_windowID = 'containerContentWindow'
    default_captionLabelPath = 'UI/Menusvc/ItemsInContainerHint'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(0)
        self.topHint = EveLabelMedium(text='', parent=self.sr.main, top=4, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, padding=4)
        self.scroll = Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding), id='containerContentWindow')

    def LoadContent(self, itemID, hasFlag, stationID, typeName, invCacheSvc):
        hint = '<center>' + GetByLabel('UI/Menusvc/ItemsInContainerHint2', containerName=typeName)
        self.topHint.SetText(hint)
        if hasFlag:
            hdr = [GetByLabel('UI/Inventory/InvItemNameShort'),
             GetByLabel('UI/Inventory/ItemGroup'),
             GetByLabel('UI/Common/Location'),
             GetByLabel('UI/Common/Quantity')]
        else:
            hdr = [GetByLabel('UI/Inventory/InvItemNameShort'), GetByLabel('UI/Inventory/ItemGroup'), GetByLabel('UI/Common/Quantity')]
        contentList = self.GetContentsList(itemID, hasFlag, stationID, invCacheSvc)
        self.scroll.Load(contentList=contentList, headers=hdr, noContentHint=GetByLabel('UI/Common/NothingFound'))

    def GetContentsList(self, itemID, hasFlag, stationID, invCacheSvc):
        contents = invCacheSvc.GetInventoryMgr().GetContainerContents(itemID, stationID)
        lst = []
        for c in contents:
            flag = c.flagID
            if flag == const.flagPilot:
                continue
            locationName = GetShipFlagLocationName(flag)
            typeName = evetypes.GetName(c.typeID)
            groupID = evetypes.GetGroupID(c.typeID)
            if hasFlag:
                txt = '%s<t>%s<t>%s<t><right>%s' % (typeName,
                 evetypes.GetGroupNameByGroup(groupID),
                 locationName,
                 c.stacksize)
            else:
                txt = '%s<t>%s<t><right>%s' % (typeName, evetypes.GetGroupNameByGroup(groupID), c.stacksize)
            data = {'label': txt,
             'typeID': c.typeID,
             'itemID': c.itemID,
             'getIcon': True}
            entry = listentry.Get(entryType='Item', data=data)
            lst.append(entry)

        return lst
