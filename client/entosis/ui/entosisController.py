#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\entosis\ui\entosisController.py
from carbon.common.lib.const import SEC, MIN
import gametime
import logging
import inventorycommon.const as invConst
import uthread2
try:
    import localization
except ImportError:
    localization = None

logger = logging.getLogger(__name__)
NEUTRAL = invConst.ownerSystem

class EntosisCounterController(object):
    isInverted = False

    def __init__(self, timer, bracket, componentRegistry, slimItem, entosisComponentInstance, *args):
        self.captureTime = entosisComponentInstance.GetCaptureTime()
        self.twoDirectionalCaptureTarget = entosisComponentInstance.IsTwoDirectionalCaptureTarget()
        self.componentRegistry = componentRegistry
        self.bracket = bracket
        self.slimItem = slimItem
        self.itemID = slimItem.itemID
        self.controllingTeamId = None
        self.scoringTeamId = None
        self.defenderTeamId = None
        self.scoreAtLastUpdateTime = None
        self.lastUpdatedScoreTime = None
        self.scoringRate = None
        self.isBlocked = False
        self.timer = timer
        self.updateLoopRunning = False
        self.sublabelInfo = None
        if slimItem.entosis_score is not None:
            controllingTeamId, scoringTeamId, scoringAttributes, defenderTeamId = slimItem.entosis_score
            self.SetScoreValues(controllingTeamId, scoringTeamId, scoringAttributes, defenderTeamId)

    def _IsScoring(self):
        return self.scoringRate is not None and self.scoringRate != 0.0

    def _UpdateTimers(self):
        currentScore = self._CalculateCurrentScore()
        self._SetTimerDisplayValue(currentScore)
        correctedCurrentScore = self._GetScoreCorrectedForInvertedMode(currentScore)
        if self._IsScoring():
            if self.scoringRate > 0:
                endPointScore = 1.0
            else:
                endPointScore = 0.0
            scoreRequiredUntilEndPoint = endPointScore - currentScore
            timeUntilEndPoint = self.captureTime * scoreRequiredUntilEndPoint / self.scoringRate
            self.timer.SetEntosisValueTimed(correctedCurrentScore, self._GetScoreCorrectedForInvertedMode(endPointScore), timeUntilEndPoint)
        elif self.isBlocked:
            self.timer.SetStalemate(correctedCurrentScore)
        else:
            self.timer.SetEntosisValueImmediate(correctedCurrentScore)
        self._UpdateSubLabel()

    def _SetTimerDisplayValue(self, currentScore):
        displayValue = True
        if not self.isInverted and currentScore >= 1.0 and not self.isBlocked:
            displayValue = False
        self.timer.SetDisplayValue(displayValue)

    def SetScoreValues(self, controllingTeamId, scoringTeamId, scoringAttributes, defenderTeamId):
        self.controllingTeamId = controllingTeamId
        self.scoringTeamId = scoringTeamId
        self.defenderTeamId = defenderTeamId
        scoreAtLastUpdateTime, lastUpdatedScoreTime, scoringRate, isBlocked = scoringAttributes
        self.scoreAtLastUpdateTime = scoreAtLastUpdateTime
        self.lastUpdatedScoreTime = lastUpdatedScoreTime
        self.scoringRate = scoringRate
        self.isBlocked = isBlocked
        self._UpdateTimers()

    def _CalculateCurrentScore(self):
        if self._IsScoring():
            timeSinceLastScoreUpdate = gametime.GetSimTime() - self.lastUpdatedScoreTime
            scoringDuration = timeSinceLastScoreUpdate / self.captureTime / float(SEC)
            score = self.scoreAtLastUpdateTime + scoringDuration * self.scoringRate
            score = min(1.0, max(score, 0.0))
        elif self.scoreAtLastUpdateTime is not None:
            score = self.scoreAtLastUpdateTime
        else:
            score = 0
        return score

    def _GetScoreCorrectedForInvertedMode(self, score):
        if self.isInverted:
            return 1 - score
        return score

    def SetTimerInvertedMode(self, isInverted):
        self.isInverted = isInverted
        self._UpdateTimers()

    def _KillBracketSubLabel(self):
        self.updateLoopRunning = False
        self.sublabelInfo = None
        self.bracket.UpdateSubLabelIfNeeded('')
        self.bracket.CloseSubLabel()

    def _ShouldShowSubLabel(self):
        if self.isBlocked:
            return True
        if self._IsScoring():
            if self.scoringRate > 0 and self.scoreAtLastUpdateTime != 1.0:
                return True
            if self.scoringRate < 0 and self.scoreAtLastUpdateTime != -1.0:
                return True
        return False

    def _UpdateSubLabel(self):
        if self._ShouldShowSubLabel():
            uthread2.StartTasklet(self._UpdateSublabel_thread)
        else:
            self._KillBracketSubLabel()

    def _GetCaptureStatusText(self):
        if not self._IsScoring():
            if self.isBlocked:
                return localization.GetByLabel('UI/Sovereignty/BracketProgressBlocked')
            else:
                return None
        if self.controllingTeamId > 0:
            controllingTeamTicker = cfg.allianceshortnames.Get(self.controllingTeamId).shortName
            return localization.GetByLabel('UI/Sovereignty/BracketEntosisStatus', allianceTicker=controllingTeamTicker)
        else:
            return localization.GetByLabel('UI/Sovereignty/BracketAttackingClaimed')

    def _GetCaptureTimestamp(self):
        if not self._IsScoring():
            return None
        fullCaptureTime = abs(self.captureTime / self.scoringRate)
        if self.scoringRate < 0:
            score = self.scoreAtLastUpdateTime
        else:
            score = 1 - self.scoreAtLastUpdateTime
        if (self.defenderTeamId is NEUTRAL or self.twoDirectionalCaptureTarget) and self.scoringRate < 0:
            score += 1
        timeInSec = score * fullCaptureTime
        time = long(round(timeInSec * SEC))
        return time + self.lastUpdatedScoreTime

    def _FormatCountdown(self, time):
        timeText = localization.formatters.FormatTimeIntervalShort(time, showFrom='minute', showTo='second')
        return timeText

    def _UpdateSublabel_thread(self):
        statusText = self._GetCaptureStatusText()
        captureTimestamp = self._GetCaptureTimestamp()
        self.sublabelInfo = (statusText, captureTimestamp)
        if self.updateLoopRunning:
            return
        self._RunUpdateLoop()

    def _RunUpdateLoop(self):
        self.updateLoopRunning = True
        while self.updateLoopRunning:
            if not self._UpdateLoopContent():
                break
            uthread2.SleepSim(1)

        self.updateLoopRunning = False

    def _UpdateLoopContent(self):
        if not self.bracket or self.bracket.destroyed or not self.sublabelInfo:
            self._KillBracketSubLabel()
            return False
        statusText, captureTimestamp = self.sublabelInfo
        if captureTimestamp is not None:
            now = gametime.GetSimTime()
            timeUntil = max(0L, captureTimestamp - now)
            timeUntilText = self._FormatCountdown(timeUntil)
            text = ' - '.join(filter(None, [statusText, timeUntilText]))
        else:
            text = statusText
        self.bracket.UpdateSubLabelIfNeeded(text)
        return True
