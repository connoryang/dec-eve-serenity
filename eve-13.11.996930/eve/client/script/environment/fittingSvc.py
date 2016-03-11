#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\fittingSvc.py
import sys
from collections import defaultdict
from eve.client.script.ui.shared.fittingGhost.fittingSearchUtil import SearchFittingHelper
from eve.client.script.ui.shared.fittingMgmtWindow import ViewFitting
from eve.common.script.sys.eveCfg import GetActiveShip
from shipfitting import Fitting
import inventorycommon
from inventorycommon.util import IsShipFittingFlag
import service
import util
import blue
from eve.client.script.ui.control import entries as listentry
import form
import localization
import carbonui.const as uiconst
import log
import evetypes
from carbonui.util.various_unsorted import SortListOfTuples, GetClipboardData
from shipfitting.importFittingUtil import FindShipAndFittingName, ImportFittingUtil
from shipfitting.exportFittingUtil import GetFittingEFTString
from utillib import KeyVal

class fittingSvc(service.Service):
    __guid__ = 'svc.fittingSvc'
    __exportedcalls__ = {'GetFittingDictForActiveShip': [],
     'ChangeOwner': []}
    __startupdependencies__ = ['settings', 'invCache']
    __notifyevents__ = ['OnSkillsChanged', 'OnFittingAdded', 'OnFittingDeleted']

    def __init__(self):
        service.Service.__init__(self)
        self.fittings = {}
        self.hasSkillByFittingID = {}
        self.importFittingUtil = None
        self.simulated = False
        self.searchFittingHelper = SearchFittingHelper(cfg)

    def Run(self, ms = None):
        self.state = service.SERVICE_RUNNING
        self.fittings = {}

    def GetFittingMgr(self, ownerID):
        if ownerID == session.charid:
            return sm.RemoteSvc('charFittingMgr')
        if ownerID == session.corpid:
            return sm.RemoteSvc('corpFittingMgr')
        raise RuntimeError("Can't find the fitting manager you're asking me to get. ownerID:", ownerID)

    def HasLegacyClientFittings(self):
        if len(settings.char.generic.Get('fittings', {})) > 0:
            return True
        return False

    def GetLegacyClientFittings(self):
        return settings.char.generic.Get('fittings', {})

    def DeleteLegacyClientFittings(self):
        settings.char.generic.Set('fittings', None)

    def GetFittingDictForCurrentFittingWindowShip(self):
        if self.IsShipSimulated():
            return self.GetFittingDictForSimulatedShip()
        else:
            return self.GetFittingDictForActiveShip()

    def GetFittingDictForActiveShip(self):
        shipID = util.GetActiveShip()
        shipInv = self.invCache.GetInventoryFromId(shipID, locationID=session.stationid2)
        fitData = self.CreateFittingData((i for i in shipInv.List() if inventorycommon.ItemIsVisible(i)))
        return (shipInv.GetItem().typeID, fitData)

    def GetFittingDictForSimulatedShip(self):
        dogmaLocation = self.GetCurrentDogmaLocation()
        shipID = dogmaLocation.shipID
        shipItem = dogmaLocation.GetDogmaItem(shipID)
        fittedItems = shipItem.GetFittedItems()
        fitData = self.CreateFittingData(fittedItems.values())
        return (shipItem.typeID, fitData)

    def CreateFittingData(self, items):
        fitData = []
        dronesByType = defaultdict(int)
        chargesByType = defaultdict(int)
        iceByType = defaultdict(int)
        for item in items:
            if IsShipFittingFlag(item.flagID) and item.categoryID in (const.categoryModule, const.categorySubSystem):
                fitData.append((int(item.typeID), int(item.flagID), 1))
            elif item.categoryID == const.categoryDrone and item.flagID == const.flagDroneBay:
                typeID = item.typeID
                dronesByType[typeID] += item.stacksize
            elif item.categoryID == const.categoryCharge and item.flagID == const.flagCargo:
                typeID = item.typeID
                chargesByType[typeID] += item.stacksize
            elif hasattr(item, 'groupID') and item.groupID == const.groupIceProduct and item.flagID == const.flagCargo:
                typeID = item.typeID
                iceByType[typeID] += item.stacksize

        flag = const.flagDroneBay
        for drone, quantity in dronesByType.iteritems():
            fitData.append((int(drone), int(flag), int(quantity)))

        flag = const.flagCargo
        for charge, quantity in chargesByType.iteritems():
            fitData.append((int(charge), int(flag), int(quantity)))

        flag = const.flagCargo
        for ice, quantity in iceByType.iteritems():
            fitData.append((int(ice), int(flag), int(quantity)))

        return fitData

    def DisplayFittingFromItems(self, shipTypeID, items):
        newItems = []
        for item in items:
            if not hasattr(item, 'flagID'):
                item.flagID = item.flag
            if not hasattr(item, 'stacksize'):
                item.stacksize = item.qtyDropped + item.qtyDestroyed
            item.categoryID = evetypes.GetCategoryID(item.typeID)
            newItems.append(item)

        fitData = self.CreateFittingData(newItems)
        fitting = util.KeyVal()
        fitting.shipTypeID = shipTypeID
        fitting.name = evetypes.GetName(shipTypeID)
        fitting.ownerID = None
        fitting.fittingID = None
        fitting.description = ''
        fitting.fitData = fitData
        self.DisplayFitting(fitting)

    def PersistFitting(self, ownerID, name, description, fit = None):
        if name is None or name.strip() == '':
            raise UserError('FittingNeedsToHaveAName')
        name = name.strip()
        fitting = util.KeyVal()
        fitting.name = name[:const.maxLengthFittingName]
        fitting.description = description[:const.maxLengthFittingDescription]
        self.PrimeFittings(ownerID)
        if ownerID == session.corpid:
            maxFittings = const.maxCorpFittings
        else:
            maxFittings = const.maxCharFittings
        if len(self.fittings[ownerID]) >= maxFittings:
            owner = cfg.eveowners.Get(ownerID).ownerName
            raise UserError('OwnerMaxFittings', {'owner': owner,
             'maxFittings': maxFittings})
        if fit is None:
            fitting.shipTypeID, fitting.fitData = self.GetFittingDictForActiveShip()
        else:
            fitting.shipTypeID, fitting.fitData = fit
        self.VerifyFitting(fitting)
        fitting.ownerID = ownerID
        fitting.fittingID = self.GetFittingMgr(ownerID).SaveFitting(ownerID, fitting)
        self.fittings[ownerID][fitting.fittingID] = fitting
        self.UpdateFittingWindow()
        sm.ScatterEvent('OnFittingsUpdated')
        return fitting

    def PersistManyFittings(self, ownerID, fittings):
        if ownerID == session.corpid:
            maxFittings = const.maxCorpFittings
        else:
            maxFittings = const.maxCharFittings
        self.PrimeFittings(ownerID)
        if len(self.fittings[ownerID]) + len(fittings) > maxFittings:
            owner = cfg.eveowners.Get(ownerID).ownerName
            raise UserError('OwnerMaxFittings', {'owner': owner,
             'maxFittings': maxFittings})
        fittingsToSave = {}
        tmpFittingID = -1
        for fitt in fittings:
            if fitt.name is None or fitt.name.strip() == '':
                raise UserError('FittingNeedsToHaveAName')
            fitting = util.KeyVal()
            fitting.fittingID = tmpFittingID
            fitting.name = fitt.name.strip()[:const.maxLengthFittingName]
            fitting.description = fitt.description[:const.maxLengthFittingDescription]
            fitting.shipTypeID = fitt.shipTypeID
            fitting.fitData = fitt.fitData
            self.VerifyFitting(fitting)
            fitting.ownerID = ownerID
            fittingsToSave[tmpFittingID] = fitting
            tmpFittingID -= 1

        newFittingIDs = self.GetFittingMgr(ownerID).SaveManyFittings(ownerID, fittingsToSave)
        for row in newFittingIDs:
            self.fittings[ownerID][row.realFittingID] = fittingsToSave[row.tempFittingID]
            self.fittings[ownerID][row.realFittingID].fittingID = row.realFittingID

        self.UpdateFittingWindow()
        return fitting

    def VerifyFitting(self, fitting):
        if fitting.name.find('@@') != -1 or fitting.description.find('@@') != -1:
            raise UserError('InvalidFittingInvalidCharacter')
        if fitting.shipTypeID is None:
            raise UserError('InvalidFittingDataTypeID', {'typeName': fitting.shipTypeID})
        shipTypeName = evetypes.GetNameOrNone(fitting.shipTypeID)
        if shipTypeName is None:
            raise UserError('InvalidFittingDataTypeID', {'typeName': fitting.shipTypeID})
        if evetypes.GetCategoryID(fitting.shipTypeID) != const.categoryShip:
            raise UserError('InvalidFittingDataShipNotShip', {'typeName': shipTypeName})
        if len(fitting.fitData) == 0:
            raise UserError('ParseFittingFittingDataEmpty')
        for typeID, flag, qty in fitting.fitData:
            if not evetypes.Exists(typeID):
                raise UserError('InvalidFittingDataTypeID', {'typeID': typeID})
            try:
                int(flag)
            except TypeError:
                raise UserError('InvalidFittingDataInvalidFlag', {'type': typeID})

            if not (IsShipFittingFlag(flag) or flag in (const.flagDroneBay, const.flagCargo)):
                raise UserError('InvalidFittingDataInvalidFlag', {'type': typeID})
            try:
                int(qty)
            except TypeError:
                raise UserError('InvalidFittingDataInvalidQuantity', {'type': typeID})

            if qty == 0:
                raise UserError('InvalidFittingDataInvalidQuantity', {'type': typeID})

        return True

    def GetFittings(self, ownerID):
        self.PrimeFittings(ownerID)
        return self.fittings[ownerID]

    def PrimeFittings(self, ownerID):
        if ownerID not in self.fittings:
            self.fittings[ownerID] = self.GetFittingMgr(ownerID).GetFittings(ownerID)

    def DeleteFitting(self, ownerID, fittingID):
        self.LogInfo('deleting fitting', fittingID, 'from owner', ownerID)
        self.GetFittingMgr(ownerID).DeleteFitting(ownerID, fittingID)
        if ownerID in self.fittings and fittingID in self.fittings[ownerID]:
            del self.fittings[ownerID][fittingID]
        self.UpdateFittingWindow()

    def LoadFittingFromFittingID(self, ownerID, fittingID):
        fitting = self.fittings.get(ownerID, {}).get(fittingID, None)
        return self.LoadFitting(fitting)

    def LoadFitting(self, fitting):
        if session.stationid is None:
            raise UserError('CannotLoadFittingInSpace')
        if fitting is None:
            raise UserError('FittingDoesNotExist')
        shipInv = self.invCache.GetInventoryFromId(util.GetActiveShip(), locationID=session.stationid2)
        chargesByType, dronesByType, iceByType, itemTypes, modulesByFlag, rigsToFit = self.GetTypesToFit(fitting, shipInv)
        fitRigs = False
        if rigsToFit:
            if self.HasRigFitted():
                eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Fitting/ShipHasRigsAlready')})
            elif eve.Message('FitRigs', {}, uiconst.YESNO) == uiconst.ID_YES:
                fitRigs = True
        inv = self.invCache.GetInventory(const.containerHangar)
        itemsToFit = defaultdict(set)
        for item in inv.List():
            if item.typeID in itemTypes:
                qtyNeeded = itemTypes[item.typeID]
                if qtyNeeded == 0:
                    continue
                quantityToTake = min(item.stacksize, qtyNeeded)
                itemsToFit[item.typeID].add(item.itemID)
                itemTypes[item.typeID] -= quantityToTake

        failedToLoad = shipInv.FitFitting(util.GetActiveShip(), itemsToFit, session.stationid2, modulesByFlag, dronesByType, chargesByType, iceByType, fitRigs)
        for typeID, qty in failedToLoad:
            itemTypes[typeID] += qty

        textList = []
        for typeID, qty in itemTypes.iteritems():
            if qty > 0:
                typeName = evetypes.GetName(typeID)
                link = '<url="showinfo:%s">%s</url>' % (typeID, typeName)
                textList.append((typeName.lower(), '%sx %s' % (qty, link)))

        if textList:
            textList = SortListOfTuples(textList)
            text = '<br>'.join(textList)
            text = localization.GetByLabel('UI/Fitting/MissingItems', types=text)
            eve.Message('CustomInfo', {'info': text}, modal=False)

    def GetTypesToFit(self, fitting, shipInv):
        fittingObj = Fitting(fitting.fitData, shipInv)
        return (fittingObj.GetChargesByType(),
         fittingObj.GetDronesByType(),
         fittingObj.GetIceByType(),
         fittingObj.GetQuantityByType(),
         fittingObj.GetModulesByFlag(),
         fittingObj.FittingHasRigs())

    def HasRigFitted(self):
        shipInv = self.invCache.GetInventoryFromId(util.GetActiveShip(), locationID=session.stationid2)
        for item in shipInv.List():
            if const.flagRigSlot0 <= item.flagID <= const.flagRigSlot7:
                return True

        return False

    def UpdateFittingWindow(self):
        wnd = form.FittingMgmt.GetIfOpen()
        if wnd is not None:
            wnd.DrawFittings()

    def ChangeNameAndDescription(self, fittingID, ownerID, name, description):
        if name is None or name.strip() == '':
            raise UserError('FittingNeedsToHaveAName')
        name = name.strip()
        fittings = self.GetFittings(ownerID)
        if fittingID in fittings:
            fitting = fittings[fittingID]
            if name != fitting.name or description != fitting.description:
                if name.find('@@') != -1 or description.find('@@') != -1:
                    raise UserError('InvalidFittingInvalidCharacter')
                self.GetFittingMgr(ownerID).UpdateNameAndDescription(fittingID, ownerID, name, description)
                self.fittings[ownerID][fittingID].name = name
                self.fittings[ownerID][fittingID].description = description
        self.UpdateFittingWindow()

    def GetFitting(self, ownerID, fittingID):
        self.PrimeFittings(ownerID)
        if fittingID in self.fittings[ownerID]:
            return self.fittings[ownerID][fittingID]

    def ChangeOwner(self, ownerID, fittingID, newOwnerID):
        fitting = self.GetFitting(ownerID, fittingID)
        if fitting is None:
            raise UserError('FittingDoesNotExistAnymore')
        fit = (fitting.shipTypeID, fitting.fitData)
        if fitting.name is None or fitting.name.strip() == '':
            raise UserError('FittingNeedsToHaveAName')
        return self.PersistFitting(newOwnerID, fitting.name.strip(), fitting.description, fit=fit)

    def CheckFittingExist(self, ownerID, shipTypeID, fitData):
        fittings = self.GetFittings(ownerID)
        fittingExists = False
        for fitting in fittings.itervalues():
            if fitting.shipTypeID != shipTypeID:
                continue
            if fitting.fitData != fitData:
                continue
            fittingExists = True

        return fittingExists

    def DisplayFittingFromString(self, fittingString):
        fitting, truncated = self.GetFittingFromString(fittingString)
        if fitting == -1:
            raise UserError('FittingInvalidForViewing')
        self.DisplayFitting(fitting, truncated=truncated)

    def DisplayFitting(self, fitting, truncated = False):
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            fittingsList = fitting.fitData[:]
            fittingsList.sort()
            newFittingStr = '%s' % fittingsList
            windowID = 'ViewFitting_%s' % newFittingStr
        else:
            windowID = 'ViewFitting'
        wnd = form.ViewFitting.GetIfOpen(windowID=windowID)
        if wnd:
            wnd.ReloadWnd(windowID=windowID, fitting=fitting, truncated=truncated)
            wnd.Maximize()
        else:
            form.ViewFitting.Open(windowID=windowID, fitting=fitting, truncated=truncated)

    def GetStringForFitting(self, fitting):
        typesByFlag = {}
        drones = []
        charges = []
        ice = []
        for typeID, flag, qty in fitting.fitData:
            categoryID = evetypes.GetCategoryID(typeID)
            groupID = evetypes.GetGroupID(typeID)
            if categoryID in (const.categoryModule, const.categorySubSystem):
                typesByFlag[flag] = typeID
            elif categoryID == const.categoryDrone:
                drones.append((typeID, qty))
            elif categoryID == const.categoryCharge:
                charges.append((typeID, qty))
            elif groupID == const.groupIceProduct:
                ice.append((typeID, qty))

        typesDict = {}
        for flag, typeID in typesByFlag.iteritems():
            if typeID not in typesDict:
                typesDict[typeID] = 0
            typesDict[typeID] += 1

        ret = str(fitting.shipTypeID) + ':'
        for typeID, qty in typesDict.iteritems():
            subString = str(typeID) + ';' + str(qty) + ':'
            ret += subString

        for typeID, qty in drones:
            subString = str(typeID) + ';' + str(qty) + ':'
            ret += subString

        for typeID, qty in charges:
            subString = str(typeID) + ';' + str(qty) + ':'
            ret += subString

        for typeID, qty in ice:
            subString = str(typeID) + ';' + str(qty) + ':'
            ret += subString

        ret = ret.strip(':')
        ret += '::'
        return ret

    def GetFittingFromString(self, fittingString):
        effectSlots = {const.effectHiPower: const.flagHiSlot0,
         const.effectMedPower: const.flagMedSlot0,
         const.effectLoPower: const.flagLoSlot0,
         const.effectRigSlot: const.flagRigSlot0,
         const.effectSubSystem: const.flagSubSystemSlot0}
        truncated = False
        if not fittingString.endswith('::'):
            truncated = True
            fittingString = fittingString[:fittingString.rfind(':')]
        data = fittingString.split(':')
        fitting = util.KeyVal()
        fitData = []
        for line in data:
            typeInfo = line.split(';')
            if line == '':
                continue
            if len(typeInfo) == 1:
                fitting.shipTypeID = int(typeInfo[0])
                continue
            typeID, qty = typeInfo
            typeID, qty = int(typeID), int(qty)
            powerEffectID = sm.GetService('godma').GetPowerEffectForType(typeID)
            if powerEffectID is not None:
                startSlot = effectSlots[powerEffectID]
                for flag in xrange(startSlot, startSlot + qty):
                    fitData.append((typeID, flag, 1))

                effectSlots[powerEffectID] = flag + 1
            else:
                categoryID = evetypes.GetCategoryID(typeID)
                groupID = evetypes.GetGroupID(typeID)
                if categoryID == const.categoryDrone:
                    fitData.append((typeID, const.flagDroneBay, qty))
                elif categoryID == const.categoryCharge:
                    fitData.append((typeID, const.flagCargo, qty))
                elif groupID == const.groupIceProduct:
                    fitData.append((typeID, const.flagCargo, qty))
                else:
                    continue

        shipName = evetypes.GetName(fitting.shipTypeID)
        fitting.name = shipName
        fitting.ownerID = None
        fitting.fittingID = None
        fitting.description = ''
        fitting.fitData = fitData
        return (fitting, truncated)

    def GetFittingInfoScrollList(self, fitting):
        scrolllist = []
        typesByRack = self.GetTypesByRack(fitting)
        for key, effectID in [('hiSlots', const.effectHiPower),
         ('medSlots', const.effectMedPower),
         ('lowSlots', const.effectLoPower),
         ('rigSlots', const.effectRigSlot),
         ('subSystems', const.effectSubSystem)]:
            slots = typesByRack[key]
            if len(slots) > 0:
                label = cfg.dgmeffects.Get(effectID).displayName
                scrolllist.append(listentry.Get('Header', {'label': label}))
                slotScrollList = []
                for typeID, qty in slots.iteritems():
                    data = util.KeyVal()
                    data.typeID = typeID
                    data.showinfo = 1
                    data.getIcon = True
                    data.singleton = 1
                    data.effectID = effectID
                    data.label = str(util.FmtAmt(qty)) + 'x ' + evetypes.GetName(typeID)
                    entry = listentry.Get('FittingModuleEntry', data=data)
                    slotScrollList.append((evetypes.GetGroupID(typeID), entry))

                slotScrollList = SortListOfTuples(slotScrollList)
                scrolllist.extend(slotScrollList)

        charges = typesByRack['charges']
        if len(charges) > 0:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Generic/Charges')}))
            for type, qty in charges.iteritems():
                data = util.KeyVal()
                data.typeID = type
                data.showinfo = 1
                data.getIcon = True
                data.label = str(util.FmtAmt(qty)) + 'x ' + evetypes.GetName(type)
                scrolllist.append(listentry.Get('FittingModuleEntry', data=data))

        ice = typesByRack['ice']
        if len(ice) > 0:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Inflight/MoonMining/Processes/Fuel')}))
            for type, qty in ice.iteritems():
                data = util.KeyVal()
                data.typeID = type
                data.showinfo = 1
                data.getIcon = True
                data.label = str(util.FmtAmt(qty)) + 'x ' + evetypes.GetName(type)
                scrolllist.append(listentry.Get('FittingModuleEntry', data=data))

        drones = typesByRack['drones']
        if len(drones) > 0:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Drones/Drones')}))
            for type, qty in drones.iteritems():
                data = util.KeyVal()
                data.typeID = type
                data.showinfo = 1
                data.getIcon = True
                data.label = str(util.FmtAmt(qty)) + 'x ' + evetypes.GetName(type)
                scrolllist.append(listentry.Get('FittingModuleEntry', data=data))

        return scrolllist

    def GetTypesByRack(self, fitting):
        ret = {'hiSlots': {},
         'medSlots': {},
         'lowSlots': {},
         'rigSlots': {},
         'subSystems': {},
         'charges': {},
         'drones': {},
         'ice': {}}
        for typeID, flag, qty in fitting.fitData:
            if evetypes.GetCategoryID(typeID) == const.categoryCharge:
                ret['charges'][typeID] = qty
            elif evetypes.GetGroupID(typeID) == const.groupIceProduct:
                ret['ice'][typeID] = qty
            elif flag >= const.flagHiSlot0 and flag <= const.flagHiSlot7:
                if typeID not in ret['hiSlots']:
                    ret['hiSlots'][typeID] = 0
                ret['hiSlots'][typeID] += 1
            elif flag >= const.flagMedSlot0 and flag <= const.flagMedSlot7:
                if typeID not in ret['medSlots']:
                    ret['medSlots'][typeID] = 0
                ret['medSlots'][typeID] += 1
            elif flag >= const.flagLoSlot0 and flag <= const.flagLoSlot7:
                if typeID not in ret['lowSlots']:
                    ret['lowSlots'][typeID] = 0
                ret['lowSlots'][typeID] += 1
            elif flag >= const.flagRigSlot0 and flag <= const.flagRigSlot7:
                if typeID not in ret['rigSlots']:
                    ret['rigSlots'][typeID] = 0
                ret['rigSlots'][typeID] += 1
            elif flag >= const.flagSubSystemSlot0 and flag <= const.flagSubSystemSlot7:
                if typeID not in ret['subSystems']:
                    ret['subSystems'][typeID] = 0
                ret['subSystems'][typeID] += 1
            elif flag == const.flagDroneBay:
                ret['drones'][typeID] = qty

        return ret

    def HasSkillForFit(self, fitting):
        fittingID = fitting.fittingID
        try:
            return self.hasSkillByFittingID[fittingID]
        except KeyError:
            self.LogInfo('HasSkillForFit::Cache miss', fittingID)
            sys.exc_clear()

        hasSkill = self.hasSkillByFittingID[fittingID] = self.CheckSkillRequirementsForFit(fitting)
        return hasSkill

    def CheckSkillRequirementsForFit(self, fitting):
        godma = sm.GetService('godma')
        if not godma.CheckSkillRequirementsForType(fitting.shipTypeID):
            return False
        for typeID, flag, qty in fitting.fitData:
            if flag in inventorycommon.const.rigSlotFlags:
                continue
            if not godma.CheckSkillRequirementsForType(typeID):
                return False

        return True

    def GetAllFittings(self):
        ret = {}
        charFittings = self.GetFittings(session.charid)
        corpFittings = self.GetFittings(session.corpid)
        for fittingID in charFittings:
            ret[fittingID] = charFittings[fittingID]

        for fittingID in corpFittings:
            ret[fittingID] = corpFittings[fittingID]

        return ret

    def OnSkillsChanged(self, *args):
        self.hasSkillByFittingID = {}

    def OnFittingAdded(self, ownerID, fitID):
        if ownerID in self.fittings:
            deleteFits = False
            if isinstance(fitID, (int, long)):
                if fitID not in self.fittings[ownerID]:
                    deleteFits = True
            elif isinstance(fitID, list):
                if any((x in self.fittings[ownerID] for x in fitID)):
                    deleteFits = True
            else:
                raise RuntimeError("fitID should always be an int, long, or list. It wasn't. fitID = {} and type(fitID) = {}".format(fitID, type(fitID)))
            if deleteFits is True:
                del self.fittings[ownerID]
                self.UpdateFittingWindow()
                sm.ScatterEvent('OnFittingsUpdated')

    def OnFittingDeleted(self, ownerID, fitID):
        if ownerID in self.fittings:
            if fitID in self.fittings[ownerID]:
                del self.fittings[ownerID][fitID]
                self.UpdateFittingWindow()
                sm.ScatterEvent('OnFittingsUpdated')

    def ImportFittingFromClipboard(self, *args):
        try:
            textInField = GetClipboardData()
            shipName, fitName = FindShipAndFittingName(textInField)
            importFittingUtil = self.GetImportFittingUtil()
            shipTypeID = importFittingUtil.nameAndTypesDict.get(shipName.lower(), None)
            if not shipTypeID:
                eve.Message('ImportingErrorFromClipboard')
                return
            itemLines, errorLines = importFittingUtil.GetAllItems(textInField)
            fitData = importFittingUtil.CreateFittingData(itemLines, shipTypeID)
            if not fitData:
                eve.Message('ImportingErrorFromClipboard')
                return
            fittingData = util.KeyVal(shipTypeID=shipTypeID, fitData=fitData, fittingID=None, description='', name=fitName, ownerID=0)
            self.DisplayFitting(fittingData)
            if errorLines:
                errorText = '<br>'.join(errorLines)
                text = '<b>%s</b><br>%s' % (localization.GetByLabel('UI/SkillQueue/CouldNotReadLines'), errorText)
                eve.Message('CustomInfo', {'info': text})
        except Exception as e:
            log.LogWarn('Failed to import fitting from clipboard, e = ', e)
            eve.Message('ImportingErrorFromClipboard')

    def GetImportFittingUtil(self):
        if self.importFittingUtil is None:
            self.importFittingUtil = ImportFittingUtil(cfg.dgmtypeeffects, sm.GetService('clientDogmaStaticSvc'))
        return self.importFittingUtil

    def ExportFittingToClipboard(self, fitting):
        fittingString = GetFittingEFTString(fitting)
        blue.pyos.SetClipboardData(fittingString)

    def SaveFitting(self, *args):
        fitting = KeyVal()
        fitting.shipTypeID, fitting.fitData = self.GetFittingDictForCurrentFittingWindowShip()
        fitting.fittingID = None
        fitting.description = ''
        fitting.name = cfg.evelocations.Get(GetActiveShip()).locationName
        fitting.ownerID = 0
        windowID = 'Save_ViewFitting_%s' % fitting.shipTypeID
        ViewFitting.Open(windowID=windowID, fitting=fitting, truncated=None)

    def GetShipIDForFittingWindow(self):
        if self.simulated:
            fittingDL = sm.GetService('clientDogmaIM').GetFittingDogmaLocation()
            return fittingDL.shipID
        import util
        return util.GetActiveShip()

    def GetCurrentDogmaLocation(self):
        if self.simulated:
            return sm.GetService('clientDogmaIM').GetFittingDogmaLocation()
        else:
            return sm.GetService('clientDogmaIM').GetDogmaLocation()

    def IsShipSimulated(self):
        return self.simulated
