#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\cameraBase.py
import blue
import math
import trinity
import geo2
import uthread2

class CameraBase(object):

    def __init__(self):
        self._camera = trinity.EveCamera()
        self._CreateErrorHandler()
        self.cameraParent = None
        self.cameraInterestID = None
        self.cameraInterest = None

    def GetTrinityCamera(self):
        return self._camera

    def LookingAt(self):
        pass

    def ResetCamera(self):
        pass

    def _ErrorListener(self, *args):

        def _threaded():
            lookat = self.LookingAt()
            ball = sm.GetService('michelle').GetBall(lookat)
            model = getattr(ball, 'model', None)
            if model is None:
                exceptionMessage = 'EveCamera: Lookat model is none. '
                exceptionMessage += str(lookat) + '/' + str(session.shipid)
                raise Exception(exceptionMessage)
            exceptionMessage = 'EveCamera: \n'
            exceptionMessage += 'Lookat: ' + str(lookat) + '/' + str(session.shipid) + '\n'
            exceptionMessage += 'WorldPos: ' + str(model.modelWorldPosition) + '\n'
            exceptionMessage += 'Curves: ' + str(model.translationCurve.GetVectorAt(blue.os.GetSimTime())) + ' / '
            exceptionMessage += str(model.rotationCurve.GetQuaternionAt(blue.os.GetSimTime())) + '\n'
            if hasattr(model.rotationCurve, 'startCurve'):
                startCurve = model.rotationCurve.startCurve
                exceptionMessage += 'Is wasd ball\n'
                exceptionMessage += 'start' + str(startCurve.GetVectorAt(blue.os.GetSimTime())) + ' / '
                exceptionMessage += str(startCurve.GetQuaternionAt(blue.os.GetSimTime())) + '\n'
                endCurve = model.rotationCurve.endCurve
                exceptionMessage += 'end' + str(endCurve.GetVectorAt(blue.os.GetSimTime())) + ' / '
                exceptionMessage += str(endCurve.GetQuaternionAt(blue.os.GetSimTime())) + '\n'
            self.ResetCamera()
            raise Exception(exceptionMessage)

        uthread2.StartTasklet(_threaded)

    def _CreateErrorHandler(self):
        eventHandler = blue.BlueEventToPython()
        eventHandler.handler = self._ErrorListener
        self.errorHandler = eventHandler

    def Dolly(self, *args, **kw):
        return self._camera.Dolly(*args, **kw)

    def OrbitParent(self, *args, **kw):
        return self._camera.OrbitParent(*args, **kw)

    def RotateOnOrbit(self, *args, **kw):
        return self._camera.RotateOnOrbit(*args, **kw)

    def SetOrbit(self, *args, **kw):
        return self._camera.SetOrbit(*args, **kw)

    def SetRotationOnOrbit(self, *args, **kw):
        return self._camera.SetRotationOnOrbit(*args, **kw)

    def Zoom(self, *args, **kw):
        return self._camera.Zoom(*args, **kw)

    def GetYaw(self):
        rot = geo2.QuaternionRotationGetYawPitchRoll(self.rotationAroundParent)
        look = geo2.QuaternionRotationGetYawPitchRoll(self.rotationOfInterest)
        yaw = rot[0] + look[0] - math.pi
        return yaw

    @property
    def alignment(self):
        return self._camera.alignment

    @alignment.setter
    def alignment(self, value):
        self._camera.alignment = value

    @property
    def audio2Listener(self):
        return self._camera.audio2Listener

    @audio2Listener.setter
    def audio2Listener(self, value):
        self._camera.audio2Listener = value

    @property
    def backClip(self):
        return self._camera.backClip

    @backClip.setter
    def backClip(self, value):
        self._camera.backClip = value

    @property
    def centerOffset(self):
        return self._camera.centerOffset

    @centerOffset.setter
    def centerOffset(self, value):
        self._camera.centerOffset = value

    @property
    def errorHandler(self):
        return self._camera.errorHandler

    @errorHandler.setter
    def errorHandler(self, value):
        self._camera.errorHandler = value

    @property
    def extraTranslation(self):
        return self._camera.extraTranslation

    @extraTranslation.setter
    def extraTranslation(self, value):
        self._camera.extraTranslation = value

    @property
    def fieldOfView(self):
        return self._camera.fieldOfView

    @fieldOfView.setter
    def fieldOfView(self, value):
        self._camera.fieldOfView = value

    @property
    def fov(self):
        return self._camera.fieldOfView

    @fov.setter
    def fov(self, value):
        self._camera.fieldOfView = value

    @property
    def friction(self):
        return self._camera.friction

    @friction.setter
    def friction(self, value):
        self._camera.friction = value

    @property
    def frontClip(self):
        return self._camera.frontClip

    @frontClip.setter
    def frontClip(self, value):
        self._camera.frontClip = value

    @property
    def idleMove(self):
        return self._camera.idleMove

    @idleMove.setter
    def idleMove(self, value):
        self._camera.idleMove = value

    @property
    def idleScale(self):
        return self._camera.idleScale

    @idleScale.setter
    def idleScale(self, value):
        self._camera.idleScale = value

    @property
    def idleSpeed(self):
        return self._camera.idleSpeed

    @idleSpeed.setter
    def idleSpeed(self, value):
        self._camera.idleSpeed = value

    @property
    def interest(self):
        return self._camera.interest

    @interest.setter
    def interest(self, value):
        self._camera.interest = value

    @property
    def intr(self):
        return self._camera.intr

    @intr.setter
    def intr(self, value):
        self._camera.intr = value

    @property
    def maxPitch(self):
        return self._camera.maxPitch

    @maxPitch.setter
    def maxPitch(self, value):
        self._camera.maxPitch = value

    @property
    def maxSpeed(self):
        return self._camera.maxSpeed

    @maxSpeed.setter
    def maxSpeed(self, value):
        self._camera.maxSpeed = value

    @property
    def maxYaw(self):
        return self._camera.maxYaw

    @maxYaw.setter
    def maxYaw(self, value):
        self._camera.maxYaw = value

    @property
    def minPitch(self):
        return self._camera.minPitch

    @minPitch.setter
    def minPitch(self, value):
        self._camera.minPitch = value

    @property
    def minYaw(self):
        return self._camera.minYaw

    @minYaw.setter
    def minYaw(self, value):
        self._camera.minYaw = value

    @property
    def noise(self):
        return self._camera.noise

    @noise.setter
    def noise(self, value):
        self._camera.noise = value

    @property
    def noiseCurve(self):
        return self._camera.noiseCurve

    @noiseCurve.setter
    def noiseCurve(self, value):
        self._camera.noiseCurve = value

    @property
    def noiseDamp(self):
        return self._camera.noiseDamp

    @noiseDamp.setter
    def noiseDamp(self, value):
        self._camera.noiseDamp = value

    @property
    def noiseDampCurve(self):
        return self._camera.noiseDampCurve

    @noiseDampCurve.setter
    def noiseDampCurve(self, value):
        self._camera.noiseDampCurve = value

    @property
    def noiseScale(self):
        return self._camera.noiseScale

    @noiseScale.setter
    def noiseScale(self, value):
        self._camera.noiseScale = value

    @property
    def noiseScaleCurve(self):
        return self._camera.noiseScaleCurve

    @noiseScaleCurve.setter
    def noiseScaleCurve(self, value):
        self._camera.noiseScaleCurve = value

    @property
    def parent(self):
        return self._camera.parent

    @parent.setter
    def parent(self, value):
        self._camera.parent = value

    @property
    def pitch(self):
        return self._camera.pitch

    @pitch.setter
    def pitch(self, value):
        self._camera.pitch = value

    @property
    def pos(self):
        return self._camera.pos

    @pos.setter
    def pos(self, value):
        self._camera.pos = value

    @property
    def eyePosition(self):
        return self._camera.pos

    @property
    def projectionMatrix(self):
        return self._camera.projectionMatrix

    @projectionMatrix.setter
    def projectionMatrix(self, value):
        self._camera.projectionMatrix = value

    @property
    def rightVec(self):
        return self._camera.rightVec

    @rightVec.setter
    def rightVec(self, value):
        self._camera.rightVec = value

    @property
    def rotationAroundParent(self):
        return self._camera.rotationAroundParent

    @rotationAroundParent.setter
    def rotationAroundParent(self, value):
        self._camera.rotationAroundParent = value

    def GetRotationQuat(self):
        return self.rotationAroundParent

    @property
    def rotationOfInterest(self):
        return self._camera.rotationOfInterest

    @rotationOfInterest.setter
    def rotationOfInterest(self, value):
        self._camera.rotationOfInterest = value

    @property
    def translationFromParent(self):
        return self._camera.translationFromParent

    @translationFromParent.setter
    def translationFromParent(self, value):
        self._camera.translationFromParent = value

    @property
    def upVec(self):
        return self._camera.upVec

    @upVec.setter
    def upVec(self, value):
        self._camera.upVec = value

    def GetYAxis(self):
        return self.upVec

    def GetXAxis(self):
        return self.rightVec

    @property
    def update(self):
        return self._camera.update

    @update.setter
    def update(self, value):
        self._camera.update = value

    @property
    def useExtraTranslation(self):
        return self._camera.useExtraTranslation

    @useExtraTranslation.setter
    def useExtraTranslation(self, value):
        self._camera.useExtraTranslation = value

    @property
    def viewMatrix(self):
        return self._camera.viewMatrix

    @viewMatrix.setter
    def viewMatrix(self, value):
        self._camera.viewMatrix = value

    @property
    def viewVec(self):
        return self._camera.viewVec

    @viewVec.setter
    def viewVec(self, value):
        self._camera.viewVec = value

    def GetLookAtDirection(self):
        return self.viewVec

    @property
    def yaw(self):
        return self._camera.yaw

    @yaw.setter
    def yaw(self, value):
        self._camera.yaw = value

    @property
    def zoomCurve(self):
        return self._camera.zoomCurve

    @zoomCurve.setter
    def zoomCurve(self, value):
        self._camera.zoomCurve = value
