#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\entosis\spacecomponents\client\entosisSovereigntyStructure.py
import logging
from entosis.spacecomponents.client.entosisCaptureTarget import EntosisCaptureTarget
TIMER_COLORS = ((1.0, 1.0, 1.0, 0.5), (1.0, 1.0, 1.0, 0.25), (0.3, 0.3, 0.3, 1.0))
logger = logging.getLogger(__name__)

class EntosisSovereigntyStructure(EntosisCaptureTarget):

    def __init__(self, *args):
        EntosisCaptureTarget.__init__(self, *args)

    def _OnAddedToSpace(self, slimItem):
        EntosisCaptureTarget._OnAddedToSpace(self, slimItem)
        self.__UpdateUI()

    def _OnSlimItemUpdated(self, slimItem):
        EntosisCaptureTarget._OnSlimItemUpdated(self, slimItem)
        self.__UpdateUI()

    def _OnBracketCreated(self, bracket, slimItem):
        EntosisCaptureTarget._OnBracketCreated(self, bracket, slimItem)
        self.__UpdateUI()

    def __UpdateUI(self):
        self.SetTimerColor(*TIMER_COLORS)
