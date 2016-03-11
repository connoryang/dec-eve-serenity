#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\controllerGhostFittingExtension.py


class FittingControllerGhostFittingExtension(object):

    def __init__(self):
        pass

    def GetScenePath(self):
        return 'res:/dx9/scene/fitting/previewAmmo.red'

    def GetDogmaLocation(self):
        return sm.GetService('clientDogmaIM').GetFittingDogmaLocation()

    def GhostFitItem(self, item):
        if item:
            dogmaItem = sm.GetService('ghostFittingSvc').TryFitModuleToOneSlot(item.typeID)
            if dogmaItem:
                dogmaItem.isPreviewItem = True
        else:
            dogmaItem = None
        return dogmaItem

    def UnFitItem(self, ghostItem):
        if ghostItem:
            sm.GetService('ghostFittingSvc').UnfitModule(ghostItem.itemID)
