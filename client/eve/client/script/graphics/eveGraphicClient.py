#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\graphics\eveGraphicClient.py
import blue
import svc
from sceneManager import SCENE_TYPE_INTERIOR

class EveGraphicClient(svc.graphicClient):
    __guid__ = 'svc.eveGraphicClient'
    __replaceservice__ = 'graphicClient'
    __dependencies__ = svc.graphicClient.__dependencies__[:]

    def _AppSetRenderingScene(self, scene):
        sceneManager = sm.GetService('sceneManager')
        sceneManager.SetSceneType(SCENE_TYPE_INTERIOR)
        sceneManager.SetActiveScene(scene)
