#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\entosis\spacecomponents\client\entosisCaptureTarget.py
from carbon.common.lib.const import SEC
import entosis.ui.entosisController
from entosis.ui.entosisTimer import EntosisTimer
from spacecomponents.client.display import EntryData, TIMER_ICON
from spacecomponents.common.components.component import Component
from spacecomponents.client.messages import MSG_ON_ADDED_TO_SPACE, MSG_ON_SLIM_ITEM_UPDATED, MSG_ON_BRACKET_CREATED
import logging
logger = logging.getLogger(__name__)

class EntosisCaptureTarget(Component):
    controllingTeamId = None
    scoringTeamId = None
    scoringAttributes = None
    entosisCounterController = None
    defenderTeamId = None
    twoDirectionalCapture = False

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self._OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self._OnSlimItemUpdated)
        self.SubscribeToMessage(MSG_ON_BRACKET_CREATED, self._OnBracketCreated)

    def _OnAddedToSpace(self, slimItem):
        self.__UpdateEntosisScoreFromSlimItem(slimItem)

    def _OnSlimItemUpdated(self, slimItem):
        self.__UpdateEntosisScoreFromSlimItem(slimItem)

    def _OnBracketCreated(self, bracket, slimItem):
        timer = EntosisTimer(parent=bracket)
        self.entosisCounterController = entosis.ui.entosisController.EntosisCounterController(timer, bracket, self.componentRegistry, slimItem, self)

    def __UpdateEntosisScoreFromSlimItem(self, slimItem):
        if slimItem.entosis_score is not None:
            self.controllingTeamId, self.scoringTeamId, self.scoringAttributes, self.defenderTeamId = slimItem.entosis_score
            if self.scoringAttributes and self.entosisCounterController is not None:
                self.entosisCounterController.SetScoreValues(self.controllingTeamId, self.scoringTeamId, self.scoringAttributes, self.defenderTeamId)

    def GetCaptureTime(self):
        return self.attributes.captureTimeSeconds

    def IsTwoDirectionalCaptureTarget(self):
        return self.twoDirectionalCapture

    def SetTimerColor(self, foregroundColor, backgroundColor, arrowColor):
        if self.entosisCounterController is not None:
            self.entosisCounterController.timer.SetTimerColor(foregroundColor, backgroundColor, arrowColor)

    def SetTimerInvertedMode(self, isInverted):
        if self.entosisCounterController is not None:
            self.entosisCounterController.SetTimerInvertedMode(isInverted)

    @staticmethod
    def GetAttributeInfo(godmaService, typeID, attributes, instance, localization):
        headerLabel = localization.GetByLabel('UI/Inflight/SpaceComponents/EntosisCaptureTarget/InfoAttributesHeader')
        attributeEntries = [EntryData('Header', headerLabel), EntryData('LabelTextSides', localization.GetByLabel('UI/Inflight/SpaceComponents/EntosisCaptureTarget/BaseCaptureTimeLabel'), localization.GetByLabel('UI/Inflight/SpaceComponents/EntosisCaptureTarget/BaseCaptureTimeValue', duration=long(attributes.captureTimeSeconds * SEC)), iconID=TIMER_ICON)]
        if attributes.defensiveRegenRate:
            regenTimeSeconds = attributes.captureTimeSeconds / attributes.defensiveRegenRate
            attributeEntries.append(EntryData('LabelTextSides', localization.GetByLabel('UI/Inflight/SpaceComponents/EntosisCaptureTarget/DefensiveRegenTimeLabel'), localization.GetByLabel('UI/Inflight/SpaceComponents/EntosisCaptureTarget/DefensiveRegenTimeValue', duration=long(regenTimeSeconds * SEC)), iconID=TIMER_ICON))
        return attributeEntries
