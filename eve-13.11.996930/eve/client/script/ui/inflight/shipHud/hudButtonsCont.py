#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\hudButtonsCont.py
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.camera.cameraUtil import IsNewCameraActive
from eve.client.script.ui.inflight.shipHud.leftSideButton import LeftSideButtonCamera, LeftSideButtonCargo, LeftSideButtonScanner, LeftSideButtonTactical, LeftSideButtonAutopilot, LeftSideButtonZoomIn, LeftSideButtonZoomOut, LeftSideButtonCameraOrbit, LeftSideButtonCameraTactical, LeftSideButtonCameraPOV
import telemetry
LEFT_COL = 0
RIGHT_COL = 28
HEIGHT = 16

class HudButtonsCont(ContainerAutoSize):
    default_name = 'HudButtonsCont'
    isAutoSizeEnabled = False

    @telemetry.ZONE_METHOD
    def InitButtons(self):
        self.Flush()
        if IsNewCameraActive():
            LeftSideButtonCargo(parent=self, left=LEFT_COL, top=0)
            LeftSideButtonTactical(parent=self, left=LEFT_COL, top=2 * HEIGHT)
            LeftSideButtonScanner(parent=self, left=LEFT_COL, top=4 * HEIGHT)
            LeftSideButtonAutopilot(parent=self, left=LEFT_COL, top=6 * HEIGHT)
            LeftSideButtonCameraTactical(parent=self, left=RIGHT_COL, top=HEIGHT)
            LeftSideButtonCameraOrbit(parent=self, left=RIGHT_COL, top=3 * HEIGHT)
            LeftSideButtonCameraPOV(parent=self, left=RIGHT_COL, top=5 * HEIGHT)
        else:
            LeftSideButtonCargo(parent=self, left=RIGHT_COL, top=0)
            LeftSideButtonCamera(parent=self, left=LEFT_COL, top=48)
            LeftSideButtonScanner(parent=self, left=RIGHT_COL, top=32)
            LeftSideButtonTactical(parent=self, left=LEFT_COL, top=16)
            LeftSideButtonAutopilot(parent=self, left=RIGHT_COL, top=64)
            showZoomBtns = settings.user.ui.Get('showZoomBtns', 0)
            if showZoomBtns:
                LeftSideButtonZoomIn(parent=self, left=LEFT_COL, top=80)
                LeftSideButtonZoomOut(parent=self, left=RIGHT_COL, top=96)
        self.EnableAutoSize()
        self.DisableAutoSize()
