#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\shipSlot.py
from carbonui import const as uiconst
import uiprimitives
import telemetry

class ShipSlot(uiprimitives.Container):
    default_pickRadius = 24

    def OnDropData(self, dragObj, nodes):
        flag1 = self.sr.slotFlag
        for node in nodes:
            decoClass = node.Get('__guid__', None)
            if decoClass == 'xtriui.ShipUIModule':
                flag2 = node.slotFlag
                if flag2 is not None:
                    uicore.layer.shipui.SwapSlots(flag1, node.slotFlag)
                break
            elif decoClass in ('xtriui.InvItem', 'listentry.InvItem'):
                item = node.rec
                if item.flagID == const.flagCargo and item.categoryID == const.categoryModule:
                    sm.GetService('invCache').GetInventoryFromId(session.shipid).Add(item.itemID, item.locationID, qty=None, flag=flag1)
                break

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        overloadBtn = uiprimitives.Sprite(parent=self, name='overloadBtn', pos=(16, 6, 32, 16), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/ShipUI/slotOverloadDisabled.png')
        self.mainShape = uiprimitives.Sprite(parent=self, name='mainshape', pos=(0, 0, 0, 0), align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotMainCombined.png')
