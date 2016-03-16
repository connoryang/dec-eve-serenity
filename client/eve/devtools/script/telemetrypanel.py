#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\telemetrypanel.py
import blue
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
import trinity
import uthread
import carbonui.const as uiconst
from carbonui.control.window import WindowCoreOverride as Window
from carbonui.control.buttons import ButtonCoreOverride as Button
from carbonui.control.checkbox import CheckboxCoreOverride as Checkbox

class TelemetryPanel(Window):
    __guid__ = 'form.TelemetryPanel'
    default_caption = 'Telemetry Panel'
    default_minSize = (400, 200)
    default_windowID = 'telemetrypanel'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(8)
        optionsContainer = LayoutGrid(parent=self.sr.main, align=uiconst.TOTOP, height=30, padding=10, columns=4, cellPadding=5)
        self.cppCaptureChk = Checkbox(parent=optionsContainer, align=uiconst.TOPLEFT, text='C++ capture', width=100, checked=blue.statistics.isCppCaptureEnabled, callback=self._OnCppCaptureChk)
        self.gpuCaptureChk = Checkbox(parent=optionsContainer, align=uiconst.TOPLEFT, text='GPU capture', width=120, checked=trinity.settings.GetValue('gpuTelemetryEnabled'), callback=self._OnGpuCaptureChk)
        self.timedCaptureChk = Checkbox(parent=optionsContainer, align=uiconst.TOPLEFT, text='Timed capture', width=120, checked=False, callback=self._OnTimedCaptureChk)
        self.durationEdit = SinglelineEdit(parent=optionsContainer, label='Duration:', floats=(0.1, 10.0))
        self.durationEdit.Disable()
        if blue.pyos.markupZonesInPython:
            msg = 'Python Telemetry markup enabled'
        else:
            msg = 'Python Telemetry markup is NOT enabled'
        Label(parent=self.sr.main, align=uiconst.TOBOTTOM, text=msg, padding=10)
        buttonContainer = LayoutGrid(parent=self.sr.main, align=uiconst.TOALL, columns=4, cellPadding=4, cellSpacing=10, padding=10)
        self.startBtn = Button(parent=buttonContainer, label='Start', func=self._Start, fixedwidth=80, fixedheight=60)
        self.stopBtn = Button(parent=buttonContainer, label='Stop', func=self._Stop, fixedwidth=80, fixedheight=60)
        self.pauseBtn = Button(parent=buttonContainer, label='Pause', func=self._Pause, fixedwidth=80, fixedheight=60)
        self.resumeBtn = Button(parent=buttonContainer, label='Resume', func=self._Resume, fixedwidth=80, fixedheight=60)
        uthread.new(self._CheckStatus)

    def _OnCppCaptureChk(self, checkbox):
        blue.statistics.isCppCaptureEnabled = checkbox.GetValue()

    def _OnGpuCaptureChk(self, checkbox):
        trinity.settings.SetValue('gpuTelemetryEnabled', checkbox.GetValue())

    def _OnTimedCaptureChk(self, checkbox):
        if checkbox.GetValue():
            self.durationEdit.Enable()
        else:
            self.durationEdit.Disable()

    def _Start(self, args):
        if self.timedCaptureChk.GetValue():
            duration = float(self.durationEdit.text)
            print 'Starting Telemetry timed capture (%4.2f seconds)' % duration
            blue.statistics.StartTimedTelemetry('localhost', duration)
        else:
            print 'Starting Telemetry'
            blue.statistics.StartTelemetry('localhost')

    def _Stop(self, args):
        print 'Stopping Telemetry'
        blue.statistics.StopTelemetry()

    def _Pause(self, args):
        print 'Pausing Telemetry'
        blue.statistics.PauseTelemetry()

    def _Resume(self, args):
        print 'Resuming Telemetry'
        blue.statistics.ResumeTelemetry()

    def _CheckStatus(self):
        while not self.destroyed:
            self.cppCaptureChk.SetChecked(blue.statistics.isCppCaptureEnabled, report=False)
            if blue.statistics.isTelemetryConnected:
                self.startBtn.Disable()
                self.stopBtn.Enable()
                if blue.statistics.isTelemetryPaused:
                    self.pauseBtn.Disable()
                    self.resumeBtn.Enable()
                else:
                    self.pauseBtn.Enable()
                    self.resumeBtn.Disable()
            else:
                self.startBtn.Enable()
                self.stopBtn.Disable()
                self.pauseBtn.Disable()
                self.resumeBtn.Disable()
            blue.synchro.SleepWallclock(500)
