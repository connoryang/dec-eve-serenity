#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatters\sovIHubBillAboutToExpire.py
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
from localization import GetByLabel
CORP_ID = 'corpID'
SOLAR_SYSTEM_ID = 'solarSystemID'
DUE_DATETIME = 'dueDate'
BILL_ID = 'billID'

class IHubBillAboutToExpire(BaseNotificationFormatter):

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel='Notifications/subjSovereigntyIHubBillWarning', bodyLabel='Notifications/bodySovereigntyIHubBillWarning')

    def Format(self, notification):
        data = notification.data
        notification.subject = GetByLabel(self.subjectLabel)
        notification.body = GetByLabel(self.bodyLabel, solarSystemID=data[SOLAR_SYSTEM_ID], dueDate=data[DUE_DATETIME])

    @staticmethod
    def MakeData(billID, corporationID, solarSystemID, dueDateTime):
        return {BILL_ID: billID,
         CORP_ID: corporationID,
         SOLAR_SYSTEM_ID: solarSystemID,
         DUE_DATETIME: dueDateTime}

    @staticmethod
    def MakeSampleData(variant = 0):
        return IHubBillAboutToExpire.MakeData(0, 99000001, 30004797, 135808394095944399L)
