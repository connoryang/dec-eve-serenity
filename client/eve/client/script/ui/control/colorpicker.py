#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\colorpicker.py
from carbonui.control.menu import ClearMenuLayer
import trinity
import carbonui.const as uiconst
import uiprimitives
import uicontrols
import uiutil
import menu
import log

class ColorPicker(uiprimitives.Container):
    __guid__ = 'uicontrols.ColorPicker'
    OnColorChange = None

    def Startup(self, hsv = None, *args):
        leftPush = 0
        self.SetHSV(hsv)
        hsv = self.orgcolor.GetHSV()
        colorPanel = ColorPanel(name='ColorPanel', align=uiconst.TOPLEFT, width=255, height=255, parent=self, state=uiconst.UI_NORMAL, clipChildren=1)
        uicontrols.Frame(parent=colorPanel)
        colorPanel.Startup()
        colorPanel.OnChange = self.ColorPanelChange
        colorPanel.SetHSV(hsv)
        self.sr.colorPanel = colorPanel
        leftPush = colorPanel.left + colorPanel.width + const.defaultPadding
        colorSlider = ColorSlider(name='ColorSlider', align=uiconst.TOPLEFT, left=leftPush, height=255, width=36, parent=self, state=uiconst.UI_NORMAL)
        colorSlider.Startup()
        colorSlider.OnSliderChange = self.ColorSliderChange
        colorSlider.SetHSV(hsv)
        self.sr.colorSlider = colorSlider
        leftPush = colorSlider.left + colorSlider.width + const.defaultPadding
        self.sr.colorInfo = uiprimitives.Container(name='colorInfo', align=uiconst.TOPLEFT, left=leftPush, width=56, height=255, parent=self)
        colorPreview = ColorPreview(name='colorPreview', align=uiconst.TOPLEFT, height=32, width=self.sr.colorInfo.width, parent=self.sr.colorInfo)
        uicontrols.Frame(parent=colorPreview)
        colorPreview.Startup()
        colorPreview.SetHSV(hsv)
        self.sr.colorPreview = colorPreview
        import xtriui
        colorControl = xtriui.ColorControl(name='colorControl', align=uiconst.TOPLEFT, width=self.sr.colorInfo.width, top=36, height=219, parent=self.sr.colorInfo)
        colorControl.Startup()
        colorControl.OnColorControlChange = self.ColorControlChange
        colorControl.SetHSV(hsv)
        self.sr.colorControl = colorControl

    def ColorSliderChange(self, slider, value):
        h, s, v = self.orgcolor.GetHSV()
        nh = (1.0 - value) * 360.0
        nColor = self.ClipHSV((nh, s, v))
        self.orgcolor.SetHSV(*nColor)
        self.sr.colorPreview.SetHSV(nColor)
        self.sr.colorPanel.SetHSV(nColor)
        self.sr.colorControl.SetHSV(nColor)
        self.OnColorChange(nColor)

    def ColorPanelChange(self, panel, value):
        h, s, v = self.orgcolor.GetHSV()
        x, y = value
        ns, nv = x, 1.0 - y
        nColor = self.ClipHSV((h, ns, nv))
        self.orgcolor.SetHSV(*nColor)
        self.sr.colorPreview.SetHSV(nColor)
        self.sr.colorControl.SetHSV(nColor)
        self.OnColorChange(nColor)

    def ColorControlChange(self, nColor):
        nColor = self.ClipHSV(nColor)
        self.orgcolor.SetHSV(*nColor)
        self.sr.colorPreview.SetHSV(nColor)
        self.sr.colorPanel.SetHSV(nColor)
        self.sr.colorSlider.SetHSV(nColor)
        self.OnColorChange(nColor)

    def SetHSV(self, hsv):
        self.orgcolor = trinity.TriColor(1.0, 0.0, 0.0)
        self.orgcolor.a = 1.0
        if hsv is not None:
            self.orgcolor.SetHSV(*hsv)

    def ClipHSV(self, hsv):
        h, s, v = hsv
        h = min(359.999, h)
        return (h, s, v)

    def OnColorChange(self, value):
        pass


class ColorSwatch(uiprimitives.Container):
    __guid__ = 'uicontrols.ColorSwatch'
    swatches = [('faf5e1', None),
     ('ebd492', None),
     ('cb9133', None),
     ('825830', None),
     ('f6e631', None),
     ('f59122', None),
     ('d95100', None),
     ('bf1616', None),
     ('790000', None),
     ('7f1157', None),
     ('abc8e2', None),
     ('598cb9', None),
     ('375d81', None),
     ('3b8bd1', None),
     ('124d8c', None),
     ('183152', None),
     ('185662', None),
     ('6e9058', None),
     ('3f740b', None),
     ('516324', None),
     ('384328', None),
     ('bfb7aa', None),
     ('625e57', None),
     ('19191c', None)]
    swatchsize = 16

    def hex_to_rgb(self, colorstring):
        colorstring = colorstring.strip()
        if len(colorstring) != 6:
            raise ValueError, 'input #%s is not in #RRGGBB format' % colorstring
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [ int(n, 16) for n in (r, g, b) ]
        return (r / 255.0, g / 255.0, b / 255.0)

    def Startup(self, frameColor = (0.5, 0.5, 0.5, 1.0), padding = 0, *args):
        l, t, w, h = self.GetAbsolute()
        swatchesperrow = abs(w / self.swatchsize)
        x, y = (0, 0)
        for hex, swatchID in self.swatches:
            sc = uiprimitives.Container(name='bottom', parent=self, align=uiconst.TOPLEFT, pos=(x * self.swatchsize,
             y * self.swatchsize,
             self.swatchsize,
             self.swatchsize), state=uiconst.UI_NORMAL, padding=(padding,
             padding,
             padding,
             padding))
            sc.OnClick = (self.OnPickColor, sc)
            sc.swatchID = swatchID
            uicontrols.Frame(parent=sc, color=frameColor)
            color = self.hex_to_rgb(hex)
            uiprimitives.Fill(parent=sc, color=color)
            x += 1
            if x == swatchesperrow:
                x = 0
                y += 1

    def OnPickColor(self, obj, *args):
        fill = uiutil.FindChild(obj, 'fill')
        if fill and self.sr.dad is not None:
            if hasattr(self.sr.dad, 'SetHSV'):
                self.sr.dad.SetHSV(fill.color.GetHSV())


class ColorPanel(uiprimitives.Container):
    __guid__ = 'uicontrols.ColorPanel'
    dragging = 0
    EndPanelMove = None
    StartPanelMove = None
    WhilePanelMove = None

    def Startup(self):
        self.sr.mark = None
        illsprite = uiprimitives.Sprite(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/colorgradient.dds')
        self.sr.colorfill = uiprimitives.Fill(parent=self, color=(0.0, 1.0, 0.0, 1.0))
        self.value = [0.0, 0.0]

    def SetHSV(self, hsv):
        h, s, v = hsv
        self.value = [s, 1.0 - v]
        self.PositionMark()
        self.sr.colorfill.color.SetHSV(h, 1.0, 1.0)

    def GetRGB(self):
        r = self.sr.colorfill.color.r
        g = self.sr.colorfill.color.g
        b = self.sr.colorfill.color.b
        return (r, g, b)

    def GetHSV(self):
        h = None
        s, v = self.value
        return (h, s, v)

    def PositionMark(self):
        l, t, w, h = self.GetAbsolute()
        x, y = self.value
        if self.sr.mark is None:
            self.sr.mark = uiprimitives.Sprite(parent=self, idx=0, pos=(0, 0, 16, 16), name='pointer', state=uiconst.UI_PICKCHILDREN, texturePath='res:/UI/Texture/Shared/circleThin16.png', align=uiconst.RELATIVE)
        self.sr.mark.left = int(w * x) - self.sr.mark.width / 2
        self.sr.mark.top = int(h * y) - self.sr.mark.height / 2

    def UpdateValue(self):
        l, t, w, h = self.GetAbsolute()
        mx = uicore.uilib.x
        my = uicore.uilib.y
        x = max(0.0, min(1.0, (mx - l) / float(w)))
        y = max(0.0, min(1.0, (my - t) / float(h)))
        self.value = [x, y]

    def OnMouseMove(self, *args):
        if self.dragging:
            self.UpdateValue()
            self.PositionMark()
            uicore.uilib.SetCursor(uiconst.UICURSOR_NONE)
            self.OnChange(self, self.value)

    def OnMouseDown(self, *args):
        self.dragging = 1
        self.UpdateValue()
        self.PositionMark()
        if getattr(self, 'StartPanelMove', None):
            self.StartPanelMove()

    def OnMouseUp(self, *args):
        self.dragging = 0
        self.PositionMark()
        if getattr(self, 'EndPanelMove', None):
            self.EndPanelMove()
        sm.GetService('ui').ForceCursorUpdate()

    def OnChange(self, me, value):
        pass


class ColorSlider(uiprimitives.Container):
    __guid__ = 'uicontrols.ColorSlider'
    dragging = 0
    value = 0.0
    OnSliderChange = None

    def Startup(self):
        self.sr.mark = None
        sub = uiprimitives.Container(name='colorSpectrum', height=self.height, width=24, align=uiconst.CENTERLEFT, parent=self)
        uicontrols.Frame(parent=sub)
        illsprite = uiprimitives.Sprite(parent=sub, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/colorspectrum.dds')

    def SetHSV(self, hsv):
        h, s, v = hsv
        self.value = 1.0 - h / 360.0
        self.PositionSliderMark()

    def GetValue(self):
        return self.value

    def SetValue(self, intColor):
        proportion = intColor / 360.0
        l, t, w, h = self.GetAbsolute()
        self.endy = int(h * proportion)
        if self.sr.mark:
            self.sr.mark.top = self.endy - self.sr.mark.height / 2

    def PositionSliderMark(self):
        if self.sr.mark is None:
            self.sr.mark = uiprimitives.Container(name='mark', parent=self, align=uiconst.TOPLEFT, width=self.width, height=self.width, idx=0, state=uiconst.UI_DISABLED)
            illsprite = uiprimitives.Sprite(parent=self.sr.mark, state=uiconst.UI_DISABLED, align=uiconst.RELATIVE, width=36, height=36, texturePath='res:/UI/Texture/colorslider.dds')
        if self.sr.mark:
            l, t, w, h = self.GetAbsolute()
            self.sr.mark.top = int(h * self.value) - self.sr.mark.height / 2

    def UpdateSliderValue(self):
        l, t, w, h = self.GetAbsolute()
        my = uicore.uilib.y
        self.value = max(0.0, min(1.0, (my - t) / float(h)))
        self.PositionSliderMark()
        self.OnSliderChange(self, self.value)

    def OnMouseDown(self, *args):
        self.dragging = 1
        self.UpdateSliderValue()

    def OnMouseUp(self, *args):
        self.dragging = 0
        self.PositionSliderMark()

    def OnMouseMove(self, *args):
        if self.dragging:
            self.UpdateSliderValue()

    def OnSliderChange(self, slider, value):
        pass


class ColorPreview(uiprimitives.Container):
    __guid__ = 'uicontrols.ColorPreview'
    expanding = 0
    expanded = 0

    def Startup(self):
        self.sr.preview = preview = uiprimitives.Container(parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_NORMAL)
        self.sr.preview.OnClick = self.OnPickColor
        self.sr.colorfill = uiprimitives.Fill(parent=preview, color=(0.0, 1.0, 0.0, 1.0))

    def OnPickColor(self, *args):
        if not self.expanding and not self.expanded:
            self.Expand()

    def Expand(self, *args):
        self.expanding = 1
        if sm.GetService('connection').IsConnected():
            eve.Message('ComboExpand')
        log.LogInfo('ColorPreview', self.name, 'expanding')
        colorpar = uiprimitives.Container(name='colors', align=uiconst.TOPLEFT, width=112, height=62)
        uicore.layer.menu.children.insert(0, colorpar)
        colorSwatch = ColorSwatch(name='colorSwatch', align=uiconst.TOALL, parent=colorpar)
        colorSwatch.Startup()
        colorSwatch.sr.dad = self
        self.sr.wndUnderlay = uicontrols.WindowUnderlay(parent=colorpar)
        self.sr.wndUnderlay.padding = -6
        l, t, w, h = self.sr.preview.GetAbsolute()
        colorpar.left = [l + w, l - colorpar.width][l + w + colorpar.width > uicore.desktop.width]
        colorpar.top = [t + h, t - colorpar.height][t + h + colorpar.height > uicore.desktop.height]
        colorpar.state = uiconst.UI_NORMAL
        self.colorpar = colorpar
        self.sr.cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalClick)
        self.expanding = 0
        self.expanded = 1
        log.LogInfo('ColorPreview', self.name, 'expanded')

    def OnGlobalClick(self, fromwhere, *etc):
        if self.colorpar:
            if uicore.uilib.mouseOver == self.colorpar or uiutil.IsUnder(fromwhere, self.colorpar):
                log.LogInfo('ColorPreview.OnGlobalClick Ignoring all clicks from colorpar')
                return 1
            self.Cleanup()
        return 0

    def Cleanup(self, setfocus = 1):
        if self.sr.cookie:
            uicore.event.UnregisterForTriuiEvents(self.sr.cookie)
            self.sr.cookie = None
            self.colorpar = None
            ClearMenuLayer()
            self.expanded = 0
        if setfocus:
            uicore.registry.SetFocus(self)

    def OnGlobalMouseDown(self, downOn):
        if not uiutil.IsUnder(downOn, self.colorpar):
            ClearMenuLayer()

    def SetHSV(self, hsv):
        self.sr.colorfill.color.SetHSV(*hsv)
        if self.sr.dad and hasattr(self.sr.dad, 'SetHSV'):
            if self.sr.layerid is not None:
                self.sr.dad.SetHSV(self.sr.layerid, self.sr.colorfill.color.GetHSV())
            else:
                self.sr.dad.SetHSV(self.sr.colorfill.color.GetHSV())

    def FromInt(self, val):
        c = trinity.TriColor()
        c.FromInt(val)
        self.sr.colorfill.SetRGBA(c.r, c.g, c.b, c.a)
        self.SetHSV(c.GetHSV())

    def AsInt(self):
        self.sr.colorfill.color.AsInt()

    def FromSwatch(self, swatch):
        cswatch = ColorSwatch()
        ccolor = cswatch.hex_to_rgb(cswatch.swatches[swatch])
        self.sr.colorfill.color.SetRGB(*ccolor)
