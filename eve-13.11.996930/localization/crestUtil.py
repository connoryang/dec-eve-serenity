#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localization\crestUtil.py
import stacklesslib.util
_localizationTLS = stacklesslib.util.local()

def SetTLSMarkerLocalized():
    _localizationTLS.wasLocalized = True


def ResetTLSMarker():
    _localizationTLS.wasLocalized = False


def WasCurrentLocalized():
    return getattr(_localizationTLS, 'wasLocalized', False)
