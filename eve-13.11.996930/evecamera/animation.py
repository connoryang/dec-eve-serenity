#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evecamera\animation.py
import evecamera
import blue
import trinutils.callbackmanager as cbmanager
FOV_ANIMATION = 0
PAN_ANIMATION = 1
TRANSLATION_ANIMATION = 2
EXTRA_TRANSLATION_ANIMATION = 3

class BaseCameraAnimation(object):

    def __init__(self, modifier, duration, priority = evecamera.PRIORITY_NORMAL, useWallclock = True):
        self.modifier = modifier
        self.duration = duration
        self.timeStart = 0
        self.priority = priority
        self.useWallclock = useWallclock
        self.isDone = False

    def Start(self, camera, simTime, clockTime):
        if self.useWallclock:
            self.timeStart = clockTime
        else:
            self.timeStart = simTime
        if self.duration == 0.0:
            self.Tick(camera, simTime, clockTime)

    def End(self, camera):
        pass

    def IsDone(self):
        return self.isDone

    def Tick(self, camera, simTime, clockTime):
        if self.isDone:
            return
        if self.useWallclock:
            now = clockTime
        else:
            now = simTime
        elapsed = blue.os.TimeDiffInMs(self.timeStart, now) / 1000.0
        if self.duration == 0.0:
            progress = 1.0
        else:
            progress = max(0.0, min(1.0, elapsed / self.duration))
        self._Tick(progress, camera)
        self.isDone = progress >= 1.0

    def RebaseStartTime(self, offset):
        if not self.useWallclock:
            self.timeStart += offset

    def _Tick(self, progress, camera):
        pass


class AnimationController(object):

    def __init__(self, camera):
        self._camera = camera
        self._animations = AnimationController.GetEmptyAnimationDict()
        cbmanager.CallbackManager.GetGlobal().ScheduleCallback(self.Tick)

    @staticmethod
    def GetEmptyAnimationDict():
        return {FOV_ANIMATION: None,
         PAN_ANIMATION: None,
         TRANSLATION_ANIMATION: None,
         EXTRA_TRANSLATION_ANIMATION: None}

    def _GetTime(self):
        return (blue.os.GetSimTime(), blue.os.GetWallclockTime())

    def _ApplyAnimation(self, animation):
        simTime, clockTime = self._GetTime()
        animation.Start(self._camera, simTime, clockTime)
        if animation.isDone:
            animation.End(self._camera)
            self._animations[animation.modifier] = None
        else:
            self._animations[animation.modifier] = animation

    def ClearAll(self):
        self._animations = AnimationController.GetEmptyAnimationDict()

    def DoSimClockRebase(self, times):
        oldSimTime, newSimTime = times
        offset = newSimTime - oldSimTime
        for each in self._animations.values():
            if each is not None and not each.useWallclock:
                each.RebaseStartTime(offset)

    def Schedule(self, animation):
        mod = animation.modifier
        if self._animations[mod] is None:
            self._ApplyAnimation(animation)
            return
        if self._animations[mod].priority <= animation.priority or self._animations[mod].isDone:
            self._animations[mod].End(self._camera)
            self._ApplyAnimation(animation)

    def Tick(self):
        simTime, clockTime = self._GetTime()
        clearAnimations = []
        for anim in self._animations.values():
            if anim is not None:
                anim.Tick(self._camera, simTime, clockTime)
                if anim.IsDone():
                    clearAnimations.append(anim.modifier)

        for anim in clearAnimations:
            self._animations[anim].End(self._camera)
            self._animations[anim] = None
