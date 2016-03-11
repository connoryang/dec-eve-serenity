#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatters\sovAllianceCapitalChange.py
import localization
from notifications.common.formatters.sovBase import SovCaptureBaseNotification, ALLIANCE_ID, SOLAR_SYSTEM_ID
from eve.common.script.util.notificationUtil import CreateItemInfoLink

class SovAllianceCapitalChanged(SovCaptureBaseNotification):

    def __init__(self):
        SovCaptureBaseNotification.__init__(self, subjectLabel='Notifications/subjSovereigntyAllianceCapitalChanged', bodyLabel='Notifications/bodySovereigntyAllianceCapitalChanged')

    @staticmethod
    def MakeData(solarSystemID, allianceID):
        data = {ALLIANCE_ID: allianceID,
         SOLAR_SYSTEM_ID: solarSystemID}
        return data

    def Format(self, notification):
        data = notification.data
        notification.subject = localization.GetByLabel(self.subjectLabel, allianceName=CreateItemInfoLink(data[ALLIANCE_ID]), solarSystemID=data[SOLAR_SYSTEM_ID])
        notification.body = localization.GetByLabel(self.bodyLabel, allianceName=CreateItemInfoLink(data[ALLIANCE_ID]))

    @staticmethod
    def MakeSampleData(variant = 0):
        return SovAllianceCapitalChanged.MakeData(30004797, 99000001 + variant)
