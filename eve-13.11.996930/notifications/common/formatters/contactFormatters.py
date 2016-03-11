#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatters\contactFormatters.py
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
import eve.common.lib.appConst as appConst
import localization

class BaseContactFormatter(BaseNotificationFormatter):

    def Format(self, notification):
        data = notification.data
        notification.subject = localization.GetByLabel(self.subjectLabel)
        notification.body = localization.GetByLabel(self.bodyLabel, notification_senderID=notification.senderID, messageText=self.GetMessageFromData(data), level=self.GetRelationshipName(data.get('level')))

    def GetMessageFromData(self, data):
        return data.get('message', '')

    def GetRelationshipName(self, level):
        if level == appConst.contactHighStanding:
            return localization.GetByLabel('Notifications/partRelationshipExcellent')
        if level == appConst.contactGoodStanding:
            return localization.GetByLabel('Notifications/partRelationshipGood')
        if level == appConst.contactNeutralStanding:
            return localization.GetByLabel('Notifications/partRelationshipNeutral')
        if level == appConst.contactBadStanding:
            return localization.GetByLabel('Notifications/partRelationshipBad')
        if level == appConst.contactHorribleStanding:
            return localization.GetByLabel('Notifications/partRelationshipHorrible')
        return level

    @staticmethod
    def MakeData(relationShipID, message = ''):
        data = {'level': relationShipID,
         'message': message}
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        return BaseContactFormatter.MakeData(relationShipID=appConst.contactNeutralStanding, message='This is a sample')


class ContactAddFormatter(BaseContactFormatter):

    def __init__(self):
        BaseContactFormatter.__init__(self, subjectLabel='Notifications/subjContactAdd', bodyLabel='Notifications/bodyContactAdd')


class BuddyContactAddFormatter(ContactAddFormatter):

    def GetMessageFromData(self, data):
        return localization.GetByLabel('UI/PeopleAndPlaces/BuddyConnectConnectedMessage')


class ContactEditFormatter(BaseContactFormatter):

    def __init__(self):
        BaseContactFormatter.__init__(self, subjectLabel='Notifications/subjContactEdit', bodyLabel='Notifications/bodyContactEdit')
