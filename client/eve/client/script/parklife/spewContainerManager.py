#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\spewContainerManager.py


class SpewContainerManager(object):
    __guid__ = 'spewContainerManager.SpewContainerManager'
    __notifyevents__ = ['OnSlimItemChange']

    def __init__(self, park):
        self.ballpark = park
        sm.RegisterNotify(self)

    def OnSlimItemChange(self, oldSlim, newSlim):
        slimItem = newSlim
        itemID = newSlim.itemID
        if slimItem.groupID in (const.groupSpewContainer, const.groupSpawnContainer) and slimItem.hackingSecurityState is not None:
            sm.GetService('invCache').InvalidateLocationCache(itemID)
            self.OnSpewSecurityStateChange(itemID, slimItem.hackingSecurityState)

    def GetSpewContainer(self, spewContainerID):
        spewContainer = None
        if self.ballpark:
            spewContainer = self.ballpark.GetBall(spewContainerID)
        return spewContainer

    def OnSpewSecurityStateChange(self, spewContainerID, securityState):
        spewContainer = self.GetSpewContainer(spewContainerID)
        if spewContainer:
            try:
                spewContainer.SetSecurityState(securityState)
            except AttributeError:
                pass
