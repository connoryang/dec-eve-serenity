#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\graphics\interiorPlaceableClient.py
import cef
import collections
import geo2
import service
import trinity
import util
import uthread
import blue

class InteriorPlaceableClientComponent:
    __guid__ = 'component.InteriorPlaceableClientComponent'


class InteriorPlaceableClient(service.Service):
    __guid__ = 'svc.interiorPlaceableClient'
    __componentTypes__ = [cef.InteriorPlaceableComponentView.GetComponentCodeName()]
    __dependencies__ = ['graphicClient']
    __notifyevents__ = ['OnGraphicSettingsChanged']

    def __init__(self):
        service.Service.__init__(self)
        self.placeableEntities = set()

    def CreateComponent(self, name, state):
        component = InteriorPlaceableClientComponent()
        if 'graphicID' in state:
            component.graphicID = state['graphicID']
        else:
            self.LogError('interiorPlaceable Component requires graphicID in its state')
            component.graphicID = 0
        if 'overrideMetaMaterialPath' in state:
            component.overrideMetaMaterialPath = state['overrideMetaMaterialPath']
        else:
            component.overrideMetaMaterialPath = None
        if 'minSpecOverideMetaMaterialPath' in state:
            component.minSpecOverideMetaMaterialPath = state['minSpecOverideMetaMaterialPath']
        else:
            component.minSpecOverideMetaMaterialPath = None
        if 'probeOffsetX' in state and 'probeOffsetY' in state and 'probeOffsetZ' in state:
            component.probeOffset = (float(state['probeOffsetX']), float(state['probeOffsetY']), float(state['probeOffsetZ']))
        else:
            component.probeOffset = (0, 0, 0)
        component.depthOffset = float(state.get('depthOffset', 0))
        component.scale = util.UnpackStringToTuple(state['scale'])
        return component

    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['graphicID'] = component.graphicID
        if component.renderObject is not None:
            report['Position'] = component.renderObject.GetPosition()
            report['Rotation'] = component.renderObject.GetRotationYawPitchRoll()
        report['minSpecOverideMetaMaterialPath'] = component.minSpecOverideMetaMaterialPath
        report['overrideMetaMaterialPath'] = component.overrideMetaMaterialPath
        return report

    def PrepareComponent(self, sceneID, entityID, component):
        if component.graphicID <= 0:
            component.renderObject = None
            return
        renderObject = trinity.Tr2InteriorPlaceable()
        self._LoadModel(component, renderObject)
        renderObject.isStatic = True
        renderObject.probeOffset = component.probeOffset
        renderObject.depthOffset = component.depthOffset
        renderObject.name = '%s: %s' % (self.graphicClient.GetGraphicName(component.graphicID) or 'BadAsset', entityID)
        component.renderObject = renderObject

    def _LoadModel(self, component, renderObject):
        if component.minSpecOverideMetaMaterialPath is not None and component.minSpecOverideMetaMaterialPath != 'None' and sm.GetService('device').GetAppFeatureState('Interior.lowSpecMaterialsEnabled', False):
            modelFile = component.minSpecOverideMetaMaterialPath
        else:
            modelFile = self.graphicClient.GetModelFilePath(component.graphicID)
        if renderObject.placeableResPath != modelFile:
            renderObject.placeableResPath = modelFile

    def SetupComponent(self, entity, component):
        if not component.renderObject:
            return
        positionComponent = entity.GetComponent('position')
        if positionComponent:
            scale = None
            if not entity.HasComponent('collisionMesh'):
                scale = component.scale
            component.renderObject.transform = util.ConvertTupleToTriMatrix(geo2.MatrixTransformation(None, None, scale, None, positionComponent.rotation, positionComponent.position))
        scene = self.graphicClient.GetScene(entity.scene.sceneID)
        scene.AddDynamic(component.renderObject)

    def RegisterComponent(self, entity, component):
        if not component.renderObject:
            return
        self.placeableEntities.add(entity)

    def UnRegisterComponent(self, entity, component):
        if not component.renderObject:
            return
        self.graphicClient.GetScene(entity.scene.sceneID).RemoveDynamic(component.renderObject)
        self.placeableEntities.remove(entity)

    def OnGraphicSettingsChanged(self, changes):
        for entity in self.placeableEntities:
            uthread.new(self._LoadModel, entity.GetComponent('interiorPlaceable'), entity.GetComponent('interiorPlaceable').renderObject)
