#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\slotsContainer.py
import random
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.inflight.moondefencebutton import DefenceStructureButton
from eve.client.script.ui.inflight.shipHud import GetSlotOrder
from eve.client.script.ui.inflight.shipHud.shipSlot import ShipSlot
import carbonui.const as uiconst
import telemetry
from eve.client.script.ui.inflight.shipModuleButton.shipmodulebutton import ModuleButton
from eve.client.script.ui.shared.fitting.fittingUtil import FITKEYS
from eve.client.script.ui.util.uix import GetTiDiAdjustedAnimationTime
from eve.common.script.sys.dbrow import LookupConstValue
from inventorycommon.util import IsShipFittingFlag
from localization import GetByLabel
import uthread
import evetypes
import blue
ICONSIZE = 32

class SlotsContainer(Container):
    default_name = 'SlotsContainer'
    __notifyevents__ = ['OnMapShortcut',
     'OnRestoreDefaultShortcuts',
     'ProcessShipEffect',
     'OnAttributes',
     'OnWeaponGroupsChanged',
     'OnRefreshModuleBanks']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.invCookie = sm.GetService('inv').Register(self)
        self.controller = attributes.controller
        self.slotsByFlag = {}
        self.slotsByOrder = {}
        self.modulesByID = {}
        self.checkingoverloadrackstate = 0
        self.totalSlaves = 0
        self.myHarpointFlags = []

    def Close(self):
        Container.Close(self)
        sm.GetService('inv').Unregister(self.invCookie)

    def GetPosFromFlag(self, slotFlag):
        return self.slotsByFlag[slotFlag].sr.slotPos

    def ChangeSlots(self, toFlag, fromFlag):
        toModule = self.GetModuleType(toFlag)
        fromModule = self.GetModuleType(fromFlag)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if toModule and fromModule and toModule[0] == fromModule[0]:
            self.LinkWeapons(toModule, fromModule, toFlag, fromFlag, merge=not shift)
            if not sm.GetService('clientDogmaIM').GetDogmaLocation().IsModuleMaster(toModule[1], session.shipid):
                self.SwapSlots(fromFlag, toFlag)
        else:
            self.SwapSlots(toFlag, fromFlag)

    def SwapSlots(self, slotFlag1, slotFlag2):
        module1 = self.GetModuleType(slotFlag1)
        module2 = self.GetModuleType(slotFlag2)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if shift and module1 is None and module2 is not None:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            if dogmaLocation.IsInWeaponBank(session.shipid, module2[1]):
                moduleID = dogmaLocation.UngroupModule(session.shipid, module2[1])
                slotFlag2 = dogmaLocation.GetItem(moduleID).flagID
        current = GetSlotOrder()[:]
        flag1Idx = current.index(slotFlag1)
        flag2Idx = current.index(slotFlag2)
        current[flag1Idx] = slotFlag2
        current[flag2Idx] = slotFlag1
        all = settings.user.ui.Get('slotOrder', {})
        all[session.shipid] = current
        settings.user.ui.Set('slotOrder', all)
        self.InitSlots()

    def LinkWeapons(self, master, slave, slotFlag1, slotFlag2, merge = False):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        groupID = evetypes.GetGroupID(master[0])
        areTurrets = groupID in const.dgmGroupableGroupIDs
        slaves = dogmaLocation.GetSlaveModules(slave[1], session.shipid)
        swapSlots = 0
        if slaves:
            swapSlots = 1
        if not areTurrets:
            eve.Message('CustomNotify', {'notify': GetByLabel('UI/Inflight/WeaponGroupingRule')})
            return
        weaponLinked = dogmaLocation.LinkWeapons(session.shipid, master[1], slave[1], merge=merge)
        if weaponLinked and swapSlots:
            self.SwapSlots(slotFlag1, slotFlag2)

    def GetModuleType(self, flag):
        if not self.slotsByFlag.has_key(flag):
            return None
        module = self.slotsByFlag[flag].sr.module
        if not module:
            return None
        return module.GetModuleType()

    def GetModuleFromID(self, moduleID):
        return self.modulesByID.get(moduleID, None)

    def GetModule(self, moduleID):
        return self.modulesByID.get(moduleID, None)

    @telemetry.ZONE_METHOD
    def InitDrawSlots(self, xstep, ystep, vgridrange, hgridrange, grid, myOrder, slotType = None):
        for r in xrange(vgridrange):
            x, y = grid[r]
            for i in xrange(hgridrange):
                slotFlag = myOrder[r * hgridrange + i]
                if slotType == 'shipslot':
                    slot = ShipSlot(parent=self, pos=(0,
                     int(ystep * y),
                     64,
                     64), name='slot', state=uiconst.UI_HIDDEN, align=uiconst.TOPLEFT)
                else:
                    slot = Container(name='defenceslot', parent=self, width=64, height=128 + 60, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, top=0)
                slot.left = int((x + i) * xstep - 40)
                slot.sr.module = None
                slot.sr.slotFlag = slotFlag
                slot.sr.slotPos = (r, i)
                self.slotsByFlag[slotFlag] = slot
                self.slotsByOrder[r, i] = slot
                slot.sr.shortcutHint = EveLabelSmall(text='<center>-', parent=slot, width=64, color=(1.0, 1.0, 1.0, 0.25), shadowOffset=(0, 0), state=uiconst.UI_DISABLED, idx=0)
                slot.sr.shortcutHint.top = 30
                if self.controller.IsControllingTurret():
                    slot.sr.shortcutHint.top -= 4

        self.RefreshShortcuts()

    def RefreshShortcuts(self):
        for (r, i), slot in self.slotsByOrder.iteritems():
            hiMedLo = ('High', 'Medium', 'Low')[r]
            slotno = i + 1
            txt = uicore.cmd.GetShortcutStringByFuncName('CmdActivate%sPowerSlot%i' % (hiMedLo, slotno))
            if not txt:
                txt = '_'
            slot.sr.shortcutHint.text = '<center>' + txt

    def OnMapShortcut(self, *blah):
        self.RefreshShortcuts()

    def OnRestoreDefaultShortcuts(self):
        self.RefreshShortcuts()

    def ProcessShipEffect(self, godmaStm, effectState):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        masterID = dogmaLocation.IsInWeaponBank(session.shipid, effectState.itemID)
        if masterID:
            module = self.GetModule(masterID)
        else:
            module = self.GetModule(effectState.itemID)
        if module:
            uthread.new(module.Update, effectState)
            uthread.new(self.CheckOverloadRackBtnState)

    def OnAttributes(self, ch):
        for each in ch:
            if each[0] == 'isOnline':
                self.CheckGroupAllButton()
            if each[0] != 'damage':
                continue
            masterID, damage = sm.GetService('godma').GetStateManager().GetMaxDamagedModuleInGroup(session.shipid, each[1].itemID)
            module = self.GetModule(masterID)
            if module is None:
                continue
            module.SetDamage(damage / module.sr.moduleInfo.hp)

    def OnInvChange(self, item, change):
        if const.ixFlag in change:
            if IsShipFittingFlag(item.flagID) or IsShipFittingFlag(change[const.ixFlag]):
                uthread.new(self.InitSlotsDelayed)

    def IsItemHere(self, rec):
        return rec.locationID == session.shipid and rec.categoryID == const.categoryModule and rec.flagID not in (const.flagCargo, const.flagDroneBay)

    def InitStructureSlots(self):
        currentControl = sm.GetService('pwn').GetCurrentControl()
        shipmodules = []
        charges = {}
        if currentControl:
            for k, v in currentControl.iteritems():
                shipmodules.append(sm.services['godma'].GetItem(k))

        xstep = int(ICONSIZE * 2.0)
        ystep = int(ICONSIZE * 1.35)
        vgridrange = 1
        hgridrange = 5
        grid = [[1.0, 0.1]]
        myOrder = [0,
         1,
         2,
         3,
         4]
        for i, moduleInfo in enumerate(shipmodules):
            if moduleInfo is None:
                continue
            myOrder[i] = moduleInfo.itemID
            if currentControl.has_key(moduleInfo.itemID):
                item = sm.services['godma'].GetItem(moduleInfo.itemID)
                if item.groupID == const.groupMobileLaserSentry and len(item.modules):
                    charges[moduleInfo.itemID] = item.modules[0]
                elif len(item.sublocations):
                    charges[moduleInfo.itemID] = item.sublocations[0]

        self.InitDrawSlots(xstep, ystep, vgridrange, hgridrange, grid, myOrder, slotType='structure')
        for moduleInfo in shipmodules:
            if moduleInfo:
                self._FitStructureSlot(moduleInfo, charges)

        self.CheckButtonVisibility(3, ['hiSlots'], 5, myOrder)

    @telemetry.ZONE_METHOD
    def InitSlots(self, animate = False):
        self.initSlotsDelayedTimer = None
        if self.destroyed:
            return
        if animate:
            self.AnimateModulesOut()
        else:
            self.Flush()
        self.modulesByID = {}
        self.totalSlaves = 0
        self.passiveFiltered = []
        if self.controller.IsControllingTurret():
            self.InitStructureSlots()
        else:
            charges = {}
            for charge in self.controller.GetCharges():
                charges[charge.flagID] = charge
                if charge.stacksize == 0:
                    sm.services['godma'].LogError('InitSlots.no quantity', charge, charge.flagID)

            for module in self.controller.GetModules():
                if module.categoryID == const.categoryCharge:
                    charges[module.flagID] = module

            xstep = int(ICONSIZE * 1.6)
            ystep = int(ICONSIZE * 1.4)
            vgridrange = 3
            hgridrange = 8
            grid = [[1.0, 0.0], [1.5, 1.0], [1.0, 2.0]]
            myOrder = GetSlotOrder()
            self.InitDrawSlots(xstep, ystep, vgridrange, hgridrange, grid, myOrder, slotType='shipslot')
            self.InitOverloadBtns()
            self.InitGroupAllButtons()
            dogmaLocation = sm.StartService('clientDogmaIM').GetDogmaLocation()
            IsSlave = lambda itemID: dogmaLocation.IsModuleSlave(itemID, session.shipid)
            for moduleInfo in self.controller.GetModules():
                if IsSlave(moduleInfo.itemID):
                    self.totalSlaves += 1
                    continue
                self._FitSlot(moduleInfo, charges)

            self.CheckButtonVisibility(0, ['hiSlots', 'medSlots', 'lowSlots'], None, myOrder)
            if animate:
                self.AnimateModulesIn()

    def InitSlotsDelayed(self):
        self.initSlotsDelayedTimer = AutoTimer(200, self.InitSlots)

    def CloseSlots_Delayed(self, toClose):
        self.closeSlotsDelayedTimer = None
        for child in toClose:
            child.Close()

    def AnimateModulesOut(self):
        toClose = self.children[:]
        for module in self.modulesByID.itervalues():
            module.ShowOffline()
            module.isInActiveState = False

        maxDuration = 1.0
        fadeTime = 0.1
        for child in toClose:
            child.opacity = 0.999
            fadeDelay = (maxDuration - fadeTime) * random.random()
            uicore.animations.FadeOut(child, duration=fadeTime, curveType=uiconst.ANIM_LINEAR, timeOffset=fadeDelay)

        self.closeSlotsDelayedTimer = AutoTimer(maxDuration, self.CloseSlots_Delayed, toClose)

    def AnimateModulesIn(self):
        for child in self.children[:]:
            if child.opacity < 1.0:
                continue
            child.opacity = 0
            uicore.animations.FadeIn(child, duration=1.0, timeOffset=1.0, curveType=uiconst.ANIM_OVERSHOT)

    @telemetry.ZONE_METHOD
    def InitGroupAllButtons(self):
        self.groupAllIcon = ic = Icon(parent=self, state=uiconst.UI_HIDDEN, icon='ui_73_16_251', idx=0, name='groupAllIcon', pos=(0, 9, 16, 16), hint='')
        ic.orgPos = ic.top
        ic.OnClick = self.OnGroupAllButtonClicked
        ic.OnMouseDown = (self.OverloadRackBtnMouseDown, ic)
        ic.OnMouseUp = (self.OverloadRackBtnMouseUp, ic)
        self.CheckGroupAllButton()

    def OnGroupAllButtonClicked(self, *args):
        if settings.user.ui.Get('lockModules', 0):
            return
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if dogmaLocation.CanGroupAll(session.shipid):
            dogmaLocation.LinkAllWeapons(session.shipid)
        else:
            dogmaLocation.UnlinkAllWeapons(session.shipid)

    @telemetry.ZONE_METHOD
    def InitOverloadBtns(self):
        overloadEffectsByRack = {}
        modulesByRack = {}
        for module in self.controller.GetModules():
            for key in module.effects.iterkeys():
                effect = module.effects[key]
                if effect.effectID in (const.effectHiPower, const.effectMedPower, const.effectLoPower):
                    if effect.effectID not in modulesByRack:
                        modulesByRack[effect.effectID] = []
                    modulesByRack[effect.effectID].append(module)
                    for key in module.effects.iterkeys():
                        effect2 = module.effects[key]
                        if effect2.effectCategory == const.dgmEffOverload:
                            if effect.effectID not in overloadEffectsByRack:
                                overloadEffectsByRack[effect.effectID] = []
                            overloadEffectsByRack[effect.effectID].append(effect2)

        grid = [[13, 52], [20, 66], [13, 80]]
        for i, each in enumerate(FITKEYS):
            x, y = grid[i]
            par = Container(parent=self, name='overloadBtn' + each, width=20, height=20, align=uiconst.TOPLEFT, left=x, top=y, state=uiconst.UI_NORMAL, pickRadius=8)
            icon = Sprite(parent=par, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/overloadBtn%sOff.png' % each)
            par.OnClick = (self.OverloadRackBtnClick, par)
            par.OnMouseDown = (self.OverloadRackBtnMouseDown, par)
            par.OnMouseUp = (self.OverloadRackBtnMouseUp, par)
            par.OnMouseExit = (self.OverloadRackBtnMouseExit, par)
            par.orgPos = par.top
            par.active = False
            par.powerEffectID = getattr(const, 'effect%sPower' % each, None)
            par.activationID = None

        self.CheckOverloadRackBtnState()

    def OverloadRackBtnClick(self, btn, *args):
        if settings.user.ui.Get('lockOverload', 0):
            eve.Message('error')
            eve.Message('LockedOverloadState')
            return
        if btn.active:
            eve.Message('click')
            sm.GetService('godma').StopOverloadRack(btn.activationID)
        else:
            eve.Message('click')
            sm.GetService('godma').OverloadRack(btn.activationID)

    def OverloadRackBtnMouseDown(self, btn, *args):
        btn.top = btn.orgPos + 1

    def OverloadRackBtnMouseUp(self, btn, *args):
        btn.top = btn.orgPos

    def OverloadRackBtnMouseExit(self, btn, *args):
        btn.top = btn.orgPos

    @telemetry.ZONE_METHOD
    def CheckOverloadRackBtnState(self):
        if self.controller.IsControllingTurret():
            return
        if self.destroyed or not self:
            return
        if self.checkingoverloadrackstate:
            self.checkingoverloadrackstate = 2
            return
        self.checkingoverloadrackstate = 1
        overloadEffectsByRack = {}
        modulesByRack = {}
        for module in self.controller.GetModules():
            for key in module.effects.iterkeys():
                effect = module.effects[key]
                if effect.effectID in (const.effectHiPower, const.effectMedPower, const.effectLoPower):
                    if effect.effectID not in modulesByRack:
                        modulesByRack[effect.effectID] = []
                    modulesByRack[effect.effectID].append(module)
                    for key in module.effects.iterkeys():
                        effect2 = module.effects[key]
                        if effect2.effectCategory == const.dgmEffOverload:
                            if effect.effectID not in overloadEffectsByRack:
                                overloadEffectsByRack[effect.effectID] = []
                            overloadEffectsByRack[effect.effectID].append(effect2)

        i = 0
        for each in FITKEYS:
            btn = self.GetChild('overloadBtn' + each)
            btn.activationID = None
            btn.active = False
            btn.children[0].LoadTexture('res:/UI/Texture/classes/ShipUI/overloadBtn%sOff.png' % each)
            btn.hint = GetByLabel('UI/Inflight/OverloadRack')
            btn.state = uiconst.UI_DISABLED
            if btn.powerEffectID in modulesByRack:
                btn.activationID = modulesByRack[btn.powerEffectID][0].itemID
            if btn.powerEffectID in overloadEffectsByRack:
                sumInactive = sum([ 1 for olEffect in overloadEffectsByRack[btn.powerEffectID] if not olEffect.isActive ])
                if not sumInactive:
                    btn.children[0].LoadTexture('res:/UI/Texture/classes/ShipUI/overloadBtn%sOn.png' % each)
                    btn.active = True
                    btn.hint = GetByLabel('UI/Inflight/StopOverloadingRack')
            btn.state = uiconst.UI_NORMAL

        if self.checkingoverloadrackstate == 2:
            self.checkingoverloadrackstate = 0
            return self.CheckOverloadRackBtnState()
        self.checkingoverloadrackstate = 0

    def UpdateGroupAllButton(self):
        if self.destroyed:
            return
        GetOpacity = sm.GetService('clientDogmaIM').GetDogmaLocation().GetGroupAllOpacity
        if sm.GetService('clientDogmaIM').GetDogmaLocation().CanGroupAll(session.shipid):
            attributeName = 'lastGroupAllRequest'
        else:
            attributeName = 'lastUngroupAllRequest'
        icon = self.groupAllIcon
        if icon is None or icon.destroyed:
            return
        icon.state = uiconst.UI_DISABLED
        while True:
            opacity = GetOpacity(attributeName)
            if opacity > 0.999:
                break
            icon.color.a = 0.2 + opacity * 0.6
            blue.pyos.synchro.Yield()
            if self.destroyed:
                return

        icon.color.a = 1.0
        icon.state = uiconst.UI_NORMAL

    def CheckGroupAllButton(self):
        if self.destroyed:
            return
        icon = self.groupAllIcon
        if icon is None or icon.destroyed:
            return
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        for typeID, qty in dogmaLocation.GetGroupableTypes(session.shipid).iteritems():
            if qty > 1:
                break
        else:
            icon.state = uiconst.UI_HIDDEN
            return

        icon.state = uiconst.UI_NORMAL
        if dogmaLocation.CanGroupAll(session.shipid):
            icon.LoadIcon('ui_73_16_252')
            hint = GetByLabel('UI/Inflight/GroupAllWeapons')
        else:
            icon.LoadIcon('ui_73_16_251')
            hint = GetByLabel('UI/Inflight/UngroupAllWeapons')
        if settings.user.ui.Get('lockModules', False):
            hint = GetByLabel('UI/Inflight/Locked', unit=hint)
        icon.hint = hint
        if getattr(self, 'updateGroupAllButtonThread', None):
            self.updateGroupAllButtonThread.kill()
        self.updateGroupAllButtonThread = uthread.new(self.UpdateGroupAllButton)

    @telemetry.ZONE_METHOD
    def CheckButtonVisibility(self, gidx, sTypes, totalslot, myOrder):
        lastType = ''
        showEmptySlots = settings.user.ui.Get('showEmptySlots', 0)
        slotUIID = 0
        for sType in sTypes:
            if totalslot is None:
                totalslots = self.GetNumSlots(sType)
            ignoredSlots = 0
            for sidx in xrange(totalslots):
                if sidx == 8:
                    break
                flagTypes = ['Hi',
                 'Med',
                 'Lo',
                 'Stuct']
                if not self.controller.IsControllingTurret():
                    if gidx < len(flagTypes):
                        slotFlag = getattr(const, 'flag%sSlot%s' % (flagTypes[gidx], sidx), None)
                    slot = self.slotsByFlag.get(slotFlag, None)
                else:
                    slotFlag = myOrder[sidx]
                    slot = self.slotsByFlag.get(slotFlag, None)
                typeNames = ['High',
                 'Medium',
                 'Low',
                 'Stuct']
                slotUIID += 1
                if gidx < len(typeNames):
                    currType = typeNames[gidx]
                    if currType != lastType:
                        slotUIID = 1
                    lastType = currType
                    if slot:
                        slot.name = 'inFlight%sSlot%s' % (typeNames[gidx], slotUIID)
                if showEmptySlots and not self.controller.IsControllingTurret():
                    if slot and slot.sr.module is None and slotFlag not in self.passiveFiltered:
                        slot.showAsEmpty = 1
                        if gidx == 0:
                            if ignoredSlots < self.totalSlaves:
                                ignoredSlots += 1
                                slot.ignored = 1
                                continue
                        slot.hint = [GetByLabel('UI/Inflight/EmptyHighSlot'), GetByLabel('UI/Inflight/EmptyMediumSlot'), GetByLabel('UI/Inflight/EmptyLowSlot')][gidx]
                        slot.state = uiconst.UI_NORMAL
                        iconpath = ['ui_8_64_11',
                         'ui_8_64_10',
                         'ui_8_64_9',
                         'ui_44_64_14'][gidx]
                        icon = Icon(icon=iconpath, parent=slot, pos=(13, 13, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0, ignoreSize=True)
                        icon.left = (slot.width - icon.width) / 2
                        icon.color.a = 0.25

            gidx += 1

    def GetNumSlots(self, slotType):
        if slotType == 'hiSlots':
            return self.controller.GetNumHiSlots()
        if slotType == 'medSlots':
            return self.controller.GetNumMedSlots()
        if slotType == 'lowSlots':
            return self.controller.GetNumLowSlots()

    def _FitStructureSlot(self, moduleInfo, charges):
        showPassive = settings.user.ui.Get('showPassiveModules', 1)
        if moduleInfo.categoryID != const.categoryStarbase:
            return
        if not showPassive and self.GetDefaultEffect(moduleInfo) is None:
            self.passiveFiltered.append(moduleInfo.flagID)
            return
        slot = self.slotsByFlag.get(moduleInfo.itemID, None)
        if slot is None:
            return
        if slot.sr.module is not None:
            return
        self.FitStructureSlot(slot, moduleInfo, charges.get(moduleInfo.itemID, None))

    @telemetry.ZONE_METHOD
    def _FitSlot(self, moduleInfo, charges, grey = 0, slotUIID = 'slot'):
        showPassive = settings.user.ui.Get('showPassiveModules', 1)
        if moduleInfo.categoryID == const.categoryCharge:
            return
        if not showPassive and self.GetDefaultEffect(moduleInfo) is None:
            self.passiveFiltered.append(moduleInfo.flagID)
            return
        slot = self.slotsByFlag.get(moduleInfo.flagID, None)
        if slot is None:
            return
        if slot.sr.module is not None:
            return
        self.FitSlot(slot, moduleInfo, charges.get(moduleInfo.flagID, None), grey=grey, slotUIID=slotUIID)

    def GetDefaultEffect(self, moduleInfo):
        for key in moduleInfo.effects.iterkeys():
            effect = moduleInfo.effects[key]
            if self.IsEffectActivatible(effect):
                return effect

    def IsEffectActivatible(self, effect):
        return effect.isDefault and effect.effectName != 'online' and effect.effectCategory in (const.dgmEffActivation, const.dgmEffTarget)

    def FitSlot(self, slot, moduleInfo, charge = None, grey = 0, slotUIID = 'slot'):
        pos = (slot.width - 48) / 2
        module = ModuleButton(parent=slot, align=uiconst.TOPLEFT, width=48, height=48, top=pos, left=pos, idx=0, state=uiconst.UI_NORMAL)
        module.Setup(moduleInfo, grey=grey)
        self.modulesByID[moduleInfo.itemID] = module
        slot.sr.module = module
        slot.state = uiconst.UI_NORMAL
        slot.sr.shortcutHint.state = uiconst.UI_HIDDEN
        slot.name = slotUIID
        if charge:
            module.SetCharge(charge)
        if moduleInfo.flagID in [const.flagHiSlot0,
         const.flagHiSlot1,
         const.flagHiSlot2,
         const.flagHiSlot3,
         const.flagHiSlot4,
         const.flagHiSlot5,
         const.flagHiSlot6,
         const.flagHiSlot7]:
            self.myHarpointFlags.append(moduleInfo.flagID)

    def FitStructureSlot(self, slot, moduleInfo, charge = None):
        pos = (slot.width - 48) / 2
        module = DefenceStructureButton(parent=slot, align=uiconst.TOPLEFT, width=64, height=250, top=0, left=0, idx=1, state=uiconst.UI_DISABLED)
        module.Setup(moduleInfo)
        self.modulesByID[moduleInfo.itemID] = module
        slot.sr.module = module
        slot.state = uiconst.UI_NORMAL
        if charge:
            module.SetCharge(charge)

    def OnReloadAmmo(self):
        modulesByCharge = {}
        for module in self.modulesByID.itervalues():
            if not cfg.IsChargeCompatible(module.sr.moduleInfo):
                continue
            chargeTypeID, chargeQuantity, roomForReload = module.GetChargeReloadInfo()
            if chargeTypeID in modulesByCharge:
                modulesByCharge[chargeTypeID].append(module)
            else:
                modulesByCharge[chargeTypeID] = [module]

        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        for chargeTypeID, modules in modulesByCharge.iteritems():
            ammoList = {}
            for typeID, ammoInfo in dogmaLocation.GetMatchingAmmo(session.shipid, modules[0].sr.moduleInfo.itemID).iteritems():
                if typeID != chargeTypeID:
                    continue
                for item in ammoInfo.singletons:
                    ammoList[item.itemID] = item.stacksize

                for item in ammoInfo.nonSingletons:
                    ammoList[item.itemID] = item.stacksize

            for module in modules:
                maxItemID = 0
                chargeTypeID, chargeQuantity, roomForReload = module.GetChargeReloadInfo()
                bestItemID = None
                for itemID, quant in ammoList.iteritems():
                    if quant >= roomForReload:
                        if not bestItemID or quant < ammoList[bestItemID]:
                            bestItemID = itemID
                    if not maxItemID or quant > ammoList[maxItemID]:
                        maxItemID = itemID

                bestItemID = bestItemID or maxItemID
                if bestItemID:
                    quant = min(roomForReload, ammoList[maxItemID])
                    uthread.new(module.AutoReload, 1, bestItemID, quant)
                    ammoList[bestItemID] -= quant

    def BlinkButton(self, key):
        btn = self.sr.Get(key.lower(), None) or self.sr.Get('%sBtn' % key.lower(), None)
        if not btn:
            for each in self.modulesByID:
                if getattr(each, 'locationFlag', None) == LookupConstValue('flag%s' % key, 'no'):
                    btn = each
                    break

        if not btn:
            return
        if hasattr(btn.sr, 'icon'):
            sm.GetService('ui').BlinkSpriteA(btn.sr.icon, 1.0, 1000, None, passColor=0)
        else:
            sm.GetService('ui').BlinkSpriteA(btn, 1.0, 1000, None, passColor=0)

    def ChangeOpacityForRange(self, currentRange, *args):
        curveSet = None
        for module in self.modulesByID.itervalues():
            maxRange, falloffDist, bombRadius = sm.GetService('tactical').FindMaxRange(module.sr.moduleInfo, module.charge)
            if maxRange == 0:
                continue
            animationDuration = GetTiDiAdjustedAnimationTime(normalDuation=0.1, minTiDiValue=0.1, minValue=0.01)
            if currentRange <= maxRange + falloffDist:
                if round(module.opacity, 3) != 1.5:
                    curveSet = uicore.animations.MorphScalar(module, 'opacity', startVal=module.opacity, endVal=1.5, duration=animationDuration, curveSet=curveSet)
            elif round(module.opacity, 3) != 1.0:
                curveSet = uicore.animations.MorphScalar(module, 'opacity', startVal=module.opacity, endVal=1.0, duration=animationDuration, curveSet=curveSet)

    def ResetModuleButtonOpacity(self, *args):
        for module in self.modulesByID.itervalues():
            module.StopAnimations()
            module.opacity = 1.0

    def ProcessPendingOverloadUpdate(self, moduleIDs):
        for moduleID in moduleIDs:
            moduleButton = self.modulesByID.get(moduleID, None)
            if moduleButton is not None:
                moduleButton.UpdateOverloadState()

    def ResetSwapMode(self):
        for each in self.children:
            each.opacity = 1.0
            if each.sr.get('module', -1) == -1:
                continue
            if each.sr.module is None and not getattr(each, 'showAsEmpty', 0) or getattr(each, 'ignored', 0):
                each.state = uiconst.UI_HIDDEN
            if getattr(each.sr, 'module', None):
                if getattr(each, 'linkDragging', None):
                    each.linkDragging = 0
                    each.sr.module.CheckOverload()
                    each.sr.module.CheckOnline()
                    each.sr.module.CheckMasterSlave()
                    each.sr.module.StopShowingGroupHighlight()
                    each.sr.module.CheckOnline()
                each.sr.module.blockClick = 0

    def OnWeaponGroupsChanged(self):
        uthread.new(self.InitSlots)

    def OnRefreshModuleBanks(self):
        uthread.new(self.InitSlots)

    def GetModuleForFKey(self, key):
        slot = int(key[1:])
        gidx = (slot - 1) / 8
        sidx = (slot - 1) % 8
        slot = self.slotsByOrder.get((gidx, sidx), None)
        if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
            return slot.sr.module

    def OnF(self, sidx, gidx):
        slot = self.slotsByOrder.get((gidx, sidx), None)
        if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
            uthread.new(slot.sr.module.Click)
        else:
            uthread.new(eve.Message, 'Disabled')

    def OnFKeyOverload(self, sidx, gidx):
        slot = self.slotsByOrder.get((gidx, sidx), None)
        if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
            if hasattr(slot.sr.module, 'ToggleOverload'):
                uthread.new(slot.sr.module.ToggleOverload)
        else:
            uthread.new(eve.Message, 'Disabled')

    def ToggleRackOverload(self, slotName):
        if slotName not in FITKEYS or self.destroyed:
            return
        btn = self.FindChild('overloadBtn' + slotName)
        if btn:
            if btn.activationID:
                uthread.new(self.OverloadRackBtnClick, btn)
            else:
                uthread.new(eve.Message, 'Disabled')

    def StartDragMode(self, itemID, typeID):
        for slot in self.children:
            if not hasattr(slot, 'sr') or not hasattr(slot.sr, 'module'):
                continue
            if slot.name.startswith('overload') or slot.name == 'groupAllIcon':
                continue
            if slot.sr.module is None:
                slot.opacity = 0.7
            slot.state = uiconst.UI_NORMAL
            if typeID is None:
                continue
            if getattr(slot.sr, 'module', None) is not None:
                moduleType = slot.sr.module.GetModuleType()
                isGroupable = slot.sr.module.sr.moduleInfo.groupID in const.dgmGroupableGroupIDs
                if isGroupable:
                    slot.linkDragging = 1
                    if slot.sr.module.sr.moduleInfo.itemID == itemID:
                        slot.sr.module.icon.SetAlpha(0.2)
                        continue
                    elif moduleType and moduleType[0] == typeID:
                        slot.sr.module.ShowGroupHighlight()

    def ToggleShowPassive(self):
        settings.user.ui.Set('showPassiveModules', not settings.user.ui.Get('showPassiveModules', 1))
        self.InitSlots()

    def ToggleShowEmpty(self):
        settings.user.ui.Set('showEmptySlots', not settings.user.ui.Get('showEmptySlots', 0))
        self.InitSlots()
