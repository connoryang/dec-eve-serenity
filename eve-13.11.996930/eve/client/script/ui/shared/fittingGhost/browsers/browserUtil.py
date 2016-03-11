#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\browsers\browserUtil.py
from collections import defaultdict
from eve.client.script.ui.control import entries as listentry
from eve.client.script.ui.shared.fitting.ghostFittingHelpers import TryGhostFitItemOnMouseAction
from eve.client.script.ui.util.uix import GetTechLevelIconID
import evetypes
from localization import GetByLabel
from localization.util import Sort
from utillib import KeyVal
validMarketMetaGroups = (const.metaGroupStoryline,
 const.metaGroupFaction,
 const.metaGroupOfficer,
 const.metaGroupDeadspace)
validCategoriesForMetaGroups = (const.categoryModule, const.categoryDrone, const.categoryStarbase)

def ShoulAddMetaGroupFolder(metaGroupID):
    if metaGroupID in validMarketMetaGroups:
        return True
    return False


def GetTypesByMetaGroups(typeIDs):
    typesByMetaGroupID = defaultdict(list)
    for typeID in typeIDs:
        metaType = cfg.invmetatypes.GetIfExists(typeID)
        if metaType is None:
            metaGroupID = None
        else:
            metaGroupID = metaType.metaGroupID
            if metaGroupID == const.metaGroupStoryline:
                metaGroupID = const.metaGroupFaction
        typesByMetaGroupID[metaGroupID].append(typeID)

    return typesByMetaGroupID


def GetMetaGroupNameAndEntry(metaGroupID, typeIDList, nodedata, subContentFunc, onDropDataFunc, idTuple):
    label = _GetLabelForMarketMetaGroup(metaGroupID)
    data = {'GetSubContent': subContentFunc,
     'label': label,
     'id': idTuple,
     'showlen': 0,
     'metaGroupID': metaGroupID,
     'sublevel': nodedata.sublevel + 1,
     'showicon': GetTechLevelIconID(metaGroupID),
     'state': 'locked',
     'BlockOpenWindow': True,
     'typeIDs': typeIDList,
     'DropData': onDropDataFunc}
    groupEntry = listentry.Get('MarketMetaGroupEntry', data=data)
    labelAndEntry = (label, groupEntry)
    return labelAndEntry


def _GetLabelForMarketMetaGroup(metaGroupID):
    if metaGroupID in (const.metaGroupStoryline, const.metaGroupFaction):
        label = GetByLabel('UI/Market/FactionAndStoryline')
    else:
        label = cfg.invmetagroups.Get(metaGroupID).metaGroupName
    return label


def GetScrollListFromTypeListInNodedata(nodedata, *args):
    invTypeIDs = nodedata.typeIDs
    sublevel = nodedata.sublevel
    onDropDataFunc = nodedata.onDropDataFunc
    return GetScrollListFromTypeList(invTypeIDs, sublevel, onDropDataFunc)


def GetScrollListFromTypeList(invTypeIDs, sublevel, onDropDataFunc):
    subList = []
    for invTypeID in invTypeIDs:
        data = KeyVal()
        data.label = evetypes.GetName(invTypeID)
        data.sublevel = sublevel + 1
        data.ignoreRightClick = 1
        data.showinfo = 1
        data.typeID = invTypeID
        data.OnDropData = onDropDataFunc
        data.OnDblClick = (TryFitModule, invTypeID)
        subList.append((evetypes.GetName(invTypeID), listentry.Get('GenericMarketItem', data=data)))

    subList = [ item[1] for item in Sort(subList, key=lambda x: x[0]) ]
    return subList


def TryFitModule(entry, moduleTypeID):
    TryGhostFitItemOnMouseAction(None, oldWindow=False)
    sm.GetService('ghostFittingSvc').TryFitModuleToOneSlot(moduleTypeID)
