#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\browsers\fittingBrowser.py
from collections import defaultdict
import itertools
from carbon.common.script.sys.serviceConst import ROLE_WORLDMOD, ROLEMASK_ELEVATEDPLAYER
from carbonui import const as uiconst
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import entries as listentry
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.listgroup import ListGroup as Group
import evetypes
from localization import GetByLabel
import log

class FittingBrowserListProvider(object):

    def __init__(self, onDropDataFunc):
        self.onDropDataFunc = onDropDataFunc
        self.fittingSvc = sm.GetService('fittingSvc')
        if session.role & ROLEMASK_ELEVATEDPLAYER:
            try:
                self.fittingSpawner = sm.GetService('fittingspawner')
            except:
                self.fittingSpawner = None

    def GetFittingScrolllist(self, ownerID, *args):
        scrolllist = []
        fittings = self.fittingSvc.GetFittings(ownerID).copy()
        maxFittings = self.GetMaxFittingNumber(ownerID)
        filterText = settings.user.ui.Get('fitting_fittingSearchField', '')
        filterTextLower = filterText.lower()
        fittings = self.FilterOutFittings(filterTextLower, fittings)
        fittingsByGroupID, shipsByGroupID, shipGroups = self.GetShipsAndGroups(filterTextLower, fittings)
        if len(fittings) == 0:
            scrolllist.append(listentry.Get('Generic', data={'label': GetByLabel('UI/Common/NothingFound')}))
        shipScrollist = []
        for groupName, groupID in shipGroups:
            fittingsForGroup = fittingsByGroupID[groupID]
            data = {'GetSubContent': self.GetShipGroupSubContent,
             'label': groupName,
             'fittings': fittingsForGroup,
             'groupItems': fittingsForGroup,
             'allShips': shipsByGroupID[groupID],
             'id': ('fittingMgmtScrollWndGroup', groupName),
             'showicon': 'hide',
             'state': 'locked',
             'BlockOpenWindow': 1,
             'DropData': self.onDropDataFunc}
            groupEntry = (groupName, listentry.Get(entryType='Group', data=data))
            shipScrollist.append(groupEntry)

        shipScrollist = SortListOfTuples(shipScrollist)
        if maxFittings is not None and shipScrollist:
            label = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FittingsListHeader', numFittings=len(fittings), maxFittings=maxFittings)
            scrolllist.append(listentry.Get('Header', {'label': label}))
        scrolllist.extend(shipScrollist)
        return scrolllist

    def GetMaxFittingNumber(self, ownerID):
        maxFittings = None
        if ownerID == session.charid:
            maxFittings = const.maxCharFittings
        elif ownerID == session.corpid:
            maxFittings = const.maxCorpFittings
        return maxFittings

    def FilterOutFittings(self, filterTextLower, fittings):
        if not filterTextLower:
            return fittings
        validFittings = {}
        for fittingID, fitting in fittings.iteritems():
            shipTypeName = evetypes.GetName(fitting.shipTypeID)
            if fitting.name.lower().find(filterTextLower) < 0 and shipTypeName.lower().find(filterTextLower) < 0:
                continue
            validFittings[fittingID] = fitting

        return validFittings

    def GetShipsAndGroups(self, filterTextLower, fittings):
        fittingsByGroupID = defaultdict(list)
        showPersonalFittings = settings.user.ui.Get('fitting_filter_hardware_personalFittings', False)
        if not showPersonalFittings:
            shipGroups, shipsByGroupID = self.GetAllShipGroupsAndShipsByGroupID(filterTextLower)
        else:
            shipGroups = set()
            shipsByGroupID = defaultdict(set)
        for fittingID, fitting in fittings.iteritems():
            shipTypeID = fitting.shipTypeID
            if not evetypes.Exists(shipTypeID):
                log.LogError('Ship in stored fittings does not exist, shipID=%s, fittingID=%s' % (shipTypeID, fittingID))
                continue
            groupID = evetypes.GetGroupID(shipTypeID)
            fittingsByGroupID[groupID].append(fitting)
            groupName = evetypes.GetGroupName(shipTypeID)
            shipGroups.add((groupName, groupID))

        return (fittingsByGroupID, shipsByGroupID, shipGroups)

    def GetAllShipGroupsAndShipsByGroupID(self, filterTextLower):
        shipGroups = set()
        shipsByGroupID = defaultdict(set)
        grouplist = sm.GetService('marketutils').GetMarketGroups()[const.marketCategoryShips]
        shipTypesIDsFromMarket = {i for i in itertools.chain.from_iterable([ x.types for x in grouplist ])}
        for shipTypeID in shipTypesIDsFromMarket:
            shipName = evetypes.GetName(shipTypeID)
            if filterTextLower and shipName.lower().find(filterTextLower) < 0:
                continue
            groupID = evetypes.GetGroupID(shipTypeID)
            groupName = evetypes.GetGroupName(shipTypeID)
            shipGroups.add((groupName, groupID))
            shipsByGroupID[groupID].add(shipTypeID)

        return (shipGroups, shipsByGroupID)

    def GetShipGroupSubContent(self, nodedata, *args):
        scrolllist = []
        fittingsByType = defaultdict(list)
        shipTypes = set()
        for fitting in nodedata.fittings:
            shipTypeID = fitting.shipTypeID
            if not evetypes.Exists(shipTypeID):
                log.LogError('Ship in stored fittings does not exist, shipID=%s, fittingID=%s' % (shipTypeID, fitting.fittingID))
                continue
            fittingsByType[shipTypeID].append(fitting)
            shipName = evetypes.GetName(shipTypeID)
            shipTypes.add((shipName, shipTypeID))

        for typeName, typeID in shipTypes:
            fittingsForType = fittingsByType[typeID]
            entry = self.GetShipTypeGroup(typeID, typeName, fittingsForType)
            scrolllist.append((typeName, entry))

        shipsWithFittings = set(fittingsByType.keys())
        allShips = nodedata.allShips
        missingShips = allShips - shipsWithFittings
        for typeID in missingShips:
            typeName = evetypes.GetName(typeID)
            entry = self.GetShipTypeGroup(typeID, typeName, [])
            scrolllist.append((typeName, entry))

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def GetShipTypeGroup(self, typeID, typeName, fittingsForType):
        data = {'GetSubContent': self.GetFittingSubContent,
         'label': typeName,
         'groupItems': fittingsForType,
         'fittings': fittingsForType,
         'id': ('fittingMgmtScrollWndType', typeName),
         'sublevel': 1,
         'showicon': 'hide',
         'state': 'locked',
         'typeID': typeID,
         'DropData': self.onDropDataFunc}
        entry = listentry.Get(entryType=None, data=data, decoClass=ShipTypeGroup)
        return entry

    def GetFittingSubContent(self, nodedata, *args):
        scrolllist = []
        for fitting in nodedata.fittings:
            fittingName = fitting.name
            data = {'label': fittingName,
             'fittingID': fitting.fittingID,
             'fitting': fitting,
             'ownerID': session.charid,
             'showinfo': 1,
             'showicon': 'hide',
             'sublevel': 2,
             'ignoreRightClick': 1,
             'OnClick': self.OnFittingClicked,
             'OnDropData': self.onDropDataFunc,
             'GetMenu': self.GetFittingMenu}
            sortBy = fittingName.lower()
            entry = listentry.Get('FittingEntry', data=data)
            scrolllist.append((sortBy, entry))

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def GetFittingMenu(self, entry):
        ownerID = entry.sr.node.ownerID
        if session.role & ROLE_WORLDMOD and self.fittingSpawner is not None:
            return [('Make ship', self.fittingSpawner.SpawnFitting, [ownerID, entry.sr.node.fitting])]
        return []

    def OnFittingClicked(self, entry, *args):
        fitting = entry.sr.node.fitting
        sm.GetService('ghostFittingSvc').SimulateFitting(fitting)


class ShipTypeGroup(Group):
    __guid__ = 'listentry.ShipTypeGroup'
    isDragObject = True

    def Startup(self, *args):
        Group.Startup(self, args)
        self.shipTypeID = None
        self.corpAccessBtn = ButtonIcon(name='corpAccessBtn', parent=self, align=uiconst.TORIGHT, width=14, padLeft=1, iconSize=8, texturePath='res:/UI/Texture/Icons/Plus.png', func=self.SimulateShip)

    def Load(self, node):
        Group.Load(self, node)
        self.shipTypeID = node.typeID

    def SimulateShip(self):
        shipDogmaItem = sm.GetService('ghostFittingSvc').LoadShip(self.shipTypeID)
        shipItemKey = shipDogmaItem.itemID
        sm.ScatterEvent('OnSimulatedShipLoaded', shipItemKey, self.shipTypeID)

    def GetDragData(self, *args):
        return [self.sr.node]

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFormItemIDTypeID(None, self.shipTypeID, ignoreMarketDetails=0)
