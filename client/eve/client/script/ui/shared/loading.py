#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\loading.py
from carbonui.util.color import Color
from eve.client.script.ui.shared.progressWnd import ProgressWnd
import service
import blue
import uiprimitives
import uthread
import carbonui.const as uiconst
import localization

class Loading(service.Service):
    __exportedcalls__ = {'CleanUp': [],
     'ProgressWnd': [],
     'Cycle': [],
     'StopCycle': [],
     'HideAllLoad': [],
     'FadeIn': [],
     'FadeOut': [],
     'GoBlack': [],
     'IsLoading': []}
    __notifyevents__ = ['OnNetClientReadProgress']
    __dependencies__ = []
    __guid__ = 'svc.loading'
    __servicename__ = 'loading'
    __displayname__ = 'Loading Service'

    def Run(self, memStream = None):
        self.LogInfo('Starting LoadingSvc')
        self.soundStarted = self.explicitSound = 0
        self.loadingwnd = None
        self.loading = 0
        self.que = []
        self.done = []
        self.premature = []
        self.currentid = None
        self.cycletext = None
        self.cycling = 0
        self.fill = None
        self.hideThread = None
        self.fadingToColor = 0
        self.fadingFromColor = 0

    def Stop(self, memStream = None):
        self.CleanUp()

    def CleanUp(self):
        self.que = []
        self.StopSound()
        self.StopCycle()
        if self.loadingwnd is not None and not self.loadingwnd.destroyed:
            self.loadingwnd.Close()
            self.loadingwnd = None
        l_loading = uicore.layer.loading
        if l_loading:
            l_loading.Flush()

    def CountDownWindow(self, question, duration, confirmFunc, abortFunc, inModalLayer = False):
        startTime = blue.os.GetWallclockTime()
        if inModalLayer:
            par = uicore.layer.mloading
        else:
            par = uicore.layer.loading
        wnd = ProgressWnd(parent=par, idx=0)
        wnd._SetCaption(question)
        if confirmFunc and abortFunc:
            wnd.SetAbortConfirmFunc(abortFunc, confirmFunc)
        elif abortFunc:
            wnd.SetAbortFunc(abortFunc)
        wnd.sr.abortFunc = abortFunc
        wnd.sr.confirmFunc = confirmFunc
        uthread.new(wnd.CountDown, startTime, duration)
        return wnd

    def ProgressWnd(self, title = None, strng = '', portion = 1, total = 1, explicitSound = 0, abortFunc = None, useMorph = 1, **kw):
        if title is None:
            title = localization.GetByLabel('UI/Common/Loading')
        if not self.loadingwnd or self.loadingwnd.destroyed:
            self.loadingwnd = ProgressWnd(parent=uicore.layer.loading, idx=0)
        left = sm.GetService('window').GetCameraLeftOffset(self.loadingwnd.width, align=uiconst.CENTER, left=0)
        self.loadingwnd.left = left
        self.loadingwnd.top = 0
        self.CheckVisibility(portion, total)
        if portion >= total:
            if self.soundStarted:
                self.StopSound()
        elif not self.soundStarted:
            self.soundStarted = 1
            self.explicitSound = explicitSound
        failed = self.loadingwnd.SetStatus(title, strng, max(0, portion), max(0, total), abortFunc, animate=useMorph)
        if failed:
            self.EndLoading()

    def CheckVisibility(self, portion, total):
        if portion is not None and total is not None:
            if portion >= total:
                self.hideThread = uthread.new(self.DelayHide)
            else:
                if self.hideThread:
                    self.hideThread.kill()
                    self.hideThread = None
                uicore.layer.loading.state = uiconst.UI_NORMAL

    def DelayHide(self):
        blue.pyos.synchro.SleepWallclock(750)
        self.EndLoading()

    def EndLoading(self):
        if self.loadingwnd:
            self.loadingwnd.Close()
            self.loadingwnd = None
        uicore.layer.loading.state = uiconst.UI_HIDDEN

    def OnNetClientReadProgress(self, have, need):
        if sm.StartService('connection').processingBulkData == 0:
            return
        wnd = getattr(self, 'loadingwnd', None)
        if not wnd or wnd.destroyed:
            return
        wnd.SetReadProgress(int(have / 1024), int(need / 1024))

    def StopSound(self):
        if self.soundStarted:
            self.soundStarted = self.explicitSound = 0

    def Cycle(self, title = None, strng = ''):
        if title is None:
            title = localization.GetByLabel('UI/Common/Loading')
        self.cycletext = (title, strng)
        uthread.new(self._Cycle)

    def _Cycle(self):
        if self.cycling:
            return
        blue.pyos.synchro.Yield()
        while self.cycletext:
            self.cycling = 1
            for i in xrange(100):
                if self.cycletext:
                    self.ProgressWnd(self.cycletext[0], self.cycletext[1], portion=i, total=100, useMorph=0)
                else:
                    self.EndLoading()
                    break
                blue.pyos.BeNice()

        self.cycling = 0

    def StopCycle(self):
        self.cycletext = None
        l_loading = uicore.layer.loading
        if l_loading:
            self.EndLoading()

    def HideAllLoad(self):
        self.StopCycle()

    def GoBlack(self):
        self.ConstructFill()
        self.fill.opacity = 1.0

    def ConstructFill(self, color = Color.BLACK):
        if not self.fill:
            self.fill = uiprimitives.Fill(parent=uicore.layer.loadingFill, state=uiconst.UI_NORMAL, padding=-2, opacity=0.0)
        color = (color[0],
         color[1],
         color[2],
         self.fill.opacity)
        self.fill.SetRGB(*color)
        self.fill.Enable()

    def IsLoading(self):
        return uicore.layer.loading.state == uiconst.UI_NORMAL or self.fadingToColor or self.fadingFromColor or self.cycling

    def FadeIn(self, time = 1000.0, color = (0, 0, 0, 1.0), sleep = True, *args):
        self.ConstructFill(color=color)
        uicore.animations.FadeTo(self.fill, self.fill.opacity, color[3], duration=time / 1000.0, sleep=sleep)

    def FadeOut(self, time = 1000.0, opacityStart = None, sleep = True, *args):
        if self.fill:
            self.fill.Disable()
            if opacityStart is not None:
                self.fill.opacity = opacityStart
            uicore.animations.FadeTo(self.fill, self.fill.opacity, 0.0, duration=time / 1000.0, sleep=sleep)
