#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\billboards\spacecomponents\client\billboard.py
from billboards import get_billboard_system
from spacecomponents.client.messages import MSG_ON_REMOVED_FROM_SPACE, MSG_ON_LOAD_OBJECT
from spacecomponents.common.components.component import Component
import logging
logger = logging.getLogger(__name__)

class BillboardComponent(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_LOAD_OBJECT, self.OnLoadObject)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)

    def OnLoadObject(self, ball):
        self.RegisterDynamicResource(ball)
        self.UpdateTickers(ball)

    def OnRemovedFromSpace(self):
        self.UnregisterDynamicResource()

    def RegisterDynamicResource(self, ball):
        billboardSystem = get_billboard_system()
        billboardSystem.register_billboard_resource(self.attributes.dynamicResourceName, self.attributes.videoPlaylist, self.itemID, self.GetTextureParameters(ball))

    def UnregisterDynamicResource(self):
        billboardSystem = get_billboard_system()
        billboardSystem.unregister_billboard_resource(self.attributes.dynamicResourceName, self.itemID)

    def GetTextureParameters(self, ball):
        textureParameters = []
        model = ball.GetModel()
        for screen in self.attributes.screens:
            try:
                for parent in model.Find(screen.parentClass):
                    if parent.name == screen.parentName:
                        textureParameters.extend([ p for p in parent.Find('trinity.TriTextureParameter') if p.name == screen.textureParameterName ])

            except:
                logger.warn('unable to get texture parameters form item %s of type %s using arguments parent_class=%s, parent_name=%s, param_name=%s', self.itemID, self.typeID, screen.parentClass, screen.parentName, screen.textureParameterName)

        return textureParameters

    def UpdateTickers(self, ball):
        model = ball.GetModel()
        for poster in self.attributes.posters:
            try:
                for parent in model.Find(poster.parentClass):
                    if parent.name == poster.parentName:
                        textureParameter = [ p for p in parent.Find('trinity.TriTextureParameter') if p.name == poster.textureParameterName ][0]
                        textureParameter.resourcePath = poster.resPath

            except:
                logger.warn('unable to get texture parameters form item %s of type %s using arguments parent_class=%s, parent_name=%s, param_name=%s res_path=%s', self.itemID, self.typeID, poster.parentClass, poster.parentName, poster.textureParameterName, poster.resPath)
