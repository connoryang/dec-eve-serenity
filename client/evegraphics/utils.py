#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\utils.py
import evetypes

def GetResPathFromGraphicID(graphicID):
    if graphicID is None:
        return
    graphicInfo = cfg.graphics.GetIfExists(graphicID)
    if graphicInfo is None:
        return
    return getattr(graphicInfo, 'graphicFile', None)


def IsValidSOFDNA(dna):
    sp = dna.split(':')
    if len(sp) < 3:
        return False
    return True


def BuildSOFDNAFromTypeID(typeID, materialSetID = None):
    if typeID is None:
        return
    if not evetypes.Exists(typeID):
        return
    if materialSetID is None:
        materialSetID = evetypes.GetSofMaterialSetIDOrNone(typeID)
    return BuildSOFDNAFromGraphicID(evetypes.GetGraphicID(typeID), materialSetID=materialSetID)


def CombineSOFDNA(sofHullName, sofFactionName, sofRaceName, sofAddition = None):
    dna = sofHullName + ':' + sofFactionName + ':' + sofRaceName
    if sofAddition is not None:
        dna += ':' + sofAddition
    return dna


def BuildSOFDNAFromGraphicID(graphicID, materialSetID = None):
    if graphicID is None:
        return
    graphicInfo = cfg.graphics.GetIfExists(graphicID)
    if graphicInfo is None:
        return
    hull = getattr(graphicInfo, 'sofHullName', None)
    faction = getattr(graphicInfo, 'sofFactionName', None)
    race = getattr(graphicInfo, 'sofRaceName', None)
    dnaAddition = None
    if hull is None or faction is None or race is None:
        return
    materialSet = None
    if materialSetID is not None:
        materialSet = cfg.graphicMaterialSets.GetIfExists(materialSetID)
    if materialSet is not None:
        faction = getattr(materialSet, 'sofFactionName', faction)
        dnaAddition = 'mesh?' + getattr(materialSet, 'material1', 'none') + ';' + getattr(materialSet, 'material2', 'none') + ';' + getattr(materialSet, 'material3', 'none') + ';' + getattr(materialSet, 'material4', 'none')
        resPathInsert = getattr(materialSet, 'resPathInsert', None)
        if resPathInsert is not None:
            dnaAddition += ':respathinsert?' + resPathInsert
    return CombineSOFDNA(hull, faction, race, dnaAddition)


def RemapDirtLevel(dirtLevel0To100):

    def lerp(min, max, f):
        return (max - min) * f + min

    if dirtLevel0To100 < 50:
        currentDirtLevel = lerp(-2.0, 0.0, dirtLevel0To100 / 50.0)
    else:
        currentDirtLevel = lerp(0.0, 0.7, (dirtLevel0To100 - 50) / 50.0)
    if currentDirtLevel == 0.55:
        currentDirtLevel = None
    return currentDirtLevel


def CalcDirtLevelFromAge(lastCleanTimeStamp):
    import blue
    dirtTimeDiff = blue.os.TimeDiffInMs(lastCleanTimeStamp, blue.os.GetWallclockTime())
    dirtTimeDiff = max(dirtTimeDiff, 0.0)
    msInWeek = 604800000.0
    dirtTimeDiffInWeeks = dirtTimeDiff / msInWeek
    dirtLevel = 0.7 - 1.0 / (pow(dirtTimeDiffInWeeks, 0.65) + 1.0 / 2.7)
    return dirtLevel


def GetPreviewScenePath(raceID):
    import const
    sceneGraphicIDs = {const.raceCaldari: 20409,
     const.raceMinmatar: 20410,
     const.raceGallente: 20411,
     const.raceAmarr: 20412}
    gfxID = sceneGraphicIDs.get(raceID, 20413)
    return GetResPathFromGraphicID(gfxID)


class DummyGroup(object):

    def __init__(self):
        self._d = {}

    def Get(self, key, default = None):
        return self._d.get(key, default)

    def Set(self, key, val):
        self._d[key] = val


def GetDnaFromResPath(respath):
    lowerCaseResPath = respath.lower()
    prefix = 'res:/dx9/model/ship/'
    if not lowerCaseResPath.startswith(prefix):
        raise RuntimeError
    lowerCaseResPath = lowerCaseResPath[len(prefix):]
    parts = lowerCaseResPath.split('/')
    if len(parts) < 4:
        raise RuntimeError
    race = parts[0]
    if len(parts) == 5:
        faction = parts[3]
        ship = parts[4]
        ship = ship.replace('_' + faction, '')
    else:
        faction = race + 'base'
        ship = parts[3]
    ship = ship.split('.')[0]
    dna = '%s:%s:%s' % (ship, faction, race)
    return dna


def GetCorrectEffectPath(effectPath, model):
    if hasattr(model, 'shadowEffect'):
        if model.shadowEffect is not None:
            if 'skinned_' in model.shadowEffect.effectFilePath.lower():
                return effectPath.replace('.red', '_skinned.red')
    return effectPath
