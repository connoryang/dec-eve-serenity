#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\scanblockregistry.py
from collections import defaultdict
import logging
from ccpProfile import TimedFunction
from inventorycommon.const import groupCosmicAnomaly, groupCosmicSignature
logger = logging.getLogger(__name__)
UNBLOCKABLE_GROUPS = [groupCosmicAnomaly, groupCosmicSignature]

class ScanBlockRegistry:

    def __init__(self, ballpark, scanLocation):
        self.ballpark = ballpark
        self.scanLocation = scanLocation
        self.blockersByBubbleID = defaultdict(lambda : defaultdict(int))
        self.systemWideBlockersByBallID = set()
        self.blocksSelfByBallID = set()

    def RegisterScanBlockingBall(self, ballID, blockRadius, blocksSelf = False, systemWideBlock = False):
        logger.debug('RegisterScanBlockingBall %s %s', ballID, blockRadius)
        bubbleID = self.ballpark.GetBall(ballID).newBubbleId
        blockers = self.blockersByBubbleID[bubbleID]
        blockers[ballID] = blockRadius
        if blocksSelf:
            self.blocksSelfByBallID.add(ballID)
        if systemWideBlock:
            self.systemWideBlockersByBallID.add(ballID)

    def UnregisterScanBlockingBall(self, ballID):
        logger.debug('UnregisterScanBlockingBall %s', ballID)
        bubbleID = self.ballpark.GetBall(ballID).newBubbleId
        blockers = self.blockersByBubbleID.get(bubbleID)
        if blockers is not None:
            blockers.pop(ballID, None)
            if len(blockers) == 0:
                del self.blockersByBubbleID[bubbleID]
        self.systemWideBlockersByBallID.discard(ballID)
        self.blocksSelfByBallID.discard(ballID)

    @TimedFunction('ScanBlockRegistry::IsScanBlocked')
    def IsScanBlocked(self, ballID):
        ball = self.ballpark.GetBallOrNone(ballID)
        if ball is None:
            return False
        if ball.isGlobal:
            return False
        if len(self.systemWideBlockersByBallID) > 0:
            return True
        slimItem = self.ballpark.slims[ballID]
        if slimItem.groupID in UNBLOCKABLE_GROUPS:
            return False
        bubbleID = ball.newBubbleId
        blockers = self.blockersByBubbleID.get(bubbleID)
        if blockers is not None:
            if ballID in blockers and ballID not in self.blocksSelfByBallID:
                return False
            for blockerBallID, blockRadius in blockers.iteritems():
                if self.ballpark.GetSurfaceDist(ballID, blockerBallID) < blockRadius:
                    return True

        return False
