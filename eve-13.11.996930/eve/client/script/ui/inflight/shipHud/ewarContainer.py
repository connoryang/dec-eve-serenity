#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\ewarContainer.py
from carbonui import const as uiconst
import evetypes
import localization
import state
import trinity
import uicontrols
import uiprimitives
import uiutil

class EwarContainer(uicontrols.ContainerAutoSize):
    __guid__ = 'uicls.EwarUIContainer'
    default_width = 500
    default_height = 500
    default_name = 'ewarcont'
    default_state = uiconst.UI_PICKCHILDREN
    __notifyevents__ = ['OnEwarStartFromTactical', 'OnEwarEndFromTactical']
    MAXNUMBERINHINT = 6

    def ApplyAttributes(self, attributes):
        self.pending = False
        self.busyRefreshing = False
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.ewarStates = {'warpScramblerMWD': const.iconModuleWarpScramblerMWD,
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
         'ewEnergyNeut': 'UI/Inflight/EwarHints/CapNeutralized'}
        self.RefreshAllButtons()
        sm.RegisterNotify(self)

    def RefreshAllButtons(self):
        self.CreateAllButtons()
        self.RefreshAllButtonDisplay()

    def CreateAllButtons(self, *args):
        self.Flush()
        for key, value in self.ewarStates.iteritems():
            btn, btnPar = self.AddButton(key, value)
            btnPar.display = False

    def AddButton(self, jammingType, graphicID):
        iconSize = 40
        btnPar = uiprimitives.Container(parent=self, align=uiconst.TOLEFT, width=iconSize + 8, name=jammingType)
        btnPar.fadingOut = False
        btn = EwarButton(parent=btnPar, name=jammingType, align=uiconst.CENTER, width=iconSize, height=iconSize, graphicID=graphicID, jammingType=jammingType)
        setattr(self, jammingType, btnPar)
        btnPar.btn = btn
        btn.GetMenu = (self.GetButtonMenu, btn)
        btn.GetButtonHint = self.GetButtonHint
        btn.OnClick = (self.OnButtonClick, btn)
        return (btn, btnPar)

    def OnEwarStartFromTactical(self, doAnimate = True, *args):
        self.RefreshAllButtonDisplay(doAnimate)

    def OnEwarEndFromTactical(self, doAnimate = True, *args):
        self.RefreshAllButtonDisplay(doAnimate)

    def ShowButton(self, jammingType, doAnimate = True):
        btnPar = getattr(self, jammingType, None)
        if btnPar:
            self.FadeButtonIn(btnPar, doAnimate)

    def HideButton(self, jammingType, doAnimate = True):
        btnPar = getattr(self, jammingType, None)
        if btnPar:
            self.FadeButtonOut(btnPar, doAnimate)

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
            self.RefreshAllButtonDisplay()

    def FadeButtonIn(self, btnPar, doAnimate = True):
        btn = btnPar.btn
        if not btnPar.display or btnPar.fadingOut:
            btnPar.fadingOut = False
            uiutil.SetOrder(btnPar, -1)
            btnPar.display = True
            if doAnimate:
                uicore.animations.FadeIn(btnPar)
                uicore.animations.MorphScalar(btnPar, 'width', startVal=0, endVal=40, duration=0.25)
            else:
                btnPar.opacity = 1.0
                btnPar.width = 40
        btnPar.btn.hint = None

    def FadeButtonOut(self, btnPar, doAnimate = True):
        if btnPar.display and not btnPar.fadingOut:
            btnPar.fadingOut = True
            btnPar.btn.hint = None
            if doAnimate:
                uicore.animations.MorphScalar(btnPar, 'width', startVal=40, endVal=0, duration=0.25)
                uicore.animations.FadeOut(btnPar, sleep=True)
                if btnPar.fadingOut:
                    btnPar.display = False
            else:
                btnPar.opacity = 0.0
                btnPar.width = 0

    def GetButtonHint(self, btn, jammingType, *args):
        if btn.hint is not None:
            return btn.hint
        attackers = self.FindWhoIsJammingMe(jammingType)
        hintList = []
        extraAttackers = 0
        for shipID, num in attackers.iteritems():
            if len(hintList) >= self.MAXNUMBERINHINT:
                extraAttackers = len(attackers) - len(hintList)
                break
            invItem = sm.StartService('michelle').GetBallpark().GetInvItem(shipID)
            if invItem:
                attackerShip = invItem.typeID
                if invItem.charID:
                    attackerID = invItem.charID
                    hintList.append(localization.GetByLabel('UI/Inflight/EwarAttacker', attackerID=attackerID, attackerShipID=attackerShip, num=num))
                else:
                    hintList.append(localization.GetByLabel('UI/Inflight/EwarAttackerNPC', attackerShipID=attackerShip, num=num))

        hintList = localization.util.Sort(hintList)
        if extraAttackers > 0:
            hintList.append(localization.GetByLabel('UI/Inflight/AndMorewarAttackers', num=extraAttackers))
        ewarHintPath = self.ewarHints.get(jammingType, None)
        if ewarHintPath is not None:
            ewarHint = localization.GetByLabel(ewarHintPath)
        else:
            ewarHint = ''
        hintList.insert(0, ewarHint)
        btn.hint = '<br>'.join(hintList)
        return btn.hint

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

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.btnName = attributes.btnName
        self.jammingType = attributes.jammingType
        self.orgTop = None
        self.pickRadius = -1
        graphicID = attributes.graphicID
        iconSize = self.height
        self.icon = uicontrols.Icon(parent=self, name='ewaricon', pos=(0,
         0,
         iconSize,
         iconSize), align=uiconst.CENTER, state=uiconst.UI_DISABLED, graphicID=graphicID, ignoreSize=1)
        self.hilite = uiprimitives.Sprite(parent=self, name='hilite', align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnBase.png', color=(0.63, 0.63, 0.63, 1.0), blendMode=trinity.TR2_SBM_ADD)
        slot = uiprimitives.Sprite(parent=self, name='slot', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(1.0, 0.0, 0.0, 2.5), texturePath='res:/UI/Texture/classes/ShipUI/utilBtnBase.png')

    def OnMouseEnter(self, *args):
        self.hilite.state = uiconst.UI_DISABLED

    def OnMouseExit(self, *args):
        self.hilite.state = uiconst.UI_HIDDEN
        if getattr(self, 'orgTop', None) is not None:
            self.top = self.orgTop

    def GetHint(self):
        return self.GetButtonHint(self, self.jammingType)

    def GetButtonHint(self, btn, jammingType):
        pass
