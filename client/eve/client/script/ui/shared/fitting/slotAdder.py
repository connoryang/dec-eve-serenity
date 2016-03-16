#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\slotAdder.py
import math
from carbonui.const import UI_NORMAL
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.shared.fitting.fittingUtil import GetScaleFactor, GetBaseShapeSize
from eve.client.script.ui.shared.fitting.slot import FittingSlot
import mathUtil
import telemetry

class SlotAdder(object):

    def __init__(self, controller, slotClass = None):
        self.controller = controller
        scaleFactor = GetScaleFactor()
        self.width = int(round(44.0 * scaleFactor))
        self.height = int(round(54.0 * scaleFactor))
        self.rad = int(239 * scaleFactor)
        self.center = GetBaseShapeSize() / 2
        if slotClass:
            self.slotClass = slotClass
        else:
            self.slotClass = FittingSlot

    def AddSlot(self, parent, flagID):
        left, top, cos, sin = self.GetPositionNumbers(self.angle)
        radCosSin = (self.rad,
         cos,
         sin,
         self.center,
         self.center)
        ret = self.slotClass(name='%s' % flagID, parent=parent, pos=(left,
         top,
         self.width,
         self.height), rotation=-mathUtil.DegToRad(self.angle), opacity=0.0, radCosSin=radCosSin, controller=self.controller.GetSlotController(flagID))
        self.angle += self.stepSize
        return ret

    def StartGroup(self, arcStart, arcLength, numSlots):
        self.angle = arcStart
        self.stepSize = arcLength / numSlots

    @telemetry.ZONE_METHOD
    def GetPositionNumbers(self, angle):
        cos = math.cos((angle - 90.0) * math.pi / 180.0)
        sin = math.sin((angle - 90.0) * math.pi / 180.0)
        left = int(round(self.rad * cos + self.center - self.width / 2.0))
        top = int(round(self.rad * sin + self.center - self.height / 2.0))
        return (left,
         top,
         cos,
         sin)


class HardpointAdder(object):

    def __init__(self, attributeConst, cX, cY, isleftSide = False):
        self.isleftSide = isleftSide
        self.attribute = cfg.dgmattribs.Get(attributeConst)
        self.cX = cX
        self.cY = cY
        self.slots = []
        self.step = 3.0 / GetScaleFactor()

    def AddIcon(self, parent, iconNum, tooltipCallback):
        angle = 306
        iconRad = int(310 * GetScaleFactor())
        left, top, cos, sin = self.GetPositionNumbers(angle, iconRad, offset=16)
        icon = Icon(name='%s_Icon' % self.attribute.attributeName, icon=iconNum, parent=parent, state=UI_NORMAL, hint=self.attribute.displayName, pos=(left,
         top,
         32,
         32), ignoreSize=True)
        icon.LoadTooltipPanel = tooltipCallback

    def AddMarkers(self, parent):
        markerRad = int(280 * GetScaleFactor())
        angle = 310.0 - self.step * 7.5
        for i in xrange(8):
            left, top, cos, sin = self.GetPositionNumbers(angle, markerRad, offset=8)
            icon = MarkerIcon(name='%s_%s_Marker' % (i, self.attribute.attributeName), parent=parent, state=UI_NORMAL, pos=(left,
             top,
             16,
             16), hint=self.attribute.displayName, idx=0)
            icon.display = False
            self.slots.insert(0, icon)
            angle += self.step

    def GetPositionNumbers(self, angle, rad, offset):
        if self.isleftSide:
            angle = 180 - angle
        cos = math.cos(angle * math.pi / 180.0)
        sin = math.sin(angle * math.pi / 180.0)
        left = int(round(rad * cos + self.cX - offset))
        top = int(round(rad * sin + self.cY - offset))
        return (left,
         top,
         cos,
         sin)


class MarkerIcon(Sprite):
    slotTaken = 'res:/UI/Texture/classes/Fitting/slotTaken.png'
    slotLeft = 'res:/UI/Texture/classes/Fitting/slotLeft.png'
    default_texturePath = slotLeft
    slotColorNormal = (1.0, 1.0, 1.0, 0.7)
    slotColorRed = (1.0, 0.0, 0.0, 0.7)
    slotColorYellow = (1.0, 1.0, 0.0, 0.7)

    def ModifyLook(self, slotIdx, slotsLeft, slotsFitted, slotsAddition):
        if slotIdx < slotsFitted:
            self.texturePath = self.slotTaken
        else:
            self.texturePath = self.slotLeft
        if slotIdx < slotsLeft + slotsFitted:
            if slotIdx < slotsLeft + slotsFitted + slotsAddition:
                self.color.SetRGB(*self.slotColorNormal)
            else:
                self.color.SetRGB(*self.slotColorRed)
            self.display = True
        elif slotIdx < slotsLeft + slotsFitted + slotsAddition:
            self.color.SetRGB(*self.slotColorYellow)
            self.display = True
        else:
            self.display = False
