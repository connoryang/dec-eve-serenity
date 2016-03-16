#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatters\sovStructureReinforced.py
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
from notifications.common.formatters.sovBase import DECLOAK_TIME, SOLAR_SYSTEM_ID
from entosis import entosisConst as entosisconst
CAMPAIGN_EVENT_TYPE = 'campaignEventType'

class SovStructureReinforced(BaseNotificationFormatter):

    def __init__(self, localizationInject = None):
        self.localization = self.GetLocalizationImpl(localizationInject)
        BaseNotificationFormatter.__init__(self, bodyLabel='Notifications/bodySovereigntyStructureReinforced')

    @staticmethod
    def MakeData(campaignType, solarSystemID, decloakTime):
        extraData = {DECLOAK_TIME: decloakTime,
         CAMPAIGN_EVENT_TYPE: campaignType,
         SOLAR_SYSTEM_ID: solarSystemID}
        return extraData

    def Format(self, notification):
        data = notification.data
        self._FormatSubject(data, notification)
        self._FormatBody(data, notification)

    def _FormatSubject(self, data, notification):
        subjectLabel = self._GetSubjectLabelByType(data[CAMPAIGN_EVENT_TYPE])
        notification.subject = self.localization.GetByLabel(subjectLabel, solarSystemID=data[SOLAR_SYSTEM_ID])

    def _FormatBody(self, data, notification):
        notification.body = self.localization.GetByLabel(self.bodyLabel, decloakTime=data[DECLOAK_TIME])

    @staticmethod
    def MakeSampleData(variant = 0):
        return SovStructureReinforced.MakeData(entosisconst.EVENT_TYPE_TCU_DEFENSE, 30004797, 130801371921935747L)

    def _GetSubjectLabelByType(self, campaignType):
        if campaignType == entosisconst.EVENT_TYPE_IHUB_DEFENSE:
            return 'Notifications/subjSovereigntyStructureReinforcedIHub'
        if campaignType in [entosisconst.EVENT_TYPE_STATION_DEFENSE, entosisconst.EVENT_TYPE_STATION_FREEPORT]:
            return 'Notifications/subjSovereigntyStructureReinforcedStation'
        if campaignType == entosisconst.EVENT_TYPE_TCU_DEFENSE:
            return 'Notifications/subjSovereigntyStructureReinforcedTCU'
