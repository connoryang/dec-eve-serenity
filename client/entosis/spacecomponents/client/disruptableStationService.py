#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\entosis\spacecomponents\client\disruptableStationService.py
import logging
from entosis.spacecomponents.client.entosisCaptureTarget import EntosisCaptureTarget
BRACKET_COLOR_ENABLED = (1.0, 1.0, 1.0)
TIMER_COLORS_ENABLED = ((1.0, 1.0, 1.0, 0.5), (1.0, 1.0, 1.0, 0.25), (0.3, 0.3, 0.3, 1.0))
BRACKET_COLOR_DISABLED = (1.0, 0.0, 0.0)
TIMER_COLORS_DISABLED = ((1.0, 0.0, 0.0, 0.8), (1.0, 0.0, 0.0, 0.35), (0.3, 0.0, 0.0, 1.0))
logger = logging.getLogger(__name__)

class DisruptableStationService(EntosisCaptureTarget):
    isStationServiceEnabled = None

    def __init__(self, *args):
        EntosisCaptureTarget.__init__(self, *args)
        self.bracketSvc = sm.GetService('bracket')

    def _OnAddedToSpace(self, slimItem):
        EntosisCaptureTarget._OnAddedToSpace(self, slimItem)
        self.__UpdateFromSlimItem(slimItem)

    def _OnSlimItemUpdated(self, slimItem):
        EntosisCaptureTarget._OnSlimItemUpdated(self, slimItem)
        self.__UpdateFromSlimItem(slimItem)

    def _OnBracketCreated(self, bracket, slimItem):
        EntosisCaptureTarget._OnBracketCreated(self, bracket, slimItem)
        self.__UpdateUI()

    def __UpdateFromSlimItem(self, slimItem):
        if slimItem.isStationServiceEnabled is not None:
            self.isStationServiceEnabled = slimItem.isStationServiceEnabled
            self.__UpdateUI()

    def __UpdateUI(self):
        if self.isStationServiceEnabled is not None:
            if self.isStationServiceEnabled:
                invertedMode = False
                timerColors = TIMER_COLORS_ENABLED
                bracketColor = BRACKET_COLOR_ENABLED
            else:
                invertedMode = True
                timerColors = TIMER_COLORS_DISABLED
                bracketColor = BRACKET_COLOR_DISABLED
            self.SetTimerInvertedMode(invertedMode)
            self.SetTimerColor(*timerColors)
            bracket = self.bracketSvc.GetBracket(self.itemID)
            if bracket is not None:
                bracket.SetColor(*bracketColor)
