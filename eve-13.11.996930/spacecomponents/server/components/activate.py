#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\activate.py
import logging
from carbon.common.lib import const
from eve.common.script.mgt.appLogConst import eventSpaceComponentBeginActivating, eventSpaceComponentActivated
import datetimeutils
from eveexceptions import UserError
from spacecomponents.common.componentConst import ACTIVATE_CLASS
from spacecomponents.common.components.component import Component
from spacecomponents.server.messages import MSG_ON_ACTIVE
from timedilation import SimTimeToWallclockTime, WallclockTimeToSimTime
logger = logging.getLogger(__name__)

class Activate(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.eventLogger = self.componentRegistry.eventLogger
        self.GetWallclockTime = componentRegistry.asyncFuncs.GetWallclockTime
        self.GetSimTime = componentRegistry.asyncFuncs.GetSimTime
        self.SleepSim = componentRegistry.asyncFuncs.SleepSim
        self.TimeDiffInMs = componentRegistry.asyncFuncs.TimeDiffInMs
        self.UThreadNew = componentRegistry.asyncFuncs.UThreadNew
        self.isActive = False
        self.activeTimestamp = None
        componentRegistry.SubscribeToItemMessage(self.itemID, 'OnAddedToSpace', self.OnAddedToSpace)
        componentRegistry.SubscribeToItemMessage(self.itemID, 'OnRemovedFromSpace', self.OnRemovedFromSpace)

    def IsActive(self):
        return self.isActive

    def OnAddedToSpace(self, ballpark, spaceComponentDB):
        logger.debug('Activate.OnAddedToSpace %d', self.itemID)
        state = spaceComponentDB.ActivateStates_Select(self.itemID)
        if len(state) == 0:
            self.isActive = False
            self.activeTimestamp = self.GetSimTime() + self.attributes.durationSeconds * const.SEC
            UpdateSlimItemFromComponent(self, ballpark)
            PersistToDB(self, spaceComponentDB)
            self.UThreadNew(BeginDelayedActivation, self, spaceComponentDB, ballpark)
            ballpark.dbLog.LogItemGenericEvent(None, eventSpaceComponentBeginActivating, self.itemID, referenceID=ballpark.solarsystemID, int_1=self.typeID, int_2=self.attributes.durationSeconds)
        else:
            state = state[0]
            self.isActive = state.activated
            if state.activeTimestamp is None:
                self.activeTimestamp = None
                UpdateSlimItemFromComponent(self, ballpark)
                if self.isActive:
                    self.SendMessage(MSG_ON_ACTIVE, ballpark)
            else:
                simTimeNow = self.GetSimTime()
                wallclockTimeNow = self.GetWallclockTime()
                self.activeTimestamp = WallclockTimeToSimTime(state.activeTimestamp, wallclockTimeNow, simTimeNow)
                if self.activeTimestamp < self.GetSimTime():
                    BecomeActive(self, spaceComponentDB, ballpark)
                else:
                    UpdateSlimItemFromComponent(self, ballpark)
                    self.UThreadNew(BeginDelayedActivation, self, spaceComponentDB, ballpark)

    def OnRemovedFromSpace(self, ballpark, spaceComponentDB):
        logger.debug('Activate.OnRemovedFromSpace %d', self.itemID)
        self.isActive = False
        self.activeTimestamp = None
        spaceComponentDB.ActivateStates_Delete(self.itemID)

    def HandleSlashCommand(self, action, ballpark, spaceComponentDB):
        logger.debug('Activate.HandleSlashCommand %d %s', self.itemID, action)
        if action[0].lower() == 'makeactive':
            if not self.isActive:
                BecomeActive(self, spaceComponentDB, ballpark)
            else:
                raise UserError('SlashError', {'reason': 'Component is already active'})
        else:
            raise UserError('SlashError', {'reason': 'Usage: /spacecomponent activate ITEMID makeactive'})

    def GetDebugText(self):
        if self.isActive:
            return '<color=green>Active</color>'
        else:
            simTimeNow = self.GetSimTime()
            wallclockTimeNow = self.GetWallclockTime()
            activeTimestampWallclock = SimTimeToWallclockTime(self.activeTimestamp, simTimeNow, wallclockTimeNow)
            timeStr = datetimeutils.any_to_datetime(activeTimestampWallclock).strftime('%Y-%m-%d %H:%M:%S')
            return 'Will activate at %s (subject to time-dilation)' % (timeStr,)

    @staticmethod
    def GetEspStateInfo(itemID, dbspacecomponent, espWriter):
        state = dbspacecomponent.ActivateStates_Select(itemID)
        if len(state):
            state = state[0]
            if state.activated:
                return '<b>Activated</b>'
            if state.activeTimestamp:
                return 'Will become active at: <b>%s</b> (subject to time-dilation and solar-system being loaded)' % datetimeutils.any_to_datetime(state.activeTimestamp).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return 'No info in DB'

    @staticmethod
    def GetEspTypeInfo(typeID, spaceComponentStaticData):
        attributes = spaceComponentStaticData.GetAttributes(typeID, ACTIVATE_CLASS)
        attributeStrings = []
        duration = attributes.durationSeconds
        attributeStrings.append('Activation time: %d seconds' % duration)
        infoString = '<br>'.join(attributeStrings)
        return infoString


def UpdateSlimItemFromComponent(component, ballpark):
    logger.debug('Activate.UpdateSlimItemFromComponent %d %d %s', component.itemID, component.isActive, component.activeTimestamp)
    ballpark.UpdateSlimItemField(component.itemID, 'component_activate', (component.isActive, component.activeTimestamp))


def BecomeActive(component, spaceComponentDB, ballpark):
    logger.debug('Activate.BecomeActive %d', component.itemID)
    component.isActive = True
    component.activeTimestamp = None
    PersistToDB(component, spaceComponentDB)
    UpdateSlimItemFromComponent(component, ballpark)
    component.SendMessage(MSG_ON_ACTIVE, ballpark)
    item = ballpark.inventory2.GetItem(component.itemID)
    component.eventLogger.LogBecomeActive(item)
    ballpark.dbLog.LogItemGenericEvent(None, eventSpaceComponentActivated, component.itemID, referenceID=ballpark.solarsystemID, int_1=component.typeID)


def BeginDelayedActivation(component, spaceComponentDB, ballpark):
    now = component.GetSimTime()
    activeTimestamp = component.activeTimestamp
    logger.debug('Activate.BeginDelayedActivation %d %s', component.itemID, activeTimestamp)
    delay = component.TimeDiffInMs(now, activeTimestamp)
    if delay > 0:
        component.SleepSim(delay)
    if activeTimestamp != component.activeTimestamp:
        return
    BecomeActive(component, spaceComponentDB, ballpark)


def PersistToDB(component, spaceComponentDB):
    if component.activeTimestamp is None:
        activeTimestampWallclock = None
    else:
        simTimeNow = component.GetSimTime()
        wallclockTimeNow = component.GetWallclockTime()
        activeTimestampWallclock = SimTimeToWallclockTime(component.activeTimestamp, simTimeNow, wallclockTimeNow)
    logger.debug('Activate.PersistToDB %d, %d, %s', component.itemID, component.isActive, activeTimestampWallclock)
    spaceComponentDB.ActivateStates_Update(component.itemID, component.isActive, activeTimestampWallclock)


def HandleSlashCommand(itemID, action, ballpark, componentRegistry, spaceComponentDB):
    component = componentRegistry.GetComponentsByItemID(itemID)[ACTIVATE_CLASS]
    component.HandleSlashCommand(action, ballpark, spaceComponentDB)
