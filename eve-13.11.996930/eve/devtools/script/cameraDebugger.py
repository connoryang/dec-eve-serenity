#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\cameraDebugger.py
from carbonui.util.color import Color
import trinity
import geo2
import blue
import uthread
COLOR_UPDIR = Color.BLUE
COLOR_LOOKDIR = Color.GREEN

class CameraDebugger(object):

    def __init__(self, camera):
        self.isEnabled = True
        self.ConstructLineSet()
        self.updateThread = None
        self.camera = camera
        uthread.new(self.UpdateThread)

    def ConstructLineSet(self):
        self.lineSet = trinity.EveCurveLineSet()
        self.lineSet.additive = True
        tex2D = trinity.TriTextureParameter()
        tex2D.name = 'TexMap'
        tex2D.resourcePath = 'res:/dx9/texture/UI/lineSolid.dds'
        self.lineSet.lineEffect.resources.append(tex2D)
        sm.GetService('sceneManager').GetActiveScene().objects.append(self.lineSet)

    def Enable(self):
        self.isEnabled = True

    def Disable(self):
        self.isEnabled = False

    def UpdateThread(self):
        while self.camera:
            if self.isEnabled and self.camera:
                self.Update()
            blue.synchro.Yield()

    def Close(self):
        self.camera = None
        sm.GetService('sceneManager').GetActiveScene().objects.fremove(self.lineSet)
        self.lineSet = None

    def Update(self):
        self.lineSet.ClearLines()
        atPosition = self.camera.atPosition
        self.lineSet.AddStraightLine(self.camera.eyePosition, COLOR_LOOKDIR, atPosition, COLOR_LOOKDIR, 5.0)
        upVec = geo2.Vec3Add(self.camera.eyePosition, geo2.Vec3Scale(self.camera.upDirection, 100.0))
        self.lineSet.AddStraightLine(self.camera.eyePosition, COLOR_UPDIR, upVec, COLOR_UPDIR, 5.0)
        self.lineSet.SubmitChanges()
