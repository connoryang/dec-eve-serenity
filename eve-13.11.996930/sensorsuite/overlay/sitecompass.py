#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sensorsuite\overlay\sitecompass.py
from carbon.common.lib import telemetry
from carbon.common.lib.const import SEC
from carbon.common.script.util.mathUtil import MATH_PI_2, MATH_2_PI, MATH_PI_8
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
import carbonui.const as uiconst
import geo2
import math
import logging
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.camera.cameraUtil import IsNewCameraActive
from eve.client.script.ui.control.buttonGroup import ButtonGroup
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.tooltips import ShortcutHint
from eve.client.script.ui.eveFontConst import STYLE_HEADER
import evecamera
import gametime
import sensorsuite.overlay.const as overlayConst
from sensorsuite.overlay.sitetype import *
from eve.client.script.util.settings import IsShipHudTopAligned
import localization
from sensorsuite.overlay.siteconst import COMPASS_DIRECTIONS_COLOR, COMPASS_SWEEP_COLOR, COMPASS_OPACITY_ACTIVE
from sensorsuite.overlay.sitefilter import SiteButton
import trinity
logger = logging.getLogger(__name__)
COMPASS_WIDTH = 200
INDICATOR_RADIUS_OFFSET = 16
INDICATOR_HEIGHT = 18
INDICATOR_WIDTH = 15
INCLINATION_TICK_MAX_OFFSET = 6
INCLINATION_TICK_TOP_OFFSET = 0
INCLINATION_TICK_BASE_OPACITY = 0.5
INCLINATION_TICK_HIGHLIGHT_OPACITY = 0.4
INCLINATION_HIGHLIGHT_RANGE_RADIANS = MATH_PI_8

def AreVectorsEqual(a, b, delta):
    for x in xrange(3):
        if math.fabs(a[x] - b[x]) > delta:
            return False

    return True


class Compass(Container):
    default_name = 'compass'
    default_width = COMPASS_WIDTH
    default_height = COMPASS_WIDTH
    default_align = uiconst.CENTER
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.michelle = sm.GetService('michelle')
        self.frameContainer = Container(name='compass_transform', parent=self, width=COMPASS_WIDTH, height=COMPASS_WIDTH, align=uiconst.CENTER)
        self.compassTransform = Transform(name='compass_transform', parent=self, width=COMPASS_WIDTH, height=COMPASS_WIDTH, align=uiconst.CENTER, opacity=COMPASS_OPACITY_ACTIVE)
        Sprite(name='compass_dots', bgParent=self.compassTransform, texturePath='res:/UI/Texture/classes/SensorSuite/compass_dots.png', color=COMPASS_DIRECTIONS_COLOR.GetRGBA())
        self.sweepTransform = Transform(bgParent=self.compassTransform, name='compass_transform', width=COMPASS_WIDTH, height=COMPASS_WIDTH, align=uiconst.CENTER, opacity=0.0)
        Sprite(name='sensor_sweep', bgParent=self.sweepTransform, texturePath='res:/UI/Texture/classes/SensorSuite/scan_sweep.png', blendMode=trinity.TR2_SBM_ADD, color=COMPASS_SWEEP_COLOR.GetRGBA())
        Sprite(name='sensor_centerline', bgParent=self.frameContainer, texturePath='res:/UI/Texture/classes/SensorSuite/compass_centerline.png', blendMode=trinity.TR2_SBM_ADD, opacity=0.2)
        Sprite(name='compass_underlay', bgParent=self.frameContainer, texturePath='res:/UI/Texture/classes/SensorSuite/compass_underlay.png')
        self.sensorSuite = sm.GetService('sensorSuite')
        self.siteIndicatorsBySiteID = {}
        self.lastPose = None
        logger.debug('Compass updating starting')
        self.timer = AutoTimer(40, self.__UpdateCompass)
        self.sensorSuite.Subscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SITE_CHANGED, self.OnSiteChanged)
        self.sensorSuite.Subscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SWEEP_STARTED, self.OnSweepStarted)
        self.sensorSuite.Subscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SWEEP_ENDED, self.OnSweepEnded)
        self.sensorSuite.Subscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_ENABLED, self.OnSensorOverlayEnabled)
        self.sensorSuite.Subscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_DISABLED, self.OnSensorOverlayDisabled)
        if self.sensorSuite.IsOverlayActive():
            self.OnSensorOverlayEnabled()
        else:
            self.OnSensorOverlayDisabled()

    def OnSensorOverlayEnabled(self):
        animations.FadeIn(self.frameContainer, endVal=1.0, duration=0.2, curveType=uiconst.ANIM_SMOOTH)
        animations.FadeIn(self.compassTransform, endVal=COMPASS_OPACITY_ACTIVE, duration=0.2, curveType=uiconst.ANIM_OVERSHOT5)

    def OnSensorOverlayDisabled(self):
        animations.FadeTo(self.frameContainer, startVal=self.frameContainer.opacity, endVal=0.1, duration=0.75, curveType=uiconst.ANIM_SMOOTH)
        animations.FadeTo(self.compassTransform, startVal=self.compassTransform.opacity, endVal=0.15, duration=0.4, curveType=uiconst.ANIM_SMOOTH)

    def GetCamera(self):
        return sm.GetService('sceneManager').GetActiveSpaceCamera()

    def Close(self):
        Container.Close(self)
        self.timer = None
        self.sensorSuite.Unsubscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SITE_CHANGED, self.OnSiteChanged)
        self.sensorSuite.Unsubscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SWEEP_STARTED, self.OnSweepStarted)
        self.sensorSuite.Unsubscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SWEEP_ENDED, self.OnSweepEnded)
        self.sensorSuite.Unsubscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_ENABLED, self.OnSensorOverlayEnabled)
        self.sensorSuite.Unsubscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_DISABLED, self.OnSensorOverlayDisabled)

    @telemetry.ZONE_METHOD
    def __UpdateCompass(self):
        bp = self.michelle.GetBallpark()
        if bp is None:
            return
        camera = self.GetCamera()
        camParentRotation = camera.GetRotationQuat()
        camRotation = geo2.QuaternionRotationGetYawPitchRoll(camParentRotation)
        cx, cy, cz = geo2.QuaternionTransformVector(camParentRotation, (0, 0, -1.0))
        camLengthInPlane = geo2.Vec2Length((cx, cz))
        camAngle = math.atan2(cy, camLengthInPlane)
        yaw = camRotation[0]
        self.compassTransform.rotation = -yaw + math.pi
        myPos = bp.GetCurrentEgoPos()
        if self.lastPose:
            lastCamRot, lastPos = self.lastPose
            isNewCamRotation = not AreVectorsEqual(lastCamRot, camRotation, 0.05)
            isNewPosition = not AreVectorsEqual(lastPos, myPos, 0.5)
            isNewPose = isNewPosition or isNewCamRotation
        else:
            isNewPosition = True
            isNewPose = True
        for siteID, indicator in self.siteIndicatorsBySiteID.iteritems():
            if indicator.isNew or isNewPose:
                toSiteVec = geo2.Vec3SubtractD(indicator.data.position, myPos)
                toSiteVec = geo2.Vec3NormalizeD(toSiteVec)
                if indicator.isNew or isNewPosition:
                    angle = math.atan2(-toSiteVec[2], toSiteVec[0])
                    indicator.SetRotation(angle + MATH_PI_2)
                sx, sy, sz = toSiteVec
                siteLengthInPlane = geo2.Vec2Length((sx, sz))
                siteAngle = math.atan2(sy, siteLengthInPlane)
                inclinationAngle = siteAngle - camAngle
                verticalAngle = min(inclinationAngle, MATH_PI_2)
                indicator.SetInclination(verticalAngle)
                indicator.isNew = False

        self.lastPose = (camRotation, myPos)

    def OnSiteChanged(self, siteData):
        indicator = self.siteIndicatorsBySiteID.get(siteData.siteID)
        if indicator:
            indicator.isNew = True
        self.UpdateVisibleSites()

    def OnSweepStarted(self, systemReadyTime, durationInSec, viewAngleInPlane, orderedDelayAndSiteList, sweepStartDelaySec):
        logger.debug('OnSweepStarted readyTime=%s durationInSec=%s angle=%s sweepStartDelayMSec=%s', systemReadyTime, durationInSec, viewAngleInPlane, sweepStartDelaySec)
        timeNow = gametime.GetSimTime()
        timeSinceStartSec = float(timeNow - systemReadyTime) / SEC
        if timeSinceStartSec > sweepStartDelaySec:
            logger.debug('OnSweepStarted too late. timeSinceStartSec=%s timeNow=%s', timeSinceStartSec, timeNow)
            self.UpdateVisibleSites()
            self.OnSweepEnded()
            return
        curveSet = animations.CreateCurveSet(useRealTime=False)
        timeOffset = sweepStartDelaySec - timeSinceStartSec
        self.UpdateVisibleSites()
        animations.FadeTo(self.sweepTransform, duration=durationInSec, startVal=0.0, endVal=0.0, curveType=((0.05, 1.0), (0.95, 1.0)), timeOffset=timeOffset, curveSet=curveSet)
        viewAngleInPlane += MATH_PI_2
        animations.Tr2DRotateTo(self.sweepTransform, duration=durationInSec, startAngle=viewAngleInPlane, endAngle=viewAngleInPlane + MATH_2_PI, curveType=uiconst.ANIM_LINEAR, timeOffset=timeOffset, curveSet=curveSet)
        for delaySec, siteData in orderedDelayAndSiteList:
            indicator = self.siteIndicatorsBySiteID.get(siteData.siteID)
            if indicator:
                animations.FadeIn(indicator, duration=0.2, curveType=uiconst.ANIM_OVERSHOT, timeOffset=delaySec - timeSinceStartSec, curveSet=curveSet)

    def OnSweepEnded(self):
        for indicator in self.compassTransform.children:
            indicator.opacity = 1.0

    @telemetry.ZONE_METHOD
    def UpdateVisibleSites(self):
        if not self.sensorSuite.IsSolarSystemReady():
            return
        siteMap = self.sensorSuite.siteController.GetVisibleSiteMap()
        for siteID in self.siteIndicatorsBySiteID.keys():
            if siteID not in siteMap:
                self.RemoveSiteIndicator(siteID)

        for siteData in siteMap.itervalues():
            if siteData.siteID not in self.siteIndicatorsBySiteID:
                self.AddSiteIndicator(siteData)

    def AddSiteIndicator(self, siteData):
        logger.debug('adding site indicator %s', siteData.siteID)
        indicator = CompassIndicator(parent=self.compassTransform, siteData=siteData)
        if self.sensorSuite.IsSweepDone() or IsSiteInstantlyAccessible(siteData):
            indicator.opacity = 1.0
        else:
            indicator.opacity = 0.0
        self.siteIndicatorsBySiteID[siteData.siteID] = indicator

    def RemoveSiteIndicator(self, siteID):
        logger.debug('removing site indicator %s', siteID)
        indicator = self.siteIndicatorsBySiteID.pop(siteID)
        indicator.Close()

    def RemoveAll(self):
        for siteID in self.siteIndicatorsBySiteID.keys():
            self.RemoveSiteIndicator(siteID)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        LoadSensorOverlayFilterTooltip(tooltipPanel)

    def GetTooltipPosition(self):
        left, top, width, height = self.GetAbsolute()
        left += width / 2
        if IsShipHudTopAligned():
            top += height - 7
        else:
            top += 9
        return (left,
         top,
         0,
         0)

    def GetTooltipPointer(self):
        if IsShipHudTopAligned():
            return uiconst.POINT_TOP_2
        return uiconst.POINT_BOTTOM_2


class CompassIndicator(Transform):
    default_height = COMPASS_WIDTH - INDICATOR_RADIUS_OFFSET
    default_width = COMPASS_WIDTH - INDICATOR_RADIUS_OFFSET
    default_name = 'compass_indicator'
    default_align = uiconst.CENTER
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        Transform.ApplyAttributes(self, attributes)
        self.data = attributes.siteData
        self.sprite = Sprite(parent=self, texturePath='res:/UI/Texture/classes/SensorSuite/small_tick.png', align=uiconst.CENTERTOP, width=INDICATOR_WIDTH, height=INDICATOR_HEIGHT, color=self.data.baseColor.GetRGBA(), blendMode=trinity.TR2_SBM_ADDX2, opacity=INCLINATION_TICK_BASE_OPACITY)
        self.verticalSprite = Sprite(parent=self, texturePath='res:/UI/Texture/classes/SensorSuite/big_tick.png', align=uiconst.CENTERTOP, width=INDICATOR_WIDTH, height=INDICATOR_HEIGHT, color=self.data.baseColor.GetRGBA(), blendMode=trinity.TR2_SBM_ADD, opacity=0.5)
        self.isNew = True

    @telemetry.ZONE_METHOD
    def SetRotation(self, rotation = 0):
        Transform.SetRotation(self, rotation)

    @telemetry.ZONE_METHOD
    def SetInclination(self, angle):
        offset = -angle / MATH_PI_2 * INCLINATION_TICK_MAX_OFFSET
        self.sprite.top = INCLINATION_TICK_TOP_OFFSET + offset
        absAngle = math.fabs(angle)
        if absAngle < INCLINATION_HIGHLIGHT_RANGE_RADIANS:
            opacity = INCLINATION_TICK_BASE_OPACITY + (1 - absAngle / INCLINATION_HIGHLIGHT_RANGE_RADIANS) * INCLINATION_TICK_HIGHLIGHT_OPACITY
        else:
            opacity = INCLINATION_TICK_BASE_OPACITY
        self.sprite.opacity = opacity


def AddShortcut(tooltipPanel, shortcut):
    ml, mt, mr, mb = tooltipPanel.margin
    shortcutObj = ShortcutHint(text=shortcut)
    tooltipPanel.AddCell(shortcutObj, cellPadding=(7,
     0,
     -mr + 6,
     0))


def LoadSensorOverlayFilterTooltip(tooltipPanel):
    sensorSuite = sm.GetService('sensorSuite')
    tooltipPanel.pickState = uiconst.TR2_SPS_ON
    tooltipPanel.LoadGeneric3ColumnTemplate()
    cmd = uicore.cmd.commandMap.GetCommandByName('CmdToggleSensorOverlay')
    label = cmd.GetName()
    shortcutStr = cmd.GetShortcutAsString()
    tooltipPanel.AddLabelMedium(text=label, padTop=2)
    tooltipPanel.AddCell(OverlaySwitch(align=uiconst.CENTERTOP))
    tooltipPanel.AddShortcutCell(shortcutStr)
    tooltipPanel.AddCell(Container(height=8, align=uiconst.NOALIGN), colSpan=3)
    buttons = []
    siteTypes = [ANOMALY,
     STATIC_SITE,
     BOOKMARK,
     SIGNATURE,
     MISSION,
     CORP_BOOKMARK]
    for siteType in siteTypes:
        handler = sensorSuite.siteController.GetSiteHandler(siteType)
        config = handler.GetFilterConfig()
        button = SiteButton(filterConfig=config, isActive=config.enabled)
        buttons.append(button)
        tooltipPanel.AddCell(button)

    maxWidth = max([ b.width for b in buttons ])
    for b in buttons:
        b.width = maxWidth


class OverlaySwitch(ButtonGroup):
    default_state = uiconst.UI_NORMAL
    default_unisize = True
    default_buttonPadding = 1
    default_fontStyle = STYLE_HEADER

    def ApplyAttributes(self, attributes):
        super(OverlaySwitch, self).ApplyAttributes(attributes)
        a = self.AddButton(localization.GetByLabel('UI/Inflight/Scanner/SensorOverlayOn'), self.OnToggle, color=Color.GREEN)
        b = self.AddButton(localization.GetByLabel('UI/Inflight/Scanner/SensorOverlayOff'), self.OnToggle, color=Color.RED)
        for button in (a, b):
            button.state = uiconst.UI_DISABLED

        knobWidth = 2 * self.buttonPadding + self.width / 2
        self.knob = Container(name='knob', parent=self, align=uiconst.TOLEFT, width=knobWidth, idx=0, opacity=1.0, bgColor=Color.BLACK)
        Button(name='knob', parent=self.knob, align=uiconst.TOLEFT, fixedwidth=knobWidth, opacity=1.0, func=self.OnToggle)
        self.sensorSuite = sm.GetService('sensorSuite')
        if self.sensorSuite.IsOverlayActive():
            self.knob.left = self.width - knobWidth
        self.Subscribe()

    def OnToggle(self, *args):
        if not self.sensorSuite.IsOverlayActive():
            self.sensorSuite.EnableSensorOverlay()
        else:
            self.sensorSuite.DisableSensorOverlay()

    def UpdateKnob(self):
        if self.sensorSuite.IsOverlayActive():
            offset = self.width - self.knob.width
            animations.MoveOutRight(self.knob, offset, duration=0.1)
        else:
            animations.MoveOutRight(self.knob, -self.knob.left, duration=0.1)

    def OnClick(self, *args):
        self.OnToggle()

    def Subscribe(self):
        self.sensorSuite.Subscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_ENABLED, self.UpdateKnob)
        self.sensorSuite.Subscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_DISABLED, self.UpdateKnob)

    def Unsubscribe(self):
        self.sensorSuite.Unsubscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_ENABLED, self.UpdateKnob)
        self.sensorSuite.Unsubscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_DISABLED, self.UpdateKnob)

    def Close(self):
        super(OverlaySwitch, self).Close()
        self.Unsubscribe()
