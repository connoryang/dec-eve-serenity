#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\entosis\spacecomponents\client\entosisCommandNode.py
import logging
from entosis.spacecomponents.client.entosisCaptureTarget import EntosisCaptureTarget
from entosis.ui import IsSameCaptureTeam
TIMER_COLORS_FRIENDLY = ((0.0, 1.0, 0.0, 0.8), (0.0, 1.0, 0.0, 0.35), (0.0, 0.3, 0.0, 1.0))
TIMER_COLORS_HOSTILE = ((1.0, 1.0, 1.0, 0.5), (1.0, 1.0, 1.0, 0.25), (0.3, 0.3, 0.3, 1.0))
logger = logging.getLogger(__name__)

class EntosisCommandNode(EntosisCaptureTarget):
    campaign_sourceInfo = None
    twoDirectionalCapture = True

    def __init__(self, *args):
        EntosisCaptureTarget.__init__(self, *args)

    def _OnAddedToSpace(self, slimItem):
        EntosisCaptureTarget._OnAddedToSpace(self, slimItem)
        self.__SetCampaignSourceInfoFromSlimItem(slimItem)
        self.__UpdateUI()

    def _OnSlimItemUpdated(self, slimItem):
        EntosisCaptureTarget._OnSlimItemUpdated(self, slimItem)
        self.__SetCampaignSourceInfoFromSlimItem(slimItem)
        self.__UpdateUI()

    def _OnBracketCreated(self, bracket, slimItem):
        self.__SetCampaignSourceInfoFromSlimItem(slimItem)
        EntosisCaptureTarget._OnBracketCreated(self, bracket, slimItem)
        self.__UpdateUI()

    def __UpdateUI(self):
        if IsSameCaptureTeam(session.allianceid, self.scoringTeamId):
            self.SetTimerColor(*TIMER_COLORS_FRIENDLY)
        else:
            self.SetTimerColor(*TIMER_COLORS_HOSTILE)

    def __SetCampaignSourceInfoFromSlimItem(self, slimItem):
        self.campaign_sourceInfo = getattr(slimItem, 'campaign_sourceInfo', None)
