#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\activeShipController.py
from eve.common.script.sys.eveCfg import GetActiveShip
from fsdlite.signal import Signal
from localization import GetByLabel
import blue
import destiny
import trinity

class ActiveShipController(object):
    __notifyevents__ = ['DoBallClear', 'ProcessActiveShipChanged']

    def __init__(self):
        sm.RegisterNotify(self)
        self.ball = None
        self.on_new_itemID = Signal()
        self.wantedspeed = None

    def GetItemID(self):
        return GetActiveShip()

    def GetTypeID(self):
        return self._GetShipItem().typeID

    def _GetShipItem(self):
        return sm.GetService('godma').GetItem(self.GetItemID())

    def GetModules(self):
        return self._GetShipItem().modules

    def GetBall(self):
        if self.ball and self.ball.id == self.GetItemID() and self.ball.ballpark is not None:
            return self.ball
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None or self.GetItemID() is None:
            return
        self.ball = bp.GetBall(self.GetItemID())
        return self.ball

    def InvalidateBall(self):
        self.ball = None

    def Close(self):
        sm.UnregisterNotify(self)

    def DoBallClear(self, solItem):
        self.InvalidateBall()

    def ProcessActiveShipChanged(self, *args):
        self.on_new_itemID()
        self.InvalidateBall()

    def IsLoaded(self):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if not self.GetBall():
            return False
        if not self.GetItemID() or not dogmaLocation.IsItemLoaded(self.GetItemID()):
            return False
        if not self._GetShipItem():
            return False
        return True

    def GetArmorHP(self):
        return max(0.0, self._GetShipItem().armorHP - self._GetShipItem().armorDamage)

    def GetArmorHPMax(self):
        return self._GetShipItem().armorHP

    def GetArmorHPPortion(self):
        armor = 0.0
        try:
            return max(0.0, min(1.0, round(self.GetArmorHP() / self.GetArmorHPMax(), 2)))
        except ZeroDivisionError:
            return 0.0

    def GetStructureHP(self):
        return max(0.0, self._GetShipItem().hp - self._GetShipItem().damage)

    def GetStructureHPMax(self):
        return self._GetShipItem().hp

    def GetStructureHPPortion(self):
        try:
            return max(0.0, min(1.0, round(self.GetStructureHP() / self.GetStructureHPMax(), 2)))
        except ZeroDivisionError:
            return 0.0

    def GetShieldHP(self):
        return self._GetShipItem().shieldCharge

    def GetShieldHPMax(self):
        return self._GetShipItem().shieldCapacity

    def GetShieldHPPortion(self):
        try:
            return max(0.0, min(1.0, round(self.GetShieldHP() / self.GetShieldHPMax(), 2)))
        except ZeroDivisionError:
            return 0.0

    def GetCapacitorCapacity(self):
        return self._GetShipItem().charge

    def GetCapacitorCapacityMax(self):
        return float(self._GetShipItem().capacitorCapacity)

    def GetCharges(self):
        return self._GetShipItem().sublocations

    def IsControllingTurret(self):
        return bool(sm.GetService('pwn').GetCurrentControl())

    def GetMenu(self):
        itemID = self.GetItemID()
        if not itemID:
            return []
        return sm.GetService('menu').CelestialMenu(itemID)

    def GetSpeed(self):
        return self.GetBall().GetVectorDotAt(blue.os.GetSimTime()).Length()

    def GetSpeedFormatted(self):
        return self._GetSpeedFormatted(self.GetSpeed())

    def GetSpeedAt(self, speedRatio):
        return speedRatio * self.GetSpeedMax()

    def GetSpeedAtFormatted(self, speedRatio):
        return self._GetSpeedFormatted(self.GetSpeedAt(speedRatio))

    def GetSpeedMax(self):
        return self.GetBall().maxVelocity

    def GetSpeedMaxFormatted(self):
        return self._GetSpeedFormatted(self.GetSpeedMax())

    def _GetSpeedFormatted(self, speed):
        if speed < 100:
            return GetByLabel('UI/Inflight/MetersPerSecond', speed=round(speed, 1))
        return GetByLabel('UI/Inflight/MetersPerSecond', speed=int(speed))

    def GetSpeedPortion(self):
        try:
            speedPortion = max(0.0, min(1.0, self.GetSpeed() / self.GetSpeedMax()))
        except ZeroDivisionError:
            speedPortion = 0.0

        return speedPortion

    def StopShip(self):
        self.wantedspeed = 0.0
        uicore.cmd.CmdStopShip()

    def SetSpeed(self, speedRatio, initing = 0):
        if (not self.GetBall() or self.IsInWarp()) and speedRatio > 0:
            return
        if self.GetBall() and self.GetBall().ballpark is None:
            self.InvalidateBall()
            return
        if self.wantedspeed is not None and int(self.GetBall().speedFraction * 1000) == int(speedRatio * 1000) == int(self.wantedspeed * 1000) and speedRatio > 0:
            return
        if speedRatio <= 0.0:
            self.StopShip()
        elif speedRatio != self.wantedspeed:
            rbp = sm.GetService('michelle').GetRemotePark()
            bp = sm.GetService('michelle').GetBallpark()
            if bp and not initing:
                ownBall = bp.GetBall(session.shipid)
                if ownBall and rbp is not None and ownBall.mode == destiny.DSTBALL_STOP:
                    if not sm.GetService('autoPilot').GetState():
                        direction = trinity.TriVector(0.0, 0.0, 1.0)
                        currentDirection = self.GetBall().GetQuaternionAt(blue.os.GetSimTime())
                        direction.TransformQuaternion(currentDirection)
                        rbp.CmdGotoDirection(direction.x, direction.y, direction.z)
            if rbp is not None:
                rbp.CmdSetSpeedFraction(min(1.0, speedRatio))
                if not initing and self.GetBall():
                    speedText = GetByLabel('UI/Inflight/SpeedChangedTo', speed=self.GetSpeedAtFormatted(speedRatio))
                    sm.GetService('logger').AddText(speedText, 'notify')
                    sm.GetService('gameui').Say(speedText)
        if not initing:
            self.wantedspeed = max(speedRatio, 0.0)

    def SetMaxSpeed(self, *args):
        bp = sm.GetService('michelle').GetBallpark()
        rbp = sm.GetService('michelle').GetRemotePark()
        if bp:
            ownBall = bp.GetBall(session.shipid)
            if ownBall and rbp is not None and ownBall.mode == destiny.DSTBALL_STOP:
                if not sm.GetService('autoPilot').GetState():
                    direction = trinity.TriVector(0.0, 0.0, 1.0)
                    currentDirection = self.GetBall().GetQuaternionAt(blue.os.GetSimTime())
                    direction.TransformQuaternion(currentDirection)
                    rbp.CmdGotoDirection(direction.x, direction.y, direction.z)
        if rbp is not None:
            rbp.CmdSetSpeedFraction(1.0)
            speed = self.GetSpeedMaxFormatted()
            speedText = GetByLabel('UI/Inflight/SpeedChangedTo', speed=speed)
            sm.GetService('logger').AddText(speedText, 'notify')
            sm.GetService('gameui').Say(speedText)
            self.wantedspeed = 1.0
        else:
            self.wantedspeed = None

    def IsInWarp(self):
        ball = self.GetBall()
        return ball is None or ball.mode == destiny.DSTBALL_WARP

    def _GetHeatStates(self):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        return dogmaLocation.GetCurrentShipHeatStates()

    def GetHeatLowPortion(self):
        return self._GetHeatStates()[const.attributeHeatLow]

    def GetHeatMedPortion(self):
        return self._GetHeatStates()[const.attributeHeatMed]

    def GetHeatHiPortion(self):
        return self._GetHeatStates()[const.attributeHeatHi]

    def GetNumHiSlots(self):
        return int(getattr(self._GetShipItem(), 'hiSlots', 0))

    def GetNumMedSlots(self):
        return int(getattr(self._GetShipItem(), 'medSlots', 0))

    def GetNumLowSlots(self):
        return int(getattr(self._GetShipItem(), 'lowSlots', 0))

    def GetModuleGroupDamage(self, itemID, *args):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        moduleDamage = dogmaLocation.GetAccurateAttributeValue(itemID, const.attributeDamage)
        masterID = dogmaLocation.IsInWeaponBank(self.GetItemID(), itemID)
        if not masterID:
            return moduleDamage
        allModulesInBank = dogmaLocation.GetModulesInBank(self.GetItemID(), masterID)
        maxDamage = moduleDamage
        for slaveID in allModulesInBank:
            damage = dogmaLocation.GetAccurateAttributeValue(slaveID, const.attributeDamage)
            if damage > maxDamage:
                maxDamage = damage

        return maxDamage
