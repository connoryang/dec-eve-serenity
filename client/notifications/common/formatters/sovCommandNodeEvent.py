#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatters\sovCommandNodeEvent.py
from entosis import entosisConst as entosisconst
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
from notifications.common.formatters.sovBase import STRUCTURE_TYPE_ID, SOLAR_SYSTEM_ID
CAMPAIGN_EVENT_TYPE = 'campaignEventType'
CONSTELLATION_ID = 'constellationID'

class SovCommandNodeEventStarted(BaseNotificationFormatter):

    def __init__(self, localizationImpl = None):
        BaseNotificationFormatter.__init__(self, bodyLabel='Notifications/bodySovereigntyCommandNodeEventStarted')
        self.localization = self.GetLocalizationImpl(localizationImpl)

    @staticmethod
    def MakeData(campaignEventType, solarSystemID, constellationID):
        data = {CONSTELLATION_ID: constellationID,
         SOLAR_SYSTEM_ID: solarSystemID,
         CAMPAIGN_EVENT_TYPE: campaignEventType}
        return data

    def Format(self, notification):
        data = notification.data
        self._FormatSubject(data, notification)
        self._FormatBody(data, notification)

    def _FormatSubject(self, data, notification):
        subjectLabel = self._GetSubjectLabelByType(data[CAMPAIGN_EVENT_TYPE])
        notification.subject = self.localization.GetByLabel(subjectLabel, solarSystemID=data[SOLAR_SYSTEM_ID])

    def _FormatBody(self, data, notification):
        notification.body = self.localization.GetByLabel(self.bodyLabel, constellationID=data[CONSTELLATION_ID])

    @staticmethod
    def MakeSampleData(variant = 0):
        return SovCommandNodeEventStarted.MakeData(campaignEventType=entosisconst.EVENT_TYPE_TCU_DEFENSE, solarSystemID=30004797, constellationID=20000702)

    def _GetSubjectLabelByType(self, campaignType):
        if campaignType == entosisconst.EVENT_TYPE_IHUB_DEFENSE:
            return 'Notifications/subjSovereigntyCommandNodeIHubEventStarted'
        if campaignType in [entosisconst.EVENT_TYPE_STATION_DEFENSE, entosisconst.EVENT_TYPE_STATION_FREEPORT]:
            return 'Notifications/subjSovereigntyCommandNodeStationEventStarted'
        if campaignType == entosisconst.EVENT_TYPE_TCU_DEFENSE:
            return 'Notifications/subjSovereigntyCommandNodeTCUEventStarted'
