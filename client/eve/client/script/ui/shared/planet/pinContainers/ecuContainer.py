#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\planet\pinContainers\ecuContainer.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
import evetypes
import uiprimitives
import util
import uicls
import blue
import eve.client.script.ui.control.entries as listentry
import localization
import form
from .BasePinContainer import BasePinContainer, CaptionAndSubtext
from .. import planetCommon
import eve.common.script.planet.entities.basePin as basePin

class ECUContainer(BasePinContainer):
    __guid__ = 'planet.ui.ECUContainer'
    default_name = 'ECUContainer'
    default_height = 185
    default_width = 300
    INFO_CONT_HEIGHT = 70

    def ApplyAttributes(self, attributes):
        BasePinContainer.ApplyAttributes(self, attributes)

    def _GetActionButtons(self):
        btns = [util.KeyVal(id=planetCommon.PANEL_SURVEYFORDEPOSITS, panelCallback=self.OpenSurveyWindow), util.KeyVal(id=planetCommon.PANEL_PRODUCTS, panelCallback=self.PanelShowProducts)]
        btns.extend(BasePinContainer._GetActionButtons(self))
        return btns

    def _GetInfoCont(self):
        self.currDepositTxt = CaptionAndSubtext(parent=self.infoContLeft, caption=localization.GetByLabel('UI/PI/Common/Extracting'), top=0)
        self.timeToDeplTxt = CaptionAndSubtext(parent=self.infoContLeft, caption=localization.GetByLabel('UI/PI/Common/TimeToDepletion'), top=40)
        self.currCycleGauge = uicls.Gauge(parent=self.infoContRight, value=0.0, color=planetCommon.PLANET_COLOR_CYCLE, label=localization.GetByLabel('UI/PI/Common/CurrentCycle'), cyclic=True, width=120)
        self.currCycleOutputTxt = CaptionAndSubtext(parent=self.infoContRight, caption=localization.GetByLabel('UI/PI/Common/CurrentCycleOutput'), top=40)

    def _UpdateInfoCont(self):
        currentTime = blue.os.GetWallclockTime()
        if self.pin.programType is not None and self.pin.qtyPerCycle > 0 and self.pin.expiryTime > currentTime:
            timeToDepletion = self.pin.GetTimeToExpiry()
            qtyRemaining = int(timeToDepletion / self.pin.GetCycleTime()) * self.pin.qtyPerCycle
            totalTimeLeft = timeToDepletion
            self.timeToDeplTxt.SetCaption(localization.GetByLabel('UI/PI/Common/TimeToDepletion'))
            if totalTimeLeft < const.DAY:
                totalTimeLeft = localization.GetByLabel('UI/PI/Common/TimeHourMinSec', time=long(totalTimeLeft))
            else:
                totalTimeLeft = localization.GetByLabel('UI/PI/Common/TimeWritten', time=long(totalTimeLeft))
            deposName = evetypes.GetName(self.pin.programType)
            if self.pin.activityState < basePin.STATE_IDLE:
                currCycle = 0
                currCycleProportion = 0.0
                cycleTime = 0
                currCycleOutput = localization.GetByLabel('UI/PI/Common/NoneOutput')
            else:
                currCycle = currentTime - self.pin.lastRunTime
                currCycleProportion = currCycle / float(self.pin.GetCycleTime())
                cycleTime = self.pin.GetCycleTime()
                currCycleOutput = localization.GetByLabel('UI/PI/Common/UnitsAmount', amount=self.pin.GetProgramOutput(blue.os.GetWallclockTime()))
        else:
            currCycle = 0L
            totalTimeLeft = localization.GetByLabel('UI/PI/Common/TimeHourMinSec', time=0L)
            currCycleProportion = 0.0
            cycleTime = 0L
            deposName = localization.GetByLabel('UI/PI/Common/NothingExtracted')
            qtyRemaining = 0
            currCycleOutput = localization.GetByLabel('UI/PI/Common/NoneOutput')
        self.currDepositTxt.SetIcon(self.pin.programType)
        self.currDepositTxt.SetSubtext(deposName)
        if sm.GetService('planetUI').GetCurrentPlanet().IsInEditMode():
            self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/InactiveEditMode'))
            self.timeToDeplTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/InactiveEditMode'))
        else:
            self.currCycleGauge.SetValueInstantly(currCycleProportion)
            self.timeToDeplTxt.SetSubtext(totalTimeLeft)
            self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/CycleTimeElapsed', currTime=currCycle, totalTime=cycleTime))
        self.currCycleOutputTxt.SetSubtext(currCycleOutput)

    def OpenSurveyWindow(self):
        if planetCommon.PinHasBeenBuilt(self.pin.id):
            sm.GetService('planetUI').myPinManager.EnterSurveyMode(self.pin.id)
            self.CloseByUser()
            return
        cont = uiprimitives.Container(parent=self.actionCont, pos=(0, 0, 0, 0), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        editBox = self._DrawEditBox(cont, localization.GetByLabel('UI/PI/Common/CantSurveyInEditMode'))
        cont.height = editBox.height + 4
        return cont

    def GetStatsEntries(self):
        scrolllist = BasePinContainer.GetStatsEntries(self)
        if self.pin.programType is not None:
            label = '%s<t>%s' % (localization.GetByLabel('UI/PI/Common/Extracting'), evetypes.GetName(self.pin.programType))
            scrolllist.append(listentry.Get('Generic', {'label': label}))
        else:
            label = '%s<t>%s' % (localization.GetByLabel('UI/PI/Common/Extracting'), localization.GetByLabel('UI/PI/Common/NothingExtracted'))
            scrolllist.append(listentry.Get('Generic', {'label': label}))
        return scrolllist

    def _DecommissionSelf(self, *args):
        if planetCommon.PinHasBeenBuilt(self.pin.id):
            surveyWnd = form.PlanetSurvey.GetIfOpen()
            if surveyWnd and surveyWnd.ecuPinID == self.pin.id:
                sm.GetService('planetUI').ExitSurveyMode()
        BasePinContainer._DecommissionSelf(self)
