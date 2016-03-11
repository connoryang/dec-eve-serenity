#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\shipfitting\importFittingUtil.py
import collections
import inventorycommon.const as invconst
import dogma.const as dogmaConst
import evetypes
from textImporting import GetLines, SplitAndStrip, GetValidNamesAndTypesDict
SHIP_FIRST_CHARACTER = '['
SHIP_LAST_CHARACTER = ']'
OFFLINE_INDICATOR = '/offline'
CHARGE_SEPARATOR = ','
MULTIPLIER_SEPARATOR = ' x'
EMPTY_TEMPLATE_STRING = '[Empty %s slot]'
emptySlotDict = {EMPTY_TEMPLATE_STRING % 'Low'.lower(): 'flagLoSlot',
 EMPTY_TEMPLATE_STRING % 'Med'.lower(): 'flagMedSlot',
 EMPTY_TEMPLATE_STRING % 'High'.lower(): 'flagHiSlot',
 EMPTY_TEMPLATE_STRING % 'Rig'.lower(): 'flagRigSlot'}
slotDict = {dogmaConst.effectRigSlot: 'flagRigSlot',
 dogmaConst.effectHiPower: 'flagHiSlot',
 dogmaConst.effectMedPower: 'flagMedSlot',
 dogmaConst.effectLoPower: 'flagLoSlot'}
NUM_SLOTS = 8
validCategoryIDs = [invconst.categoryShip,
 invconst.categoryModule,
 invconst.categorySubSystem,
 invconst.categoryCharge,
 invconst.groupIceProduct,
 invconst.categoryDrone]

class ImportFittingUtil(object):

    def __init__(self, dgmtypeeffectDict, clientDogmaStaticSvc):
        self.nameAndTypesDict = GetValidNamesAndTypesDict(validCategoryIDs)
        self.dgmtypeeffectDict = dgmtypeeffectDict
        self.clientDogmaStaticSvc = clientDogmaStaticSvc

    def GetLineInfo(self, line):
        parts = SplitAndStrip(line, CHARGE_SEPARATOR)
        typeName = parts[0]
        if len(parts) > 1:
            chargeName = parts[1].strip().lower()
        else:
            chargeName = None
        parts = SplitAndStrip(typeName, MULTIPLIER_SEPARATOR)
        typeName = parts[0]
        if len(parts) > 1:
            numItems = int(parts[1])
        else:
            numItems = 1
        if typeName:
            typeName = typeName.lower()
        typeID = self.nameAndTypesDict.get(typeName, None)
        chargeTypeID = self.nameAndTypesDict.get(chargeName, None)
        isEmpty = True
        slotLocation = None
        if typeName in emptySlotDict:
            slotLocation = emptySlotDict[typeName]
        elif typeID:
            slotLocation = self.GetSlot(typeID)
            isEmpty = False
        if typeID is None and chargeTypeID is None and slotLocation is None:
            return
        categoryID = None
        capacity = None
        chargeVolume = None
        if evetypes.Exists(typeID):
            categoryID = evetypes.GetCategoryID(typeID)
            capacity = evetypes.GetCapacity(typeID)
        if evetypes.Exists(chargeTypeID):
            chargeVolume = evetypes.GetVolume(chargeTypeID)
        info = {'typeName': typeName,
         'typeID': typeID,
         'categoryID': categoryID,
         'capacity': capacity,
         'numItems': numItems,
         'chargeName': chargeName,
         'chargeTypeID': chargeTypeID,
         'chargeVolume': chargeVolume,
         'slotLocation': slotLocation,
         'isEmpty': isEmpty}
        return info

    def GetAllItems(self, text):
        lines = GetItemLines(text)
        allItemsInfo = []
        errorLines = []
        for eachLine in lines:
            lineInfo = self.GetLineInfo(eachLine)
            if lineInfo:
                allItemsInfo.append(lineInfo)
            else:
                errorLines.append(eachLine)

        return (allItemsInfo, errorLines)

    def GetSlot(self, typeID):
        for effect in self.dgmtypeeffectDict.get(typeID, []):
            if effect.effectID in slotDict:
                return slotDict.get(effect.effectID)

        subsystemSlot = self.clientDogmaStaticSvc.GetTypeAttribute2(typeID, dogmaConst.attributeSubSystemSlot)
        if subsystemSlot:
            return int(subsystemSlot)

    def GetSlotNumbers(self, typeID):
        slotDict = {'flagRigSlot': self.clientDogmaStaticSvc.GetTypeAttribute2(typeID, dogmaConst.attributeRigSlots)}
        if evetypes.GetGroupID(typeID) == invconst.groupStrategicCruiser:
            slotDict['flagHiSlot'] = NUM_SLOTS
            slotDict['flagMedSlot'] = NUM_SLOTS
            slotDict['flagLoSlot'] = NUM_SLOTS
            for location in invconst.subSystemSlotFlags:
                slotDict[location] = 1

        else:
            slotDict['flagHiSlot'] = self.clientDogmaStaticSvc.GetTypeAttribute2(typeID, dogmaConst.attributeHiSlots)
            slotDict['flagMedSlot'] = self.clientDogmaStaticSvc.GetTypeAttribute2(typeID, dogmaConst.attributeMedSlots)
            slotDict['flagLoSlot'] = self.clientDogmaStaticSvc.GetTypeAttribute2(typeID, dogmaConst.attributeLowSlots)
        return slotDict

    def CreateFittingData(self, infoLines, shipTypeID):
        fitData = []
        dronesByType = collections.defaultdict(int)
        cargoByType = collections.defaultdict(int)
        locationDict = collections.defaultdict(int)
        allowedSlotsDict = self.GetSlotNumbers(shipTypeID)
        for eachLine in infoLines:
            slotLocation = eachLine['slotLocation']
            typeID = eachLine['typeID']
            categoryID = eachLine['categoryID']
            capacity = eachLine['capacity']
            if slotLocation:
                if locationDict[slotLocation] >= allowedSlotsDict.get(slotLocation, 0):
                    continue
                slotIdx = locationDict[slotLocation]
                locationDict[slotLocation] += 1
                if eachLine['isEmpty'] or not typeID:
                    continue
                typeID = typeID
                if categoryID == invconst.categorySubSystem:
                    slotLocationConst = slotLocation
                else:
                    slotLocationConst = getattr(invconst, '%s%s' % (slotLocation, slotIdx), None)
                fitData.append((typeID, slotLocationConst, 1))
                chargeTypeID = eachLine['chargeTypeID']
                if chargeTypeID:
                    chargeAmount = capacity / eachLine['chargeVolume']
                    cargoByType[chargeTypeID] += chargeAmount
            if not typeID:
                continue
            if categoryID in (invconst.categoryCharge, invconst.groupIceProduct):
                cargoByType[typeID] += eachLine['numItems']
            if categoryID == invconst.categoryDrone:
                dronesByType[typeID] += eachLine['numItems']

        cargoAndDrones = [(cargoByType, invconst.flagCargo), (dronesByType, invconst.flagDroneBay)]
        for dictByType, locationFlag in cargoAndDrones:
            for typeID, amount in dictByType.iteritems():
                fitData.append((typeID, locationFlag, int(amount)))

        return fitData


def IsShipLine(text):
    return text.startswith(SHIP_FIRST_CHARACTER) and text[-1] == SHIP_LAST_CHARACTER and text not in emptySlotDict


def GetItemLines(text):
    lines = GetLines(text, wordsToRemove=[OFFLINE_INDICATOR])
    lines = [ x for x in lines if not IsShipLine(x) ]
    return lines


def FindShipAndFittingName(text):
    lines = GetLines(text, wordsToRemove=[OFFLINE_INDICATOR])
    for eachLine in lines:
        if not eachLine:
            continue
        if IsShipLine(eachLine):
            shipInfo = eachLine[1:-1]
            parts = SplitAndStrip(shipInfo, CHARGE_SEPARATOR)
            commaIdx = shipInfo.find(CHARGE_SEPARATOR)
            return (parts[0], shipInfo[commaIdx + 1:].strip())
