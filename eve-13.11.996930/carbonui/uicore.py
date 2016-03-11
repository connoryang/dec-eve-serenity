#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\uicore.py
import uthread
import blue
import log
import trinity
import weakref
import carbonui.const as uiconst
import carbonui
import carbonui.uilib
import carbonui.util.effect
import carbonui.uianimations
from carbonui.control.xposeCoreClasses import ExposeCoreClassesWithOutCorePostfix

class UIDeviceResource():

    def __init__(self):
        dev = trinity.device
        dev.RegisterResource(self)

    def OnInvalidate(self, level):
        pass

    def OnCreate(self, dev):
        if getattr(uicore, 'uilib', None) is None:
            return
        uicore.UpdateCursor(uicore.uilib.mouseOver, 1)


class UICoreBase():
    fontHandler = None
    audioHandler = None
    imeHandler = None
    commandHandler = None
    tooltipHandler = None
    dpiScaling = 1.0

    def __init__(self, appName = None):
        import __builtin__
        if 'uicore' in __builtin__.__dict__.keys():
            pass
        else:
            if appName is None:
                try:
                    appName = boot.appname
                except:
                    appName = 'CarbonUI'

            self.newRendererEnabled = False
            self.fontSizeFactor = 1.0
            self._lastCursor = None
            self._cursorSprite = None
            self._hint = None
            self.isRunning = False
            self.desktop = None
            self.dragData = None
            self.dragObject = None
            self.triappargs = {'title': appName,
             'left': 0,
             'top': 0,
             'colordepth': 0,
             'exclusiveInput': 0,
             'refreshrate': 0}
            __builtin__.uicore = self
        self.textObjects = weakref.WeakSet()
        self.deviceResource = UIDeviceResource()

    def Startup(self, layerlist = None, clientStartup = True):
        if clientStartup:
            sm.GetService('settings').LoadSettings()
            deviceSvc = sm.StartServiceAndWaitForRunningState('device')
            deviceSvc.CreateDevice()
            self.device = deviceSvc
            ExposeCoreClassesWithOutCorePostfix()
        self.uilib = self.event = carbonui.uilib.Uilib()
        self.desktop = self.uilib.desktop
        if self.fontHandler is None:
            self.LoadBaseFontHandler()
        if self.audioHandler is None:
            self.LoadBaseAudioHandler()
        from carbonui.services.registry import RegistryHandler
        self.registry = RegistryHandler()
        if clientStartup:
            from carbonui.services.ime import ImeHandler
            self.imeHandler = ImeHandler()
        self.LoadLayers(layerlist)
        self.effect = carbonui.util.effect.UIEffects()
        self.animations = carbonui.uianimations.animations
        trinity.device.RegisterResource(self)
        self.isRunning = True

    def LoadBaseFontHandler(self):
        from carbonui.services.font import FontHandler
        self.SetFontHandler(FontHandler())

    def SetFontHandler(self, fontHandler):
        self.fontHandler = fontHandler
        self.font = fontHandler

    def LoadBaseAudioHandler(self):
        from carbonui.handlers.audioHandler import AudioHandler
        self.audioHandler = AudioHandler()

    def SetAudioHandler(self, audioHandler):
        self.audioHandler = audioHandler

    def SetCommandHandler(self, commandHandler):
        self.commandHandler = commandHandler
        self.cmd = commandHandler

    def SetTooltipHandler(self, tooltipHandler):
        self.tooltipHandler = tooltipHandler

    def IsReady(self):
        return getattr(self, 'isRunning', False)

    def OnInvalidate(self, *args):
        self.layer.hint.Flush()
        self._hint = None

    def OnCreate(self, *args):
        self.layer.hint.Flush()
        self._hint = None

    def LoadLayers(self, layerlist):
        self.layer = carbonui.control.layer.LayerManager()
        self.layerData = {}
        self.layerList = layerlist
        layerlist = layerlist or self.GetDefaultLayers()
        for layerName, className, subLayers in layerlist:
            self.desktop.AddLayer(layerName, className, subLayers)

    def GetDefaultLayers(self):
        layers = [('l_hint', None, None),
         ('l_menu', None, None),
         ('l_modal', None, None),
         ('l_abovemain', None, None),
         ('l_main', None, None),
         ('l_loading', None, None),
         ('l_dragging', None, None)]
        return layers

    def CheckCursor(self):
        self.UpdateCursor(uicore.uilib.mouseOver)

    def CheckHint(self):
        pass

    def UpdateHint(self, item, force = 0):
        pass

    def IsHintVisible(self):
        return self._hint and self._hint.display

    def HideHint(self):
        if self.IsHintVisible():
            self._hint.LoadHint('')

    def UpdateCursor(self, item, force = 0):
        cursor = 0
        ic = getattr(item, 'cursor', None)
        if ic is not None and ic >= 0:
            cursor = ic
        elif item:
            if item.HasEventHandler('OnChar'):
                cursor = 7
            else:
                hasGetMenu = item.HasEventHandler('GetMenu')
                clickFunc = item.HasEventHandler('OnClick')
                if clickFunc:
                    if hasGetMenu:
                        cursor = 22
                    else:
                        cursor = 1
                elif hasGetMenu:
                    cursor = 12
        if force or self._lastCursor != cursor:
            self.uilib.SetCursor(cursor)
            self._lastCursor = cursor

    def GetLayer(self, name):
        return self.layer.GetLayer(name)

    def Message(self, *args, **kw):
        print 'Unhandled carbonui.Message', args, kw

    def WaitForResourceLoad(self):
        fence = trinity.device.GetCurrentResourceLoadFence()
        timeWaited = 0
        while trinity.device.GetLastResourceLoadFenceReached() < fence:
            waitMs = 100
            blue.pyos.synchro.SleepWallclock(waitMs)
            timeWaited += waitMs
            if timeWaited % 5000 == 0:
                log.general.Log('WaitForResourceLoad has waited for %d seconds! (%d vs. %d)' % (timeWaited / 1000, trinity.device.GetLastResourceLoadFenceReached(), fence), log.LGERR)

    def ScaleDpi(self, value):
        return int(value * self.dpiScaling + 0.5)

    def ScaleDpiF(self, value):
        return value * self.dpiScaling

    def ReverseScaleDpi(self, value):
        if self.dpiScaling != 1.0:
            try:
                return int(value / self.dpiScaling + 0.5)
            except (ValueError, OverflowError):
                return 0

        else:
            return int(value)

    def IsDragging(self):
        return not self.dragObject == None

    def DrawDebugLine(self, pos1, pos2, width = 2, color1 = None, color2 = None):
        import util
        color1 = color1 or util.Color.YELLOW
        color2 = color2 or util.Color.RED
        self.ConstructDebugLineset()
        self.debugLineSet.AddStraightLine(pos1, color1, pos2, color2, width)
        self.debugLineSet.SubmitChanges()

    def DrawDebugAxis(self, pos = None, lineWidth = 5, len = 1000.0):
        import geo2, util
        self.ConstructDebugLineset()
        if not pos:
            pos = (0, 0, 0)
        self.debugLineSet.AddStraightLine(pos, util.Color.YELLOW, geo2.Add(pos, (len, 0, 0)), util.Color.YELLOW, lineWidth)
        self.debugLineSet.AddStraightLine(pos, util.Color.RED, geo2.Add(pos, (0, len, 0)), util.Color.RED, lineWidth)
        self.debugLineSet.AddStraightLine(pos, util.Color.GREEN, geo2.Add(pos, (0, 0, len)), util.Color.GREEN, lineWidth)
        self.debugLineSet.SubmitChanges()

    def ClearDebugLines(self):
        self.debugLineSet.ClearLines()
        self.debugLineSet.SubmitChanges()

    def ConstructDebugLineset(self):
        if hasattr(self, 'debugLineSet'):
            scene = sm.GetService('sceneManager').GetActiveScene()
            if self.debugLineSet in scene.objects:
                return
        self.debugLineSet = trinity.EveCurveLineSet()
        self.debugLineSet.scaling = (1.0, 1.0, 1.0)
        tex2D1 = trinity.TriTextureParameter()
        tex2D1.name = 'TexMap'
        tex2D1.resourcePath = 'res:/texture/global/lineSolid.dds'
        self.debugLineSet.lineEffect.resources.append(tex2D1)
        tex2D2 = trinity.TriTextureParameter()
        tex2D2.name = 'OverlayTexMap'
        tex2D2.resourcePath = 'res:/UI/Texture/Planet/link.dds'
        self.debugLineSet.lineEffect.resources.append(tex2D2)
        scene = sm.GetService('sceneManager').GetActiveScene()
        scene.objects.append(self.debugLineSet)
        return self.debugLineSet


uicorebase = UICoreBase()
