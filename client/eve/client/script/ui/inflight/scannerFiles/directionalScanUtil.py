#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\scannerFiles\directionalScanUtil.py
SCANMODE_TARGET = 1
SCANMODE_CAMERA = 2

def SetActiveScanMode(scanMode):
    if GetActiveScanMode() != scanMode:
        settings.char.ui.Set('directionalScannerMode', scanMode)
        sm.ScatterEvent('OnDirectionalScannerScanModeChanged', scanMode)


def GetActiveScanMode():
    return settings.char.ui.Get('directionalScannerMode', SCANMODE_TARGET)


def ToggleScanMode():
    scanMode = GetActiveScanMode()
    if scanMode == SCANMODE_TARGET:
        SetActiveScanMode(SCANMODE_CAMERA)
    else:
        SetActiveScanMode(SCANMODE_TARGET)


def SetScanConeDisplayState(displayState):
    if GetScanConeDisplayState() != displayState:
        settings.char.ui.Set('directionalScannerShowCone', displayState)
        sm.ScatterEvent('OnDirectionalScannerShowCone', displayState)


def GetScanConeDisplayState():
    return settings.char.ui.Get('directionalScannerShowCone', True)
