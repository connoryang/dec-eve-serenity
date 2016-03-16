#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\graphics\loadedLightClient.py
import blue
import cef
import graphics
import trinity
import util

class LoadedLightClientComponent:
    __guid__ = 'component.LoadedLightClientComponent'


class LightClient(graphics.LightClient):
    __guid__ = 'svc.loadedLightClient'
    __componentTypes__ = [cef.LoadedLightComponentView.GetComponentCodeName()]

    def CreateComponent(self, name, state):
        component = LoadedLightClientComponent()
        component.resPath = state['resPath']
        component.renderObject = blue.resMan.LoadObject(component.resPath)
        component.renderObject.name = self.GetName(state['_spawnID'])
        return component
