#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\markers\mapMarkerSpaceObjectRadialMenu.py
from eve.client.script.ui.inflight.scannerFiles.directionalScannerWindow import DirectionalScanner
from eve.client.script.ui.shared.radialMenu.radialMenu import RadialMenuSpace
from eve.client.script.ui.shared.radialMenu.radialMenuUtils import SimpleRadialMenuAction

class MapMarkerSpaceObjectRadialMenu(RadialMenuSpace):

    def SetSpecificValues(self, attributes):
        RadialMenuSpace.SetSpecificValues(self, attributes)
        self.markerObject = attributes.markerObject

    def LoadButtons(self, parentLayer, optionsInfo, alternate = False, startingDegree = 0, animate = False, doReset = False):
        if getattr(self, 'busyReloading', False):
            return
        self.busyReloading = True
        try:
            filteredOptions = []
            for each in optionsInfo.allWantedMenuOptions:
                if each.option1Path in ('UI/Inflight/LockTarget', 'UI/Inflight/UnlockTarget'):
                    dScanAction = SimpleRadialMenuAction(option1='UI/Inflight/Scanner/DirectionalScan', alwaysAvailable=True, func=self.DirectionalScan, funcArgs=(self.itemID,))
                    filteredOptions.append(dScanAction)
                    optionsInfo.activeSingleOptions['UI/Inflight/Scanner/DirectionalScan'] = dScanAction
                elif each.option1Path in ('UI/Inflight/OrbitObject', 'UI/Inflight/Submenus/KeepAtRange', 'UI/Inflight/LookAtObject', 'UI/Inflight/ResetCamera'):
                    filteredOptions.append(SimpleRadialMenuAction())
                else:
                    filteredOptions.append(each)

            optionsInfo.allWantedMenuOptions = filteredOptions
            parentLayer.LoadButtons(self.itemID, self.stepSize, alternate, animate, doReset, optionsInfo, startingDegree, self.GetIconTexturePath)
            self.OnGlobalMove()
        finally:
            self.busyReloading = False

    def DirectionalScan(self, itemID, *args, **kwds):
        if itemID:
            markerPosition = self.markerObject.position
            directionalScanner = DirectionalScanner.Open()
            if directionalScanner:
                directionalScanner.ScanTowardsItem(itemID, mapPosition=markerPosition)
