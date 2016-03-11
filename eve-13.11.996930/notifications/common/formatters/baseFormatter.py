#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatters\baseFormatter.py


class BaseNotificationFormatter(object):

    def __init__(self, subjectLabel = None, bodyLabel = None, subtextLabel = None):
        self.subjectLabel = subjectLabel
        self.bodyLabel = bodyLabel
        self.subtextLabel = subtextLabel

    def Format(self, notification):
        pass

    @staticmethod
    def MakeSampleData(variant = 0):
        return {}

    def GetLocalizationImpl(self, localizationInject):
        if localizationInject is None:
            import localization
            localizationInject = localization
        return localizationInject
