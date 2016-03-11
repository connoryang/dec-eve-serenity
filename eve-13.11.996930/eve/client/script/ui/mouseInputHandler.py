#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\mouseInputHandler.py


class MouseInputHandler(object):
    __notifyevents__ = ['OnCameraZoomModifierChanged']

    def __init__(self):
        self.SetZoomModifier()
        sm.RegisterNotify(self)

    def GetCameraZoomModifier(self):
        return self.cameraZoomModifier

    def OnCameraZoomModifierChanged(self):
        self.SetZoomModifier()

    def SetZoomModifier(self):
        invertCameraZoom = settings.user.ui.Get('invertCameraZoom', False)
        if invertCameraZoom:
            self.cameraZoomModifier = -1
        else:
            self.cameraZoomModifier = 1
