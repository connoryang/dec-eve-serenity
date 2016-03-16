#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\progressWnd.py
import types
from carbonui import const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveCaptionMedium
from eve.client.script.ui.control.progressBar import ProgressBar
import localization
import uicontrols
import util
import blue

class ProgressWnd(ContainerAutoSize):
    default_width = 320
    default_height = 87
    default_windowID = 'progresswindow'
    default_state = uiconst.UI_PICKCHILDREN
    default_align = uiconst.CENTER
    default_clipChildren = True
    default_padBottom = -4

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.abortbtn = None
        self.abortbtnpar = None
        self.confirmbtn = None
        self.abortconfirmbtnpar = None
        self.sr.readprogress = util.KeyVal(text='', prev=0)
        self.caption = EveCaptionMedium(name='caption', parent=self, align=uiconst.TOTOP, padding=(25, 0, 25, 0), top=12, idx=0, state=uiconst.UI_DISABLED)
        self.progressText = EveLabelMedium(parent=self, width=270, left=2, top=4, state=uiconst.UI_NORMAL, align=uiconst.TOTOP, padding=(25, 0, 25, 0))
        self.progressBar = ProgressBar(parent=self, height=10, padding=(25, 10, 25, 10), align=uiconst.TOTOP)
        uicontrols.WindowUnderlay(bgParent=self)

    def SetAbortFunc(self, func):
        args = None
        if type(func) == types.TupleType:
            func, args = func
        if self.abortbtnpar is None:
            if func is None:
                return
            self.abortbtnpar = uicontrols.ButtonGroup(parent=self, align=uiconst.TOTOP, btns=[[localization.GetByLabel('UI/Commands/Abort'),
              func,
              args,
              66]])
            self.abortbtn = self.abortbtnpar.GetBtnByIdx(0)
        if func is None:
            self.abortbtnpar.state = uiconst.UI_HIDDEN
        else:
            self.abortbtnpar.state = uiconst.UI_NORMAL
            self.abortbtn.OnClick = (func, args)

    def SetAbortConfirmFunc(self, abortFunc, confirmFunc):
        abortArgs = None
        confirmArgs = None
        if type(abortFunc) == types.TupleType:
            abortFunc, abortArgs = abortFunc
        if type(confirmFunc) == types.TupleType:
            confirmFunc, confirmArgs = confirmFunc
        if self.abortconfirmbtnpar is None:
            btns = ((localization.GetByLabel('UI/Common/Yes'),
              self.Confirm,
              (),
              None,
              0,
              1,
              0), (localization.GetByLabel('UI/Common/No'),
              self.Abort,
              (),
              None,
              0,
              0,
              1))
            self.abortconfirmbtnpar = uicontrols.ButtonGroup(parent=self, btns=btns, align=uiconst.TOTOP)
            self.confirmbtn = self.abortconfirmbtnpar.GetBtnByIdx(0)
            self.abortbtn = self.abortconfirmbtnpar.GetBtnByIdx(1)
        uicore.registry.AddModalWindow(self)

    def Abort(self, *args):
        if self.sr.Get('abortFunc', None) is not None:
            abortFunc = self.sr.Get('abortFunc', None)
            if type(abortFunc) == types.TupleType:
                abortFunc, abortArgs = abortFunc
                abortFunc(*abortArgs)
            else:
                abortFunc()
        uicore.registry.RemoveModalWindow(self)
        self.Close()

    def Confirm(self, *args):
        if self.sr.Get('confirmFunc', None) is not None:
            confirmFunc = self.sr.Get('confirmFunc', None)
            if type(confirmFunc) == types.TupleType:
                confirmFunc, confirmArgs = confirmFunc
                confirmFunc(*confirmArgs)
            else:
                confirmFunc()
        uicore.registry.RemoveModalWindow(self)
        self.Close()

    def SetModalResult(self, modalResult, *args):
        if modalResult in (uiconst.ID_CANCEL, uiconst.ID_NONE):
            self.Abort()

    def CountDown(self, startTime, duration):
        while True and not self.destroyed:
            dt = blue.os.TimeDiffInMs(startTime, blue.os.GetWallclockTimeNow())
            if dt > duration:
                break
            self.progressText.text = util.FmtDate(long((duration - dt) * 10000) + const.SEC)
            blue.pyos.synchro.SleepWallclock(10)

        if not self.destroyed:
            self.progressText.text = util.FmtDate(0L)
            self.Abort()

    def SetReadProgress(self, have, need):
        if self is None or self.destroyed:
            return
        if not self.sr.readprogress.text:
            return
        strng = localization.GetByLabel('UI/Shared/ReadProgress', text=self.sr.readprogress.text, done=have + self.sr.readprogress.prev, total=need + self.sr.readprogress.prev)
        if have == need:
            self.sr.readprogress.prev += have
        if self.progressText.text != strng:
            self.progressText.text = strng
            sm.services['loading'].LogWarn('Setting progress text to: ', strng)
            blue.pyos.synchro.Yield()
        else:
            sm.services['loading'].LogWarn('Not setting progress text to: ', strng)

    def SetStatus(self, title, strng, portion = None, total = None, abortFunc = None, animate = 1):
        self._SetCaption(title)
        self.SetAbortFunc(abortFunc)
        self.sr.readprogress = util.KeyVal(text=strng, prev=0)
        if self.progressText.text != strng:
            self.progressText.text = strng
        return 0

    def _SetCaption(self, title):
        self.caption.text = ['<center>', title]
