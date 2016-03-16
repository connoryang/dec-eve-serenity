#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\baseSlot.py
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_WORLDMOD
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import const as uiconst
from carbonui.control.menuLabel import MenuLabel
from carbonui.primitives.transform import Transform
from carbonui.util.various_unsorted import GetAttrs, IsUnder
from eve.client.script.ui.shared.fitting.utilBtns import UtilBtnData
import inventorycommon.const as invConst
from localization import GetByLabel
import localization

class FittingSlotBase(Transform):
    slotsToHintDict = {}

    def ApplyAttributes(self, attributes):
        Transform.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.utilButtons = []
        self._emptyHint, self._emptyTooltip = self.PrimeToEmptySlotHint()
        self.controller.on_online_state_change.connect(self.UpdateOnlineDisplay)
        self.controller.on_item_fitted.connect(self.UpdateFitting)

    def UpdateFitting(self):
        pass

    def DisableSlot(self):
        self.opacity = 0.1
        self.state = uiconst.UI_DISABLED
        self.flagIcon.state = uiconst.UI_HIDDEN

    def EnableSlot(self):
        self.opacity = 1.0
        self.state = uiconst.UI_NORMAL
        self.flagIcon.state = uiconst.UI_DISABLED

    def HideSlot(self):
        self.state = uiconst.UI_HIDDEN

    def ColorUnderlay(self, color = None):
        a = self.sr.underlay.color.a
        r, g, b = color or (1.0, 1.0, 1.0)
        self.sr.underlay.color.SetRGB(r, g, b, a)
        self.UpdateOnlineDisplay()

    def GetMenu(self):
        if self.controller.GetModuleTypeID() and self.controller.GetModuleID():
            m = []
            if eve.session.role & (ROLE_GML | ROLE_WORLDMOD):
                m += [(str(self.controller.GetModuleID()), self.CopyItemIDToClipboard, (self.controller.GetModuleID(),)), None]
            m += [(MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo)]
            if self.controller.IsRigSlot():
                m += [(MenuLabel('UI/Fitting/Destroy'), self.controller.Unfit)]
            else:
                if session.stationid2 is not None:
                    m += [(MenuLabel('UI/Fitting/Unfit'), self.controller.Unfit)]
                if self.controller.IsOnlineable():
                    if self.controller.IsOnline():
                        m.append((MenuLabel('UI/Fitting/PutOffline'), self.ToggleOnline))
                    else:
                        m.append((MenuLabel('UI/Fitting/PutOnline'), self.ToggleOnline))
            return m

    def OnClick(self, *args):
        uicore.registry.SetFocus(self)
        if self.controller.IsOnlineable():
            self.ToggleOnline()

    def ToggleOnline(self):
        self.controller.ToggleOnlineModule()
        self.UpdateOnlineDisplay()

    def CopyItemIDToClipboard(self, itemID):
        blue.pyos.SetClipboardData(str(itemID))

    def ShowInfo(self, *args):
        sm.GetService('info').ShowInfo(self.controller.GetModuleTypeID(), self.controller.GetModuleID())

    def OnMouseEnter(self, *args):
        if self.controller.GetModule() is not None:
            self.ShowUtilButtons()
        else:
            self.hint = self._emptyHint
            self.Hilite(1)
            uicore.Message('ListEntryEnter')

    def OnMouseExit(self, *args):
        if not self.controller.GetModule():
            self.Hilite(0)

    def Hilite(self, state):
        if state:
            self.sr.underlay.color.a = 1.0
        else:
            self.sr.underlay.color.a = 0.3

    def GetDragData(self, *args):
        return self.controller.GetDragData()

    def HiliteIfMatching(self, flagID, powerType):
        if flagID is None and powerType is None:
            if self.controller.GetModuleID() is None:
                self.Hilite(0)
        elif self.state != uiconst.UI_DISABLED and self.controller.GetModuleID() is None:
            if powerType is not None and self.controller.GetPowerType() == powerType:
                self.Hilite(1)
            if flagID is not None and self.controller.GetFlagID() == flagID:
                self.Hilite(1)

    def GetDroppedItems(self, nodes):
        items = []
        for node in nodes:
            if node.__guid__ in ('listentry.InvItem', 'xtriui.InvItem'):
                invType = node.rec
                if self.controller.IsFittableType(invType.typeID):
                    items.append(invType)

        return items

    def SetDragState(self):
        if not self.controller.GetModule() and not self.controller.GetCharge():
            self.DisableDrag()
        elif self.controller.SlotExists():
            self.EnableDrag()

    def PrimeToEmptySlotHint(self):
        flagID = self.controller.GetFlagID()
        slotKey = self.GetSlotKey(flagID)
        if slotKey is None or slotKey not in self.slotsToHintDict:
            return (GetByLabel('UI/Fitting/EmptySlot'), '')
        labelPath, tooltipName = self.slotsToHintDict[slotKey]
        return (GetByLabel(labelPath), tooltipName)

    def GetSlotKey(self, flagID):
        if flagID in invConst.hiSlotFlags:
            return 'hiSlot'
        if flagID in invConst.medSlotFlags:
            return 'medSlot'
        if flagID in invConst.loSlotFlags:
            return 'loSlot'
        if flagID in invConst.subSystemSlotFlags:
            return 'subSystemSlot'
        if flagID in invConst.rigSlotFlags:
            return 'rigSlot'

    def UpdateOnlineDisplay(self):
        if self.controller.parentController.GetItemID() == self.controller.dogmaLocation.shipIDBeingDisembarked:
            return
        if self.controller.GetModule() is not None and self.controller.IsOnlineable():
            if self.controller.IsOnline():
                self.flagIcon.SetRGBA(1.0, 1.0, 1.0, 1.0)
                if GetAttrs(self, 'sr', 'onlineButton') and self.sr.onlineButton.hint == localization.GetByLabel('UI/Fitting/PutOnline'):
                    self.sr.onlineButton.hint = localization.GetByLabel('UI/Fitting/PutOffline')
            else:
                self.flagIcon.SetRGBA(1.0, 1.0, 1.0, 0.25)
                if GetAttrs(self, 'sr', 'onlineButton') and self.sr.onlineButton.hint == localization.GetByLabel('UI/Fitting/PutOffline'):
                    self.sr.onlineButton.hint = localization.GetByLabel('UI/Fitting/PutOnline')
        elif self.flagIcon:
            if self.controller.GetModule() is None or self.controller.SlotExists():
                self.flagIcon.SetRGBA(1.0, 1.0, 1.0, 1.0)
            else:
                self.flagIcon.SetRGBA(0.7, 0.0, 0.0, 0.5)

    def GetRigsBtns(self):
        btns = [UtilBtnData(localization.GetByLabel('UI/Fitting/Destroy'), 'ui_38_16_200', self.controller.Unfit, 1, 0), UtilBtnData(localization.GetByLabel('UI/Commands/ShowInfo'), 'ui_38_16_208', self.ShowInfo, 1, 0)]
        return btns

    def GetModuleBtns(self, isOnlinable):
        if bool(self.controller.IsOnline):
            toggleLabel = localization.GetByLabel('UI/Fitting/PutOffline')
        else:
            toggleLabel = localization.GetByLabel('UI/Fitting/PutOnline')
        btns = [UtilBtnData(localization.GetByLabel('UI/Fitting/UnfitModule'), 'ui_38_16_200', self.controller.UnfitModule, 1, 0), UtilBtnData(localization.GetByLabel('UI/Commands/ShowInfo'), 'ui_38_16_208', self.ShowInfo, 1, 0), UtilBtnData(toggleLabel, 'ui_38_16_207', self.ToggleOnline, isOnlinable, 1)]
        return btns

    def ShowUtilButtons(self, *args):
        flagID = self.controller.GetFlagID()
        self.controller.parentController.SetSlotWithMenu(flagID)
        for button in self.utilButtons:
            button.SetBtnColorBasedOnIsActive()

        self.utilButtonsTimer = AutoTimer(500, self.HideUtilButtons)

    def HideUtilButtons(self, force = 0):
        mo = uicore.uilib.mouseOver
        if not force and (mo in self.utilButtons or mo == self or IsUnder(mo, self)):
            return
        for button in self.utilButtons:
            button.Hide()

        self.utilButtonsTimer = None
