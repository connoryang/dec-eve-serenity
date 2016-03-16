#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\control\browser\browserPane.py
import trinity
import corebrowserutil
from carbonui.primitives.base import Base
from carbonui.primitives.container import Container

class CoreBrowserPane(Base):
    __guid__ = 'browser.CoreBrowserPane'
    __renderObject__ = trinity.Tr2Sprite2dRenderJob

    def __init__(self, *args, **kwargs):
        self.viewport = trinity.TriViewport()
        Base.__init__(self, *args, **kwargs)
        self.isReady = True

    @apply
    def displayRect():
        doc = '\n            displayRect is a tuple of (displayX,displayY,displayWidth,displayHeight).\n            Prefer this over setting x, y, width and height separately if all are\n            being set.\n            '
        fget = Base.displayRect.fget

        def fset(self, value):
            Base.displayRect.fset(self, value)
            self.AdjustTextureSize()

        return property(**locals())

    @apply
    def displayX():
        doc = 'x-coordinate of render object'
        fget = Base.displayX.fget

        def fset(self, value):
            Base.displayX.fset(self, value)
            self.AdjustTextureSize()

        return property(**locals())

    @apply
    def displayY():
        doc = 'y-coordinate of render object'
        fget = Base.displayY.fget

        def fset(self, value):
            Base.displayY.fset(self, value)
            self.AdjustTextureSize()

        return property(**locals())

    @apply
    def displayWidth():
        doc = 'Width of render object'
        fget = Base.displayWidth.fget

        def fset(self, value):
            Base.displayWidth.fset(self, value)
            self.AdjustTextureSize()

        return property(**locals())

    @apply
    def displayHeight():
        doc = 'Height of render object'
        fget = Base.displayHeight.fget

        def fset(self, value):
            Base.displayHeight.fset(self, value)
            self.AdjustTextureSize()

        return property(**locals())

    def Startup(self, *args):
        self.texture = trinity.TriTextureRes(4, 4, 1, trinity.PIXEL_FORMAT.B8G8R8X8_UNORM)
        self.isTabStop = True
        self.cursor = 0
        self.browserSessionSurfaceManager = None
        self._browserSession = None
        self.surface = None
        self.textureAwaitingSwap = None
        self.textureWidth = 0
        self.textureHeight = 0
        self.renderJob = trinity.CreateRenderJob('Browser')
        self.renderObject.renderJob = self.renderJob
        self.renderJob.PythonCB(self.AdjustViewport)
        self.renderJob.SetViewport(self.viewport)
        self.renderJob.SetStdRndStates(trinity.RM_SPRITE2D)
        self.renderTextureStep = self.renderJob.RenderTexture(self.texture)
        trinity.device.RegisterResource(self)
        self.StartBrowserView()

    @apply
    def browserSession():

        def fget(self):
            return self._browserSession

        def fset(self, value):
            self._browserSession = value
            if self._browserSession:
                self.AdjustTextureSize()
                self.AdjustViewport()

        return property(**locals())

    def StartBrowserView(self):
        self.AdjustTextureSize()
        self.AdjustViewport()

    def SetCursor(self, cursorType):
        self.cursor = cursorType

    def OnSetFocus(self, *args):
        if self.browserSession is not None:
            self.browserSession.OnSetFocus(args)
            if uicore.imeHandler:
                uicore.imeHandler.SetFocus(self)

    def OnKillFocus(self, *args):
        if self.browserSession is not None:
            self.browserSession.OnKillFocus(args)
            if uicore.imeHandler:
                uicore.imeHandler.KillFocus(self)

    def CheckFocusChange(self, browse):
        return True

    def AdjustViewport(self):
        if not hasattr(self, 'isReady'):
            return
        l, t = self.displayX, self.displayY
        parent = self.GetParent()
        while parent:
            l += parent.displayX
            t += parent.displayY
            parent = parent.GetParent()

        self.viewport.x = l
        self.viewport.y = t
        self.viewport.width = self.displayWidth
        self.viewport.height = self.displayHeight

    def AdjustTextureSize(self):
        if not hasattr(self, 'isReady'):
            return
        w = self.displayWidth
        if w < 16:
            w = 16
        h = self.displayHeight
        if h < 16:
            h = 16
        if self.browserSession is not None:
            self.browserSession.SetBrowserSize(w, h)
        else:
            print 'browserSession is None'
        if w > self.textureWidth or h > self.textureHeight or w < self.textureWidth / 2 or h < self.textureHeight / 2:
            self.textureWidth = min(corebrowserutil.NextPowerOfTwo(max(w, self.AppGetMinWidth())), self.AppGetMaxWidth())
            self.textureHeight = min(corebrowserutil.NextPowerOfTwo(max(h, self.AppGetMinHeight())), self.AppGetMaxHeight())
            dev = trinity.device
            self.OnCreate(dev)
        if self.textureAwaitingSwap:
            return
        self.renderTextureStep.brTexCoord = (float(w) / self.textureWidth, float(h) / self.textureHeight)

    def GetTooltipPosition(self, *args, **kwds):
        return (uicore.uilib.x - 5,
         uicore.uilib.y - 5,
         10,
         10)

    def OnCreate(self, device):
        texture = trinity.TriTextureRes(self.textureWidth, self.textureHeight, 1, trinity.PIXEL_FORMAT.B8G8R8X8_UNORM)
        self.textureAwaitingSwap = texture
        self.surface = texture
        if self.browserSession is not None:
            self.browserSession.SetBrowserSurface(self.surface, self._OnSurfaceReady)

    def _OnClose(self):
        Container._OnClose(self)
        self.browserSession = None
        self.renderTextureStep = None
        self.renderJob = None

    def _OnSurfaceReady(self):
        if self.textureAwaitingSwap:
            self.renderTextureStep.brTexCoord = (float(self.displayWidth) / self.textureWidth, float(self.displayHeight) / self.textureHeight)
            self.renderTextureStep.texture = self.textureAwaitingSwap
            self.textureAwaitingSwap = None

    def ResizeBrowser(self):
        self.AdjustTextureSize()

    _OnResize = ResizeBrowser

    def OnBrowseTo(self):
        self.StartBrowserView()
        uicore.registry.SetFocus(self)

    def OnKeyDown(self, vkey, flag):
        if self.browserSession is not None:
            self.browserSession.OnKeyDown(vkey, flag)

    def OnKeyUp(self, vkey, flag):
        if self.browserSession is not None:
            self.browserSession.OnKeyUp(vkey, flag)

    def OnChar(self, char, flag):
        if self.browserSession is not None:
            self.browserSession.OnChar(char, flag)
            return True

    def OnMouseMove(self, *args):
        if self.browserSession is not None:
            l, t = self.GetAbsolutePosition()
            x = int((uicore.uilib.x - l) * uicore.desktop.dpiScaling)
            y = int((uicore.uilib.y - t) * uicore.desktop.dpiScaling)
            self.browserSession.OnMouseMove(x, y)

    def OnMouseDown(self, *args):
        if self.browserSession is not None:
            self.browserSession.OnMouseDown(args[0])

    def OnMouseUp(self, *args):
        if self.browserSession is not None:
            self.browserSession.OnMouseUp(args[0])

    def OnMouseWheel(self, *args):
        if self.browserSession is not None:
            self.browserSession.OnMouseWheel(uicore.uilib.dz)

    def GetSurface(self):
        return self.surface

    def AppGetMinWidth(self):
        return 16

    def AppGetMinHeight(self):
        return 16

    def AppGetMaxWidth(self):
        return 4096

    def AppGetMaxHeight(self):
        return 4096

    def SetLangIndicator(self, lang):
        pass


exports = {'browser.CoreBrowserPane': CoreBrowserPane}
