#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\fittingRadialMenu.py
from eve.client.script.ui.shared.radialMenu.radialMenuUtils import SimpleRadialMenuAction, RadialMenuOptionsInfo, RadialMenuSizeInfo
from eve.client.script.ui.inflight.radialMenuShipUI import RadialMenuShipUI
RMO_SizeInfo = RadialMenuSizeInfo(width=220, height=220, shadowSize=256, rangeSize=128, sliceCount=8, buttonWidth=100, buttonHeight=70, buttonPaddingTop=12, buttonPaddingBottom=6, actionDistance=110)

class RadialMenuFitting(RadialMenuShipUI):
    default_width = RMO_SizeInfo.width
    default_height = RMO_SizeInfo.height
    sizeInfo = RMO_SizeInfo
    shadowTexture = 'res:/UI/Texture/classes/RadialMenu/menuShadow2.png'

    def ApplyAttributes(self, attributes):
        self.slotList = attributes.slotList
        RadialMenuShipUI.ApplyAttributes(self, attributes)

    def GetMyActions(self, *args):
        iconOffset = 1
        allWantedMenuOptions = [SimpleRadialMenuAction(option1='UI/Fitting/FittingWindow/RadialMenu/Activate', func=sm.GetService('ghostFittingSvc').ActivateAllHighSlots, funcArgs=(self.slotList,), iconPath='res:/UI/Texture/classes/RadialMenuActions/fitting/active.png', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='UI/Fitting/FittingWindow/RadialMenu/Overheat', func=sm.GetService('ghostFittingSvc').OverheatAllInRack, funcArgs=(self.slotList,), iconPath='res:/UI/Texture/classes/RadialMenuActions/fitting/heat.png', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='', func=None, iconPath='', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='UI/Fitting/FittingWindow/RadialMenu/UnloadModules', func=sm.GetService('ghostFittingSvc').UnfitAllModulesInRack, funcArgs=(self.slotList,), iconPath='res:/UI/Texture/classes/RadialMenuActions/fitting/unload.png', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='UI/Fitting/FittingWindow/RadialMenu/Offline', func=sm.GetService('ghostFittingSvc').OfflineAllInRack, funcArgs=(self.slotList,), iconPath='res:/UI/Texture/classes/RadialMenuActions/fitting/offline.png', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='UI/Fitting/FittingWindow/RadialMenu/UnloadAmmo', func=sm.GetService('ghostFittingSvc').UnfitAllAmmoInRack, funcArgs=(self.slotList,), iconPath='res:/UI/Texture/classes/RadialMenuActions/fitting/unloadAmmo.png', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='', func=None, iconPath='', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='UI/Fitting/FittingWindow/RadialMenu/Online', func=sm.GetService('ghostFittingSvc').OnlineAllInRack, funcArgs=(self.slotList,), iconPath='res:/UI/Texture/classes/RadialMenuActions/fitting/online.png', iconOffset=iconOffset)]
        activeSingleOptions = {menuAction.option1Path:menuAction for menuAction in allWantedMenuOptions if menuAction.option1Path}
        optionsInfo = RadialMenuOptionsInfo(allWantedMenuOptions=allWantedMenuOptions, activeSingleOptions=activeSingleOptions)
        return optionsInfo
