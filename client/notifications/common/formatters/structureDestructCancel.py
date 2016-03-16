#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatters\structureDestructCancel.py
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
STRUCTURE_TYPE_ID = 'structureTypeID'
SOLAR_SYSTEM_ID = 'solarSystemID'
CHAR_ID = 'charID'

class StructureDestructCancel(BaseNotificationFormatter):

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel='Notifications/subjSovereigntyStructureDestroyedCancel', bodyLabel='Notifications/bodySovereigntyStructureDestroyedCancel')

    @staticmethod
    def MakeData(structureTypeID, solarSystemID, charID):
        data = {STRUCTURE_TYPE_ID: structureTypeID,
         SOLAR_SYSTEM_ID: solarSystemID,
         CHAR_ID: charID}
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        return StructureDestructCancel.MakeData(1926, 30004797, 150135866)

    def _FormatSubject(self, data, notification):
        notification.subject = GetByLabel(self.subjectLabel, structureTypeID=data[STRUCTURE_TYPE_ID], solarSystemID=data[SOLAR_SYSTEM_ID])

    def _FormatBody(self, data, notification):
        notification.body = GetByLabel(self.bodyLabel, structureTypeID=data[STRUCTURE_TYPE_ID], solarSystemID=data[SOLAR_SYSTEM_ID], charID=data[CHAR_ID])

    def Format(self, notification):
        data = notification.data
        self._FormatSubject(data, notification)
        self._FormatBody(data, notification)
