#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\cameraTool.py
from eve.client.script.ui.camera.cameraUtil import SetNewCameraActive, SetNewCameraInactive
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveWindow import Window
import carbonui.const as uiconst
import evecamera
import uthread
import blue

class CameraTool(Window):
    default_caption = ('Camera Tool',)
    default_windowID = 'CameraToolID'
    default_width = 250
    default_height = 150
    default_topParentHeight = 0
    default_minSize = (250, 150)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        Button(parent=self.sr.main, align=uiconst.TOTOP, label='Toggle New/Old camera', func=self.ReloadCamera)
        self.atLabel = Label(parent=self.sr.main, align=uiconst.TOTOP)
        uthread.new(self.Update)

    def Update(self):
        while not self.destroyed:
            cam = sm.GetService('sceneManager').GetActiveCamera()
            text = '_atPosition: %2.2f, %2.2f, %2.2f' % cam._atPosition
            atOffset = cam._atOffset or (0, 0, 0)
            text += '\n_atOffset: %2.2f, %2.2f, %2.2f' % atOffset
            text += '\n_eyePosition: %2.2f, %2.2f, %2.2f' % cam._eyePosition
            eyeOffset = cam._eyeOffset or (0, 0, 0)
            text += '\n_eyeOffset: %2.2f, %2.2f, %2.2f' % eyeOffset
            eyeAndAtOffset = cam._eyeAndAtOffset or (0, 0, 0)
            text += '\n_eyeAndAtOffset: %2.2f, %2.2f, %2.2f' % eyeAndAtOffset
            self.atLabel.text = text
            blue.synchro.Yield()

    def ReloadCamera(self, *args):
        sceneMan = sm.GetService('sceneManager')
        camera = sceneMan.GetActiveCamera()
        if camera.cameraID == evecamera.CAM_SPACE_PRIMARY:
            sceneMan.SetActiveCameraByID(evecamera.CAM_SHIPORBIT)
            SetNewCameraActive()
        else:
            sceneMan.SetActiveCameraByID(evecamera.CAM_SPACE_PRIMARY)
            for cameraID in (evecamera.CAM_SHIPORBIT, evecamera.CAM_SHIPPOV, evecamera.CAM_TACTICAL):
                sceneMan.UnregisterCamera(cameraID)

            SetNewCameraInactive()
        if session.stationid is None:
            uicore.layer.shipui.CloseView()
            uicore.layer.shipui.OpenView()
