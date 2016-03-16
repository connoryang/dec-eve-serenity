#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\entities\inputComponents.py


class ContextMenuComponent:
    __guid__ = 'entities.ContextMenuComponent'

    def __init__(self):
        self.menuEntries = {}

    def AddMenuEntry(self, label, callback):
        self.menuEntries[label] = callback
