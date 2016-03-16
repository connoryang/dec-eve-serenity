#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\videowindow.py
import urllib2
import blue
from carbonui import const as uiconst
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import StreamingVideoSprite
import uthread2
import eve.common.lib.appConst as const
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.control.eveLabel import EveCaptionLarge

def _ParseTime(timeStr):
    import re

    def matchToMilliseconds(offset):
        return int(match.group(3 + offset)) + int(match.group(2 + offset)) * 1000 + int(match.group(1 + offset)) * 1000 * 60 + int(match.group(0 + offset)) * 1000 * 60 * 60

    match = re.match('(\\d{1,2}):(\\d{1,2}):(\\d{1,2}),(\\d{1,3})\\s+-->\\s+(\\d{1,2}):(\\d{1,2}):(\\d{1,2}),(\\d{1,3}).*', timeStr)
    if match is None:
        raise ValueError
    return (matchToMilliseconds(1), matchToMilliseconds(5))


class Subtitles(object):

    def __init__(self, path):
        self._subtitles = []
        uthread2.StartTasklet(self._LoadSubtitles, path)

    def _LoadSubtitles(self, path):
        if path.lower().startswith('res:/') or path.find(':') < 2:
            try:
                text = blue.paths.GetFileContentsWithYield(path).read()
            except IOError:
                return

        else:
            try:
                text = urllib2.urlopen(path).read()
            except IOError:
                return

        text = text.decode('utf-8')
        state = 'number'
        time = ''
        subText = []
        for line in text.split('\n'):
            if state == 'number':
                state = 'time'
            elif state == 'time':
                time = line.strip()
                state = 'text'
            else:
                line = line.strip()
                if line == '':
                    try:
                        self._subtitles.append((_ParseTime(time), '\n'.join(subText)))
                    except ValueError:
                        pass

                    state = 'number'
                    subText = []
                else:
                    subText.append(line)

    def GetSubtitle(self, milliseconds):
        for time, text in self._subtitles:
            if time[0] <= milliseconds <= time[1]:
                return text

        return ''


class VideoPlayerWindow(Window):
    default_caption = 'Video'
    default_minSize = (500, 400)
    default_windowID = 'VideoPlayer'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(0)
        self._stopUpdate = False
        self._onFinish = None
        self._subtitles = None
        self._finished = False
        self.bottomContainer = Container(name='bottomContainer', parent=self.sr.main, align=uiconst.TOBOTTOM, height=16, padding=const.defaultPadding)
        self.layoutAreaParent = Container(parent=self.sr.main, padding=const.defaultPadding)
        self.layoutAreaParent._OnSizeChange_NoBlock = self.RecalcLayout
        self.layoutArea = Container(parent=self.layoutAreaParent, align=uiconst.CENTER, width=100, height=100)
        self.video = StreamingVideoSprite(parent=self.layoutArea, align=uiconst.TOALL)
        self.video.OnVideoSizeAvailable = self.RecalcLayout
        self.video.OnVideoFinished = self._OnVideoFinished
        self.playPauseBtn = ButtonIcon(parent=self.bottomContainer, func=self.Play, align=uiconst.TOLEFT)
        self.muteBtn = ButtonIcon(parent=self.bottomContainer, func=self.Mute, align=uiconst.TOLEFT)
        self.volumeSlider = Slider(parent=self.bottomContainer, width=48, minValue=0, maxValue=100, startValue=100, showLabel=False, onsetvaluefunc=self.SetVolume, align=uiconst.TOLEFT)
        self.volume = settings.user.ui.Get('videoPlayerVolume', 100)
        self.volumeSlider.SetValue(self.volume, updateHandle=True, triggerCallback=False)
        self.subtitlesBtn = ButtonIcon(parent=self.bottomContainer, func=self.SwitchSubtitles, align=uiconst.TORIGHT)
        self.showSubtitles = True
        positionContainer = Container(parent=self.bottomContainer, align=uiconst.TOALL, padding=6)
        self.positionFill = Fill(parent=Container(parent=positionContainer, state=uiconst.UI_DISABLED), name='progressFill', align=uiconst.TOLEFT_PROP, color=(0.1804, 0.5412, 0.6392, 1))
        self.downloadedFill = Fill(parent=Container(parent=positionContainer, state=uiconst.UI_DISABLED), name='downloadFill', align=uiconst.TOLEFT_PROP, color=(0.4667, 0.7529, 0.8392, 1))
        Fill(parent=positionContainer, align=uiconst.TOALL, color=(1.0, 1.0, 1.0, 0.3))
        self.followUpContainer = Container(parent=self.layoutAreaParent, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        self.sr.subtitleCont = Container(parent=self.layoutArea, name='subtitleCont', idx=0, align=uiconst.TOBOTTOM_NOPUSH, state=uiconst.UI_DISABLED, height=100)
        self.sr.subtitleCont.Flush()
        self.UpdateLayoutArea()
        uthread2.StartTasklet(self._UpdatePosition)

    def _OnVideoFinished(self):
        for each in self.followUpContainer.children[:]:
            each.Close()

        self._finished = True
        self.playPauseBtn.SetTexturePath('res:/ui/texture/icons/replay.png')
        if self._onFinish:
            self.followUpContainer.SetState(uiconst.UI_NORMAL)
            self.layoutArea.SetState(uiconst.UI_HIDDEN)
            self._onFinish(self.followUpContainer)

    def PlayVideo(self, path, title = None, subtitles = None, onFinish = None):
        self.playPauseBtn.SetTexturePath('res:/ui/texture/icons/pause.png')
        self.muteBtn.SetTexturePath('res:/ui/texture/icons/73_16_35.png')
        self.subtitlesBtn.SetTexturePath('res:/ui/texture/icons/73_16_10.png')
        self.layoutArea.SetState(uiconst.UI_NORMAL)
        self.followUpContainer.SetState(uiconst.UI_HIDDEN)
        self.video.SetVideoPath(path)
        self.video.SetVolume(float(self.volume) / 100.0)
        self.volumeSlider.SetValue(self.volume, updateHandle=True, triggerCallback=False)
        self.SetCaption(title if title is not None else VideoPlayerWindow.default_caption)
        self._onFinish = onFinish
        self._finished = False
        self._replayArgs = (path,
         title,
         subtitles,
         onFinish)
        if subtitles is None:
            self._subtitles = None
        else:
            self._subtitles = Subtitles(subtitles)

    def Close(self, *args, **kwds):
        self._stopUpdate = True
        self.video = None
        Window.Close(self, *args, **kwds)

    def _UpdatePosition(self):
        while not self._stopUpdate:
            if self.video:
                duration = float((self.video.duration or 1) / 1000000)
                if duration == 0:
                    duration = 1
                mediaTime = min(float((self.video.mediaTime or 0) / 1000000) / duration, 1)
                downloadedTime = min(float((self.video.downloadedTime or 0) / 1000000) / duration, 1)
                if mediaTime == 0:
                    self.positionFill.Hide()
                else:
                    self.positionFill.Show()
                    self.positionFill.width = mediaTime
                if downloadedTime == 0:
                    self.downloadedFill.Hide()
                else:
                    self.downloadedFill.Show()
                    self.downloadedFill.width = downloadedTime
                self._UpdateSubtitles()
            uthread2.Sleep(0.1)

    def _UpdateSubtitles(self):
        if self._subtitles is None or not self.showSubtitles:
            return
        currentTime = self.video.mediaTime or 0
        currentTime /= 1000000
        self.sr.subtitleCont.Flush()
        text = self._subtitles.GetSubtitle(currentTime)
        if text is not None:
            EveCaptionLarge(text=u'<center>%s' % text, parent=self.sr.subtitleCont, color=(0.75, 0.75, 0.75, 1), align=uiconst.TOBOTTOM, bold=False, state=uiconst.UI_DISABLED)

    def UpdateLayoutArea(self):
        size = self.video.GetVideoSize()
        if not size:
            return
        areaWidth, areaHeight = self.layoutAreaParent.GetAbsoluteSize()
        xFitScale = areaWidth / float(size[0])
        yFitScale = areaHeight / float(size[1])
        scaling = min(xFitScale, yFitScale)
        self.layoutArea.width = int(size[0] * scaling)
        self.layoutArea.height = int(size[1] * scaling)

    def RecalcLayout(self, *args):
        self.UpdateLayoutArea()

    def Play(self, *args):
        if self._finished:
            self._finished = False
            self.PlayVideo(*self._replayArgs)
        elif self.video.isPaused:
            self.video.Play()
            self.playPauseBtn.SetTexturePath('res:/ui/texture/icons/pause.png')
        else:
            self.video.Pause()
            self.playPauseBtn.SetTexturePath('res:/ui/texture/icons/play.png')

    def Mute(self, *args):
        if self.video.isMuted:
            self.video.UnmuteAudio()
            self.volumeSlider.SetValue(self.volume, updateHandle=True, triggerCallback=False)
            self.muteBtn.SetTexturePath('res:/ui/texture/icons/73_16_35.png')
        else:
            self.video.MuteAudio()
            self.volumeSlider.SetValue(0, updateHandle=True, triggerCallback=False)
            self.muteBtn.SetTexturePath('res:/ui/texture/icons/73_16_37.png')

    def SetVolume(self, slider):
        self.video.SetVolume(float(slider.value) / 100.0)
        self.volume = slider.value
        settings.user.ui.Set('videoPlayerVolume', self.volume)
        if self.volume:
            self.muteBtn.SetTexturePath('res:/ui/texture/icons/73_16_35.png')

    def SwitchSubtitles(self):
        self.showSubtitles = not self.showSubtitles
        if self.showSubtitles:
            self.subtitlesBtn.opacity = 1.0
        else:
            self.subtitlesBtn.opacity = 0.2
            self.sr.subtitleCont.Flush()
