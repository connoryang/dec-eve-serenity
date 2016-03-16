#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\graphics\graphicClient.py
import service
import carbon.client.script.graphics.graphicWrappers.loadAndWrap as graphicWrappers
import trinity

class GraphicClient(service.Service):
    __guid__ = 'svc.graphicClient'
    __dependencies__ = ['worldSpaceClient']

    def __init__(self):
        service.Service.__init__(self)
        self.isServiceReady = False
        self.scenes = {}

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.isServiceReady = True

    def OnLoadEntityScene(self, sceneID):
        worldSpaceTypeID = self.worldSpaceClient.GetWorldSpaceTypeIDFromWorldSpaceID(sceneID)
        worldSpaceRow = cfg.worldspaces.Get(worldSpaceTypeID)
        if worldSpaceRow.isInterior:
            sceneType = const.world.INTERIOR_SCENE
        else:
            sceneType = const.world.EXTERIOR_SCENE
        self.CreateScene(sceneID, sceneType)
        if sceneID == session.worldspaceid or session.worldspaceid == 0:
            self._AppSetRenderingScene(self.scenes[sceneID])

    def _AppSetRenderingScene(self, scene):
        raise NotImplementedError('Game specific versions of graphicClient must implement _AppSetRenderingScene')

    def OnEntitySceneUnloaded(self, sceneID):
        self.DestroyScene(sceneID)

    def CreateScene(self, sceneID, sceneType):
        if sceneID in self.scenes:
            raise RuntimeError('Trinity Scene Already Exists %d' % sceneID)
        if sceneType == const.world.INTERIOR_SCENE:
            self.scenes[sceneID] = trinity.Tr2InteriorScene()
        else:
            raise RuntimeError('Trying to create a nonexistent type of scene')
        graphicWrappers.Wrap(self.scenes[sceneID], convertSceneType=False)
        if hasattr(self.scenes[sceneID], 'SetID'):
            worldSpaceTypeID = self.worldSpaceClient.GetWorldSpaceTypeIDFromWorldSpaceID(sceneID)
            self.scenes[sceneID].SetID(worldSpaceTypeID)

    def DestroyScene(self, sceneID):
        del self.scenes[sceneID]

    def GetScene(self, sceneID):
        if sceneID in self.scenes:
            return self.scenes[sceneID]
        else:
            return None

    def GetModelFilePath(self, graphicID):
        if graphicID in cfg.graphics:
            return cfg.graphics.Get(graphicID).graphicFile

    def GetGraphicName(self, graphicID):
        graphicFile = self.GetModelFilePath(graphicID)
        if graphicFile:
            return graphicFile[graphicFile.rfind('/') + 1:graphicFile.rfind('.')]

    def GetIsServiceReady(self):
        return self.isServiceReady
