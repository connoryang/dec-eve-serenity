#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\flightControls.py
import geo2
import math
import blue
import util
import service
import uthread
import destiny
import trinity
import evecamera
import collections
from eveexceptions.exceptionEater import ExceptionEater
from carbonui.uicore import uicorebase as uicore
import carbonui.const as uiconst

class FlightControls(service.Service):
    __guid__ = 'svc.flightControls'
    __dependencies__ = ['michelle', 'machoNet']
    __notifyevents__ = ['OnBallparkSetState',
     'OnSessionChanged',
     'DoBallsAdded',
     'OnMapShortcut',
     'OnRestoreDefaultShortcuts',
     'DoSimClockRebase',
     'OnActiveCameraChanged']

    def Run(self, *args):
        service.Service.Run(self, *args)
        self.controls = KeyboardControls()
        self.simulation = FlightSimulation(callback=self.OnGotoDirection, controls=self.controls, throttle=self.GetThrottle())
        self.statistics = FlightControlStatistics(self.controls)
        self.simulation.Start()
        self.statistics.Start()

    def GetThrottle(self):
        return int(self.machoNet.GetGlobalConfig().get('flightControlsThrottle', 400)) / float(1000) * const.SEC

    def OnGotoDirection(self, direction):
        remote = self.michelle.GetRemotePark()
        if remote:
            remote.CmdSteerDirection(*direction)
            self.statistics.Increment()

    def AttachShip(self):
        self.controls.PrimeKeys()
        ballpark = self.michelle.GetBallpark()
        if ballpark and session.shipid:
            self.simulation.AttachShip(ballpark.GetBall(session.shipid))
        else:
            self.simulation.DetachShip()

    def DoSimClockRebase(self, times):
        self.simulation.AdjustTimes(times[1] - times[0])
        self.controls.Reset()

    def OnBallparkSetState(self):
        self.AttachShip()
        self.controls.Reset()

    def OnSessionChanged(self, isRemote, session, change):
        self.AttachShip()
        self.controls.Reset()

    def DoBallsAdded(self, balls):
        with ExceptionEater('FlightControls.DoBallsAdded'):
            if any([ ball for ball, item in balls if item.itemID == session.shipid ]):
                self.AttachShip()
                self.controls.Reset()

    def OnMapShortcut(self, *args):
        self.controls.PrimeKeys()

    def OnRestoreDefaultShortcuts(self, *args):
        self.controls.PrimeKeys()

    def OnActiveCameraChanged(self, cameraID):
        self.simulation.SetWorldRelative(cameraID != evecamera.CAM_SHIPPOV)


class FlightSimulation(object):
    ENGAGE_TIME = 6.0
    RELEASE_TIME = 4.0

    def __init__(self, callback, controls, throttle = None):
        self.callback = callback
        self.controls = controls
        self.throttle = throttle or 0
        self.ballpark = blue.classes.CreateInstance('destiny.Ballpark')
        self.ballpark.tickInterval = 100
        self.ball = self.ballpark.AddBall(1, 1.0, 0.0, 0, True, False, False, False, False, 0, 0, 0, 0, 0, 0, 0, 0)
        self.ballpark.ego = 1
        self.ship = None
        self.thread = None
        self.controlling = False
        self.direction = None
        self.lastCalled = 0
        self.worldRelative = True
        self.curve = trinity.Tr2QuaternionLerpCurve()

    def Start(self):
        if self.thread is None:
            self.ballpark.Start()
            self.thread = uthread.new(self.Update)
            self.thread.context = 'FlightSimulation::Update'

    def Stop(self):
        if self.thread is not None:
            self.ballpark.Pause()
            self.thread.kill()
            self.thread = None

    def SetWorldRelative(self, relative):
        self.worldRelative = relative

    def AdjustTimes(self, delta):
        self.lastCalled += delta
        self.ballpark.AdjustTimes(delta)

    def AttachShip(self, ship):
        if ship is None or self.ship != ship:
            self.DetachShip(self.ship)
            self.ship = ship
            self.controlling = False
            if getattr(self, 'localModel', None):
                self.DisableDebug()
                self.EnableDebug()

    def DetachShip(self, ship = None):
        if ship in (self.ship, None):
            if self.ship and getattr(self.ship, 'model', None):
                self.ship.model.rotationCurve = self.ship
            self.ship = None
            self.controlling = False

    def Update(self):
        while True:
            blue.synchro.Yield()
            if self.ship and self.controls and self.callback:
                with util.ExceptionEater('FlightSimulation'):
                    self.AttachBalls()
                    self.ProcessInput()
                    self.UpdateDirection()
                    self.TriggerCallback()

    def AttachBalls(self):
        self.ballpark.tickInterval = 100
        if getattr(self.ship, 'model', None) and self.ship.model.rotationCurve != self.curve:
            self.ship.model.rotationCurve = self.curve
            velocity = self.ship.GetVectorDotAt(blue.os.GetSimTime())
            self.ballpark.SetBallVelocity(self.ball.id, velocity.x, velocity.y, velocity.z)
            self.curve.startCurve = self.ball
            self.curve.endCurve = self.ship
            self.curve.start = 0
            self.curve.length = 1

    def CanControl(self):
        return self.ship.mode in (destiny.DSTBALL_ORBIT, destiny.DSTBALL_FOLLOW, destiny.DSTBALL_GOTO)

    def ProcessInput(self):
        if self.CanControl():
            yaw, pitch = self.controls.GetYawPitch()
        else:
            yaw, pitch = (0, 0)
        currentYaw, currentPitch, currentRoll = self.curve.GetQuaternionAt(blue.os.GetSimTime()).GetYawPitchRoll()
        if self.worldRelative:
            currentPitch = max(-math.pi / 2.0, min(math.pi / 2.0, currentPitch + pitch))
            current = geo2.QuaternionRotationSetYawPitchRoll(currentYaw, currentPitch, 0)
            rotation = geo2.QuaternionRotationSetYawPitchRoll(yaw, 0, 0)
        else:
            current = geo2.QuaternionRotationSetYawPitchRoll(currentYaw, currentPitch, currentRoll)
            rotation = geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, 0)
        result = geo2.QuaternionMultiply(rotation, current)
        self.direction = geo2.QuaternionTransformVector(result, (0, 0, 1))
        if not self.controlling:
            self.controlling = bool(yaw or pitch)

    def UpdateDirection(self):
        self.ball.x, self.ball.y, self.ball.z = self.ship.x, self.ship.y, self.ship.z
        self.ballpark.SetBallMass(self.ball.id, self.ship.mass)
        self.ballpark.SetBallAgility(self.ball.id, self.ship.Agility)
        self.ballpark.SetBallRadius(self.ball.id, self.ship.radius)
        self.ballpark.SetMaxSpeed(self.ball.id, self.ship.maxVelocity)
        self.ballpark.SetSpeedFraction(self.ball.id, self.ship.speedFraction)
        if self.controlling:
            self.ballpark.GotoDirection(self.ball.id, self.direction[0], self.direction[1], self.direction[2])
            if self.curve.endCurve != self.ball:
                self.curve.startCurve = self.ship
                self.curve.endCurve = self.ball
                self.curve.length = self.ENGAGE_TIME
                self.curve.start = blue.os.GetSimTime() - long(max(0, self.curve.start + self.ENGAGE_TIME * const.SEC - blue.os.GetSimTime()))
        else:
            if blue.os.GetSimTime() - self.lastCalled > self.RELEASE_TIME * const.SEC and self.curve.endCurve != self.ship:
                if self.curve.endCurve != self.ship:
                    self.curve.startCurve = self.ball
                    self.curve.endCurve = self.ship
                    self.curve.length = self.ENGAGE_TIME
                    self.curve.start = blue.os.GetSimTime() - long(max(0, self.curve.start + self.ENGAGE_TIME * const.SEC - blue.os.GetSimTime()))
            if self.curve.endCurve == self.ship:
                velocity = self.ship.GetVectorDotAt(blue.os.GetSimTime())
                self.ballpark.GotoDirection(self.ball.id, velocity.x, velocity.y, velocity.z)

    def TriggerCallback(self):
        if self.controlling and self.lastCalled + self.throttle < blue.os.GetSimTime():
            self.lastCalled = blue.os.GetSimTime()
            self.callback(self.direction)
            self.controlling = False

    def EnableDebug(self):
        scaling = [(self.ship.radius + 20) * 2, (self.ship.radius + 20) * 2, (self.ship.radius + 20) * 2]
        self.localModel = trinity.EveRootTransform()
        self.localGfx = trinity.Load('res:/model/global/gridSphere.red')
        self.localGfx.scaling = geo2.Vec3Scale(scaling, 1.0)
        self.localModel.name = 'FlightSimulationLocal'
        self.localModel.translationCurve = self.ball
        self.localModel.rotationCurve = self.ball
        self.localModel.children.append(self.localGfx)
        sm.GetService('sceneManager').GetRegisteredScene('default').objects.append(self.localModel)
        self.remoteModel = trinity.EveRootTransform()
        self.remoteGfx = trinity.Load('res:/model/global/gridSphere.red')
        self.remoteGfx.scaling = geo2.Vec3Scale(scaling, 1.5)
        color = self.remoteGfx.mesh.additiveAreas[0].effect.parameters[1].value
        self.remoteGfx.mesh.additiveAreas[0].effect.parameters[1].value = (color[0],
         color[2],
         color[1],
         color[3])
        self.remoteModel.name = 'FlightSimulationRemote'
        self.remoteModel.translationCurve = self.ship
        self.remoteModel.rotationCurve = self.ship
        self.remoteModel.children.append(self.remoteGfx)
        sm.GetService('sceneManager').GetRegisteredScene('default').objects.append(self.remoteModel)
        self.curveModel = trinity.EveRootTransform()
        self.curveGfx = trinity.Load('res:/model/global/gridSphere.red')
        self.curveGfx.scaling = geo2.Vec3Scale(scaling, 1.25)
        color = self.curveGfx.mesh.additiveAreas[0].effect.parameters[1].value
        self.curveGfx.mesh.additiveAreas[0].effect.parameters[1].value = (color[2],
         color[1],
         color[0],
         color[3])
        self.curveModel.name = 'FlightSimulationRemote'
        self.curveModel.translationCurve = self.ball
        self.curveModel.rotationCurve = self.curve
        self.curveModel.children.append(self.curveGfx)
        sm.GetService('sceneManager').GetRegisteredScene('default').objects.append(self.curveModel)

    def DisableDebug(self):
        sm.GetService('sceneManager').GetRegisteredScene('default').objects.fremove(self.localModel)
        self.localModel = None
        sm.GetService('sceneManager').GetRegisteredScene('default').objects.fremove(self.remoteModel)
        self.remoteModel = None
        sm.GetService('sceneManager').GetRegisteredScene('default').objects.fremove(self.curveModel)
        self.curveModel = None

    def ToggleDebug(self):
        if getattr(self, 'localModel', None):
            self.DisableDebug()
        else:
            self.EnableDebug()


class KeyboardControls(object):
    DECAY = 1.2
    ACCEL = 1
    MAX = 1.3

    def __init__(self):
        self.keyUp = []
        self.keyDown = []
        self.keyLeft = []
        self.keyRight = []
        self.Reset()

    def Reset(self):
        self.yaw = 0.0
        self.pitch = 0.0
        self.time = 0

    def PrimeKeys(self):
        self.keyUp = uicore.cmd.GetShortcutByFuncName('CmdFlightControlsUp') or []
        self.keyDown = uicore.cmd.GetShortcutByFuncName('CmdFlightControlsDown') or []
        self.keyLeft = uicore.cmd.GetShortcutByFuncName('CmdFlightControlsLeft') or []
        self.keyRight = uicore.cmd.GetShortcutByFuncName('CmdFlightControlsRight') or []

    def GetYawPitch(self):
        now = blue.os.GetSimTime()
        delta = (now - self.time) / float(const.SEC)
        self.time = now
        if self.yaw > 0:
            self.yaw = max(0, self.yaw - self.DECAY * delta)
        else:
            self.yaw = min(0, self.yaw + self.DECAY * delta)
        if self.pitch > 0:
            self.pitch = max(0, self.pitch - self.DECAY * delta)
        else:
            self.pitch = min(0, self.pitch + self.DECAY * delta)
        if trinity.app.IsActive() and uicore.registry.GetFocus() == uicore.desktop:
            if self.KeysAreDown(self.keyUp):
                self.pitch = max(-self.MAX, self.pitch - (self.ACCEL + self.DECAY) * delta)
            if self.KeysAreDown(self.keyDown):
                self.pitch = min(self.MAX, self.pitch + (self.ACCEL + self.DECAY) * delta)
            if self.KeysAreDown(self.keyRight):
                self.yaw = max(-self.MAX, self.yaw - (self.ACCEL + self.DECAY) * delta)
            if self.KeysAreDown(self.keyLeft):
                self.yaw = min(self.MAX, self.yaw + (self.ACCEL + self.DECAY) * delta)
        return (self.yaw, self.pitch)

    def KeysAreDown(self, mapping):
        if mapping and all([ uicore.uilib.Key(key) for key in mapping ]):
            if all([ not uicore.uilib.Key(key) for key in uiconst.MODKEYS if key not in mapping ]):
                return True
        return False


class FlightControlStatistics(object):

    def __init__(self, controls):
        self.ships = {}
        self.counters = collections.defaultdict(int)
        self.thread = None
        self.controls = controls

    def Start(self):
        if self.thread is None:
            self.thread = uthread.new(self.Update)
            self.thread.context = 'FlightControlStatistics::Update'

    def Stop(self):
        if self.thread is not None:
            self.thread.kill()
            self.thread = None

    def Update(self):
        while True:
            with ExceptionEater('FlightControlStatistics::Update'):
                self.Flush()
                blue.synchro.Sleep(self.GetInterval())

    def GetInterval(self):
        return int(sm.GetService('machoNet').GetGlobalConfig().get('flightControlStatisticsInterval', 300)) * 1000

    def Increment(self):
        self.counters[(session.solarsystemid, session.shipid)] += 1
        self.SaveShip()

    def SaveShip(self):
        with ExceptionEater('FlightControlStatistics::SaveShip'):
            if session.shipid and session.shipid not in self.ships:
                self.ships[session.shipid] = sm.GetService('godma').GetItem(session.shipid).typeID

    def Flush(self):
        for (solarSystemID, shipID), counter in self.counters.iteritems():
            with ExceptionEater('eventLog'):
                if solarSystemID and shipID and counter:
                    sm.ProxySvc('eventLog').LogClientEvent('flightControls', ['solarSystemID',
                     'shipTypeID',
                     'counter',
                     'keyUp',
                     'keyDown',
                     'keyLeft',
                     'keyRight'], 'Counter', solarSystemID, self.ships.get(shipID), counter, '+'.join([ uicore.cmd.GetKeyNameFromVK(key) for key in self.controls.keyUp ]), '+'.join([ uicore.cmd.GetKeyNameFromVK(key) for key in self.controls.keyDown ]), '+'.join([ uicore.cmd.GetKeyNameFromVK(key) for key in self.controls.keyLeft ]), '+'.join([ uicore.cmd.GetKeyNameFromVK(key) for key in self.controls.keyRight ]))

        self.counters.clear()
        self.ships.clear()
