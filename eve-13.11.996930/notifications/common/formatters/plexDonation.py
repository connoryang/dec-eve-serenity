#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatters\plexDonation.py
import localization
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class PlexDonationReceivedFormatter(BaseNotificationFormatter):

    def Format(self, notification):
        notification.subject = localization.GetByLabel('Notifications/NotificationNames/PlexDonation')
        recipient = LinkifyOwner(notification.data['senderCharID'])
        body = localization.GetByLabel('Notifications/Plex/PlexReceived', charactername=recipient)
        notification.subtext = body
        notification.body = body
        return notification


class PlexDonationSentFormatter(BaseNotificationFormatter):

    def Format(self, notification):
        notification.subject = localization.GetByLabel('Notifications/NotificationNames/PlexDonation')
        sender = LinkifyOwner(notification.data['receiverCharID'])
        body = localization.GetByLabel('Notifications/Plex/PlexDonated', charactername=sender)
        notification.subtext = body
        notification.body = body
        return notification


def LinkifyOwner(ownerID):
    owner = cfg.eveowners.Get(ownerID)
    return u'<a href="showinfo:{typeID}//{itemID}">{itemName}</a>'.format(typeID=owner.typeID, itemID=ownerID, itemName=owner.name)
