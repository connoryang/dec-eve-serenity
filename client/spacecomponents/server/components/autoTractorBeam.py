#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\autoTractorBeam.py
from eveexceptions import UserError
from dogma.const import effectTractorBeamCan
from spacecomponents.common.componentConst import AUTO_TRACTOR_BEAM_CLASS
from spacecomponents.common.components.component import Component
from spacecomponents.common import helper
from inventorycommon import const
import logging
from spacecomponents.server.messages import MSG_ON_BALLPARK_RELEASE
from ccpProfile import TimedFunction
from math import sqrt
logger = logging.getLogger(__name__)

class AutoTractorBeam(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        logger.debug('AutoTractorBeam component created for item %s of type %s', itemID, typeID)
        self.isThreadActive = False
        self.ballpark = None
        self.targetID = None
        self.ownerID = None
        self.SubscribeToMessage('OnAddedToSpace', self.OnAddedToSpace)
        self.SubscribeToMessage('OnRemovedFromSpace', self.OnRemovedFromSpace)
        self.SubscribeToMessage(MSG_ON_BALLPARK_RELEASE, self.OnBallparkRelease)
        self.SetIntervalInSeconds(self.attributes.cycleTimeSeconds)

    def SetBallpark(self, ballpark):
        self.ballpark = ballpark

    def OnAddedToSpace(self, ballpark, spaceComponentDB):
        self.SetBallpark(ballpark)
        self.ownerID = ballpark.slims[self.itemID].ownerID
        self.UThreadNew(self.TractorBeamWorker)

    def OnRemovedFromSpace(self, ballpark, spaceComponentDB):
        self.StopWorkerThread()
        self.DeactivateTractorBeam()

    def OnBallparkRelease(self):
        self.StopWorkerThread()

    def StopWorkerThread(self):
        logger.debug('%s worker thread is stopping', self.itemID)
        self.isThreadActive = False

    @TimedFunction('SpaceComponent::AutoTractorBeam::ProcessTractorBeam')
    def ProcessTractorBeam(self):
        if not helper.IsActiveComponent(self.componentRegistry, self.typeID, self.itemID):
            self.DeactivateTractorBeam()
            return
        if self.IsTractorBeamActive():
            if self.HasTargetArrived():
                logger.debug('%s target has arrived %s', self.itemID, self.targetID)
                self.DeactivateTractorBeam()
        else:
            targetID = self.FindValidTarget()
            if targetID is not None:
                self.ActivateTractorBeam(targetID)

    def TractorBeamWorker(self):
        if self.IsWorkerThreadActive():
            return
        self.isThreadActive = True
        logger.debug('%s starting worker thread', self.itemID)
        self.SleepSim(5000)
        try:
            while self.IsWorkerThreadActive():
                self.ProcessTractorBeam()
                self.SleepSim(self.intervalMS)

        finally:
            self.StopWorkerThread()

    def IsTractorBeamActive(self):
        return self.ballpark.dogmaLM.GetActiveEffectData(self.itemID, effectTractorBeamCan) is not None

    @TimedFunction('SpaceComponent::AutoTractorBeam::HasTargetArrived')
    def HasTargetArrived(self):
        distance = self.ballpark.GetSurfaceDist(self.itemID, self.targetID)
        logger.debug('AutoTractorBeam HasTargetArrived: ball surface distance from %s to %s is %s', self.itemID, self.targetID, distance)
        return distance <= self.attributes.minRange

    @TimedFunction('SpaceComponent::AutoTractorBeam::DeactivateTractorBeam')
    def DeactivateTractorBeam(self):
        self.ballpark.dogmaLM.StopEffect(effectTractorBeamCan, self.itemID, forced=True)
        self.ballpark.dogmaLM.RemoveTarget(self.itemID, self.targetID)
        logger.debug('%s deactivated tractor beam and unlocked %s', self.itemID, self.targetID)
        self.targetID = None
        self.ballpark.RemoveBubbleKeepAliveBall(self.itemID)

    @TimedFunction('SpaceComponent::AutoTractorBeam::FindValidTarget')
    def FindValidTarget(self):
        targetID = None
        validTargets = []
        ballIDsInRange = self.ballpark.GetBallIdsAndDistInRange(self.itemID, self.attributes.maxRange)
        for distanceSq, ballID in ballIDsInRange:
            if ballID < 0:
                continue
            ball = self.ballpark.balls[ballID]
            slimItem = self.ballpark.slims[ballID]
            if self.IsTargetValid(ball, slimItem, distanceSq):
                validTargets.append((distanceSq, ballID))

        if validTargets:
            validTargets.sort()
            targetID = validTargets[0][1]
            logger.debug('%s searched for a valid target and found %s', self.itemID, targetID)
        return targetID

    def IsTargetValid(self, ball, slimItem, distanceSq):
        if not (slimItem.typeID == const.typeCargoContainer or slimItem.groupID == const.groupWreck):
            return False
        if not self.ballpark.lootRights.HaveLootRight(ball.id, self.ownerID):
            return False
        if self.IfTargetIsAlreadyBeingTractored(ball):
            return False
        distance = sqrt(distanceSq) - ball.radius - self.ballpark.balls[self.itemID].radius
        logger.debug('IsTargetValid: Calculated distance from %s to %s is %s', slimItem.itemID, self.itemID, distance)
        if distance <= self.attributes.minRange:
            return False
        return True

    @TimedFunction('SpaceComponent::AutoTractorBeam::ActivateTractorBeam')
    def ActivateTractorBeam(self, targetID):
        try:
            self.DeactivateTractorBeam()
            self.ballpark.dogmaLM.AddTargetEx(self.itemID, targetID)
            self.ballpark.dogmaLM.ActivateWithContext(self.ownerID, self.itemID, effectTractorBeamCan, targetid=targetID, repeat=1000)
            self.targetID = targetID
            self.ballpark.AddBubbleKeepAliveBall(self.itemID)
            logger.debug('%s locked target %s and activated tractor beam', self.itemID, targetID)
        except UserError:
            logger.debug('%s Failed to lock and activate tractor beam on target %s', self.itemID, targetID)
            self.DeactivateTractorBeam()
        except:
            logger.exception('%s Failed to lock and activate tractor beam on target %s', self.itemID, targetID)
            self.DeactivateTractorBeam()
            raise

    def IsWorkerThreadActive(self):
        return self.isThreadActive

    def SetIntervalInSeconds(self, interval):
        self.intervalMS = max(1, interval) * 1000

    def IfTargetIsAlreadyBeingTractored(self, ball):
        return ball.isFree or self.ballpark.GetPendingStateChangeEvents(ball.id, 'SetBallFree')

    @staticmethod
    def GetEspTypeInfo(typeID, spaceComponentStaticData):
        attributes = spaceComponentStaticData.GetAttributes(typeID, AUTO_TRACTOR_BEAM_CLASS)
        attributeStrings = []
        attributeStrings.append('Cycle time: %d seconds' % attributes.cycleTimeSeconds)
        attributeStrings.append('Max range: %d m' % attributes.maxRange)
        attributeStrings.append('Min range: %d m' % attributes.minRange)
        infoString = '<br>'.join(attributeStrings)
        return infoString
