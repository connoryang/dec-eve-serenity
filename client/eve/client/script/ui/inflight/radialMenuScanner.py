#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\radialMenuScanner.py
import blue
from eve.client.script.ui.shared.radialMenu.radialMenuUtils import SimpleRadialMenuAction, RadialMenuOptionsInfo
from eve.client.script.ui.inflight.radialMenuShipUI import RadialMenuShipUI
import carbonui.const as uiconst
from eve.client.script.ui.shared.systemMenu.betaOptions import IsBetaScannersEnabled

def OpenProbeScanner():
    if IsBetaScannersEnabled():
        from eve.client.script.ui.inflight.probeScannerWindow import ProbeScannerWindow
        ProbeScannerWindow.Open()
    else:
        from eve.client.script.ui.inflight.scanner import Scanner
        Scanner.Open()


def OpenDirectionalScanner():
    if IsBetaScannersEnabled():
        from eve.client.script.ui.inflight.scannerFiles.directionalScannerWindow import DirectionalScanner
        DirectionalScanner.Open()
    else:
        from eve.client.script.ui.inflight.scannerFiles.directionalScanner import DirectionalScanner
        DirectionalScanner.Open()


def OpenMoonScanner():
    from eve.client.script.ui.inflight.scannerFiles.moonScanner import MoonScanner
    MoonScanner.Open()


class RadialMenuScanner(RadialMenuShipUI):

    def ApplyAttributes(self, attributes):
        RadialMenuShipUI.ApplyAttributes(self, attributes)

    def GetMyActions(self, *args):
        iconOffset = 1
        allWantedMenuOptions = [SimpleRadialMenuAction(option1='UI/Inflight/Scanner/MoonAnalysis', func=OpenMoonScanner, iconPath='res:/UI/Texture/Icons/moonscan.png', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='UI/Inflight/Scanner/DirectionalScan', func=OpenDirectionalScanner, iconPath='res:/UI/Texture/Icons/d-scan.png', iconOffset=iconOffset, commandName='OpenDirectionalScanner'),
         SimpleRadialMenuAction(option1='', func=None, iconPath='', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='UI/Inflight/Scanner/ProbeScanner', func=OpenProbeScanner, iconPath='res:/UI/Texture/Icons/probe_scan.png', iconOffset=iconOffset, commandName='OpenScanner')]
        activeSingleOptions = {menuAction.option1Path:menuAction for menuAction in allWantedMenuOptions if menuAction.option1Path}
        optionsInfo = RadialMenuOptionsInfo(allWantedMenuOptions=allWantedMenuOptions, activeSingleOptions=activeSingleOptions)
        return optionsInfo
