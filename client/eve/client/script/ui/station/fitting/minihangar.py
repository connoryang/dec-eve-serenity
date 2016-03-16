#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\fitting\minihangar.py
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from eve.client.script.ui.shared.fitting.fittingStatsChanges import FittingStatsChanges
from inventorycommon.util import IsShipFittingFlag
import uicontrols
import uthread
import util
import carbonui.const as uiconst
import localization
import invCtrl

class CargoSlots(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.controller.on_stats_changed.connect(self.UpdateCargoSpace)
        invController = self.GetInvController()
        self.sr.icon = uicontrols.Icon(parent=self, size=32, state=uiconst.UI_DISABLED, ignoreSize=True, icon=invController.GetIconName())
        self.sr.hint = invController.GetName()
        self.sr.hilite = Fill(parent=self, name='hilite', align=uiconst.RELATIVE, state=uiconst.UI_HIDDEN, idx=-1, width=32, height=self.height)
        self.sr.icon.color.a = 0.8
        Container(name='push', parent=self, align=uiconst.TOLEFT, width=32)
        self.sr.statusCont = Container(name='statusCont', parent=self, align=uiconst.TOLEFT, width=50)
        self.sr.statustext1 = uicontrols.EveLabelMedium(text='status', parent=self.sr.statusCont, name='cargo_statustext', left=0, top=2, idx=0, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
        self.sr.statustext2 = uicontrols.EveLabelMedium(text='status', parent=self.sr.statusCont, name='cargo_statustext', left=0, top=14, idx=0, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
        m3TextCont = Container(name='m3Cont', parent=self, align=uiconst.TOLEFT, width=12)
        self.sr.m3Text = uicontrols.EveLabelMedium(text=localization.GetByLabel('UI/Fitting/FittingWindow/CubicMeters'), parent=m3TextCont, name='m3', left=4, top=14, idx=0)
        sm.GetService('inv').Register(self)
        self.invReady = 1
        self.UpdateCargoSpace()

    def IsItemHere(self, item):
        return self.GetInvController().IsItemHere(item)

    def AddItem(self, item):
        self.Update()

    def UpdateItem(self, item, *etc):
        self.Update()

    def RemoveItem(self, item):
        self.Update()

    def OnMouseEnter(self, *args):
        self.DoMouseEntering()

    def OnMouseEnterDrone(self, *args):
        if eve.session.stationid:
            self.DoMouseEntering()

    def DoMouseEntering(self):
        self.Hilite(1)
        self.sr.statustext1.OnMouseEnter()
        self.sr.statustext2.OnMouseEnter()
        self.sr.m3Text.OnMouseEnter()

    def OnMouseExit(self, *args):
        self.Hilite(0)
        self.sr.statustext1.OnMouseExit()
        self.sr.statustext2.OnMouseExit()
        self.sr.m3Text.OnMouseExit()
        uthread.new(self.Update)

    def Hilite(self, state):
        self.sr.icon.color.a = [0.8, 1.0][state]

    def SetStatusText(self, text1, text2, color):
        self.sr.statustext1.text = text1
        self.sr.statustext2.text = localization.GetByLabel('UI/Fitting/FittingWindow/CargoUsage', color=color, text=text2)
        self.sr.statusCont.width = max(0, self.sr.statustext1.textwidth, self.sr.statustext2.textwidth)

    def OnDropData(self, dragObj, nodes):
        self.Hilite(0)

    def Update(self, multiplier = 1.0):
        uthread.new(self._Update, multiplier)

    def _Update(self, multiplier):
        cap = self.GetCapacity()
        if not cap:
            return
        if not self or self.destroyed:
            return
        cap2 = cap.capacity * multiplier
        color = '<color=0xc0ffffff>'
        if multiplier != 1.0:
            color = '<color=0xffffff00>'
        used = util.FmtAmt(cap.used, showFraction=1)
        cap2 = util.FmtAmt(cap2, showFraction=1)
        self.SetStatusText(used, cap2, color)

    def GetCapacity(self, flag = None):
        return self.GetInvController().GetCapacity()


class CargoDroneSlots(CargoSlots):

    def GetInvController(self):
        return invCtrl.ShipDroneBay(self.controller.GetItemID())

    def OnDropData(self, dragObj, nodes):
        invCtrl.ShipDroneBay(util.GetActiveShip()).OnDropData(nodes)
        CargoSlots.OnDropData(self, dragObj, nodes)

    def OnClick(self, *args):
        uicore.cmd.OpenDroneBayOfActiveShip()

    def UpdateCargoSpace(self):
        typeID = self.controller.GetGhostFittedTypeID()
        fittingChanges = FittingStatsChanges(typeID)
        xtraDroneSpace = fittingChanges.GetExtraDroneSpaceMultiplier()
        self.Update(xtraDroneSpace)


class CargoCargoSlots(CargoSlots):

    def GetInvController(self):
        return invCtrl.ShipCargo(self.controller.GetItemID())

    def OnDropData(self, dragObj, nodes):
        self.Hilite(0)
        if len(nodes) == 1:
            item = nodes[0].item
            if IsShipFittingFlag(item.flagID):
                dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
                shipID = util.GetActiveShip()
                if cfg.IsFittableCategory(item.categoryID):
                    dogmaLocation.UnloadModuleToContainer(shipID, item.itemID, (shipID,), flag=const.flagCargo)
                    return
                if item.categoryID == const.categoryCharge:
                    dogmaLocation.UnloadChargeToContainer(shipID, item.itemID, (shipID,), const.flagCargo)
                    return
        invCtrl.ShipCargo(util.GetActiveShip()).OnDropData(nodes)
        CargoSlots.OnDropData(self, dragObj, nodes)

    def OnClick(self, *args):
        uicore.cmd.OpenCargoHoldOfActiveShip()

    def UpdateCargoSpace(self):
        typeID = self.controller.GetGhostFittedTypeID()
        fittingChanges = FittingStatsChanges(typeID)
        xtraCargoSpace = fittingChanges.GetExtraCargoSpaceMultiplier()
        self.Update(xtraCargoSpace)
