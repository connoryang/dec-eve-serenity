#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\reinforce.py
import logging
from carbon.common.lib import const
from eve.common.script.mgt.appLogConst import eventSpaceComponentEnterReinforce, eventSpaceComponentExitReinforce
import datetimeutils
from eveexceptions import UserError
from spacecomponents.common.componentConst import REINFORCE_CLASS
from spacecomponents.common import helper
from spacecomponents.server.messages import MSG_ON_DAMAGE_STATE_CHANGE
logger = logging.getLogger(__name__)

class Reinforce(object):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        self.itemID = itemID
        self.typeID = typeID
        self.attributes = attributes
        self.componentRegistry = componentRegistry
        self.GetWallclockTime = componentRegistry.asyncFuncs.GetWallclockTime
        self.SleepWallclock = componentRegistry.asyncFuncs.SleepWallclock
        self.TimeDiffInMs = componentRegistry.asyncFuncs.TimeDiffInMs
        self.UThreadNew = componentRegistry.asyncFuncs.UThreadNew
        self.isReinforced = False
        self.reinforceTimestamp = None
        self.lastShieldLevel = None
        self.reinforcedEntryLevel = 0.25
        self.reinforcedExitLevel = 0.001
        componentRegistry.SubscribeToItemMessage(self.itemID, 'OnAddedToSpace', self.OnAddedToSpace)
        componentRegistry.SubscribeToItemMessage(self.itemID, 'OnRemovedFromSpace', self.OnRemovedFromSpace)
        componentRegistry.SubscribeToItemMessage(self.itemID, MSG_ON_DAMAGE_STATE_CHANGE, self.OnDamageStateChange)

    def OnAddedToSpace(self, ballpark, spaceComponentDB):
        logger.debug('Reinforce.OnAddedToSpace %d', self.itemID)
        self.ballpark = ballpark
        self.spaceComponentDB = spaceComponentDB
        state = spaceComponentDB.ReinforceStates_Select(self.itemID)
        if len(state) == 0:
            self.isReinforced = False
            self.reinforceTimestamp = None
            PersistToDB(self, spaceComponentDB)
        else:
            state = state[0]
            self.isReinforced = state.reinforced
            self.reinforceTimestamp = state.reinforceTimestamp
            if self.isReinforced:
                if self.reinforceTimestamp < self.GetWallclockTime():
                    self.ExitReinforced()
                else:
                    self.SetBallInvulnerability(True)
                    self.UThreadNew(self.ReinforceCountdownThread)
        UpdateSlimItemFromComponent(self, ballpark)

    def OnRemovedFromSpace(self, ballpark, spaceComponentDB):
        logger.debug('Reinforce.OnRemovedFromSpace %d', self.itemID)
        self.isReinforced = False
        self.reinforceTimestamp = None
        spaceComponentDB.ReinforceStates_Delete(self.itemID)

    def CanEnterReinforce(self, shieldLevel):
        if shieldLevel > self.reinforcedEntryLevel:
            if helper.IsActiveComponent(self.componentRegistry, self.typeID, self.itemID):
                return True
        return False

    def OnDamageStateChange(self, oldDamageState, newDamageState):
        newShieldLevel = newDamageState[0][0]
        if oldDamageState is not None:
            oldShieldLevel = oldDamageState[0][0]
        else:
            oldShieldLevel = self.lastShieldLevel
        if oldShieldLevel is None:
            self.lastShieldLevel = newShieldLevel
        elif helper.IsActiveComponent(self.componentRegistry, self.typeID, self.itemID) and oldShieldLevel >= self.reinforcedEntryLevel > newShieldLevel:
            self.EnterReinforced()
        else:
            self.lastShieldLevel = newShieldLevel

    def IsReinforced(self):
        return self.isReinforced

    def SetBallInvulnerability(self, isInvulnerable):
        if isInvulnerable:
            self.ballpark.MakeInvulnerablePermanently(self.itemID, 'ReinforceComponent')
        else:
            self.ballpark.CancelCurrentInvulnerability(self.itemID)

    def EnterReinforced(self):
        if self.isReinforced:
            return
        self.isReinforced = True
        self.reinforceTimestamp = self.GetWallclockTime() + self.attributes.durationSeconds * const.SEC
        PersistToDB(self, self.spaceComponentDB)
        UpdateSlimItemFromComponent(self, self.ballpark)
        self.SetBallInvulnerability(True)
        self.lastShieldLevel = self.reinforcedExitLevel
        self.UThreadNew(self.ReinforceCountdownThread)
        self.ballpark.dbLog.LogItemGenericEvent(None, eventSpaceComponentEnterReinforce, self.itemID, referenceID=self.ballpark.solarsystemID, int_1=self.typeID, int_2=self.attributes.durationSeconds)

    def ExitReinforced(self):
        if not self.isReinforced:
            return
        self.isReinforced = False
        self.reinforceTimestamp = None
        PersistToDB(self, self.spaceComponentDB)
        UpdateSlimItemFromComponent(self, self.ballpark)
        self.ballpark.dogmaLM.SetDamageState(self.itemID, {'shield': self.reinforcedExitLevel})
        self.ballpark.dogmaLM.PersistItem(self.itemID)
        self.SetBallInvulnerability(False)
        self.ballpark.dbLog.LogItemGenericEvent(None, eventSpaceComponentExitReinforce, self.itemID, int_1=self.typeID, referenceID=self.ballpark.solarsystemID)

    def ReinforceCountdownThread(self):
        reinforceTimestamp = self.reinforceTimestamp
        logger.debug('Reinforce.ReinforceCountdownThread %d %s', self.itemID, reinforceTimestamp)
        delay = self.TimeDiffInMs(self.GetWallclockTime(), reinforceTimestamp)
        while delay > 0:
            self.SleepWallclock(min(delay, 12 * const.HOUR / 10000))
            if reinforceTimestamp != self.reinforceTimestamp:
                return
            delay = self.TimeDiffInMs(self.GetWallclockTime(), reinforceTimestamp)

        logger.debug('Reinforce period completed - %d', self.itemID)
        self.ExitReinforced()

    def HandleSlashCommand(self, action, ballpark, spaceComponentDB):
        logger.debug('Reinforce.HandleSlashCommand %d %s', self.itemID, action)
        if action[0].lower() == 'on':
            if not self.IsReinforced():
                self.EnterReinforced()
            else:
                raise UserError('SlashError', {'reason': 'Reinforce component %s is already reinforced!' % (self.itemID,)})
        elif action[0].lower() == 'off':
            if self.IsReinforced():
                self.ExitReinforced()
            else:
                raise UserError('SlashError', {'reason': 'Reinforce component %s is not currently reinforced!' % (self.itemID,)})
        else:
            raise UserError('SlashError', {'reason': 'Usage: /spacecomponent reinforce ITEMID on|off'})

    def GetDebugText(self):
        if self.isReinforced:
            timeStr = datetimeutils.any_to_datetime(self.reinforceTimestamp).strftime('%Y-%m-%d %H:%M:%S')
            return '<color=red>Reinforced</color> until %s' % (timeStr,)
        else:
            return '<color=green>Not reinforced</color>'

    @staticmethod
    def GetEspStateInfo(itemID, dbspacecomponent, espWriter):
        state = dbspacecomponent.ReinforceStates_Select(itemID)
        if len(state):
            state = state[0]
            if not state.reinforced:
                return 'Not currently Reinforced'
            else:
                return '<b>Is Reinforced</b> - Will exit at: <b>%s</b> (subject to solar-system being loaded)' % datetimeutils.any_to_datetime(state.reinforceTimestamp).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return 'No info in DB'

    @staticmethod
    def GetEspTypeInfo(typeID, spaceComponentStaticData):
        attributes = spaceComponentStaticData.GetAttributes(typeID, REINFORCE_CLASS)
        attributeStrings = []
        duration = attributes.durationSeconds
        attributeStrings.append('Reinforce time: %d seconds' % duration)
        infoString = '<br>'.join(attributeStrings)
        return infoString


def UpdateSlimItemFromComponent(component, ballpark):
    logger.debug('Reinforce.UpdateSlimItemFromComponent %d %d %s', component.itemID, component.isReinforced, component.reinforceTimestamp)
    ballpark.UpdateSlimItemField(component.itemID, 'component_reinforce', (component.isReinforced, component.reinforceTimestamp))


def PersistToDB(component, spaceComponentDB):
    logger.debug('Reinforce.PersistToDB %d, %d, %s', component.itemID, component.isReinforced, component.reinforceTimestamp)
    spaceComponentDB.ReinforceStates_Update(component.itemID, component.isReinforced, component.reinforceTimestamp)


def HandleSlashCommand(itemID, action, ballpark, componentRegistry, spaceComponentDB):
    component = componentRegistry.GetComponentsByItemID(itemID)[REINFORCE_CLASS]
    component.HandleSlashCommand(action, ballpark, spaceComponentDB)
