#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\decay.py
import logging
from carbon.common.lib import const
from eve.common.script.mgt.appLogConst import eventSpaceComponentDecayed
import datetimeutils
from eveexceptions import UserError
from spacecomponents.common.componentConst import DECAY_CLASS
from timedilation import WallclockTimeToSimTime, SimTimeToWallclockTime
logger = logging.getLogger(__name__)
MINIMUM_DECAY_REFRESH_INTERVAL = 10 * const.MIN
MSG_ON_PLAYER_INTERACTION = 'OnPlayerInteraction'

class Decay(object):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        self.itemID = itemID
        self.typeID = typeID
        self.attributes = attributes
        self.componentRegistry = componentRegistry
        self.eventLogger = self.componentRegistry.eventLogger
        self.GetWallclockTime = componentRegistry.asyncFuncs.GetWallclockTime
        self.GetSimTime = componentRegistry.asyncFuncs.GetSimTime
        self.SleepSim = componentRegistry.asyncFuncs.SleepSim
        self.TimeDiffInMs = componentRegistry.asyncFuncs.TimeDiffInMs
        self.UThreadNew = componentRegistry.asyncFuncs.UThreadNew
        self.decayTimestamp = None
        componentRegistry.SubscribeToItemMessage(self.itemID, 'OnAddedToSpace', self.OnAddedToSpace)
        componentRegistry.SubscribeToItemMessage(self.itemID, 'OnRemovedFromSpace', self.OnRemovedFromSpace)
        componentRegistry.SubscribeToItemMessage(self.itemID, MSG_ON_PLAYER_INTERACTION, self.OnPlayerInteraction)

    def OnAddedToSpace(self, ballpark, spaceComponentDB):
        logger.debug('Decay.OnAddedToSpace %d', self.itemID)
        self.ballpark = ballpark
        self.spaceComponentDB = spaceComponentDB
        state = spaceComponentDB.DecayStates_Select(self.itemID)
        if len(state) == 0:
            decayTimestamp = self.GetSimTime() + self.attributes.durationSeconds * const.SEC
        else:
            state = state[0]
            simTimeNow = self.GetSimTime()
            wallclockTimeNow = self.GetWallclockTime()
            decayTimestamp = WallclockTimeToSimTime(state.decayTimestamp, wallclockTimeNow, simTimeNow)
        self.SetDecayTimestamp(decayTimestamp)

    def OnRemovedFromSpace(self, ballpark, spaceComponentDB):
        logger.debug('Decay.OnRemovedFromSpace %d', self.itemID)
        self.decayTimestamp = None
        spaceComponentDB.DecayStates_Delete(self.itemID)

    def OnPlayerInteraction(self):
        logger.debug('Decay.OnPlayerInteraction %d', self.itemID)
        extendedDecayTimestamp = self.GetSimTime() + self.attributes.durationSeconds * const.SEC
        if self.TimeDiffInMs(self.decayTimestamp, extendedDecayTimestamp) < MINIMUM_DECAY_REFRESH_INTERVAL / 10000:
            return
        self.SetDecayTimestamp(extendedDecayTimestamp)

    def SetDecayTimestamp(self, timestamp):
        logger.debug('Decay.SetDecayTimestamp %d %s', self.itemID, timestamp)
        if self.decayTimestamp == timestamp:
            return
        if timestamp < self.GetSimTime():
            logger.debug('Component has past decay time, insta-decaying now %d %s', self.itemID, self.decayTimestamp)
            self.decayTimestamp = self.GetSimTime() + const.SEC * 5
        else:
            self.decayTimestamp = timestamp
            PersistToDB(self, self.spaceComponentDB)
        self.UpdateSlimItem()
        self.UThreadNew(self.BeginDelayedDecay)

    def BeginDelayedDecay(self):
        decayTimestamp = self.decayTimestamp
        logger.debug('Decay.BeginDelayedDecay %d %s', self.itemID, decayTimestamp)
        delay = self.TimeDiffInMs(self.GetSimTime(), decayTimestamp)
        while delay > 0:
            self.SleepSim(min(delay, 12 * const.HOUR / 10000))
            if decayTimestamp != self.decayTimestamp:
                return
            delay = self.TimeDiffInMs(self.GetSimTime(), decayTimestamp)

        logger.debug('Decay completed - exploding %d', self.itemID)
        self.decayTimestamp = None
        self.ballpark.ExplodeEx(self.itemID)
        item = self.ballpark.inventory2.GetItem(self.itemID)
        self.eventLogger.LogDecayed(item)
        self.ballpark.dbLog.LogItemGenericEvent(None, eventSpaceComponentDecayed, self.itemID, referenceID=self.ballpark.solarsystemID, int_1=self.typeID)

    def HandleSlashCommand(self, action, ballpark, spaceComponentDB):
        logger.debug('Decay.HandleSlashCommand %d %s', self.itemID, action)
        usageString = 'Usage: /spacecomponent decay ITEMID decay now|DELAY_SECONDS'
        if len(action) != 2:
            raise UserError('SlashError', {'reason': usageString})
        if action[0].lower() == 'decay':
            if action[1].lower() == 'now':
                delay = 1
            else:
                delay = int(action[1])
                if delay < 1:
                    raise UserError('SlashError', {'reason': usageString})
            decayTimestamp = self.GetSimTime() + delay * const.SEC
            self.SetDecayTimestamp(decayTimestamp)
        else:
            raise UserError('SlashError', {'reason': usageString})

    def GetDebugText(self):
        simTimeNow = self.GetSimTime()
        wallclockTimeNow = self.GetWallclockTime()
        decayTimestampWallclock = SimTimeToWallclockTime(self.decayTimestamp, simTimeNow, wallclockTimeNow)
        timeStr = datetimeutils.any_to_datetime(decayTimestampWallclock).strftime('%Y-%m-%d %H:%M:%S')
        return 'Will decay at %s (subject to time-dilation)' % (timeStr,)

    def UpdateSlimItem(self):
        logger.debug('Decay.UpdateSlimItemFromComponent %s %s', self.itemID, self.decayTimestamp)
        self.ballpark.UpdateSlimItemField(self.itemID, 'component_decay', self.decayTimestamp)

    @staticmethod
    def GetEspStateInfo(itemID, dbspacecomponent, espWriter):
        state = dbspacecomponent.DecayStates_Select(itemID)
        if len(state):
            state = state[0]
            return 'Will decay at: <b>%s</b> (subject to time-dilation and solar-system being loaded)' % datetimeutils.any_to_datetime(state.decayTimestamp).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return 'No info in DB'

    @staticmethod
    def GetEspTypeInfo(typeID, spaceComponentStaticData):
        attributes = spaceComponentStaticData.GetAttributes(typeID, DECAY_CLASS)
        attributeStrings = []
        duration = attributes.durationSeconds
        attributeStrings.append('Decay time: %d seconds' % duration)
        infoString = '<br>'.join(attributeStrings)
        return infoString


def PersistToDB(component, spaceComponentDB):
    if component.decayTimestamp is None:
        decayTimestampWallclock = None
    else:
        simTimeNow = component.GetSimTime()
        wallclockTimeNow = component.GetWallclockTime()
        decayTimestampWallclock = SimTimeToWallclockTime(component.decayTimestamp, simTimeNow, wallclockTimeNow)
    logger.debug('Decay.PersistToDB %d, %s', component.itemID, decayTimestampWallclock)
    spaceComponentDB.DecayStates_Update(component.itemID, decayTimestampWallclock)


def HandleSlashCommand(itemID, action, ballpark, componentRegistry, spaceComponentDB):
    component = componentRegistry.GetComponentsByItemID(itemID)[DECAY_CLASS]
    component.HandleSlashCommand(action, ballpark, spaceComponentDB)
