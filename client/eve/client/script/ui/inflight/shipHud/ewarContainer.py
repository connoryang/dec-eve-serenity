#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\ewarContainer.py
import evetypes
import localization
import state
import trinity
import uicontrols
import uiprimitives
import uiutil
from carbonui import const as uiconst
from dogma.effects import DEFENSIVE_EWAR_TYPES
from eve.client.script.ui.inflight.moduleEffectTimer import ModuleEffectTimer
from collections import OrderedDict

class EwarContainer(uicontrols.ContainerAutoSize):
    __guid__ = 'uicls.EwarUIContainer'
    default_width = 500
    default_height = 500
    default_name = 'ewarcont'
    default_state = uiconst.UI_PICKCHILDREN
    __notifyevents__ = ['OnEwarStartFromTactical', 'OnEwarEndFromTactical']
    MAXNUMBERINHINT = 6
    ICONSIZE = 40
    PADRIGHT = 5

    def ApplyAttributes(self, attributes):
        self.pending = False
        self.busyRefreshing = False
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.ewarOffensiveStates = {'warpScramblerMWD': const.iconModuleWarpScramblerMWD,
         'warpScrambler': const.iconModuleWarpScrambler,
         'focusedWarpScrambler': const.iconModuleFocusedWarpScrambler,
         'webify': const.iconModuleStasisWeb,
         'electronic': const.iconModuleECM,
         'ewRemoteSensorDamp': const.iconModuleSensorDamper,
         'ewTrackingDisrupt': const.iconModuleTrackingDisruptor,
         'ewGuidanceDisrupt': const.iconModuleGuidanceDisruptor,
         'ewTargetPaint': const.iconModuleTargetPainter,
         'ewEnergyVampire': const.iconModuleNosferatu,
         'ewEnergyNeut': const.iconModuleEnergyNeutralizer}
        self.ewarDefensiveStates = {'remoteTracking': const.iconModuleRemoteTracking,
         'energyTransfer': const.iconModuleEnergyTransfer,
         'sensorBooster': const.iconModuleSensorBooster,
         'eccmProjector': const.iconModuleECCMProjector,
         'remoteHullRepair': const.iconModuleHullRepairer,
         'remoteArmorRepair': const.iconModuleArmorRepairer,
         'shieldTransfer': const.iconModuleShieldBooster}
        self.ewarStates = self.ewarDefensiveStates.copy()
        self.ewarStates.update(self.ewarOffensiveStates)
        self.ewarHints = {'warpScramblerMWD': 'UI/Inflight/EwarHints/WarpScrambledMWD',
         'warpScrambler': 'UI/Inflight/EwarHints/WarpScrambled',
         'focusedWarpScrambler': 'UI/Inflight/EwarHints/FocusedWarpScrambled',
         'webify': 'UI/Inflight/EwarHints/Webified',
         'electronic': 'UI/Inflight/EwarHints/Jammed',
         'ewRemoteSensorDamp': 'UI/Inflight/EwarHints/SensorDampened',
         'ewTrackingDisrupt': 'UI/Inflight/EwarHints/TrackingDisrupted',
         'ewGuidanceDisrupt': 'UI/Inflight/EwarHints/GuidanceDisrupted',
         'ewTargetPaint': 'UI/Inflight/EwarHints/TargetPainted',
         'ewEnergyVampire': 'UI/Inflight/EwarHints/CapDrained',
         'ewEnergyNeut': 'UI/Inflight/EwarHints/CapNeutralized',
         'remoteTracking': 'UI/Inflight/EwarHints/RemoteTracking',
         'energyTransfer': 'UI/Inflight/EwarHints/EnergyTransfer',
         'sensorBooster': 'UI/Inflight/EwarHints/SensorBooster',
         'eccmProjector': 'UI/Inflight/EwarHints/ECCMProjector',
         'remoteHullRepair': 'UI/Inflight/EwarHints/RemoteHullRepair',
         'remoteArmorRepair': 'UI/Inflight/EwarHints/RemoteArmorRepair',
         'shieldTransfer': 'UI/Inflight/EwarHints/ShieldTransfer'}
        self.RefreshAllButtons()
        sm.RegisterNotify(self)

    def RefreshAllButtons(self, doAnimate = True):
        self.CreateAllButtons()
        self.RefreshAllButtonDisplay(doAnimate)

    def CreateAllButtons(self, *args):
        self.Flush()
        for key, value in self.ewarStates.iteritems():
            btn, btnPar = self.AddButton(key, value)
            btnPar.display = False

    def AddButton(self, jammingType, graphicID):
        btnPar = uiprimitives.Container(parent=self, align=uiconst.TOLEFT, width=self.ICONSIZE + 8, padRight=self.PADRIGHT, name=jammingType)
        btnPar.fadingOut = False
        btn = EwarButton(parent=btnPar, name=jammingType, align=uiconst.CENTER, width=self.ICONSIZE, height=self.ICONSIZE, graphicID=graphicID, jammingType=jammingType)
        setattr(self, jammingType, btnPar)
        btnPar.btn = btn
        btn.GetMenu = (self.GetButtonMenu, btn)
        btn.GetButtonHint = self.GetButtonHint
        btn.OnClick = (self.OnButtonClick, btn)
        return (btn, btnPar)

    def OnEwarStartFromTactical(self, doAnimate = True, *args):
        self.RefreshAllButtonDisplay(doAnimate)

    def OnEwarEndFromTactical(self, jammingType = None, ewarId = None, doAnimate = True, *args):
        self.RefreshAllButtonDisplay(doAnimate)
        if jammingType and ewarId:
            self.RemoveTimer(jammingType, ewarId)

    def ShowButton(self, jammingType, doAnimate = True):
        btnPar = getattr(self, jammingType, None)
        if btnPar:
            isBuff = jammingType in self.ewarDefensiveStates
            order = -1 if isBuff else self.GetNumberOfActiveDebuffs() - 1
            self.FadeButtonIn(btnPar, doAnimate, order)

    def HideButton(self, jammingType, doAnimate = True):
        btnPar = getattr(self, jammingType, None)
        if btnPar:
            self.FadeButtonOut(btnPar, doAnimate)

    def StartTimer(self, jammingType, id, duration, *args):
        btnPar = getattr(self, jammingType, None)
        if btnPar and btnPar.btn:
            timer = btnPar.btn.GetTimer(id)
            timer.StartTimer(duration)

    def RemoveTimer(self, jammingType, id):
        btnPar = getattr(self, jammingType, None)
        if btnPar and btnPar.btn:
            btnPar.btn.RemoveTimer(id)

    def RefreshAllButtonDisplay(self, doAnimate = True):
        if self.busyRefreshing:
            self.pending = True
            return
        self.pending = False
        self.busyRefreshing = True
        try:
            jammersByType = sm.GetService('tactical').jammersByJammingType
            for jammingType in self.ewarStates.iterkeys():
                if not jammersByType.get(jammingType, set()):
                    self.HideButton(jammingType, doAnimate)
                else:
                    self.ShowButton(jammingType, doAnimate)

        finally:
            self.busyRefreshing = False

        if self.pending:
            self.RefreshAllButtonDisplay(doAnimate)

    def GetNumberOfActiveDebuffs(self):
        jammersByType = sm.GetService('tactical').jammersByJammingType
        numberOfActiveDebuffs = 0
        for jammingType in self.ewarOffensiveStates:
            if jammersByType.get(jammingType, set()):
                numberOfActiveDebuffs += 1

        return numberOfActiveDebuffs

    def FadeButtonIn(self, btnPar, doAnimate = False, order = -1):
        if not btnPar.display or btnPar.fadingOut:
            btnPar.fadingOut = False
            uiutil.SetOrder(btnPar, order)
            btnPar.display = True
            if doAnimate:
                uicore.animations.FadeIn(btnPar)
                uicore.animations.MorphScalar(btnPar, 'width', startVal=0, endVal=40, duration=0.25)
            else:
                btnPar.opacity = 1.0
                btnPar.width = 40
        self._ResetButtonHint(btnPar)

    def FadeButtonOut(self, btnPar, doAnimate = True):
        if btnPar.display and not btnPar.fadingOut:
            btnPar.fadingOut = True
            self._ResetButtonHint(btnPar)
            if doAnimate:
                uicore.animations.MorphScalar(btnPar, 'width', startVal=40, endVal=0, duration=0.25)
                uicore.animations.FadeOut(btnPar, sleep=True)
                if btnPar.fadingOut:
                    btnPar.display = False
            else:
                btnPar.opacity = 0.0
                btnPar.width = 0

    def _ResetButtonHint(self, btnPar = None):
        if btnPar and btnPar.btn:
            btnPar.btn.hint = None

    def GetButtonHint(self, btn, jammingType, *args):
        if jammingType == 'electronic':
            hintList = self.GetEcmHintList(jammingType)
        else:
            hintList = self.GetEwarHintList(jammingType)
        btn.hint = '<br>'.join(hintList)
        return btn.hint

    def GetEwarHintList(self, jammingType):
        attackers = self.FindWhoIsJammingMe(jammingType)
        hintList = []
        extraAttackers = 0
        for shipID, num in attackers.iteritems():
            if len(hintList) >= self.MAXNUMBERINHINT:
                extraAttackers = len(attackers) - len(hintList)
                break
            self.AddEwarAttackerText(hintList, shipID, num)

        hintList = localization.util.Sort(hintList)
        self.AddExtraAttackers(hintList, extraAttackers)
        ewarHint = self.GetEwarHintCaption(jammingType)
        hintList.insert(0, ewarHint)
        return hintList

    def GetEwarHintCaption(self, jammingType):
        ewarHintPath = self.ewarHints.get(jammingType, None)
        if ewarHintPath is not None:
            ewarHint = localization.GetByLabel(ewarHintPath)
        else:
            ewarHint = ''
        return ewarHint

    def AddEwarAttackerText(self, hintList, sourceID, numModules):
        invItem = sm.StartService('michelle').GetBallpark().GetInvItem(sourceID)
        if invItem:
            attackerShipTypeID = invItem.typeID
            if invItem.charID:
                attackerID = invItem.charID
                hintList.append(localization.GetByLabel('UI/Inflight/EwarAttacker', attackerID=attackerID, attackerShipID=attackerShipTypeID, num=numModules))
            else:
                hintList.append(localization.GetByLabel('UI/Inflight/EwarAttackerNPC', attackerShipID=attackerShipTypeID, num=numModules))

    def GetEcmHintList(self, jammingType):
        ewarAggressors = self.GetEwarAggressorsByJammingType(jammingType)
        activeList = []
        inactiveList = []
        for sourceID, moduleCount, activeCount in ewarAggressors:
            if activeCount:
                self.AddEwarAttackerText(activeList, sourceID, activeCount)
            if moduleCount > activeCount:
                self.AddEwarAttackerText(inactiveList, sourceID, moduleCount - activeCount)

        localization.util.Sort(activeList)
        localization.util.Sort(inactiveList)
        hintList = [self.GetEwarHintCaption(jammingType)]
        hintList.extend(activeList[:self.MAXNUMBERINHINT])
        if len(activeList) < self.MAXNUMBERINHINT and len(inactiveList):
            hintList.append('<color=gray>%s</color>' % localization.GetByLabel('UI/Inflight/EwarHints/FailedEwarAttempts'))
            hintList.extend(inactiveList[:self.MAXNUMBERINHINT - len(activeList)])
        extraAttackers = len(activeList) + len(inactiveList) - self.MAXNUMBERINHINT
        self.AddExtraAttackers(hintList, extraAttackers)
        return hintList

    def AddExtraAttackers(self, hintList, extraAttackers):
        if extraAttackers > 0:
            hintList.append(localization.GetByLabel('UI/Inflight/AndMorewarAttackers', num=extraAttackers))

    def GetButtonMenu(self, btn, *args):
        attackers = self.FindWhoIsJammingMe(btn.jammingType)
        m = []
        for shipID, num in attackers.iteritems():
            invItem = sm.StartService('michelle').GetBallpark().GetInvItem(shipID)
            if invItem:
                if invItem.charID:
                    attackerName = cfg.eveowners.Get(invItem.charID).name
                else:
                    attackerName = evetypes.GetName(invItem.typeID)
                m += [[attackerName, ('isDynamic', sm.GetService('menu').CelestialMenu, (invItem.itemID,
                    None,
                    invItem,
                    0,
                    invItem.typeID))]]

        m = localization.util.Sort(m, key=lambda x: x[0])
        return m

    def FindWhoIsJammingMe(self, jammingType):
        jammers = sm.GetService('tactical').jammersByJammingType.get(jammingType, set())
        if not jammers:
            return {}
        attackers = {}
        for jamInfo in jammers:
            sourceID, moduleID = jamInfo
            numberOfTimes = attackers.get(sourceID, 0)
            numberOfTimes += 1
            attackers[sourceID] = numberOfTimes

        return attackers

    def FindActiveJammers(self, jammingType):
        allActiveJams = sm.GetService('godma').activeJams
        activeJammers = {}
        for sourceBallID, moduleID, targetBallID, _jammingType in allActiveJams:
            if jammingType != _jammingType:
                continue
            count = activeJammers.get(sourceBallID, 0)
            activeJammers[sourceBallID] = count + 1

        return activeJammers

    def GetEwarAggressorsByJammingType(self, jammingType):
        allModulesActiveBySource = self.FindWhoIsJammingMe(jammingType)
        activeModulesBySource = self.FindActiveJammers(jammingType)
        ewarAggressors = []
        for sourceID, moduleCount in allModulesActiveBySource.iteritems():
            activeCount = activeModulesBySource.get(sourceID, 0)
            ewarAggressors.append((sourceID, moduleCount, activeCount))

        ewarAggressors.sort(key=lambda x: -x[2])
        return ewarAggressors

    def OnButtonClick(self, btn, *args):
        attackers = self.FindWhoIsJammingMe(btn.jammingType)
        michelle = sm.GetService('michelle')
        targets = []
        stateSvc = sm.GetService('state')
        targetStates = (state.targeted, state.targeting)
        if uicore.cmd.IsSomeCombatCommandLoaded():
            targeting = uicore.cmd.combatCmdLoaded.name == 'CmdLockTargetItem'
            for sourceID in attackers:
                try:
                    if targeting and any(stateSvc.GetStates(sourceID, targetStates)):
                        continue
                    ball = michelle.GetBall(sourceID)
                    targets.append((ball.surfaceDist, sourceID))
                except:
                    pass

            if len(targets) > 0:
                targets.sort()
                itemID = targets[0][1]
                uicore.cmd.ExecuteCombatCommand(itemID, uiconst.UI_CLICK)


class EwarButton(uiprimitives.Container):
    __guid__ = 'uicls.EwarButton'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.RELATIVE
    ICON_BASE_ALPHA = 1.0
    ICON_HIGHLIGHTED_ALPHA = 1.5
    OFFENSIVE_ICON_COLOR = (1.0,
     0.7,
     0.7,
     ICON_BASE_ALPHA)
    DEFENSIVE_ICON_COLOR = (0.7,
     1,
     1,
     ICON_BASE_ALPHA)
    OFFENSIVE_SLOT_COLOR = (0.7, 0.0, 0.0, 1)
    DEFENSIVE_SLOT_COLOR = (0.0, 0.6, 0.6, 1)
    SLOT_TEXTURE_PATH = 'res:/UI/Texture/classes/ShipUI/EwarBar/ewarBarUnderlayClean.png'
    SLOT_GRADIENT_TEXTURE_PATH = 'res:/UI/Texture/classes/ShipUI/EwarBar/ewarBarUnderlayGrad.png'
    SLOT_BASE_ALPHA = 0.2
    SLOT_GRADIENT_ALPHA = 0.25
    SHADOW_COLOR = (1.0, 1.0, 1.0, 0.25)
    SHADOW_TEXTURE_PATH = 'res:/UI/Texture/classes/ShipUI/EwarBar/ewarBarShadow.png'
    TIMER_OPACITY = 0.65
    OFFENSIVE_TIMER_COLOR = (1.0, 0.3, 0.0)
    DEFENSIVE_TIMER_COLOR = (0.0, 0.8, 0.8)
    TIMER_RIGHT_COUNTER_TEXTURE_PATH = 'res:/UI/Texture/classes/ShipUI/EwarBar/ewarCounterRight.png'
    TIMER_LEFT_COUNTER_TEXTURE_PATH = 'res:/UI/Texture/classes/ShipUI/EwarBar/ewarCounterLeft.png'
    TIMER_COUNTER_GAUGE_TEXTURE_PATH = 'res:/UI/Texture/classes/ShipUI/EwarBar/ewarCounterGauge.png'
    TIMER_INCREASE = False

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.btnName = attributes.btnName
        self.jammingType = attributes.jammingType
        self.orgTop = None
        self.pickRadius = -1
        self.timers = OrderedDict()
        self.isOffensive = self.jammingType not in DEFENSIVE_EWAR_TYPES.values()
        graphicID = attributes.graphicID
        iconSize = self.height
        iconColor = self.OFFENSIVE_ICON_COLOR if self.isOffensive else self.DEFENSIVE_ICON_COLOR
        slotColor = self.OFFENSIVE_SLOT_COLOR if self.isOffensive else self.DEFENSIVE_SLOT_COLOR
        self.icon = uicontrols.Icon(parent=self, name='ewaricon', pos=(0,
         0,
         iconSize,
         iconSize), align=uiconst.CENTER, state=uiconst.UI_DISABLED, graphicID=graphicID, ignoreSize=1, color=iconColor)
        uiprimitives.Sprite(parent=self, name='slot_gradient', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=slotColor, blendMode=trinity.TR2_SBM_ADD, texturePath=self.SLOT_GRADIENT_TEXTURE_PATH, opacity=self.SLOT_GRADIENT_ALPHA)
        uiprimitives.Sprite(parent=self, name='slot_base', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=slotColor, blendMode=trinity.TR2_SBM_ADD, texturePath=self.SLOT_TEXTURE_PATH, opacity=self.SLOT_BASE_ALPHA)
        uiprimitives.Sprite(parent=self, name='shadow', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=self.SHADOW_COLOR, texturePath=self.SHADOW_TEXTURE_PATH)

    def GetTimer(self, id):
        if id not in self.timers:
            timerColor = self.OFFENSIVE_TIMER_COLOR if self.isOffensive else self.DEFENSIVE_TIMER_COLOR
            timer = ModuleEffectTimer(parent=self, timerColor=timerColor, timerOpacity=self.TIMER_OPACITY, timerRightCounterTexturePath=self.TIMER_RIGHT_COUNTER_TEXTURE_PATH, timerLeftCounterTexturePath=self.TIMER_LEFT_COUNTER_TEXTURE_PATH, timerCounterGaugeTexturePath=self.TIMER_COUNTER_GAUGE_TEXTURE_PATH, timeIncreases=self.TIMER_INCREASE)
            self.timers[id] = timer
        else:
            timer = self.timers[id]
            del self.timers[id]
            self.timers[id] = timer
        return self.timers[id]

    def RemoveTimer(self, id):
        if id in self.timers:
            self.timers[id].RemoveTimer()
            del self.timers[id]

    def GetHint(self):
        return self.GetButtonHint(self, self.jammingType)

    def GetButtonHint(self, btn, jammingType):
        pass

    def OnMouseEnter(self, *args):
        self.icon.SetAlpha(self.ICON_HIGHLIGHTED_ALPHA)

    def OnMouseExit(self, *args):
        if getattr(self, 'orgTop', None) is not None:
            self.top = self.orgTop
        self.icon.SetAlpha(self.ICON_BASE_ALPHA)
