#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\shipFighterState.py
from collections import namedtuple
import signals
import logging
from eve.common.script.mgt.fighterConst import TUBE_STATE_READY, TUBE_STATE_EMPTY
logger = logging.getLogger('ShipFighterState')
FighterInSpaceTuple = namedtuple('FighterInSpaceTuple', ['itemID',
 'typeID',
 'tubeFlagID',
 'squadronSize'])
FighterInTubeTuple = namedtuple('FighterInTubeTuple', ['itemID',
 'typeID',
 'tubeFlagID',
 'squadronSize'])
TubeStatusTuple = namedtuple('TubeStatusTuple', ['statusID', 'startTime', 'endTime'])
EMPTY_TUBE = TubeStatusTuple(statusID=TUBE_STATE_EMPTY, startTime=None, endTime=None)

class ShipFighterState(object):
    __notifyevents__ = ['ProcessActiveShipChanged',
     'OnFighterTubeContentUpdate',
     'OnFighterTubeContentEmpty',
     'OnFighterAddedToController',
     'OnFighterRemovedFromController',
     'OnFighterTubeTaskStatus',
     'OnFighterAbilitySlotActivated',
     'OnFighterAbilitySlotDeactivated']
    fightersSvc = None
    shipID = None
    fightersInLaunchTubes = None
    fightersInSpace = None
    statusByTube = None
    activeAbilities = None
    signalOnFighterTubeStateUpdate = None
    signalOnFighterTubeContentUpdate = None
    signalOnFighterInSpaceUpdate = None
    signalOnAbilityActivated = None
    signalOnAbilityDeactivated = None

    def __init__(self, fightersSvc):
        self.fightersSvc = fightersSvc
        sm.RegisterNotify(self)
        self.fightersInLaunchTubes = {}
        self.fightersInSpace = {}
        self.statusByTube = {}
        self.activeAbilities = set()
        self._UpdateStateForShip(session.shipid)
        self.signalOnFighterTubeStateUpdate = signals.Signal()
        self.signalOnFighterTubeContentUpdate = signals.Signal()
        self.signalOnFighterInSpaceUpdate = signals.Signal()
        self.signalOnAbilityActivated = signals.Signal()
        self.signalOnAbilityDeactivated = signals.Signal()

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        self._UpdateStateForShip(shipID)

    def OnFighterTubeContentUpdate(self, tubeFlagID, fighterID, fighterTypeID, squadronSize):
        fighterInTube = FighterInTubeTuple(fighterID, fighterTypeID, tubeFlagID, squadronSize)
        self.fightersInLaunchTubes[tubeFlagID] = fighterInTube
        self.signalOnFighterTubeContentUpdate(tubeFlagID)

    def OnFighterTubeContentEmpty(self, tubeFlagID):
        del self.fightersInLaunchTubes[tubeFlagID]
        self.signalOnFighterTubeContentUpdate(tubeFlagID)

    def OnFighterAddedToController(self, fighterID, fighterTypeID, tubeFlagID, squadronSize):
        logger.debug('OnFighterAddedToController %s', (fighterID,
         fighterTypeID,
         tubeFlagID,
         squadronSize))
        fighterInSpace = FighterInSpaceTuple(fighterID, fighterTypeID, tubeFlagID, squadronSize)
        self.fightersInSpace[tubeFlagID] = fighterInSpace
        self.signalOnFighterInSpaceUpdate(tubeFlagID)

    def OnFighterRemovedFromController(self, fighterID, tubeFlagID):
        logger.debug('OnFighterRemovedFromController %s', (fighterID, tubeFlagID))
        self.fightersInSpace.pop(tubeFlagID)
        self.signalOnFighterInSpaceUpdate(tubeFlagID)

    def OnFighterTubeTaskStatus(self, tubeFlagID, statusID, statusStartTime, statusEndTime):
        logger.debug('OnFighterTubeTaskStatus %s', (tubeFlagID,
         statusID,
         statusStartTime,
         statusEndTime))
        self._SetTubeStatus(tubeFlagID, statusID, statusStartTime, statusEndTime)
        self.signalOnFighterTubeStateUpdate(tubeFlagID)

    def OnFighterAbilitySlotActivated(self, fighterID, abilitySlotID):
        logger.debug('OnFighterAbilitySlotActivated %s', (fighterID, abilitySlotID))
        self.activeAbilities.add((fighterID, abilitySlotID))
        self.signalOnAbilityActivated(fighterID, abilitySlotID)

    def OnFighterAbilitySlotDeactivated(self, fighterID, abilitySlotID):
        logger.debug('OnFighterAbilitySlotDeactivated %s', (fighterID, abilitySlotID))
        self.activeAbilities.discard((fighterID, abilitySlotID))
        self.signalOnAbilityDeactivated(fighterID, abilitySlotID)

    def _UpdateStateForShip(self, shipID):
        self.shipID = shipID
        self.fightersInLaunchTubes.clear()
        self.statusByTube.clear()
        self.activeAbilities.clear()
        fightersInTubes, fightersInSpace = self.fightersSvc.GetFightersForShip()
        for tubeFlagID, fighterItemID, fighterTypeID, squadronSize in fightersInTubes:
            fighterInTube = FighterInTubeTuple(fighterItemID, fighterTypeID, tubeFlagID, squadronSize)
            self.fightersInLaunchTubes[tubeFlagID] = fighterInTube
            self._SetTubeStatus(tubeFlagID, TUBE_STATE_READY, None, None)

        for tubeFlagID, fighterItemID, fighterTypeID, squadronSize in fightersInSpace:
            fighterInSpace = FighterInSpaceTuple(fighterItemID, fighterTypeID, tubeFlagID, squadronSize)
            self.fightersInSpace[tubeFlagID] = fighterInSpace

    def _SetTubeStatus(self, tubeFlagID, statusID, startTime, endTime):
        self.statusByTube[tubeFlagID] = TubeStatusTuple(statusID=statusID, startTime=startTime, endTime=endTime)

    def GetFightersInTube(self, tubeFlagID):
        return self.fightersInLaunchTubes.get(tubeFlagID)

    def GetFightersInSpace(self, tubeFlagID):
        return self.fightersInSpace.get(tubeFlagID)

    def GetTubeStatus(self, tubeFlagID):
        return self.statusByTube.get(tubeFlagID, EMPTY_TUBE)

    def IsAbilityActive(self, fighterID, abilitySlotID):
        return (fighterID, abilitySlotID) in self.activeAbilities


def GetShipFighterState():
    return sm.GetService('fighters').shipFighterState
