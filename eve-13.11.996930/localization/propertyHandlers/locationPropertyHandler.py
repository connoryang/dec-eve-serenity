#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localization\propertyHandlers\locationPropertyHandler.py
import eveLocalization
import localization
from basePropertyHandler import BasePropertyHandler
import log
from .. import const as locconst
from ..logger import LogInfo, LogWarn
import eve.common.script.sys.eveCfg as evecfg

class LocationPropertyHandler(BasePropertyHandler):
    PROPERTIES = {locconst.CODE_UNIVERSAL: ('name', 'rawName')}

    def _GetName(self, locationID, languageID, *args, **kwargs):
        try:
            return cfg.evelocations.Get(locationID).locationName
        except KeyError:
            log.LogException()
            return '[no location: %d]' % locationID

    def _GetRawName(self, locationID, languageID, *args, **kwargs):
        try:
            return cfg.evelocations.Get(locationID).GetRawName(languageID)
        except KeyError:
            log.LogException()
            return '[no location: %d]' % locationID

    if boot.role != 'client':
        _GetName = _GetRawName

    def Linkify(self, locationID, linkText):
        if evecfg.IsRegion(locationID):
            locationTypeID = const.typeRegion
        elif evecfg.IsConstellation(locationID):
            locationTypeID = const.typeConstellation
        elif evecfg.IsSolarSystem(locationID):
            locationTypeID = const.typeSolarSystem
        else:
            if evecfg.IsCelestial(locationID):
                warnText = "LOCALIZATION ERROR: 'linkify' argument used for a location of type celestial."
                warnText += " This is not supported. Please use the 'linkinfo' tag with arguments instead. locID:"
                LogWarn(warnText, locationID)
                return linkText
            if evecfg.IsStation(locationID):
                try:
                    locationTypeID = cfg.stations.Get(locationID).stationTypeID
                except KeyError:
                    return '[no station: %d]' % locationID

            else:
                LogInfo("LOCALIZATION LINK: The 'linkify' argument was used for a location whose type can not be identified.", locationID)
                return linkText
        return '<a href=showinfo:%d//%d>%s</a>' % (locationTypeID, locationID, linkText)


eveLocalization.RegisterPropertyHandler(eveLocalization.VARIABLE_TYPE.LOCATION, LocationPropertyHandler())
