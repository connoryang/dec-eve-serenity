#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\securityOfficeSvc.py
import service
import crimewatch.const
from collections import defaultdict

class SecurityOfficeService(service.Service):
    __guid__ = 'svc.securityOfficeSvc'
    __dependencies__ = ['map', 'ui', 'invCache']
    __startupdependencies__ = []
    __notifyevents__ = []

    def CanAccessServiceInStation(self, stationID):
        stationInfo = self.ui.GetStation(stationID)
        if stationInfo is not None:
            if stationInfo.ownerID in const.stationOwnersWithSecurityService:
                if self.map.GetSecurityClass(stationInfo.solarSystemID) == const.securityClassLowSec:
                    return True
        return False

    def GetTagsInHangar(self):
        invContainer = self.invCache.GetInventory(const.containerHangar)
        items = invContainer.List()
        tagCountByTypeID = defaultdict(int)
        for item in items:
            if item.typeID in crimewatch.const.securityLevelsPerTagType:
                tagCountByTypeID[item.typeID] += item.stacksize

        return tagCountByTypeID
