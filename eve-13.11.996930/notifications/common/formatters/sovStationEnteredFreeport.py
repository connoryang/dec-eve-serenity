#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatters\sovStationEnteredFreeport.py
from notifications.common.formatters.sovBase import SovCaptureBaseNotification

class SovStationEnteredFreeport(SovCaptureBaseNotification):

    def __init__(self):
        SovCaptureBaseNotification.__init__(self, subjectLabel='Notifications/subjSovereigntyStationEnteredFreeport', bodyLabel='Notifications/bodySovereigntyStationEnteredFreeport')

    @staticmethod
    def MakeData(structureTypeID, solarSystemID, freeportExitTime):
        extraData = {'freeportexittime': freeportExitTime}
        extraData.update(SovCaptureBaseNotification.MakeData(structureTypeID=structureTypeID, solarSystemID=solarSystemID))
        return extraData

    @staticmethod
    def MakeSampleData(variant = 0):
        return SovStationEnteredFreeport.MakeData(1926, 30004797, 130801371921935747L)

    def _FormatBody(self, data, notification):
        notification.body = self.localization.GetByLabel(self.bodyLabel, freeportexittime=data['freeportexittime'])
