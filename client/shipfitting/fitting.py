#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\shipfitting\fitting.py
from collections import defaultdict
import inventorycommon
import inventorycommon.const as invconst
from inventorycommon.util import IsShipFittingFlag
import logging
import evetypes
logger = logging.getLogger(__name__)

class Fitting(object):

    def __init__(self, fitData, shipInv):
        self.itemTypes = defaultdict(lambda : 0)
        self.modulesByFlag = {}
        self.dronesByType = {}
        self.chargesByType = {}
        self.fuelByType = {}
        self.rigsToFit = False
        for typeID, flag, qty in fitData:
            groupID = evetypes.GetGroupID(typeID)
            if self._IsRig(flag):
                self.rigsToFit = True
            if self._IsModule(flag):
                self.modulesByFlag[flag] = typeID
            elif self._IsDrone(flag):
                self.dronesByType[typeID] = qty
            elif self._IsFuel(flag, groupID):
                self.fuelByType[typeID] = qty
            elif self._IsAmmo(flag, groupID):
                self.chargesByType[typeID] = qty
            else:
                logger.error('LoadFitting::flag neither fitting nor drone bay %s, %s', typeID, flag)
                continue
            skipType = False
            for item in shipInv.List(flag):
                if item.typeID == typeID:
                    itemQty = item.stacksize
                    if itemQty == qty:
                        skipType = True
                        break
                    else:
                        qty -= itemQty

            if skipType:
                continue
            self.itemTypes[typeID] += qty

    def _IsRig(self, flag):
        return invconst.flagRigSlot0 <= flag <= invconst.flagRigSlot7

    def _IsModule(self, flag):
        return IsShipFittingFlag(flag) and flag != invconst.flagHiddenModifers

    def _IsDrone(self, flag):
        return flag == invconst.flagDroneBay

    def _IsFuel(self, flag, groupID):
        return flag == invconst.flagCargo and groupID == invconst.groupIceProduct

    def _IsAmmo(self, flag, groupID):
        return flag == invconst.flagCargo and groupID

    def GetQuantityByType(self):
        return self.itemTypes

    def GetChargesByType(self):
        return self.chargesByType

    def GetIceByType(self):
        return self.fuelByType

    def GetModulesByFlag(self):
        return self.modulesByFlag

    def FittingHasRigs(self):
        return self.rigsToFit

    def GetDronesByType(self):
        return self.dronesByType
