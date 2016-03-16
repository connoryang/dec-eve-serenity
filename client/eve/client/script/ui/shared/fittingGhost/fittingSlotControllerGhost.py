#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\fittingSlotControllerGhost.py
from eve.client.script.ui.shared.fitting.fittingSlotController import ShipFittingSlotController

class ShipFittingSlotControllerGhost(ShipFittingSlotController):

    def GetModule(self):
        if self.IsModulePreviewModule():
            return None
        return self.dogmaModuleItem

    def IsModulePreviewModule(self):
        if not self.dogmaModuleItem:
            return False
        if getattr(self.dogmaModuleItem, 'isPreviewItem', False):
            return True
        return False
