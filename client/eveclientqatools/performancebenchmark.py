#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveclientqatools\performancebenchmark.py
import blue
import math
import evecamera
import uthread
from eve.client.script.ui.control.eveWindow import Window
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.checkbox import Checkbox
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveLabel import EveHeaderSmall
from eve.client.script.ui.util.uix import TextBox
import carbonui.const as uiconst
from .performancebenchmarkdata import *

class SceneDirector(object):

    def __init__(self):
        self.slash = sm.GetService('slash').SlashCmd
        self.initialSceneState = set([])

    def SetCamera(self, yaw, pitch, pan):
        cam = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SPACE_PRIMARY)
        cam.SetOrbit(math.radians(yaw), math.radians(pitch))
        cam.translationFromParent = pan

    def GoToAndReturnStartPosition(self, stayHere):
        bp = sm.GetService('michelle').GetBallpark()
        if stayHere:
            startPos = bp.GetCurrentEgoPos()
        else:
            startPos = (2500000000000.0, 0.0, 0.0)
            self.slash('/tr me pos=%s,%s,%s' % (startPos[0], startPos[1], startPos[2]))
        return startPos

    def SpawnTestcase(self, testID, startPos):
        self._SpawnShips(startPos, TEST_CASES[testID])

    def _SpawnShips(self, startPos, testCase):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        self.initialSceneState = set(scene.objects)
        yCount = 0
        xPos = startPos[0]
        for cntr in xrange(testCase.number_of_rows ** 2):
            typeId = testCase.ship_list[cntr % len(testCase.ship_list)]
            if yCount >= testCase.number_of_rows:
                xPos += testCase.distance_between_ships
                yCount = 0
            for zCount in xrange(testCase.number_of_rows):
                self.slash('/spawn %s pos=%s,%s,%s' % (typeId,
                 xPos,
                 yCount * testCase.distance_between_ships + startPos[1],
                 zCount * testCase.distance_between_ships + startPos[2]))

            yCount += 1

    def ClearAll(self, *args):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        ids = []
        for each in scene.objects:
            if each.__bluetype__ != 'trinity.EveShip2':
                continue
            ball = each.translationCurve
            if ball.id != session.shipid:
                ids.append(ball.id)

        for bid in ids:
            self.slash('/unspawn %s' % str(bid))

    def ApplyDamage(self, *args):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        additions = set(scene.objects) - self.initialSceneState
        for each in additions:
            if each.name.startswith('10000'):
                self.slash('/heal %s 0.5' % each.name)


class PerformanceBenchmarkWindow(Window):
    default_caption = 'Performance Tools'
    default_windowID = 'PerformanceToolsWindowID'
    default_width = 220
    default_height = 200
    default_topParentHeight = 0
    default_minSize = (default_width, default_height)
    default_wontUseThis = 10

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.lastPitch = 0.0
        self.lastYaw = 0.0
        self.camLock = False
        self.benchmarkRunning = False
        self.sceneDirector = SceneDirector()
        self.testOptions = [('classic cube of death', CUBE_CLASSIC),
         ('capital wrecks of death', CUBE_CAPITAL_WRECKS),
         ('AmarrCube', CUBE_AMARR),
         ('CaldariCube', CUBE_CALDARI),
         ('GallenteCube', CUBE_GALLENTE),
         ('MinmatarCube', CUBE_MINMATAR),
         ('UltraLODCube', CUBE_LOD),
         ('Add More Here', CUBE_ADD_MORE_HERE)]
        self.testCaseDescription = {CUBE_CLASSIC: 'Spawns a cube with a lot of different ships.',
         CUBE_CAPITAL_WRECKS: 'Spawns a cube with a lot of wrecks.',
         CUBE_AMARR: 'Spawns a cube of Amarr ships.',
         CUBE_CALDARI: 'Spawns a cube of Caldari ships.',
         CUBE_GALLENTE: 'Spawns a cube of Gallente ships.',
         CUBE_MINMATAR: 'Spawns a cube of Minmatar ships.',
         CUBE_LOD: 'Spawns a cube of ships around the camera.',
         CUBE_ADD_MORE_HERE: 'Does nothing useful.'}
        self.camPresetOptions = [('None', CAMERA_PRESET_NONE),
         ('Deathcube Far', CAMERA_PRESET_FAR),
         ('Deathcube Near', CAMERA_PRESET_NEAR),
         ('Deathcube UltraLOD', CAMERA_PRESET_ULTRA_LOD)]
        self._AddHeader('Test Cases')
        self._SetupTestCasePanel(self.sr.main)
        self._AddHeader('Camera')
        self._SetupCameraPanel(self.sr.main)
        self.benchmarkButton = Button(name='myButton', parent=self.sr.main, align=uiconst.CENTERBOTTOM, label='Start Benchmark', func=self.ToggleBenchmark, width=40, padding=(0, 0, 0, 6))

    def _AddHeader(self, text):
        EveHeaderSmall(parent=self.sr.main, text=text, align=uiconst.TOTOP, padding=(8, 6, 0, 3))

    def _SetupTestCasePanel(self, mainCont):
        cont = Container(name='cont', parent=mainCont, align=uiconst.TOTOP, padLeft=4, padRight=4, height=40)
        self.testCombo = Combo(parent=cont, align=uiconst.TOTOP, options=self.testOptions, callback=self.TestComboChanged)
        self.testCombo.SetHint(self.testCaseDescription[1])
        buttonBox = Container(name='buttonBox', parent=cont, align=uiconst.TOTOP, padTop=3, height=20)
        self.stayHereCheckbox = Checkbox(parent=buttonBox, text=u'Stay where you are', align=uiconst.TOLEFT, checked=False, height=18, width=120)
        Button(parent=buttonBox, label='Spawn', align=uiconst.TORIGHT, func=self.SpawnTestcase, width=40, height=18)
        Button(parent=buttonBox, label='Clear', align=uiconst.TORIGHT, func=self.sceneDirector.ClearAll, width=40, height=18)
        Button(parent=buttonBox, label='Damage', align=uiconst.TORIGHT, func=self.sceneDirector.ApplyDamage, width=40, height=18, hint='Wait for ships to load before calling this')

    def _SetupCameraPanel(self, mainCont):
        presetCont = Container(name='presetCont', parent=mainCont, align=uiconst.TOTOP, height=20, padLeft=4, padRight=4)
        Label(name='presetCombo', parent=presetCont, align=uiconst.TOLEFT, width=40, text='Preset')
        self.cboCamPresets = Combo(parent=presetCont, align=uiconst.TOTOP, options=self.camPresetOptions, callback=self.OnCamPreset)
        pitchCont = Container(name='pitchCont', parent=mainCont, align=uiconst.TOTOP, height=20, padLeft=4, padRight=4)
        Label(name='pitchLabel', parent=pitchCont, align=uiconst.TOLEFT, width=40, padTop=3, text='Pitch')
        self.pitchField = SinglelineEdit(name='pitchField', parent=pitchCont, align=uiconst.TOTOP, floats=[-90.0, 90.0, 1], setvalue=str(self.lastPitch))
        self.pitchField.OnChange = self.OnCamChange
        yawCont = Container(name='yawCont', parent=mainCont, align=uiconst.TOTOP, height=20, padLeft=4, padRight=4)
        Label(name='yawLabel', parent=yawCont, align=uiconst.TOLEFT, width=40, padTop=3, text='Yaw')
        self.yawField = SinglelineEdit(name='yawField', parent=yawCont, align=uiconst.TOTOP, floats=[-180.0, 180.0, 1], setvalue=str(self.lastYaw))
        self.yawField.OnChange = self.OnCamChange
        panCont = Container(name='panCont', parent=mainCont, align=uiconst.TOTOP, height=20, padLeft=4, padRight=4)
        Label(name='panLabel', parent=panCont, align=uiconst.TOLEFT, width=40, padTop=3, text='Pan')
        self.panField = SinglelineEdit(name='panField', parent=panCont, align=uiconst.TOTOP, ints=[0, 1000000], setvalue=0)
        self.panField.OnChange = self.OnCamChange
        uthread.new(self._GetCurrentCameraValues)

    def TestComboChanged(self, *args):
        self.testCombo.SetHint(self.testCaseDescription[self.testCombo.GetValue()])

    def OnCamChange(self, *args):
        if self.camLock:
            return
        self.lastPitch = float(self.pitchField.GetValue())
        self.lastYaw = float(self.yawField.GetValue())
        self.pan = int(self.panField.GetValue())
        self.sceneDirector.SetCamera(self.lastYaw, self.lastPitch, self.pan)

    def OnCamPreset(self, *args):
        presId = self.cboCamPresets.GetValue()
        if presId == 0:
            return
        pitch, yaw, pan = CAMERA_PRESETS[presId]
        self.camLock = True
        self.pitchField.SetValue(pitch)
        self.yawField.SetValue(yaw)
        self.panField.SetValue(pan)
        self.camLock = False
        self.OnCamChange()

    def ToggleBenchmark(self, *args):

        def _thread():
            frameTimes = []
            t0 = blue.os.GetWallclockTime()
            startTime = blue.os.GetWallclockTime()
            while self.benchmarkRunning:
                blue.synchro.Yield()
                t1 = blue.os.GetWallclockTime()
                ms = float(blue.os.TimeDiffInUs(t0, t1)) / 1000.0
                t0 = t1
                frameTimes.append(ms)
                if len(frameTimes) > 100000 or blue.os.TimeDiffInMs(startTime, t1) > 5000.0:
                    self.benchmarkRunning = False
                    break

            frameTimes.sort()
            median = frameTimes[len(frameTimes) / 2]
            minMS = frameTimes[0]
            maxMS = frameTimes[-1]
            summed = reduce(lambda x, y: x + y, frameTimes)
            avg = summed / len(frameTimes)
            result = 'Min: %0.1fms Max: %0.1fms\n' % (minMS, maxMS)
            result += 'Median:  %0.1fms %0.1ffps\n' % (median, 1000.0 / median)
            result += 'Average: %0.1fms %0.1ffps\n' % (avg, 1000.0 / avg)
            TextBox('Benchmark Results', result)
            self.benchmarkButton.SetLabel('Start Benchmark')

        if self.benchmarkRunning:
            self.benchmarkRunning = False
        else:
            self.benchmarkRunning = True
            self.benchmarkButton.SetLabel('Stop Benchmark')
            uthread.new(_thread)

    def _GetCurrentCameraValues(self):
        self.camLock = True
        cam = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SPACE_PRIMARY)
        self.lastPitch = math.degrees(cam.pitch)
        self.lastYaw = math.degrees(cam.yaw)
        self.pan = int(cam.translationFromParent)
        self.pitchField.SetValue(self.lastPitch)
        self.yawField.SetValue(self.lastYaw)
        self.panField.SetValue(self.pan)
        self.camLock = False
        self.OnCamChange()

    def SpawnTestcase(self, *args):
        testID = self.testCombo.GetValue()
        stayHere = self.stayHereCheckbox.GetValue()
        startPos = self.sceneDirector.GoToAndReturnStartPosition(stayHere)
        self.sceneDirector.SpawnTestcase(testID, startPos)
