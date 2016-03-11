#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\microJumpDriver.py
import sys
from eveexceptions import UserError
from eveexceptions.const import UE_DIST, UE_AMT
from eve.server.script.mgt.dogma.microJumpDrive import CheckMicroJumpDrivePreconditions
from eve.server.script.mgt.dogma.microJumpDrive import StartMicroJumpSpoolup
from eve.server.script.mgt.dogma.microJumpDrive import EngageMicroJump
from eve.server.script.mgt.dogma.microJumpDrive import AbortMicroJump
from spacecomponents.common.componentConst import MICRO_JUMP_DRIVER_CLASS
from spacecomponents.common.componentregistry import ExportCall
from spacecomponents.common.components.component import Component
import logging
from spacecomponents.common.helper import IsActiveComponent
from spacecomponents.server.messages import MSG_ON_ADDED_TO_SPACE
from spacecomponents.server.messages import MSG_ON_REMOVED_FROM_SPACE
logger = logging.getLogger(__name__)

class MicroJumpDriver(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        logger.debug('Micro jump driver component created for item %s of type %s', itemID, typeID)
        self.interactionRange = self.attributes.interactionRange
        self.maxShipMass = self.attributes.maxShipMass
        self.spoolUpDurationMillisec = self.attributes.spoolUpDurationMillisec
        self.ballpark = None
        self.microJumpingShips = set()
        self.componentRegistry.SubscribeToItemMessage(itemID, MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.componentRegistry.SubscribeToItemMessage(itemID, MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)

    def Initialize(self, ballpark):
        self.ballpark = ballpark
        self.ownerID = ballpark.slims[self.itemID].ownerID

    def OnAddedToSpace(self, ballpark, spaceComponentDB):
        self.Initialize(ballpark)

    def OnRemovedFromSpace(self, ballpark, spaceComponentDB):
        for shipID in self.microJumpingShips:
            try:
                self.AbortMicroJumpForShip(shipID)
            except RuntimeError:
                sys.exc_clear()

        self.microJumpingShips = set()

    def CheckInteractionRange(self, shipID):
        if self.ballpark.DistanceBetween(shipID, self.itemID) > self.interactionRange:
            raise UserError('CantActivateMjdTooFarAway', dict(distance=(UE_DIST, self.interactionRange)))

    def CheckMaxShipMass(self, shipID):
        shipBall = self.ballpark.GetBall(shipID)
        if self.maxShipMass < shipBall.mass:
            raise UserError('CantActivateMjdShipToMassive', dict(maxMass=(UE_AMT, self.maxShipMass)))

    def InitiateMicroJump(self, shipID):
        StartMicroJumpSpoolup(self.ballpark, self.itemID, shipID)
        self.ApplyGraphicEffectToJumperShip(shipID)
        self.NotifySpectators()

    def AbortMicroJumpForShip(self, shipID):
        logger.debug('Aborting micro jump for ship %s', shipID)
        if self.IsItemAlive(shipID):
            AbortMicroJump(self.ballpark.dogmaLM, self.itemID, shipID)

    def FinalizeMicroJump(self, shipID):
        if self.IsItemAlive(self.itemID):
            if self.IsItemAlive(shipID):
                EngageMicroJump(self.ballpark.dogmaLM, self.itemID, shipID)
            else:
                logger.debug('Ship %s is no longer in space', shipID)

    def ProcessMicroJumpThread(self, shipID):
        try:
            self.CheckPreconditions(shipID)
        except UserError:
            return

        try:
            if shipID in self.microJumpingShips:
                logger.error('ShipID %s is marked as already in the process of jumping', shipID)
            else:
                self.microJumpingShips.add(shipID)
            self.InitiateMicroJump(shipID)
            self.SleepSim(self.spoolUpDurationMillisec)
            self.FinalizeMicroJump(shipID)
        except Exception:
            logger.exception('Micro jump thread failed to complete')
            self.AbortMicroJumpForShip(shipID)
        finally:
            self.microJumpingShips.discard(shipID)

    def IsItemAlive(self, itemID):
        return self.ballpark.HasBall(itemID) and not self.ballpark.IsExploding(itemID)

    def NotifySpectators(self):
        self.ballpark.UpdateSlimItemField(self.itemID, 'component_microJumpDriver', self.GetSimTime())

    def CheckPreconditions(self, shipID):
        try:
            self.CheckInteractionRange(shipID)
            self.CheckMaxShipMass(shipID)
            CheckMicroJumpDrivePreconditions(self.ballpark, shipID)
        except UserError as e:
            charID = self.ballpark.slims.get(shipID).charID
            self.ballpark.broker.machoNet.SinglecastByCharID(charID, 'OnRemoteMessage', *e.args)
            raise

    def ApplyGraphicEffectToJumperShip(self, shipID):
        args = (shipID,
         None,
         None,
         None,
         None,
         'effects.MicroJumpDriveEngage',
         0,
         1,
         0,
         self.spoolUpDurationMillisec)
        self.ballpark.AddToSystemHistory(shipID, ('OnSpecialFX', args))

    @ExportCall
    def StartMicroJumpDriveForShip(self, sess):
        self._StartMicroJumpDriveForShip(sess)

    def _StartMicroJumpDriveForShip(self, sess):
        if IsActiveComponent(self.componentRegistry, self.typeID, self.itemID):
            shipID = sess.shipid
            self.UThreadNew(self.ProcessMicroJumpThread, shipID)

    @staticmethod
    def GetEspTypeInfo(typeID, spaceComponentStaticData):
        attributes = spaceComponentStaticData.GetAttributes(typeID, MICRO_JUMP_DRIVER_CLASS)
        attributeStrings = ['Interaction Range: %0.f m' % attributes.interactionRange, 'Maximum Ship Mass: %0.f kg' % attributes.maxShipMass, 'Spoolup Duration: %0.f msec' % attributes.spoolUpDurationMillisec]
        infoString = '<br>'.join(attributeStrings)
        return infoString
