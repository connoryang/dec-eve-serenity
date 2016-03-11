#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\sovereigntyClaimMarker.py
import eve.client.script.environment.nodemanager as nodemanager
from eve.client.script.environment.spaceObject.LargeCollidableStructure import LargeCollidableStructure
ANIMATION_OFFLINE = 'Offline'
ANIMATION_ONLINING = 'Onlining'
ANIMATION_ONLINE = 'Online'

class SovereigntyClaimMarker(LargeCollidableStructure):
    __notifyevents__ = ['OnAllianceLogoReady']

    def __init__(self):
        LargeCollidableStructure.__init__(self)
        sm.RegisterNotify(self)

    def LoadModel(self, fileName = None, loadedModel = None):
        LargeCollidableStructure.LoadModel(self)
        animationState = self._GetAnimationState()
        self.TriggerAnimation(animationState)
        self._LoadAllianceLogo()

    def OnSlimItemUpdated(self, slimItem):
        oldAllianceID = self._GetAllianceID()
        self.typeData['slimItem'] = slimItem
        newAllianceID = self._GetAllianceID()
        if oldAllianceID != newAllianceID:
            animationState = self._GetAnimationState()
            self.TriggerAnimation(animationState)
            self._LoadAllianceLogo()

    def OnAllianceLogoReady(self, allianceID):
        if self.ballpark is None or self.id not in self.ballpark.slimItems:
            return
        if self.model is None:
            return
        if allianceID == self._GetAllianceID():
            iconPath = self.sm.GetService('photo').GetAllianceLogo(allianceID, 128, orderIfMissing=False)
            if iconPath is not None:
                self._ApplyAllianceLogo(iconPath)

    def _GetAllianceID(self):
        slimItem = self.typeData['slimItem']
        return getattr(slimItem, 'allianceID', None)

    def _GetAnimationState(self):
        allianceID = self._GetAllianceID()
        if allianceID is not None:
            return ANIMATION_ONLINE
        else:
            return ANIMATION_OFFLINE

    def _LoadAllianceLogo(self):
        if self.ballpark is None or self.id not in self.ballpark.slimItems:
            return
        allianceID = self._GetAllianceID()
        if allianceID is None:
            iconPath = ''
        else:
            iconPath = self.sm.GetService('photo').GetAllianceLogo(allianceID, 128, callback=True)
        if iconPath is not None:
            self._ApplyAllianceLogo(iconPath)

    def _ApplyAllianceLogo(self, iconPath):
        screenNode = nodemanager.FindNode(self.model.planeSets, 'Hologram', 'trinity.EvePlaneSet')
        for res in screenNode.effect.resources:
            if res.name == 'ImageMap':
                res.resourcePath = iconPath
