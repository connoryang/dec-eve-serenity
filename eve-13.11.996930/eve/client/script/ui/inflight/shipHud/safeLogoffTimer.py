#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\safeLogoffTimer.py
from carbonui import const as uiconst
import localization
import uicontrols
import uiprimitives
import uthread
import util
import blue

class SafeLogoffTimer(uiprimitives.Container):
    __guid__ = 'uicls.SafeLogoffTimer'
    default_align = uiconst.CENTERTOP
    default_state = uiconst.UI_NORMAL
    default_width = 300
    default_height = 130
    default_top = 300
    default_bgColor = (0.05, 0.05, 0.05, 0.75)

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.SetHint(localization.GetByLabel('UI/Inflight/SafeLogoffTimerHint'))
        uicontrols.Frame(parent=self)
        self.logoffTime = attributes.logoffTime
        topCont = uiprimitives.Container(parent=self, align=uiconst.TOTOP, height=30)
        timerCont = uiprimitives.Container(parent=self, align=uiconst.TOTOP, height=70)
        bottomCont = uiprimitives.Container(parent=self, align=uiconst.TOALL)
        self.caption = uicontrols.Label(parent=topCont, fontsize=24, bold=True, align=uiconst.CENTERTOP, text=localization.GetByLabel('UI/Inflight/SafeLogoffTimerCaption'), top=4)
        self.timer = uicontrols.Label(parent=timerCont, align=uiconst.CENTER, fontsize=60, color=util.Color.YELLOW, bold=True)
        self.button = uicontrols.Button(parent=bottomCont, label=localization.GetByLabel('UI/Inflight/SafeLogoffAbortLogoffLabel'), align=uiconst.CENTER, func=self.AbortSafeLogoff)
        self.UpdateLogoffTime()
        uthread.new(self.UpdateLogoffTime_Thread)

    def UpdateLogoffTime(self):
        timeLeft = self.logoffTime - blue.os.GetSimTime()
        self.timer.text = '%.1f' % max(0.0, timeLeft / float(const.SEC))

    def UpdateLogoffTime_Thread(self):
        self.countingDown = True
        while self.countingDown:
            self.UpdateLogoffTime()
            blue.pyos.synchro.SleepSim(100)

    def AbortLogoff(self, *args):
        self.countingDown = False
        uthread.new(self.AbortLogoff_Thread)

    def AbortLogoff_Thread(self):
        blue.pyos.synchro.SleepSim(1000)
        uicore.animations.FadeOut(self, duration=1.0, sleep=True)
        self.Close()

    def AbortSafeLogoff(self, *args):
        shipAccess = sm.GetService('gameui').GetShipAccess()
        shipAccess.AbortSafeLogoff()
        self.AbortLogoff()

    def OnClose(self, *args):
        self.countingDown = False
