#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sensorsuite\overlay\staticsites.py
from eve.client.script.ui.shared.radialMenu.spaceRadialMenuFunctions import bookMarkOption
import localization
from sensorsuite.overlay.brackets import SensorSuiteBracket, INNER_ICON_COLOR
from sensorsuite.overlay.siteconst import SITE_COLOR_STATIC_SITE, SITE_STATIC_SITE
from sensorsuite.overlay.sitedata import SiteData
from sensorsuite.overlay.sitehandler import SiteHandler
from sensorsuite.overlay.sitetype import STATIC_SITE
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToItem

class StaticSiteData(SiteData):
    siteType = STATIC_SITE
    baseColor = SITE_COLOR_STATIC_SITE

    def __init__(self, siteID, position, dungeonNameID, factionID):
        SiteData.__init__(self, siteID, position)
        self.factionID = factionID
        self.dungeonNameID = dungeonNameID
        self.dungeonName = localization.GetByMessageID(dungeonNameID)

    def GetBracketClass(self):
        return StaticSiteBracket

    def GetName(self):
        return self.dungeonName

    def GetMenu(self):
        return sm.GetService('menu').CelestialMenu(self.siteID)

    def WarpToAction(self, _, distance, *args):
        return WarpToItem(self.siteID, warpRange=distance)

    def GetSecondaryActions(self):
        return [bookMarkOption]


class StaticSiteBracket(SensorSuiteBracket):
    outerColor = SITE_STATIC_SITE.color.GetRGBA()
    outerTextures = SITE_STATIC_SITE.outerTextures
    innerColor = INNER_ICON_COLOR.GetRGBA()
    innerIconResPath = SITE_STATIC_SITE.icon

    def ApplyAttributes(self, attributes):
        SensorSuiteBracket.ApplyAttributes(self, attributes)

    def GetMenu(self):
        return self.data.GetMenu()


class StaticSiteHandler(SiteHandler):
    siteType = STATIC_SITE
    filterIconPath = 'res:/UI/Texture/classes/SensorSuite/diamond2.png'
    filterLabel = 'UI/Inflight/Scanner/LandmarkSiteFilterLabel'
    color = SITE_COLOR_STATIC_SITE
    siteIconData = SITE_STATIC_SITE

    def GetSiteData(self, siteID, position, dungeonNameID, factionID):
        return StaticSiteData(siteID, position, dungeonNameID, factionID)
