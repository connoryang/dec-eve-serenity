#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\Alliances\all_ui_sovereignty.py
from carbon.common.script.util.format import FmtDate
from carbonui.primitives.container import Container
from entosis.entosisConst import CHANGE_PRIMETIME_DELAY
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveLabelLargeBold
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.common.lib.appConst import corpRoleDirector
from inventorycommon.util import IsNPC
from localization import GetByLabel
from sovDashboard.dashboard import SovDashboard
import carbonui.const as uiconst
import blue
import uthread

class FormAlliancesSovereignty(Container):

    def CreateWindow(self):
        self.primeTimeInfo = None
        topCont = Container(parent=self, height=24, align=uiconst.TOTOP, padding=const.defaultPadding)
        FillThemeColored(parent=topCont, colorType=uiconst.COLORTYPE_UIHEADER, opacity=0.15)
        EveLabelSmall(parent=topCont, text=GetByLabel('UI/Sovereignty/DefaultVulnerabilityTimeLabel'), align=uiconst.CENTERLEFT, left=const.defaultPadding)
        menuCont = Container(parent=topCont, align=uiconst.TORIGHT, width=18)
        self.primeTimeMenu = UtilMenu(parent=menuCont, align=uiconst.CENTERRIGHT, menuAlign=uiconst.TOPRIGHT, GetUtilMenu=self.PrimeTimeMenu)
        menuCont.display = False
        execCorpID = sm.GetService('alliance').GetAlliance(session.allianceid).executorCorpID
        timeTextLeft = const.defaultPadding
        if self._IsDirectorInExecCorp(execCorpID):
            timeTextLeft = 18
            menuCont.display = True
        self.timeLabel = EveLabelSmall(parent=topCont, align=uiconst.CENTERRIGHT, left=timeTextLeft)
        uthread.new(self.UpdatePrimeInfo)
        self.sovDashBoard = SovDashboard(parent=self)
        self.sovDashBoard.CreateWindow()

    def UpdatePrimeInfo(self):
        self.primeTimeInfo = sm.GetService('alliance').GetPrimeTimeInfo()
        self.UpdateText()

    def UpdateText(self):
        if self.primeTimeInfo is None or self.primeTimeInfo.currentPrimeHour is None:
            text = GetByLabel('UI/Common/Unknown')
        else:
            newPrimeHour = self.primeTimeInfo.newPrimeHour
            validAfter = self.primeTimeInfo.newPrimeHourValidAfter
            now = blue.os.GetWallclockTime()
            if newPrimeHour is not None and now < validAfter:
                text = GetByLabel('UI/Sovereignty/VulnerabilityTimeWithFutureChange', hour=self.primeTimeInfo.currentPrimeHour, newHour=self.primeTimeInfo.newPrimeHour, validAfterDate=self.primeTimeInfo.newPrimeHourValidAfter)
            else:
                currentPrimeHour = self.GetCurrentPrimeHour()
                text = GetByLabel('UI/Sovereignty/VulnerabilityTime', hour=currentPrimeHour)
        self.timeLabel.SetText(text)

    def PrimeTimeMenu(self, menuParent):
        headerCont = menuParent.AddContainer(align=uiconst.TOTOP, height=20, padding=const.defaultPadding)
        EveLabelLargeBold(parent=headerCont, text=GetByLabel('UI/Sovereignty/SetSovereigntyHour'), align=uiconst.TOTOP)
        menuParent.AddSpace(height=10)
        text = menuParent.AddText(GetByLabel('UI/Sovereignty/SetNewVulnerabilityTimeDescription'))
        text.GetEntryWidth = lambda mc = text: 250
        cont = menuParent.AddContainer(align=uiconst.TOTOP, height=60, padding=const.defaultPadding)
        myCont = Container(name='myCont', parent=cont, align=uiconst.TOTOP, height=22, padTop=10)
        currentPrimeHour = self.GetCurrentPrimeHour()
        self.primeTimeCombo = Combo(name='primeTimeCombo', parent=myCont, options=self.GetTimeComboOptions(), select=currentPrimeHour, width=150)
        setBtn = Button(name='SetPrimeTimeBtn', align=uiconst.TOPRIGHT, parent=myCont, label=GetByLabel('UI/Common/CommandSet'), func=self.SetPrimeTime)

    def SetPrimeTime(self, *args):
        primeTimeNewValue = self.primeTimeCombo.GetValue()
        if self.primeTimeInfo and self.primeTimeInfo.newPrimeHour:
            newPrimeHour = self.primeTimeInfo.newPrimeHour
            validAfter = self.primeTimeInfo.newPrimeHourValidAfter
            newerPrimeHour = blue.os.GetWallclockTime() + CHANGE_PRIMETIME_DELAY
            if eve.Message('updateNewPrimeTime', {'currentPendingTime': '%s:00' % newPrimeHour,
             'currentPendingDate': FmtDate(validAfter, 'ss'),
             'newPendingTime': '%s:00' % primeTimeNewValue,
             'newPendingDate': FmtDate(newerPrimeHour, 'ss')}, uiconst.YESNO) != uiconst.ID_YES:
                return
        sm.GetService('alliance').SetPrimeHour(primeTimeNewValue)
        self.UpdatePrimeInfo()
        self.primeTimeMenu.CloseMenu()

    def GetTimeComboOptions(self):
        return [ (GetByLabel('UI/Sovereignty/VulnerabilityTime', hour=i), i) for i in xrange(24) ]

    def GetCurrentPrimeHour(self):
        currentPrimeHour = 0
        if self.primeTimeInfo and self.primeTimeInfo.currentPrimeHour is not None:
            currentPrimeHour = self.primeTimeInfo.currentPrimeHour
        return currentPrimeHour

    def _IsDirectorInExecCorp(self, executorCorpID):
        if session.allianceid is None:
            return False
        if IsNPC(session.corpid):
            return False
        if session.corpid != executorCorpID:
            return False
        if corpRoleDirector & session.corprole != corpRoleDirector:
            return False
        return True
