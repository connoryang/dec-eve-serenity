#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\client\development\baseHistoryProvider.py


class BaseHistoryProvider(object):

    def __init__(self, scatterDebug = False, onlyShowAfterDate = None):
        self.scatterDebug = scatterDebug
        self.onlyShowAfterDate = onlyShowAfterDate

    def IsNotificationTooOld(self, notificationDate):
        if self.onlyShowAfterDate and notificationDate <= self.onlyShowAfterDate:
            return True
        return False
