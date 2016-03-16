#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\shipfitting\exportFittingUtil.py
import inventorycommon.const as invconst
import evetypes
EXTRA_ITEM_TEMPLATE = '%s x%s'
EMPTY_TEMPLATE_STRING = '[Empty %s slot]'
SHIP_AND_FITTINGNAME_TEMPLATE = '[%s, %s]'
LINEBREAK = '\r\n'
NUM_SLOTS = 8
NUM_SUBSYSTEMS = 5
emptySlotDict = {invconst.flagLoSlot0: EMPTY_TEMPLATE_STRING % 'Low',
 invconst.flagMedSlot0: EMPTY_TEMPLATE_STRING % 'Med',
 invconst.flagHiSlot0: EMPTY_TEMPLATE_STRING % 'High',
 invconst.flagRigSlot0: EMPTY_TEMPLATE_STRING % 'Rig'}

def GetFittingEFTString(fitting):
    fitData = fitting.fitData
    cargoItems = [ x for x in fitData if x[1] == invconst.flagCargo ]
    droneItems = [ x for x in fitData if x[1] == invconst.flagDroneBay ]
    fitDataFlagDict = {x[1]:x for x in fitData}
    slotTuples = [(NUM_SLOTS, invconst.flagLoSlot0),
     (NUM_SLOTS, invconst.flagMedSlot0),
     (NUM_SLOTS, invconst.flagHiSlot0),
     (NUM_SLOTS, invconst.flagRigSlot0),
     (NUM_SUBSYSTEMS, invconst.flagSubSystemSlot0)]
    shipName = evetypes.GetEnglishName(fitting.shipTypeID)
    mysStringList = [SHIP_AND_FITTINGNAME_TEMPLATE % (shipName, fitting.name)]
    for numSlots, firstSlot in slotTuples:
        tempStringList = []
        emptyString = emptySlotDict.get(firstSlot, '')
        for i in xrange(numSlots):
            currentSlotIdx = firstSlot + i
            moduleInfo = fitDataFlagDict.get(currentSlotIdx, None)
            if moduleInfo:
                mysStringList += tempStringList
                tempStringList = []
                typeID = moduleInfo[0]
                mysStringList.append(evetypes.GetEnglishName(typeID))
            else:
                tempStringList.append(emptyString)

        mysStringList.append('')

    for location in (droneItems, cargoItems):
        for eachItem in location:
            typeID = eachItem[0]
            typeName = evetypes.GetEnglishName(typeID)
            lineText = EXTRA_ITEM_TEMPLATE % (typeName, eachItem[2])
            mysStringList.append(lineText)

        mysStringList.append('')

    fittingString = LINEBREAK.join(mysStringList)
    return fittingString
