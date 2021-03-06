#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\target.py
from eve.client.script.ui.shared.stateFlag import AddAndSetFlagIcon
from gametime import GetDurationInClient, GetSimTime
import uicontrols
import blue
import uiprimitives
import uthread
import uix
import uiutil
import util
import state
import base
import random
import _weakref
import carbonui.const as uiconst
import xtriui
import localization
import telemetry
import math
accuracyThreshold = 0.8

class Target(uiprimitives.Container):
    __guid__ = 'xtriui.Target'
    __notifyevents__ = ['ProcessShipEffect',
     'OnStateChange',
     'OnJamStart',
     'OnJamEnd',
     'OnSlimItemChange',
     'OnDroneStateChange2',
     'OnDroneControlLost',
     'OnStateSetupChange',
     'OnSetPlayerStanding',
     'OnItemNameChange',
     'OnUIRefresh',
     'OnFleetJoin_Local',
     'OnFleetLeave_Local']

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.gaugesInited = 0
        self.gaugesVisible = 0
        self.lastDistance = None
        self.sr.gaugeParent = None
        self.sr.gauge_shield = None
        self.sr.gauge_armor = None
        self.sr.gauge_structure = None
        self.sr.updateTimer = None
        self.drones = {}
        self.activeModules = {}
        self.lastDataUsedForLabel = None
        self.timers = {}
        self.jammers = {}
        self.timerNames = {'propulsion': localization.GetByLabel('UI/Inflight/ScramblingShort'),
         'electronic': localization.GetByLabel('UI/Inflight/JammingShort'),
         'unknown': localization.GetByLabel('UI/Inflight/MiscellaneousShort')}

    def OnUIRefresh(self):
        self.Flush()
        self.init()
        bp = sm.GetService('michelle').GetBallpark()
        if bp is not None:
            slimItem = bp.GetInvItem(self.id)
        self.Startup(slimItem)

    def Startup(self, slimItem):
        sm.RegisterNotify(self)
        self.ball = _weakref.ref(sm.GetService('michelle').GetBall(slimItem.itemID))
        self.slimItem = _weakref.ref(slimItem)
        self.id = slimItem.itemID
        self.itemID = slimItem.itemID
        self.updatedamage = slimItem.categoryID != const.categoryAsteroid and slimItem.groupID != const.groupHarvestableCloud
        iconPar = uiprimitives.Container(parent=self, width=64, height=64, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        icon = uicontrols.Icon(parent=iconPar, align=uiconst.TOALL, typeID=slimItem.typeID, size=64)
        self.sr.iconPar = iconPar
        self.slimForFlag = slimItem
        self.SetStandingIcon()
        self.sr.hilite = uiprimitives.Fill(parent=iconPar, color=(1.0, 1.0, 1.0, 0.125), state=uiconst.UI_HIDDEN)
        self.sr.activeTarget = xtriui.ActiveTarget(parent=iconPar)
        rot = uiutil.GetChild(self.sr.activeTarget, 'rotate')
        sm.GetService('ui').Rotate(rot, 2.0, timeFunc=blue.os.GetSimTime)
        sm.GetService('ui').BlinkSpriteA(rot.children[0], 1.0, 500.0, 0, timeFunc=blue.os.GetSimTime)
        self.sr.diode = uiprimitives.Fill(parent=self, color=(0.0, 1.0, 0.0, 1.0), align=uiconst.TOLEFT, width=6, state=uiconst.UI_HIDDEN)
        self.sr.diode.state = uiconst.UI_HIDDEN
        labelClass = uicontrols.EveLabelSmall
        self.sr.label = labelClass(text=' ', parent=self, left=0, top=68, width=96, state=uiconst.UI_DISABLED)
        self.SetTargetLabel()
        self.sr.assigned = uiprimitives.Container(name='assigned', align=uiconst.TOPLEFT, parent=self, width=32, height=128, left=64)
        self.sr.updateTimer = base.AutoTimer(random.randint(750, 1000), self.UpdateData)
        self.UpdateData()
        selected = sm.GetService('state').GetExclState(state.selected)
        self.Select(selected == slimItem.itemID)
        hilited = sm.GetService('state').GetExclState(state.mouseOver)
        self.Hilite(hilited == slimItem.itemID)
        activeTargetID = sm.GetService('target').GetActiveTargetID()
        self.ActiveTarget(activeTargetID == slimItem.itemID)
        drones = sm.GetService('michelle').GetDrones()
        for key in drones:
            droneState = drones[key]
            if droneState.targetID == self.id:
                self.drones[droneState.droneID] = droneState.typeID

        self.UpdateDrones()

    def OnItemNameChange(self, *args):
        uthread.new(self.SetTargetLabel)

    def SetTargetLabel(self):
        self.label = uix.GetSlimItemName(self.slimForFlag)
        if self.slimForFlag.corpID:
            self.label = localization.GetByLabel('UI/Inflight/Target/TargetLabelWithTicker', target=uix.GetSlimItemName(self.slimForFlag), ticker=cfg.corptickernames.Get(self.slimForFlag.corpID).tickerName)
        self.UpdateData()

    def OnSetPlayerStanding(self, *args):
        self.SetStandingIcon()

    def OnStateSetupChange(self, *args):
        self.SetStandingIcon()

    def SetStandingIcon(self):
        stateMgr = sm.GetService('state')
        flag = stateMgr.CheckStates(self.slimForFlag, 'flag')
        self.standingIcon = AddAndSetFlagIcon(parentCont=self, flag=flag, top=51, left=36, showHint=False)

    def OnFleetJoin_Local(self, member, *args):
        if session.charid == member.charID or self.slimForFlag.charID == member.charID:
            self.SetStandingIcon()

    def OnFleetLeave_Local(self, member, *args):
        if session.charid == member.charID or self.slimForFlag.charID == member.charID:
            self.SetStandingIcon()

    def OnSlimItemChange(self, oldSlim, newSlim):
        uthread.new(self._OnSlimItemChange, oldSlim, newSlim)

    def _OnSlimItemChange(self, oldSlim, newSlim):
        if self.itemID != oldSlim.itemID or self.destroyed:
            return
        self.itemID = newSlim.itemID
        self.slimItem = _weakref.ref(newSlim)
        if oldSlim.corpID != newSlim.corpID or oldSlim.charID != newSlim.charID:
            self.label = uix.GetSlimItemName(newSlim)
            self.UpdateData()

    def OnStateChange(self, itemID, flag, true, *args):
        if not self.destroyed:
            uthread.new(self._OnStateChange, itemID, flag, true)

    def _OnStateChange(self, itemID, flag, true):
        if self.destroyed or self.itemID != itemID:
            return
        if flag == state.mouseOver:
            self.Hilite(true)
        elif flag == state.selected:
            self.Select(true)
        elif flag == state.activeTarget:
            self.ActiveTarget(true)

    def Hilite(self, state):
        if self.sr.hilite:
            self.sr.hilite.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][state]

    def Select(self, state):
        pass

    def OnJamStart(self, sourceBallID, moduleID, targetBallID, jammingType, startTime, duration):
        if jammingType not in self.jammers:
            self.jammers[jammingType] = {}
        durationInClient = GetDurationInClient(startTime, duration)
        if durationInClient < 0.0:
            return
        self.jammers[jammingType][sourceBallID, moduleID, targetBallID] = (GetSimTime(), durationInClient)
        self.CheckJam()

    def OnJamEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        if self and not self.destroyed and hasattr(self, 'jammers'):
            if jammingType in self.jammers:
                id = (sourceBallID, moduleID, targetBallID)
                if id in self.jammers[jammingType]:
                    del self.jammers[jammingType][id]
            self.CheckJam()

    def CheckJam(self):
        jams = self.jammers.keys()
        jams.sort()
        for jammingType in jams:
            jam = self.jammers[jammingType]
            sortList = []
            for id in jam.iterkeys():
                sourceBallID, moduleID, targetBallID = id
                if targetBallID == self.id:
                    startTime, duration = jam[id]
                    sortList.append((startTime + duration, (sourceBallID,
                      moduleID,
                      targetBallID,
                      jammingType,
                      startTime,
                      duration)))

            if sortList:
                sortList = uiutil.SortListOfTuples(sortList)
                sourceBallID, moduleID, targetBallID, jammingType, startTime, duration = sortList[-1]
                self.ShowTimer(jammingType, startTime, duration, self.timerNames.get(jammingType, '???'))
            else:
                self.KillTimer(jammingType)

    @telemetry.ZONE_METHOD
    def ShowTimer(self, timerID, startTime, duration, label):
        check = self.GetTimer(timerID)
        if check:
            if check.endTime <= startTime + duration:
                check.Close()
            else:
                return
        timer = uiprimitives.Container(name='%s' % timerID, parent=self.sr.gaugeParent, align=uiconst.TOTOP, height=7, padTop=5, padBottom=1)
        timer.endTime = startTime + duration
        timer.timerID = timerID
        self.ArrangeGauges()
        t1 = uicontrols.EveHeaderSmall(text=label, parent=timer, left=68, top=-1, state=uiconst.UI_DISABLED)
        uicontrols.Frame(parent=timer, padding=-1, color=(1.0, 1.0, 1.0, 0.5))
        t = uicontrols.EveLabelSmall(text='', parent=timer, left=5, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
        p = uiprimitives.Fill(parent=timer, align=uiconst.TOLEFT)
        timer.height = max(7, t.textheight - 3, t1.textheight - 3)
        duration = float(duration)
        while 1 and not timer.destroyed:
            now = blue.os.GetSimTime()
            dt = blue.os.TimeDiffInMs(startTime, now)
            timeLeft = (duration - dt) / 1000.0
            timer.timeLeft = timeLeft
            if timer.destroyed or dt > duration:
                t.text = localization.GetByLabel('UI/Common/Done')
                p.width = 0
                break
            t.text = localization.GetByLabel('UI/Inflight/Target/TimerDuration', timeLeft=timeLeft)
            p.width = int(timer.displayWidth * ((duration - dt) / duration))
            timer.height = max(7, t.textheight - 3)
            blue.pyos.synchro.Yield()

        blue.pyos.synchro.SleepWallclock(250)
        if not timer.destroyed and not self.destroyed:
            t.text = ''
            blue.pyos.synchro.SleepWallclock(250)
        if not timer.destroyed and not self.destroyed:
            t.text = localization.GetByLabel('UI/Common/Done')
            blue.pyos.synchro.SleepWallclock(250)
        if not timer.destroyed and not self.destroyed:
            t.text = ''
            blue.pyos.synchro.SleepWallclock(250)
        if not timer.destroyed and not self.destroyed:
            t.text = localization.GetByLabel('UI/Common/Done')
            blue.pyos.synchro.SleepWallclock(250)
        if not timer.destroyed and not self.destroyed:
            t.text = ''
            timer.Close()
        if not self.destroyed:
            self.ArrangeGauges()

    def KillTimer(self, timerID):
        timer = self.GetTimer(timerID)
        if timer:
            timer.Close()

    def GetTimer(self, timerID):
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('gaugeParent') and hasattr(self.sr.gaugeParent, 'children'):
            for each in self.sr.gaugeParent.children:
                if each.name == '%s' % timerID:
                    return each

        else:
            return None

    def ArrangeGauges(self):
        if self.gaugesInited:
            totalGaugeHeight = sum([ each.height + each.padTop + each.padBottom for each in self.sr.gaugeParent.children if each.state != uiconst.UI_HIDDEN ])
            self.sr.gaugeParent.height = totalGaugeHeight
            self.sr.label.top = self.sr.gaugeParent.top + self.sr.gaugeParent.height + 5

    def UpdateDamage(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            self.sr.updateTimer = None
            return
        dmg = bp.GetDamageState(self.itemID)
        if dmg is not None:
            self.SetDamageState(dmg)

    def SetDamageState(self, state):
        self.InitGauges()
        visible = 0
        for i, gauge in enumerate((self.sr.gauge_shield, self.sr.gauge_armor, self.sr.gauge_structure)):
            if state[i] is None:
                gauge.state = uiconst.UI_HIDDEN
            else:
                healthState = state[i]
                damageBarWidth = gauge.displayWidth * (1.0 - healthState)
                if healthState != 1.0:
                    damageBarWidth = max(1.0, damageBarWidth)
                gauge.damageBar.renderObject.displayX = gauge.displayWidth - damageBarWidth
                gauge.damageBar.renderObject.displayWidth = damageBarWidth
                gauge.damageBar.renderObject.displayHeight = gauge.displayHeight
                gauge.state = uiconst.UI_NORMAL
                visible += 1
                percLeft = max(healthState, 0) * 100
                if percLeft >= 1.0:
                    math.floor(percLeft)
                self.SetHint(gauge, percLeft)

        self.gaugesVisible = visible
        self.ArrangeGauges()

    def SetHint(self, gauge, percLeft):
        if gauge.name == 'gauge_shield':
            hintLabel = 'UI/Inflight/Target/GaugeShieldRemaining'
        elif gauge.name == 'gauge_armor':
            hintLabel = 'UI/Inflight/Target/GaugeArmorRemaining'
        elif gauge.name == 'gauge_structure':
            hintLabel = 'UI/Inflight/Target/GaugeStructureRemaining'
        else:
            return
        gauge.hint = localization.GetByLabel(hintLabel, percentage=percLeft)

    def InitGauges(self):
        if self.gaugesInited:
            self.sr.gaugeParent.state = uiconst.UI_NORMAL
            return
        par = uiprimitives.Container(name='gauges', parent=self, align=uiconst.TOPLEFT, width=66, height=32, top=66, left=0, state=uiconst.UI_NORMAL)
        gauges = ['shield', 'armor', 'structure']
        for gaugeName in gauges:
            g = uiprimitives.Container(name='gauge_%s' % gaugeName, parent=par, align=uiconst.TOTOP, height=7, padTop=5, padBottom=1)
            g.damageBar = uiprimitives.Fill(parent=g, align=uiconst.NOALIGN, color=(158 / 256.0,
             11 / 256.0,
             14 / 256.0,
             1.0))
            uicontrols.Frame(parent=g, color=(1.0, 1.0, 1.0, 0.5), padding=-1)
            uiprimitives.Fill(parent=g, padding=-1)
            setattr(self.sr, 'gauge_%s' % gaugeName, g)

        self.sr.gaugeParent = par
        self.gaugesInited = 1
        self.ArrangeGauges()

    def GetShipID(self):
        return self.itemID

    def GetIcon(self, icon, typeID, size):
        if not self.destroyed:
            icon.LoadIconByTypeID(typeID)
            icon.SetSize(size, size)

    def _OnClose(self, *args):
        sm.UnregisterNotify(self)
        self.sr.updateTimer = None

    def ProcessShipEffect(self, godmaStm, effectState):
        slimItem = self.slimItem()
        if slimItem and effectState.environment[3] == slimItem.itemID:
            if effectState.start:
                if self.GetWeapon(effectState.itemID):
                    return
                moduleInfo = self.GetModuleInfo(effectState.itemID)
                if moduleInfo:
                    self.AddWeapon(moduleInfo)
                    self.activeModules[effectState.itemID] = moduleInfo
            else:
                self.RemoveWeapon(effectState.itemID)
                self.activeModules.pop(effectState.itemID, None)

    def AddWeapon(self, moduleInfo):
        if self is None or self.destroyed:
            return
        icon = uicontrols.Icon(parent=self.sr.assigned, align=uiconst.RELATIVE, width=16, height=16, state=uiconst.UI_HIDDEN, typeID=moduleInfo.typeID, size=32)
        icon.sr.moduleID = moduleInfo.itemID
        icon.OnClick = (self.ClickWeapon, icon)
        icon.OnMouseEnter = (self.OnMouseEnterWeapon, icon)
        icon.OnMouseExit = (self.OnMouseExitWeapon, icon)
        icon.baseAlpha = 1.0
        self.ArrangeWeapons()

    def ClickWeapon(self, icon):
        if uicore.layer.shipui:
            module = uicore.layer.shipui.GetModule(icon.sr.moduleID)
            if module:
                module.Click()

    def OnMouseEnterWeapon(self, icon):
        sm.GetService('bracket').ShowHairlinesForModule(icon.sr.moduleID, reverse=True)

    def OnMouseExitWeapon(self, icon):
        sm.GetService('bracket').StopShowingModuleRange(icon.sr.moduleID)

    def IsEffectActivatible(self, effect):
        return effect.isDefault and effect.effectName != 'online' and effect.effectCategory in (const.dgmEffActivation, const.dgmEffTarget)

    def RemoveWeapon(self, moduleID):
        icon = self.GetWeapon(moduleID)
        if icon:
            icon.Close()
        self.ArrangeWeapons()

    def ArrangeWeapons(self):
        if self and not self.destroyed and self.sr.assigned:
            size = [32, 16][len(self.sr.assigned.children) > 2]
            left = 0
            top = 0
            for icon in self.sr.assigned.children:
                icon.width = icon.height = size
                icon.left = left
                icon.top = top
                top += size
                if top == 64:
                    top = 0
                    left += size
                icon.state = uiconst.UI_NORMAL

    def GetWeapon(self, moduleID):
        if self is None or self.destroyed:
            return
        if self.sr.assigned:
            for each in self.sr.assigned.children:
                if each.sr.moduleID == moduleID:
                    return each

    def GetModuleInfo(self, moduleID):
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        if ship is None:
            return
        for module in ship.modules:
            if module.itemID == moduleID:
                return module

    def OnClick(self, *args):
        sm.GetService('state').SetState(self.itemID, state.selected, 1)
        sm.GetService('state').SetState(self.itemID, state.activeTarget, 1)
        sm.GetService('menu').TacticalItemClicked(self.itemID)

    def GetMenu(self):
        m = sm.GetService('menu').CelestialMenu(self.itemID)
        return m

    def OnMouseHover(self, *args):
        pass

    def OnMouseDown(self, *args):
        if args[0] != uiconst.MOUSELEFT or len(uicore.layer.target.children) <= 1:
            return
        horizontalAlign = settings.user.ui.Get('alignHorizontally', True)
        rows, cols = sm.GetService('target').GetTargetsSize()
        width = height = 0
        left = top = None
        for target in uicore.layer.target.children:
            if isinstance(target, xtriui.Target):
                tl, tt, tw, th = target.GetAbsolute()
                width = max(int(cols * tw), width)
                height = max(int(rows * th), height)
                if left == None:
                    left = tl
                else:
                    left = min(left, tl)
                if top == None:
                    top = tt
                else:
                    top = min(top, tt)

        clipper = (left,
         top,
         left + width,
         top + height)
        uthread.new(self.DoRepositionDrag, clipper)

    def OnMouseUp(self, *args):
        if args[0] != uiconst.MOUSELEFT:
            return
        uicore.uilib.UnclipCursor()

    def OnMouseEnter(self, *args):
        sm.GetService('state').SetState(self.id, state.mouseOver, 1)

    def OnMouseExit(self, *args):
        sm.GetService('state').SetState(self.itemID, state.mouseOver, 0)

    def DoRepositionDrag(self, cursorClipper):
        blue.synchro.Sleep(200)
        if uicore.uilib.leftbtn and uicore.uilib.mouseOver == self:
            uicore.uilib.ClipCursor(*cursorClipper)
        else:
            return
        origin = self.GetAbsolute()
        xOffset = uicore.uilib.x - origin[0]
        yOffset = uicore.uilib.y - origin[1]
        horizontalAlign = settings.user.ui.Get('alignHorizontally', True)
        repositionLine = uiprimitives.Line(align=uiconst.TORIGHT, weight=4, color=(1, 1, 1, 0.5))
        uiutil.Transplant(self, uicore.layer.abovemain)
        targetSvc = sm.GetService('target')
        targetSvc.ArrangeTargets()
        while uicore.uilib.leftbtn:
            self.SetAlign(uiconst.TOPLEFT)
            self.left = uicore.uilib.x - xOffset
            self.top = uicore.uilib.y - yOffset
            (x, y), (toLeft, toTop) = targetSvc.GetOriginPosition(getDirection=1)
            lessThanAll = True
            for target in uicore.layer.target.children:
                if isinstance(target, xtriui.Target):
                    tl, tt, tw, th = target.GetAbsolute()
                    if tl - 2 <= uicore.uilib.x <= tl + tw + 2 and tt - 2 <= uicore.uilib.y <= tt + th + 2:
                        if horizontalAlign:
                            repositionLine.padTop = repositionLine.padBottom = 32
                            if not toLeft:
                                repositionLine.SetAlign(uiconst.TOLEFT)
                                repositionLine.padLeft = -10
                            else:
                                repositionLine.SetAlign(uiconst.TORIGHT)
                                repositionLine.padLeft = 0
                            lessThanAll = False
                            break
                        else:
                            if not toTop:
                                repositionLine.SetAlign(uiconst.TOTOP)
                                repositionLine.padTop = 0
                            else:
                                repositionLine.SetAlign(uiconst.TOBOTTOM)
                                repositionLine.padTop = -10
                            lessThanAll = False
                            break

            if lessThanAll:
                if horizontalAlign:
                    repositionLine.padTop = repositionLine.padBottom = 32
                    if not toLeft:
                        repositionLine.SetAlign(uiconst.TORIGHT)
                        repositionLine.padLeft = 0
                    else:
                        repositionLine.SetAlign(uiconst.TOLEFT)
                        repositionLine.padLeft = -10
                elif not toTop:
                    repositionLine.SetAlign(uiconst.TOBOTTOM)
                    repositionLine.padTop = -10
                else:
                    repositionLine.SetAlign(uiconst.TOTOP)
                    repositionLine.padTop = 0
            uiutil.Transplant(repositionLine, target)
            blue.pyos.synchro.Yield()

        uicore.uilib.UnclipCursor()
        uiutil.Transplant(self, uicore.layer.target, idx=uicore.layer.target.children.index(repositionLine.parent) if not lessThanAll else None)
        repositionLine.Close()
        targetSvc.ArrangeTargets()

    @telemetry.ZONE_METHOD
    def UpdateData(self):
        ball = self.ball()
        if not ball:
            return
        dist = ball.surfaceDist
        distanceInMeters = int(dist)
        dataUsedForLabel = (self.label, int(distanceInMeters))
        if dataUsedForLabel != self.lastDataUsedForLabel:
            newText = localization.GetByLabel('UI/Inflight/Target/DataLabel', label=self.label, distance=util.FmtDist(dist))
            self.sr.label.text = newText
            self.lastDataUsedForLabel = dataUsedForLabel
        if self.updatedamage:
            self.UpdateDamage()

    def ActiveTarget(self, true):
        if self.destroyed:
            return
        targetSvc = sm.GetService('target')
        if true:
            self.sr.iconPar.width = self.sr.iconPar.height = 56
            self.sr.iconPar.left = self.sr.iconPar.top = 5
            if not targetSvc.disableSpinnyReticule:
                self.sr.activeTarget.state = uiconst.UI_DISABLED
        else:
            self.sr.iconPar.width = self.sr.iconPar.height = 64
            self.sr.iconPar.left = self.sr.iconPar.top = 1
            self.sr.activeTarget.state = uiconst.UI_HIDDEN

    def OnDroneStateChange2(self, itemID, oldActivityState, activityState):
        michelle = sm.GetService('michelle')
        droneState = michelle.GetDroneState(itemID)
        if activityState in (const.entityCombat, const.entityEngage, const.entityMining):
            if droneState.targetID == self.id:
                self.drones[itemID] = droneState.typeID
            elif self.drones.has_key(itemID):
                del self.drones[itemID]
        elif self.drones.has_key(itemID):
            del self.drones[itemID]
        self.UpdateDrones()

    def OnDroneControlLost(self, droneID):
        if self.drones.has_key(droneID):
            del self.drones[droneID]
        self.UpdateDrones()

    def UpdateDrones(self):
        if not self.drones:
            self.RemoveWeapon('drones')
            return
        droneIcon = self.GetWeapon('drones')
        if not droneIcon:
            icon = uiprimitives.Sprite(align=uiconst.RELATIVE, width=16, height=16, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/Icons/56_64_5.png', parent=self.sr.assigned)
            icon.sr.moduleID = 'drones'
            self.ArrangeWeapons()
        self.UpdateDroneHint()

    def UpdateDroneHint(self):
        dronesByTypeID = {}
        droneIcon = self.GetWeapon('drones')
        for droneID, droneTypeID in self.drones.iteritems():
            if not dronesByTypeID.has_key(droneTypeID):
                dronesByTypeID[droneTypeID] = 0
            dronesByTypeID[droneTypeID] += 1

        hintLines = []
        for droneTypeID, number in dronesByTypeID.iteritems():
            hintLines.append(localization.GetByLabel('UI/Inflight/Target/DroneHintLine', drone=droneTypeID, count=number))

        droneIcon.hint = localization.GetByLabel('UI/Inflight/Target/DroneHintLabel', droneHintLines='<br>'.join(hintLines))
