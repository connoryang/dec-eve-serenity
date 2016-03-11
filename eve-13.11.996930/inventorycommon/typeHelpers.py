#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\inventorycommon\typeHelpers.py
try:
    import eve.common.script.sys.eveCfg
    graphics = eve.common.script.sys.eveCfg.CfgGraphics
    fsdDustIcons = eve.common.script.sys.eveCfg.CfgFsdDustIcons
    icons = eve.common.script.sys.eveCfg.CfgIcons
    sounds = eve.common.script.sys.eveCfg.CfgSounds
    invcontrabandFactionsByType = eve.common.script.sys.eveCfg.CfgInvcontrabandFactionsByType
    shiptypes = eve.common.script.sys.eveCfg.CfgShiptypes
    _averageMarketPrice = eve.common.script.sys.eveCfg.CfgAverageMarketPrice
except ImportError:
    graphics = None
    fsdDustIcons = []
    icons = None
    sounds = None
    invcontrabandFactionsByType = None
    shiptypes = None
    _averageMarketPrice = None

import evetypes
import const

def GetGraphic(typeID):
    try:
        graphicID = evetypes.GetGraphicID(typeID)
        return graphics().Get(graphicID)
    except Exception:
        pass


def GetGraphicFile(typeID):
    try:
        return GetGraphic(typeID).graphicFile
    except Exception:
        return ''


def GetAnimationStates(typeID):
    graphic = GetGraphic(typeID)
    try:
        return graphic.animationStates
    except Exception:
        return []


def GetIcon(typeID):
    if typeID >= const.minDustTypeID:
        return fsdDustIcons().get(typeID, None)
    try:
        iconID = evetypes.GetIconID(typeID)
        return icons().Get(iconID)
    except Exception:
        pass


def GetIconFile(typeID):
    try:
        iconID = evetypes.GetIconID(typeID)
        return icons().Get(iconID).iconFile
    except Exception:
        return ''


def GetSound(typeID):
    try:
        soundID = evetypes.GetSoundID(typeID)
        return sounds().Get(soundID)
    except Exception:
        pass


def GetIllegality(typeID, factionID = None):
    if factionID:
        return invcontrabandFactionsByType().get(typeID, {}).get(factionID, None)
    else:
        return invcontrabandFactionsByType().get(typeID, {})


def GetShipType(typeID):
    return shiptypes().Get(typeID)


def GetAdjustedAveragePrice(typeID):
    try:
        return _averageMarketPrice()[typeID].adjustedPrice
    except KeyError:
        return None


def GetAveragePrice(typeID):
    try:
        return _averageMarketPrice()[typeID].averagePrice
    except KeyError:
        return None
