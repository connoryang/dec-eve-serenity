#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\MicroJumpDrive.py
from eve.client.script.environment.effects.GenericEffect import GenericEffect, ShipEffect, STOP_REASON_BALL_REMOVED, STOP_REASON_DEFAULT
import trinity
import blue
import uthread
SECOND = 1000
CAMERA_RESET_TIME = 1500
MICRO_JUMP_DRIVE_GRAPHIC_ID = 21232
MICRO_JUMP_FIELD_GRAPHIC_ID = 21235
MICROJUMPDRIVE_SOUND_EVENTS = {MICRO_JUMP_DRIVE_GRAPHIC_ID: 'microjumpdrive_jump_play',
 MICRO_JUMP_FIELD_GRAPHIC_ID: 'ship_effect_microjump_fieldgenerator_jump_play'}

class MicroJumpDriveEngage(ShipEffect):
    __guid__ = 'effects.MicroJumpDriveEngage'

    def __init__(self, trigger, *args):
        ShipEffect.__init__(self, trigger, *args)
        self.playerEffect = None
        self.graphicID = None if args[0] is None else getattr(args[0], 'graphicID', None)

    def Prepare(self):
        ShipEffect.Prepare(self, False)
        if session.shipid == self.GetEffectShipID():
            self.playerEffect = self.RecycleOrLoad(self.secondaryGraphicFile)
            self.AddSoundToEffect(2)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if reason == STOP_REASON_BALL_REMOVED:
            ShipEffect.Stop(self, reason)

    def _DelayedStop(self, delay):
        blue.synchro.SleepSim(delay)
        if self.playerEffect is not None:
            self.RemoveFromScene(self.playerEffect)
            self.playerEffect = None
        if self.gfx is not None:
            ShipEffect.Stop(self)

    def Start(self, duration):
        if self.gfx is None:
            raise RuntimeError('MicroJumpDriveEngage: no effect defined:' + self.__guid__)
        self.curveSets = self.gfx.curveSets
        self.controllerCurve = None
        length = 0
        for each in self.gfx.curveSets:
            length = max(each.GetMaxCurveDuration() * 1000, length)
            each.Play()
            if each.name == 'PLAY_START':
                self.controllerCurve = each.curves[0]

        self.AddToScene(self.gfxModel)
        if self.playerEffect is None:
            self._SetCurveTime(duration * 0.001)
        else:
            self._SetCurveTime(duration * 0.001 - 0.25)
            length = 0
            for each in self.playerEffect.curveSets:
                length = max(each.GetMaxCurveDuration() * 1000, length)
                each.Stop()

            triggerDelayPlayer = duration - length
            uthread.new(self._TriggerPlaybackPlayer, triggerDelayPlayer)
        uthread.new(self._DelayedStop, duration + 2 * SECOND)

    def _SetCurveTime(self, duration):
        lastKey = self.controllerCurve.GetKeyCount() - 1
        timeDelta = self.controllerCurve.length - self.controllerCurve.GetKeyTime(lastKey)
        self.controllerCurve.length = duration
        self.controllerCurve.SetKeyTime(lastKey, duration - timeDelta)
        self.controllerCurve.Sort()

    def _TriggerPlaybackPlayer(self, delay):
        blue.synchro.SleepSim(delay - CAMERA_RESET_TIME)
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if cam.GetLookAtItemID() != session.shipid:
            cam.LookAt(session.shipid)
        blue.synchro.SleepSim(CAMERA_RESET_TIME)
        self.AddToScene(self.playerEffect)
        for each in self.playerEffect.curveSets:
            each.Play()

        soundEvent = MICROJUMPDRIVE_SOUND_EVENTS.get(self.graphicID, None)
        if soundEvent is not None:
            sm.GetService('audio').SendUIEvent(soundEvent)


class MicroJumpDriveJump(GenericEffect):
    __guid__ = 'effects.MicroJumpDriveJump'

    def __init__(self, trigger, *args):
        GenericEffect.__init__(self, trigger, *args)
        self.position = trigger.graphicInfo
        self.gfxModel = None

    def Prepare(self):
        self.ball = self._SpawnClientBall(self.position)
        gfx = self.RecycleOrLoad(self.graphicFile)
        if gfx is None:
            return
        model = getattr(self.GetEffectShipBall(), 'model', None)
        if model is None:
            return
        radius = model.GetBoundingSphereRadius()
        gfx.scaling = (radius, radius, radius)
        self.gfxModel = trinity.EveRootTransform()
        self.gfxModel.children.append(gfx)
        self.gfxModel.boundingSphereRadius = radius
        self.gfxModel.translationCurve = self.ball
        self.sourceObject = self.gfxModel
        self.gfx = gfx
        self.AddSoundToEffect(2)

    def Start(self, duration):
        if self.gfxModel is not None:
            self.AddToScene(self.gfxModel)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        self._DestroyClientBall(self.ball)
        self.ball = None
        self.sourceObject = None
        self.gfx = None
        if self.gfxModel is not None:
            self.RemoveFromScene(self.gfxModel)
            self.gfxModel.translationCurve = None
            self.gfxModel = None
