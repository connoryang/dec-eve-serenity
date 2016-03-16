#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\machonethelpers\__init__.py
from carbon.common.lib.cluster import SERVICE_CLUSTERSINGLETON

class RemoteCallHelper(object):

    def __init__(self, machoNet):
        self.machoNet = machoNet

    def GetRemoteSolarSystemBoundService(self, serviceName, solarSystemID):
        nodeID = self.machoNet.GetNodeFromAddress('beyonce', solarSystemID)
        return self.machoNet.ConnectToRemoteService(serviceName, nodeID)

    def GetClusterSingletonService(self, serviceName, numMod):
        nodeID = self.machoNet.GetNodeFromAddress(SERVICE_CLUSTERSINGLETON, numMod)
        return self.machoNet.ConnectToRemoteService(serviceName, nodeID)
