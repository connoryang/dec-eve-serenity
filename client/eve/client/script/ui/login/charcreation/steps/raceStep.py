#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\login\charcreation\steps\raceStep.py
import blue
import uicontrols
import carbonui.const as uiconst
import uicls
import uiprimitives
import uthread
import localization
from eve.client.script.ui.login.charcreation.charCreationButtons import RaceButton
from eve.client.script.ui.login.charcreation.charCreation import BaseCharacterCreationStep
import charactercreator.const as ccConst
import eve.common.lib.appConst as const

class RaceStep(BaseCharacterCreationStep):
    __guid__ = 'uicls.RaceStep'
    stepID = ccConst.RACESTEP
    racialMovies = {const.raceCaldari: 'res:/video/charactercreation/caldari.bik',
     const.raceMinmatar: 'res:/video/charactercreation/minmatar.bik',
     const.raceAmarr: 'res:/video/charactercreation/amarr.bik',
     const.raceGallente: 'res:/video/charactercreation/gallente.bik'}
    racialMusic = {const.raceCaldari: 'wise:/music_switch_race_caldari',
     const.raceMinmatar: 'wise:/music_switch_race_minmatar',
     const.raceAmarr: 'wise:/music_switch_race_amarr',
     const.raceGallente: 'wise:/music_switch_race_gallente',
     None: 'music_switch_race_norace'}
    raceColorCodes = {(0, 0, 1, 1): const.raceCaldari,
     (1, 0, 0, 1): const.raceMinmatar,
     (1, 1, 0, 1): const.raceAmarr,
     (0, 1, 0, 1): const.raceGallente}

    def ApplyAttributes(self, attributes):
        self.raceInfo = {}
        self.bloodlineInfo = {}
        self.movieStateCheckRunning = 0
        self.padValue = 6
        self.raceID = None
        self.hoveredRaceID = None
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        info = self.GetInfo()
        if uicore.desktop.width <= 1360:
            fontsize = 12
        else:
            fontsize = 14
        self.sr.raceInfoCont = uiprimitives.Container(name='raceInfoCont', parent=self.sr.uiContainer, align=uiconst.CENTERTOP, width=600, height=uicore.desktop.height, state=uiconst.UI_PICKCHILDREN)
        self.sr.textCont = uiprimitives.Container(name='raceCont', parent=self.sr.raceInfoCont, align=uiconst.TOTOP, pos=(0, 38, 0, 20), state=uiconst.UI_NORMAL)
        header = uicls.CCLabel(text=localization.GetByLabel('UI/CharacterCreation/RaceSelection'), name='header', parent=self.sr.textCont, align=uiconst.CENTERTOP, uppercase=1, letterspace=2, color=(0.9, 0.9, 0.9, 0.8), fontsize=22, bold=False)
        self.sr.raceCont = uiprimitives.Container(name='raceCont', parent=self.sr.raceInfoCont, align=uiconst.TOTOP, pos=(0, 40, 0, 80), state=uiconst.UI_HIDDEN)
        self.raceSprite = uiprimitives.Sprite(name='raceSprite', parent=self.sr.raceCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self.raceHeaderPath, pos=(0, 0, 512, 128))
        uiprimitives.Container(name='push', parent=self.sr.raceInfoCont, align=uiconst.TOTOP, pos=(0, 0, 0, 15), state=uiconst.UI_DISABLED)
        self.sr.movieCont = uiprimitives.Container(name='movieCont', parent=self.sr.raceInfoCont, align=uiconst.TOTOP, pos=(0, 0, 0, 338), state=uiconst.UI_HIDDEN)
        self.sr.raceTextCont = uiprimitives.Container(name='raceTextCont', parent=self.sr.raceInfoCont, align=uiconst.TOTOP, padding=(0,
         15,
         0,
         self.padValue), state=uiconst.UI_HIDDEN)
        self.sr.raceText = uicls.CCLabel(parent=self.sr.raceTextCont, fontsize=fontsize, align=uiconst.TOPLEFT, text='', letterspace=0, top=0, pos=(0, 0, 600, 0), bold=0, color=ccConst.COLOR75)
        self.sr.buttonCont = uiprimitives.Container(parent=self.sr.uiContainer, align=uiconst.CENTERBOTTOM, pos=(0, 60, 512, 128))
        self.raceBtns = []
        for race in sm.GetService('cc').GetRaceData(shuffleFirstTime=True):
            raceBtn = RaceButton(name='raceBtn', parent=self.sr.buttonCont, align=uiconst.TOLEFT, pos=(0, 0, 128, 128), raceID=race.raceID, mouseExitCallback=self.ResetHoverRaceID)
            btnName = 'raceBtn_%s' % race.raceID
            self.raceBtns.append(raceBtn)
            setattr(self.sr, btnName, raceBtn)
            if info.raceID and info.raceID == race.raceID:
                raceBtn.Select()

        if info.raceID:
            self.raceID = info.raceID
            self.UpdateRaceHeader(info.raceID)
            self.GetRaceText()
        uicontrols.Frame(parent=self.sr.movieCont, color=(1.0, 1.0, 1.0, 0.2))
        self.sr.racialImage = uiprimitives.Sprite(name='racialImage', parent=self.sr.movieCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.sr.movieCont.OnMouseEnter = self.OnMovieEnter
        self.movie = uiprimitives.VideoSprite(parent=self.sr.movieCont, pos=(0, 0, 600, 338), videoPath=self.racialMovies.get(info.raceID, ''), videoAutoPlay=False)
        self.movie.display = False
        self.sr.movieControlCont = uiprimitives.Container(name='controlCont', parent=self.sr.movieCont, align=uiconst.CENTERBOTTOM, pos=(0, 0, 60, 22), idx=0, state=uiconst.UI_HIDDEN)
        uiprimitives.Fill(parent=self.sr.movieControlCont, padding=(0, 0, 0, 1), color=(0, 0, 0, 0.3))
        self.UpdateLayout()
        buttons = [('playpPauseBtn',
          4,
          'ui_73_16_225',
          self.ClickPlayPause), ('soundBtn',
          40,
          'ui_73_16_230',
          self.ClickSound), ('noSoundBtn',
          40,
          'ui_38_16_111',
          self.ClickSound)]
        for name, left, iconPath, function in buttons:
            icon = uicontrols.Icon(parent=self.sr.movieControlCont, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, pos=(left,
             2,
             16,
             16), icon=iconPath, idx=0)
            icon.OnClick = function
            icon.OnMouseEnter = (self.MouseOverButton, icon)
            icon.OnMouseExit = (self.MouseExitButton, icon)
            icon.SetAlpha(0.5)
            self.sr.Set(name, icon)

        self.sr.noSoundBtn.state = uiconst.UI_HIDDEN
        self.setupDone = 1
        self.TryPlayMovie()

    def UpdateLayout(self):
        if not self.sr.raceInfoCont:
            return
        if uicore.desktop.height <= 900:
            self.sr.raceInfoCont.width = 400
            self.sr.movieCont.height = 225
            self.sr.raceText.width = self.sr.raceInfoCont.width - self.padValue * 2
            self.sr.raceText.fontsize = 12
            self.sr.buttonCont.top = 60
            self.sr.raceCont.top = 40
        else:
            self.sr.raceInfoCont.width = 600
            self.sr.raceText.width = self.sr.raceInfoCont.width - self.padValue * 2
            self.sr.movieCont.height = 338
            self.sr.raceText.fontsize = 14
            self.sr.buttonCont.top = 80
            self.sr.raceCont.top = 80
        uthread.new(self.UpdateTextHeight)
        self.movie.width = self.sr.raceInfoCont.width
        self.movie.height = self.sr.movieCont.height

    def UpdateTextHeight(self):
        blue.pyos.synchro.Yield()
        self.sr.raceTextCont.height = self.sr.raceText.textheight

    def OnRaceSelected(self, raceID, *args):
        for i in [const.raceAmarr,
         const.raceMinmatar,
         const.raceGallente,
         const.raceCaldari]:
            raceBtn = self.sr.Get('raceBtn_%d' % i)
            raceBtn.Deselect()

        btn = self.sr.Get('raceBtn_%d' % raceID)
        btn.Select()
        uicore.layer.charactercreation.UpdateBackdropLite(raceID)
        self.UpdateRaceHeader(raceID)
        self.UpdateRaceInfo(raceID)

    def UpdateRaceHeader(self, raceID):
        self.sr.raceCont.state = uiconst.UI_DISABLED
        height = 128
        top = self.racialHeader.get(raceID, None)
        self.raceSprite.rectTop, self.raceSprite.rectHeight = top, height

    def UpdateRaceInfo(self, raceID):
        oldRaceID = self.raceID
        self.raceID = raceID
        uicore.layer.charactercreation.UpdateRaceMusic(raceID)
        self.TryPlayMovie(oldRaceID)
        self.GetRaceText()

    def GetRaceText(self):
        info = self.GetInfo()
        if info.raceID is None:
            return
        if not len(self.raceInfo):
            self.raceInfo = sm.GetService('cc').GetRaceDataByID()
        self.sr.raceTextCont.state = uiconst.UI_NORMAL
        raceInfo = self.raceInfo[info.raceID]
        raceText = localization.GetByMessageID(raceInfo.descriptionID)
        color = self.raceFontColor.get(info.raceID, (1.0, 1.0, 1.0, 0.75))
        self.sr.raceText.text = raceText
        self.sr.raceText.color.SetRGB(*color)
        uthread.new(self.UpdateTextHeight)

    def TryPlayMovie(self, oldRaceID = None, *args):
        info = self.GetInfo()
        if info.raceID is None:
            return
        self.sr.movieCont.state = uiconst.UI_NORMAL
        if not getattr(self, 'setupDone', 0):
            return
        if info.raceID != oldRaceID:
            self.Pause()
        if settings.user.ui.Get('cc_racialMoviePlayed_%s' % info.raceID, 0):
            self.ShowMovieRacialImage()
        else:
            uthread.new(self.MovieState)
            self.PlayMovie()

    def OnMovieEnter(self, *args):
        self.sr.movieControlCont.state = uiconst.UI_NORMAL

    def OnMouseEnter(self, *args):
        if self.sr.movieControlCont:
            self.sr.movieControlCont.state = uiconst.UI_HIDDEN

    def PlayMovie(self):
        info = self.GetInfo()
        if info.raceID is None:
            return
        videoPath = self.racialMovies.get(info.raceID, None)
        self.movie.SetVideoPath(videoPath)
        sm.StartService('dynamicMusic').StopLocationMusic('music_character_creation')
        uicore.layer.charactercreation.raceMusicStarted = False
        uthread.new(self.MovieState)
        self.movie.display = True
        self.movie.Play()
        settings.user.ui.Set('cc_racialMoviePlayed_%s' % info.raceID, 1)
        self.sr.racialImage.state = uiconst.UI_HIDDEN
        self.movie.state = uiconst.UI_DISABLED
        self.sr.playpPauseBtn.LoadIcon('ui_73_16_226')

    def ClickPlayPause(self, *args):
        if getattr(self, 'movie', None) is not None:
            if not getattr(self.movie, 'isPaused', None):
                self.Pause()
            else:
                self.PlayMovie()

    def Pause(self, *args):
        if not uicore.layer.charactercreation.raceMusicStarted:
            sm.StartService('dynamicMusic').PlayLocationMusic('music_character_creation')
        self.movie.Pause()
        self.sr.playpPauseBtn.LoadIcon('ui_73_16_225')

    def ClickSound(self, *args):
        if self.movie.isMuted:
            self.movie.UnmuteAudio()
            self.sr.noSoundBtn.state = uiconst.UI_HIDDEN
        else:
            self.movie.MuteAudio()
            self.sr.noSoundBtn.state = uiconst.UI_NORMAL

    def MouseOverButton(self, btn, *args):
        btn.SetAlpha(1.0)

    def MouseExitButton(self, btn, *args):
        btn.SetAlpha(0.5)

    def MovieState(self):
        if self.movieStateCheckRunning:
            return
        self.movieStateCheckRunning = 1
        while self and not self.destroyed and self.movieStateCheckRunning:
            if getattr(self, 'movie', None) and self.sr:
                if getattr(self.movie, 'isPaused', None):
                    self.sr.playpPauseBtn.LoadIcon('ui_73_16_225')
                else:
                    self.sr.playpPauseBtn.LoadIcon('ui_73_16_226')
                if self.movie.isFinished:
                    self.ShowMovieRacialImage()
            blue.pyos.synchro.SleepWallclock(1000)

        if self and not self.destroyed:
            self.movieStateCheckRunning = 0

    def ShowMovieRacialImage(self, *args):
        info = self.GetInfo()
        if info.raceID not in [const.raceCaldari,
         const.raceMinmatar,
         const.raceAmarr,
         const.raceGallente]:
            return
        self.movieStateCheckRunning = 0
        self.movie.display = False
        self.sr.racialImage.state = uiconst.UI_DISABLED
        self.sr.racialImage.LoadTexture('res:/UI/Texture/Charsel/movieImage_%s.dds' % info.raceID)
        if not uicore.layer.charactercreation.raceMusicStarted:
            sm.StartService('dynamicMusic').PlayLocationMusic('music_character_creation')

    def OnMouseMove(self, *args):
        uicls.BaseCharacterCreationStep.OnMouseMove(self, *args)
        info = self.GetInfo()
        if info.raceID:
            return
        raceID = self.FindRaceFromColorMap()
        if raceID != self.hoveredRaceID:
            self.hoveredRaceID = raceID
            for eachBtn in self.raceBtns:
                eachBtn.normalSprite.SetAlpha(0.3)

            if self.hoveredRaceID is not None:
                btn = getattr(self.sr, 'raceBtn_%s' % raceID, None)
                btn.OnMouseEnter()
            uicore.layer.charactercreation.UpdateBackdropLite(raceID=raceID, mouseEnter=True)
            if raceID is None:
                self.cursor = uiconst.UICURSOR_DEFAULT
            else:
                self.cursor = uiconst.UICURSOR_SELECT

    def OnMouseUp(self, btn, *args):
        uicls.BaseCharacterCreationStep.OnMouseUp(self, btn, *args)
        raceID = self.FindRaceFromColorMap()
        if raceID is not None:
            sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_select_play'))
            uicore.layer.charactercreation.SelectRace(raceID)

    def ResetHoverRaceID(self, *args):
        self.hoveredRaceID = None

    def FindRaceFromColorMap(self, *args):
        pos = (int(uicore.uilib.x * uicore.desktop.dpiScaling), int(uicore.uilib.y * uicore.desktop.dpiScaling))
        bdScene = sm.GetService('sceneManager').Get2DBackdropScene()
        raceID = None
        for each in bdScene.children:
            if each.name != 'backdropSprite':
                continue
            colorCodedBackDrop = uicore.layer.charactercreation.colorCodedBackDrop
            if colorCodedBackDrop is None:
                continue
            xPosInBackDrop = pos[0] - each.displayX
            yPosInBackDrop = pos[1] - each.displayY
            xRatioPos = xPosInBackDrop / float(each.displayWidth)
            yRatioPos = yPosInBackDrop / float(each.displayHeight)
            xPosInMask = int(xRatioPos * colorCodedBackDrop.width)
            yPosInMask = int(yRatioPos * colorCodedBackDrop.height)
            colorCode = colorCodedBackDrop.GetPixelColor(xPosInMask, yPosInMask)
            raceID = self.raceColorCodes.get(colorCode, None)

        return raceID
