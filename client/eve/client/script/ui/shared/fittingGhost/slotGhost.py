#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\slotGhost.py
import math
import logging
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from eve.client.script.ui.shared.fitting.fittingUtil import GetScaleFactor, RigFittingCheck
import evetypes
from eve.client.script.ui.shared.fittingGhost.ghostFittingUtil import ONLINE, OFFLINE, ACTIVE, OVERHEATED
from shipfitting.fittingStuff import IsRightSlotForType
import uicontrols
import uix
import uiutil
import mathUtil
import uthread
import blue
import util
import carbon.client.script.util.lg as lg
import service
import base
import uicls
import carbonui.const as uiconst
import localization
from eve.client.script.ui.inflight.shipModuleButton.moduleButtonTooltip import TooltipModuleWrapper
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
import telemetry
import inventorycommon.typeHelpers
MAXMODULEHINTWIDTH = 300
logger = logging.getLogger(__name__)

class FittingSlotGhost(Transform):
    __guid__ = 'xtriui.FittingSlotGhost'
    __notifyevents__ = ['OnRefreshModuleBanks']
    default_name = 'fittingSlot'
    default_width = 44
    default_height = 54
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    isDragObject = True

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        Transform.ApplyAttributes(self, attributes)
        self.flagIcon = uicontrols.Icon(parent=self, name='flagIcon', align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=self.width, height=self.height)
        self.sr.underlay = Sprite(bgParent=self, name='underlay', state=uiconst.UI_DISABLED, padding=(-10, -5, -10, -5), texturePath='res:/UI/Texture/Icons/81_64_1.png')
        self.dontHaveLine = None
        self.moduleSlotFill = None
        self.skillSprite = None
        self.groupMark = None
        self.chargeIndicator = None
        sm.RegisterNotify(self)
        self.radCosSin = attributes.radCosSin
        self.controller = attributes.controller
        self.utilButtons = []
        self._emptyHint, self._emptyTooltip = self.PrimeToEmptySlotHint()
        self.invReady = 1
        self.hilitedFromMathing = False
        self.UpdateFitting()
        self.controller.on_online_state_change.connect(self.UpdateOnlineDisplay)
        self.controller.on_item_fitted.connect(self.UpdateFitting)

    def ConstructDontHaveLine(self):
        if self.dontHaveLine:
            return
        self.dontHaveLine = Sprite(parent=self, name='dontHaveLine', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/moduleFrameDots.png', padding=(-10, -5, -10, -5), color=(1, 1, 0, 1.0))

    def ConstructModuleSlotFill(self):
        if self.moduleSlotFill:
            return
        self.moduleSlotFill = Sprite(parent=self, name='moduleSlotFill', align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=(-8, -4, -8, -4), texturePath='res:/UI/Texture/classes/Fitting/moduleSlotFill.png', color=(1, 1, 1, 0.5))
        self.moduleSlotFill.display = False

    def ConstructSkillSprite(self):
        if self.skillSprite:
            return
        self.skillSprite = Sprite(name='skillSprite', parent=self, pos=(0, 0, 16, 16), align=uiconst.CENTERBOTTOM, texturePath='res:/UI/Texture/Icons/38_16_193.png', idx=0)

    def ConstructGroupMark(self):
        if self.groupMark:
            return
        self.groupMark = Sprite(parent=self, name='groupMark', pos=(-10, 14, 16, 16), align=uiconst.CENTER, state=uiconst.UI_NORMAL, idx=0)
        self.groupMark.GetMenu = self.GetGroupMenu

    def ConstructChargeIndicator(self):
        if self.chargeIndicator:
            return
        self.chargeIndicator = Sprite(parent=self, name='chargeIndicator', padTop=-2, height=7, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/Icons/81_64_2.png', ignoreSize=True)
        self.chargeIndicator.rectWidth = 44
        self.chargeIndicator.rectHeight = 7

    def OnRefreshModuleBanks(self):
        self.SetGroup()

    def SetGroup(self):
        try:
            if self.controller.GetModule() is not None and not self.controller.SlotExists():
                self.controller.DestroyWeaponBank()
        except ReferenceError:
            pass

        parentID = self.controller.GetParentID()
        allGroupsDict = settings.user.ui.Get('linkedWeapons_groupsDict', {})
        groupDict = allGroupsDict.get(parentID, {})
        ret = self.GetBankGroup(groupDict)
        if ret is None:
            if self.groupMark:
                self.groupMark.Hide()
            return
        groupNumber = ret.groupNumber
        self.ConstructGroupMark()
        self.groupMark.state = uiconst.UI_NORMAL
        self.groupMark.rotation = -self.GetRotation()
        if groupNumber < 0:
            availGroups = [1,
             2,
             3,
             4,
             5,
             6,
             7,
             8]
            for masterID, groupNum in groupDict.iteritems():
                if groupNum in availGroups:
                    availGroups.remove(groupNum)

            groupNumber = availGroups[0] if availGroups else ''
        self.groupMark.texturePath = 'res:/UI/Texture/Icons/73_16_%s.png' % (176 + groupNumber)
        self.groupMark.hint = localization.GetByLabel('UI/Fitting/GroupNumber', groupNumber=groupNumber)
        groupDict[ret.masterID] = groupNumber
        allGroupsDict[parentID] = groupDict
        settings.user.ui.Set('linkedWeapons_groupsDict', allGroupsDict)

    def GetBankGroup(self, groupDict):
        module = self.controller.GetModule()
        try:
            if not module:
                return None
        except ReferenceError:
            return None

        masterID = self.controller.IsInWeaponBank()
        if not masterID:
            return None
        if masterID in groupDict:
            groupNumber = groupDict.get(masterID)
        else:
            groupNumber = -1
        ret = util.KeyVal()
        ret.masterID = masterID
        ret.groupNumber = groupNumber
        return ret

    def PrepareUtilButtons(self):
        for btn in self.utilButtons:
            btn.Close()

        self.utilButtons = []
        if not self.controller.GetModule():
            return
        toggleLabel = localization.GetByLabel('UI/Fitting/PutOffline') if bool(self.controller.IsOnline) is True else localization.GetByLabel('UI/Fitting/PutOnline')
        myrad, cos, sin, cX, cY = self.radCosSin
        btns = []
        if self.controller.GetCharge():
            btns += [(localization.GetByLabel('UI/Fitting/RemoveCharge'),
              'ui_38_16_200',
              self.controller.Unfit,
              1,
              0), (localization.GetByLabel('UI/Fitting/ShowChargeInfo'),
              'ui_38_16_208',
              self.ShowChargeInfo,
              1,
              0), ('',
              inventorycommon.typeHelpers.GetIconFile(self.controller.GetModuleTypeID()),
              None,
              1,
              0)]
        isRig = False
        for effect in cfg.dgmtypeeffects.get(self.controller.GetModuleTypeID(), []):
            if effect.effectID == const.effectRigSlot:
                isRig = True
                break

        isSubSystem = evetypes.GetCategoryID(self.controller.GetModuleTypeID()) == const.categorySubSystem
        isOnlinable = self.controller.IsOnlineable()
        if isRig:
            btns += [(localization.GetByLabel('UI/Fitting/Destroy'),
              'ui_38_16_200',
              self.controller.Unfit,
              1,
              0), (localization.GetByLabel('UI/Commands/ShowInfo'),
              'ui_38_16_208',
              self.ShowInfo,
              1,
              0)]
        elif isSubSystem:
            btns += [(localization.GetByLabel('UI/Commands/ShowInfo'),
              'ui_38_16_208',
              self.ShowInfo,
              1,
              0)]
        else:
            btns += [(localization.GetByLabel('UI/Fitting/UnfitModule'),
              'ui_38_16_200',
              self.controller.UnfitModule,
              1,
              0), (localization.GetByLabel('UI/Commands/ShowInfo'),
              'ui_38_16_208',
              self.ShowInfo,
              1,
              0), (toggleLabel,
              'ui_38_16_207',
              self.ToggleOnline,
              isOnlinable,
              1)]
        rad = myrad - 34
        i = 0
        for hint, icon, func, active, onlinebtn in btns:
            left = int((rad - i * 16) * cos) + cX - 16 / 2
            top = int((rad - i * 16) * sin) + cY - 16 / 2
            icon = uicontrols.Icon(icon=icon, parent=self.parent, pos=(left,
             top,
             16,
             16), idx=0, pickRadius=-1, ignoreSize=True)
            icon.OnMouseEnter = self.ShowUtilButtons
            icon.hint = hint
            icon.color.a = 0.0
            icon.isActive = active
            if active:
                icon.OnClick = func
            elif self.controller.GetModule() is None or self.controller.SlotExists():
                icon.hint = localization.GetByLabel('UI/Fitting/Disabled', moduleName=hint)
            else:
                icon.hint = localization.GetByLabel('UI/Fitting/CantOnlineIllegalSlot')
            if onlinebtn == 1:
                self.sr.onlineButton = icon
            self.utilButtons.append(icon)
            i += 1

    def PrimeToEmptySlotHint(self):
        if self.controller.GetFlagID() in const.hiSlotFlags:
            return (localization.GetByLabel('UI/Fitting/EmptyHighPowerSlot'), 'EmptyHighSlot')
        if self.controller.GetFlagID() in const.medSlotFlags:
            return (localization.GetByLabel('UI/Fitting/EmptyMediumPowerSlot'), 'EmptyMidSlot')
        if self.controller.GetFlagID() in const.loSlotFlags:
            return (localization.GetByLabel('UI/Fitting/EmptyLowPowerSlot'), 'EmptyLowSlot')
        if self.controller.GetFlagID() in const.subSystemSlotFlags:
            return (localization.GetByLabel('UI/Fitting/EmptySubsystemSlot'), '')
        if self.controller.GetFlagID() in const.rigSlotFlags:
            return (localization.GetByLabel('UI/Fitting/EmptyRigSlot'), '')
        return (localization.GetByLabel('UI/Fitting/EmptySlot'), '')

    def DisableSlot(self):
        self.opacity = 0.1
        self.state = uiconst.UI_DISABLED
        self.flagIcon.state = uiconst.UI_HIDDEN
        self.UpdateGhostFittingIcons(None)
        self.Hilite(0)

    def EnableSlot(self):
        self.opacity = 1.0
        self.state = uiconst.UI_NORMAL
        self.flagIcon.state = uiconst.UI_DISABLED
        self.sr.underlay.display = True

    def HideSlot(self):
        self.state = uiconst.UI_HIDDEN

    @telemetry.ZONE_METHOD
    def UpdateFitting(self):
        if self.destroyed:
            return
        if not self.controller.SlotExists() and not self.controller.GetModule():
            if self.controller.IsSubsystemSlot() and self.controller.parentController.HasStance():
                self.HideSlot()
            else:
                self.DisableSlot()
            return
        self.EnableSlot()
        if not self.controller.GetModule() and not self.controller.GetCharge():
            self.DisableDrag()
        elif self.controller.SlotExists():
            self.EnableDrag()
        if self.controller.GetCharge():
            chargeQty = self.controller.GetChargeQuantity()
            if self.controller.GetModule() is None:
                portion = 1.0
            else:
                cap = self.controller.GetChargeCapacity()
                if cap.capacity == 0:
                    portion = 1.0
                else:
                    portion = cap.used / cap.capacity
            step = max(0, min(4, int(portion * 5.0)))
            self.ConstructChargeIndicator()
            self.chargeIndicator.rectTop = 10 * step
            self.chargeIndicator.state = uiconst.UI_NORMAL
            self.chargeIndicator.hint = '%s %d%%' % (evetypes.GetName(self.controller.GetCharge().typeID), portion * 100)
        elif not self.controller.GetModule():
            self.HideUtilButtons(1)
            if self.chargeIndicator:
                self.chargeIndicator.Hide()
        elif self.controller.IsChargeable():
            self.ConstructChargeIndicator()
            self.chargeIndicator.rectTop = 0
            self.chargeIndicator.state = uiconst.UI_NORMAL
            self.chargeIndicator.hint = localization.GetByLabel('UI/Fitting/NoCharge')
        elif self.chargeIndicator:
            self.chargeIndicator.Hide()
        if self.controller.GetModule():
            self.tooltipPanelClassInfo = TooltipModuleWrapper()
            modulehint = evetypes.GetName(self.controller.GetModuleTypeID())
            if self.controller.GetCharge():
                modulehint += '<br>%s' % localization.GetByLabel('UI/Fitting/ChargeQuantity', charge=self.controller.GetCharge().typeID, chargeQuantity=chargeQty)
            if not self.controller.SlotExists():
                modulehint = localization.GetByLabel('UI/Fitting/SlotDoesNotExist')
            self.hint = modulehint
        else:
            self.tooltipPanelClassInfo = None
            self.hint = self._emptyHint
            tooltipName = self._emptyTooltip
            if tooltipName:
                SetFittingTooltipInfo(targetObject=self, tooltipName=tooltipName, includeDesc=False)
        self.PrepareUtilButtons()
        iconSize = int(48 * GetScaleFactor())
        self.flagIcon.SetSize(iconSize, iconSize)
        if self.controller.GetCharge() or self.controller.GetModule():
            self.flagIcon.LoadIconByTypeID((self.controller.GetCharge() or self.controller.GetModule()).typeID, ignoreSize=True)
            self.flagIcon.rotation = -self.GetRotation()
        else:
            rev = 0
            slotIcon = {const.flagSubSystemSlot0: 'res:/UI/Texture/Icons/81_64_9.png',
             const.flagSubSystemSlot1: 'res:/UI/Texture/Icons/81_64_10.png',
             const.flagSubSystemSlot2: 'res:/UI/Texture/Icons/81_64_11.png',
             const.flagSubSystemSlot3: 'res:/UI/Texture/Icons/81_64_12.png',
             const.flagSubSystemSlot4: 'res:/UI/Texture/Icons/81_64_13.png'}.get(self.controller.GetFlagID(), None)
            if slotIcon is None:
                slotIcon = {const.effectLoPower: 'res:/UI/Texture/Icons/81_64_5.png',
                 const.effectMedPower: 'res:/UI/Texture/Icons/81_64_6.png',
                 const.effectHiPower: 'res:/UI/Texture/Icons/81_64_7.png',
                 const.effectRigSlot: 'res:/UI/Texture/Icons/81_64_8.png'}.get(self.controller.GetPowerType(), None)
            else:
                rev = 1
            if slotIcon is not None:
                self.flagIcon.LoadIcon(slotIcon, ignoreSize=True)
            if rev:
                self.flagIcon.rotation = mathUtil.DegToRad(180.0)
            else:
                self.flagIcon.rotation = 0.0
        self.SetGroup()
        self.UpdateOnlineDisplay()
        self.UpdateStatusDisplay()
        self.UpdateGhostFittingIcons(self.controller.GetModule())
        if not self.hilitedFromMathing:
            self.Hilite(0)

    def ColorUnderlay(self, color = None):
        a = self.sr.underlay.color.a
        r, g, b = color or (1.0, 1.0, 1.0)
        self.sr.underlay.color.SetRGB(r, g, b, a)
        self.UpdateOnlineDisplay()

    def UpdateOnlineDisplay(self):
        if self.controller.GetModule() is not None and self.controller.IsOnlineable():
            if self.controller.IsOnline():
                self.flagIcon.SetRGBA(1.0, 1.0, 1.0, 1.0)
                if util.GetAttrs(self, 'sr', 'onlineButton') and self.sr.onlineButton.hint == localization.GetByLabel('UI/Fitting/PutOnline'):
                    self.sr.onlineButton.hint = localization.GetByLabel('UI/Fitting/PutOffline')
            else:
                self.flagIcon.SetRGBA(1.0, 1.0, 1.0, 0.25)
                if util.GetAttrs(self, 'sr', 'onlineButton') and self.sr.onlineButton.hint == localization.GetByLabel('UI/Fitting/PutOffline'):
                    self.sr.onlineButton.hint = localization.GetByLabel('UI/Fitting/PutOnline')
        elif self.flagIcon:
            if self.controller.GetModule() is None or self.controller.SlotExists():
                self.flagIcon.SetRGBA(1.0, 1.0, 1.0, 1.0)
            else:
                self.flagIcon.SetRGBA(0.7, 0.0, 0.0, 0.5)

    def IsCharge(self, typeID):
        return evetypes.GetCategoryID(typeID) == const.categoryCharge

    def Add(self, item, sourceLocation = None):
        if self.controller.parentController.IsSimulated():
            return self.AddSimulatedItem(item, sourceLocation)
        else:
            guid = getattr(item, '__guid__', None)
            if guid is None or guid in ('listentry.InvItem', 'xtriui.InvItem'):
                return self.AddRealItem(item, sourceLocation)
            sm.GetService('ghostFittingSvc').LoadCurrentShip()
            return self.AddSimulatedItem(item, sourceLocation)

    def AddSimulatedItem(self, item, sourceLocation):
        if not IsRightSlotForType(item.typeID, self.controller.GetPowerType()):
            return
        shipID = self.controller.GetParentID()
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        ghostFittingSvc.FitModuleToShipAndChangeState(shipID, self.controller.GetFlagID(), item.typeID)
        sm.ScatterEvent('OnFakeUpdateFittingWindow')

    def AddRealItem(self, item, sourceLocation = None):
        if not getattr(item, 'typeID', None):
            return
        if not RigFittingCheck(item):
            return
        requiredSkills = sm.GetService('skills').GetRequiredSkills(item.typeID)
        for skillID, level in requiredSkills.iteritems():
            if getattr(sm.GetService('skills').HasSkill(skillID), 'skillLevel', 0) < level:
                sm.GetService('tutorial').OpenTutorialSequence_Check(uix.skillfittingTutorial)
                break

        if self.IsCharge(item.typeID) and self.controller.IsChargeable():
            self.controller.FitCharge(item)
        validFitting = False
        for effect in cfg.dgmtypeeffects.get(item.typeID, []):
            if effect.effectID in (const.effectHiPower,
             const.effectMedPower,
             const.effectLoPower,
             const.effectSubSystem,
             const.effectRigSlot):
                validFitting = True
                if effect.effectID == self.controller.GetPowerType():
                    shift = uicore.uilib.Key(uiconst.VK_SHIFT)
                    isFitted = item.locationID == self.controller.GetParentID() and item.flagID != const.flagCargo
                    if isFitted and shift:
                        if self.controller.GetModule():
                            if self.controller.GetModule().typeID == item.typeID:
                                self.controller.LinkWithWeapon(item)
                                return
                            else:
                                uicore.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Fitting/GroupingIncompatible')})
                                return
                    self.controller.FitModule(item)
                    return
                uicore.Message('ItemDoesntFitPower', {'item': evetypes.GetName(item.typeID),
                 'slotpower': cfg.dgmeffects.Get(self.controller.GetPowerType()).displayName,
                 'itempower': cfg.dgmeffects.Get(effect.effectID).displayName})

        if not validFitting:
            raise UserError('ItemNotHardware', {'itemname': item.typeID})

    def GetMenu(self):
        if self.controller.GetModuleTypeID() and self.controller.GetModuleID():
            m = []
            if eve.session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
                m += [(str(self.controller.GetModuleID()), self.CopyItemIDToClipboard, (self.controller.GetModuleID(),)), None]
            m += [(uiutil.MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo)]
            if self.controller.IsRigSlot():
                m += [(uiutil.MenuLabel('UI/Fitting/Destroy'), self.controller.Unfit)]
            else:
                if session.stationid2 is not None:
                    m += [(uiutil.MenuLabel('UI/Fitting/Unfit'), self.controller.Unfit)]
                if self.controller.IsOnlineable():
                    if self.controller.IsOnline():
                        m.append((uiutil.MenuLabel('UI/Fitting/PutOffline'), self.ToggleOnline))
                    else:
                        m.append((uiutil.MenuLabel('UI/Fitting/PutOnline'), self.ToggleOnline))
            m += self.GetGroupMenu()
            return m

    def GetGroupMenu(self, *args):
        masterID = self.controller.IsInWeaponBank()
        if masterID:
            return [(uiutil.MenuLabel('UI/Fitting/ClearGroup'), self.UnlinkModule, ())]
        return []

    def OnClickNotSimulated(self, *args):
        if self.controller.IsOnlineable():
            self.ToggleOnline()

    def OnClick(self, *args):
        uicore.registry.SetFocus(self)
        if self.controller.IsSimulated():
            return self.OnClickSimulated()
        else:
            return self.OnClickNotSimulated()

    def OnClickSimulated(self):
        if self.controller.GetModule() is None:
            return
        typeID = self.controller.GetModuleTypeID()
        itemKey = self.controller.GetModuleID()
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        ghostFittingSvc.SwitchBetweenModes(itemKey, typeID)
        self.UpdateStatusDisplay()

    def UpdateStatusDisplay(self):
        self.HideElement(self.moduleSlotFill)
        if not self.controller.parentController.IsSimulated():
            return
        itemKey = self.controller.GetModuleID()
        typeID = self.controller.GetModuleTypeID()
        if itemKey is None or typeID is None:
            return
        currentStatus = sm.GetService('ghostFittingSvc').GetModuleStatus(itemKey, typeID)
        self.flagIcon.SetAlpha(1.0)
        if currentStatus == OFFLINE:
            self.flagIcon.SetAlpha(0.25)
        elif currentStatus == ONLINE:
            pass
        elif currentStatus == ACTIVE:
            self.ConstructModuleSlotFill()
            self.moduleSlotFill.display = True
            self.moduleSlotFill.SetRGB(1, 1, 1, 0.5)
        elif currentStatus == OVERHEATED:
            self.ConstructModuleSlotFill()
            self.moduleSlotFill.display = True
            self.moduleSlotFill.SetRGB(1, 0, 0, 0.5)

    def ToggleOnline(self):
        self.controller.ToggleOnlineModule()
        self.UpdateOnlineDisplay()

    def CopyItemIDToClipboard(self, itemID):
        blue.pyos.SetClipboardData(str(itemID))

    def ShowChargeInfo(self, *args):
        if self.controller.GetCharge():
            sm.GetService('info').ShowInfo(self.controller.GetCharge().typeID, self.controller.GetCharge().itemID)

    def ShowInfo(self, *args):
        sm.GetService('info').ShowInfo(self.controller.GetModuleTypeID(), self.controller.GetModuleID())

    def UnlinkModule(self):
        self.controller.DestroyWeaponBank()

    def _OnEndDrag(self, *args):
        self.left = self.top = -2

    def OnEndDrag(self, *args):
        if self.controller.GetModule() is not None:
            sm.ScatterEvent('OnResetSlotLinkingMode', self.controller.GetModule().typeID)

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

    def GetTooltipPosition(self):
        rect, point = self.PositionHint()
        return rect

    def GetTooltipPointer(self):
        rect, point = self.PositionHint()
        return point

    def UpdateInfo_TimedCall(self, *args):
        if self.destroyed or self.moduleButtonHint.destroyed:
            self.moduleButtonHint = None
            self.updateTimer = None
            return
        if self.controller.GetModuleTypeID():
            if self.controller.GetCharge():
                chargeItemID = self.controller.GetCharge().itemID
            else:
                chargeItemID = None
            self.moduleButtonHint.UpdateAllInfo(self.controller.GetModuleID(), chargeItemID, fromWhere='fitting')

    def PositionHint(self, *args):
        myRotation = self.rotation + 2 * math.pi
        myRotation = -myRotation
        sl, st, sw, sh = self.parent.GetAbsolute()
        cX = sl + sw / 2.0
        cY = st + sh / 2.0
        rad, cos, sin, oldcX, oldcY = self.radCosSin
        hintLeft = int(round(rad * cos))
        hintTop = int(round(rad * sin))
        cap = rad * 0.7
        if hintLeft < -cap:
            point = uiconst.POINT_RIGHT_2
        elif hintLeft > cap:
            point = uiconst.POINT_LEFT_2
        elif hintTop < -cap:
            if hintLeft < 0:
                point = uiconst.POINT_BOTTOM_3
            else:
                point = uiconst.POINT_BOTTOM_1
        elif hintLeft < 0:
            point = uiconst.POINT_TOP_3
        else:
            point = uiconst.POINT_TOP_1
        return ((hintLeft + cX - 15,
          hintTop + cY - 15,
          30,
          30), point)

    def ShowUtilButtons(self, *args):
        fittingbase = self.FindParentByName('fittingBase')
        fittingbase.ClearSlotsWithMenu()
        fittingbase.AddToSlotsWithMenu(self)
        for button in self.utilButtons:
            if button.isActive:
                button.color.a = 1.0
            else:
                button.color.a = 0.25

        self.utilButtonsTimer = base.AutoTimer(500, self.HideUtilButtons)

    def HideUtilButtons(self, force = 0):
        mo = uicore.uilib.mouseOver
        if not force and (mo in self.utilButtons or mo == self or uiutil.IsUnder(mo, self)):
            return
        for button in self.utilButtons:
            button.color.a = 0.0

        self.utilButtonsTimer = None

    def Hilite(self, state):
        if state:
            self.sr.underlay.color.a = 1.0
        else:
            self.sr.underlay.color.a = 0.3

    def GetDragData(self, *args):
        return self.controller.GetDragData()

    def HiliteIfMatching(self, flagID, powerType):
        if flagID is None and powerType is None:
            if self.controller.GetModule() is None:
                self.SetHiliteFromMatching(0)
        elif self.state != uiconst.UI_DISABLED and self.controller.GetModule() is None:
            if powerType is not None and self.controller.GetPowerType() == powerType:
                self.SetHiliteFromMatching(1)
            if flagID is not None and self.controller.GetFlagID() == flagID:
                self.SetHiliteFromMatching(1)

    def SetHiliteFromMatching(self, value):
        self.Hilite(value)
        self.hilitedFromMathing = value

    def OnDropData(self, dragObj, nodes):
        if self.controller.GetModule() is not None and not self.controller.SlotExists():
            return
        items, subSystemGroupIDs = self.GetDroppedItems(nodes)
        chargeTypeID = None
        chargeItems = []
        for item in items:
            if not getattr(item, 'typeID', None):
                lg.Info('fittingUI', 'Dropped a non-item here', item)
                return
            if self.controller.IsChargeable() and self.IsCharge(item.typeID):
                if chargeTypeID is None:
                    chargeTypeID = item.typeID
                if chargeTypeID == item.typeID:
                    chargeItems.append(item)
            else:
                uthread.new(self.Add, item)

        if len(chargeItems):
            self.controller.FitCharges(chargeItems)

    def _OnClose(self, *args):
        self.updateTimer = None
        moduleButtonHint = getattr(uicore.layer.hint, 'moduleButtonHint', None)
        if moduleButtonHint and not moduleButtonHint.destroyed:
            if moduleButtonHint.fromWhere == 'fitting':
                uicore.layer.hint.moduleButtonHint.FadeOpacity(0.0)

    def GetDroppedItems(self, nodes):
        items = []
        subSystemGroupIDs = set()
        for node in nodes:
            if node.__guid__ in ('listentry.InvItem', 'xtriui.InvItem'):
                invType = node.rec
                self.AddItemToCollections(invType.typeID, items, subSystemGroupIDs)
            elif node.__guid__ in ('listentry.GenericMarketItem', 'listentry.Item', 'listentry.FittingModuleEntry'):
                invType = node.invtype
                self.AddItemToCollections(node.typeID, items, subSystemGroupIDs, invType)

        return (items, subSystemGroupIDs)

    def AddItemToCollections(self, invTypeID, items, subSystemGroupIDs, invType = None):
        if invType is None:
            invType = util.KeyVal(typeID=invTypeID)
        if evetypes.GetCategoryID(invTypeID) not in (const.categoryCharge, const.categorySubSystem, const.categoryModule):
            return
        if evetypes.GetCategoryID(invTypeID) == const.categorySubSystem:
            if evetypes.GetGroupID(invTypeID) in subSystemGroupIDs:
                return
            subSystemGroupIDs.add(evetypes.GetGroupID(invTypeID))
        items.append(invType)

    def UpdateGhostFittingIcons(self, invItem):
        fittingSvc = sm.GetService('fittingSvc')
        if fittingSvc.IsShipSimulated() and invItem:
            self.SetMissingIcon(invItem)
            self.SetSkillIcon(invItem)
        else:
            self.HideElement(self.dontHaveLine)
            self.HideElement(self.skillSprite)
            self.HideElement(self.moduleSlotFill)
            self.sr.underlay.display = True

    def HideElement(self, element):
        if element:
            element.display = False

    def SetMissingIcon(self, invItem):
        self.ConstructDontHaveLine()
        self.dontHaveLine.display = False
        self.sr.underlay.display = True
        if invItem is None or not session.stationid2:
            return
        hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
        items = hangarInv.List()
        for eachItem in items:
            if eachItem.typeID == invItem.typeID:
                return

        self.dontHaveLine.display = True
        self.sr.underlay.display = False

    def SetSkillIcon(self, invItem):
        if invItem is None:
            self.HideElement(self.skillSprite)
            return
        fittingSvc = sm.GetService('fittingSvc')
        if fittingSvc.IsShipSimulated():
            dogmaLocation = fittingSvc.GetCurrentDogmaLocation()
            missingSkills = dogmaLocation.CheckSkillRequirementsForType(invItem.typeID)
            if missingSkills:
                self.ConstructSkillSprite()
                texturePath = 'res:/UI/Texture/Icons/38_16_194.png'
                self.skillSprite.LoadTexture(texturePath)
                self.skillSprite.display = True
            else:
                self.HideElement(self.skillSprite)
        else:
            self.HideElement(self.skillSprite)
