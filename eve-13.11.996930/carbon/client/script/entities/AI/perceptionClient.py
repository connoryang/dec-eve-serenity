#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\entities\AI\perceptionClient.py
import GameWorld
from carbon.common.script.sys.service import Service
from carbon.common.script.entities.AI.perceptionCommon import perceptionCommon

class PerceptionClient(perceptionCommon):
    __guid__ = 'svc.perceptionClient'
    __notifyevents__ = []
    __dependencies__ = ['gameWorldClient']

    def __init__(self):
        perceptionCommon.__init__(self)

    def Run(self, *etc):
        self.gameWorldService = self.gameWorldClient
        Service.Run(self, etc)

    def MakePerceptionManager(self):
        return GameWorld.PerceptionManagerClient()

    def IsClientServerFlagValid(self, clientServerFlag):
        return clientServerFlag & const.aiming.AIMING_CLIENTSERVER_FLAG_CLIENT
