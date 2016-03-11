#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\billboard.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
import uthread
import sys
import blue

class Billboard(SpaceObject):

    def __init__(self):
        SpaceObject.__init__(self)
        self.bountyTextParam = None
        self.bountyImageParam = None
        self.advertImageParam = None
        self.headlineTextParam = None

    def Assemble(self):
        self.UnSync()
        self.CollectTextureParameters()
        self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        uthread.pool('Billboard::LateAssembleUpdate', self.LateAssembleUpdate)

    def CollectTextureParameters(self):
        for planeSet in self.model.planeSets:
            params = planeSet.Find('trinity.TriTextureParameter')
            if planeSet.name == 'Screen_Advert':
                self.advertImageParam = [ param for param in params if param.name == 'ImageMap' ][0]
            if planeSet.name == 'Screen_Bounty':
                params = planeSet.Find('trinity.TriTextureParameter')
                self.bountyImageParam = [ param for param in params if param.name == 'ImageMap' ][0]
            if planeSet.name == 'Ticker_Headline':
                params = planeSet.Find('trinity.TriTextureParameter')
                self.headlineTextParam = [ param for param in params if param.name == 'Layer2Map' ][0]
            if planeSet.name == 'Ticker_Bounty':
                params = planeSet.Find('trinity.TriTextureParameter')
                self.bountyTextParam = [ param for param in params if param.name == 'Layer2Map' ][0]

    def LateAssembleUpdate(self):
        billboardSvc = self.sm.GetService('billboard')
        billboardSvc.Update(self)

    def SetMap(self, parameter, path, hint):
        if path is None or not blue.paths.exists(path) or parameter is None:
            self.LogWarn('Failed to set', hint, 'billboard texture', parameter, 'to', path)
            return
        self.LogInfo('Setting', hint, 'to', path)
        parameter.resourcePath = path

    def UpdateBillboardContents(self, advertPath, facePath):
        self.LogInfo('UpdateBillboardWithPictureAndText:', advertPath, facePath)
        if self.model is None:
            return
        self.SetMap(self.bountyImageParam, facePath, 'FaceMap')
        self.SetMap(self.advertImageParam, advertPath, 'AdvertMap')
        self.SetMap(self.headlineTextParam, 'cache:/Temp/headlines.dds', 'DiffuseMap')
        self.SetMap(self.bountyTextParam, 'cache:/Temp/bounty_caption.dds', 'DiffuseMap')
