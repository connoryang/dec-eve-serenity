#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\graphics\cylinderLightClient.py
import cef
import graphics
import carbon.client.script.graphics.graphicWrappers.loadAndWrap as graphicWrappers
import trinity
import util

class CylinderLightClientComponent:
    __guid__ = 'component.CylinderLightClientComponent'


class CylinderLightClient(graphics.LightClient):
    __guid__ = 'svc.cylinderLightClient'
    __componentTypes__ = [cef.CylinderLightComponentView.GetComponentCodeName()]

    def CreateComponent(self, name, state):
        component = CylinderLightClientComponent()
        renderObject = trinity.Tr2InteriorCylinderLight()
        component.renderObject = renderObject
        graphicWrappers.Wrap(renderObject)
        component.originalPrimaryLighting = bool(state['primaryLighting'])
        component.performanceLevel = state['performanceLevel']
        renderObject.SetColor((state['red'], state['green'], state['blue']))
        renderObject.SetRadius(state['radius'])
        renderObject.SetLength(state['length'])
        renderObject.SetFalloff(state['falloff'])
        if 'sectorAngleOuter' in state:
            renderObject.sectorAngleOuter = float(state['sectorAngleOuter'])
        if 'sectorAngleInner' in state:
            renderObject.sectorAngleInner = float(state['sectorAngleInner'])
        renderObject.primaryLighting = bool(state['primaryLighting'])
        renderObject.projectedTexturePath = state['projectedTexturePath'].encode()
        renderObject.specularIntensity = float(state.get('specularIntensity', '1'))
        renderObject.useKelvinColor = bool(state['useKelvinColor'])
        if renderObject.useKelvinColor:
            renderObject.kelvinColor.temperature = state['temperature']
            renderObject.kelvinColor.tint = state['tint']
            renderObject.kelvinColor.whiteBalance = int(state['whiteBalance'])
        if '_spawnID' in state:
            component.renderObject.name = self.GetName(state['_spawnID'])
        return component

    def ApplyPerformanceLevelLightDisable(self, entity):
        component = entity.GetComponent('cylinderLight')
        if component is None:
            return
        appPerformanceLevel = sm.GetService('device').GetAppFeatureState('Interior.lightPerformanceLevel', 2)
        if component.performanceLevel > appPerformanceLevel:
            component.renderObject.primaryLighting = False
        else:
            component.renderObject.primaryLighting = component.originalPrimaryLighting
