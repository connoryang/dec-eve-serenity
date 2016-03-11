#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatters\sovBase.py
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
DECLOAK_TIME = 'decloakTime'
ALLIANCE_ID = 'allianceID'
STRUCTURE_TYPE_ID = 'structureTypeID'
SOLAR_SYSTEM_ID = 'solarSystemID'

class SovCaptureBaseNotification(BaseNotificationFormatter):

    def __init__(self, subjectLabel, bodyLabel, localizationInject = None):
        BaseNotificationFormatter.__init__(self, subjectLabel=subjectLabel, bodyLabel=bodyLabel)
        self.localization = self.GetLocalizationImpl(localizationInject)

    @staticmethod
    def MakeData(structureTypeID, solarSystemID):
        data = {STRUCTURE_TYPE_ID: structureTypeID,
         SOLAR_SYSTEM_ID: solarSystemID}
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        return SovCaptureBaseNotification.MakeData(1926, 30004797)

    def _FormatSubject(self, data, notification):
        notification.subject = self.localization.GetByLabel(self.subjectLabel, structureTypeID=data[STRUCTURE_TYPE_ID], solarSystemID=data[SOLAR_SYSTEM_ID])

    def _FormatBody(self, data, notification):
        notification.body = self.localization.GetByLabel(self.bodyLabel, structureTypeID=data[STRUCTURE_TYPE_ID], solarSystemID=data[SOLAR_SYSTEM_ID])

    def Format(self, notification):
        data = notification.data
        self._FormatSubject(data, notification)
        self._FormatBody(data, notification)


class SovEntosisCaptureStarted(SovCaptureBaseNotification):

    def __init__(self):
        SovCaptureBaseNotification.__init__(self, subjectLabel='Notifications/subjSovereigntyCaptureStarted', bodyLabel='Notifications/bodySovereigntyCaptureStarted')


class SovStationServiceEnabled(SovCaptureBaseNotification):

    def __init__(self):
        SovCaptureBaseNotification.__init__(self, subjectLabel='Notifications/subjSovereigntyServiceEnabled', bodyLabel='Notifications/bodySovereigntyServiceEnabled')


class SovStationServiceDisabled(SovCaptureBaseNotification):

    def __init__(self):
        SovCaptureBaseNotification.__init__(self, subjectLabel='Notifications/subjSovereigntyServiceDisabled', bodyLabel='Notifications/bodySovereigntyServiceDisabled')


class SovStationServiceHalfCaptured(SovCaptureBaseNotification):

    def __init__(self):
        SovCaptureBaseNotification.__init__(self, subjectLabel='Notifications/subjSovereigntyServiceHalfCapture', bodyLabel='Notifications/bodySovereigntyServiceHalfCapture')


class SovStructureDestroyed(SovCaptureBaseNotification):

    def __init__(self):
        SovCaptureBaseNotification.__init__(self, subjectLabel='Notifications/subjSovereigntyStructureDestroyed', bodyLabel='Notifications/bodySovereigntyStructureDestroyed')


class SovStructureDestructFinished(SovCaptureBaseNotification):

    def __init__(self):
        SovCaptureBaseNotification.__init__(self, subjectLabel='Notifications/subjSovereigntyStructureDestroyedFinished', bodyLabel='Notifications/bodySovereigntyStructureDestroyedFinished')


class SovIHubDestroyedByBillFailure(SovCaptureBaseNotification):

    def __init__(self):
        SovCaptureBaseNotification.__init__(self, subjectLabel='Notifications/subjSovereigntyIHubDestroyedByBillFailure', bodyLabel='Notifications/bodySovereigntyIHubDestroyedByBillFailure')
