#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sensorsuite\overlay\sitedata.py


class SiteData:
    siteType = None
    baseColor = None
    hoverSoundEvent = None

    def __init__(self, siteID, position):
        self.siteID = siteID
        self.position = position
        self.ballID = None

    def IsAccurate(self):
        return True

    def GetBracketClass(self):
        raise NotImplementedError('GetBracketClass is not implemented')

    def GetSiteType(self):
        return self.siteType

    def GetName(self):
        raise NotImplementedError('You need to provide a name for site')

    def GetSortKey(self):
        return (self.GetSiteType(), self.GetName())

    def GetMenu(self):
        return []

    def WarpToAction(self, *args):
        pass

    def GetSecondaryActions(self):
        return []

    def GetSiteActions(self):
        return None
