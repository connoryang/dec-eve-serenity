#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\graphics\physicalPortalClient.py
import cef
import service
import carbon.client.script.graphics.graphicWrappers.loadAndWrap as graphicWrappers
import collections
import geo2
import trinity

class PhysicalPortalClientComponent:
    __guid__ = 'component.PhysicalPortalClientComponent'


class PhysicalPortalClient(service.Service):
    __guid__ = 'svc.physicalPortalClient'
    __componentTypes__ = [cef.PhysicalPortalComponentView.GetComponentCodeName()]
    __dependencies__ = ['graphicClient']

    def __init__(self):
        service.Service.__init__(self)
        self.isServiceReady = False

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.isServiceReady = True

    def CreateComponent(self, name, state):
        component = PhysicalPortalClientComponent()
        return component

    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        return report

    def PrepareComponent(self, sceneID, entityID, component):
        pass

    def SetupComponent(self, entity, component):
        pass

    def UnRegisterComponent(self, entity, component):
        pass
