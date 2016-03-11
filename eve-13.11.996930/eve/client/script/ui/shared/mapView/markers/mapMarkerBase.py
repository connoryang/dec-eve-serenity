#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\markers\mapMarkerBase.py
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.base import ScaleDpiF
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveBaseLink import BaseLink
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
from eve.client.script.ui.shared.mapView.mapViewUtil import MapPosToSolarSystemPos
from eve.client.script.ui.shared.maps.maputils import GetMyPos
from eve.client.script.ui.tooltips.tooltipHandler import TOOLTIP_SETTINGS_BRACKET, TOOLTIP_DELAY_BRACKET
import trinity
import weakref
import geo2
import carbonui.const as uiconst
from eve.client.script.ui.shared.mapView.mapViewConst import SOLARSYSTEM_SCALE
import telemetry
import uthread

class MarkerContainerBase(Container):
    default_align = uiconst.NOALIGN
    default_opacity = 1.0
    default_state = uiconst.UI_NORMAL
    default_cursor = uiconst.UICURSOR_POINTER
    markerObject = None
    isDragObject = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.markerObject = attributes.markerObject
        self.renderObject.displayY = -1000

    def Close(self, *args):
        Container.Close(self, *args)
        self.markerObject = None

    def OnClick(self, *args):
        return self.markerObject.OnClick(*args)

    def OnDblClick(self, *args):
        return self.markerObject.OnDblClick(*args)

    def OnMouseDown(self, *args):
        return self.markerObject.OnMouseDown(*args)

    def OnMouseUp(self, *args):
        return self.markerObject.OnMouseUp(*args)

    def OnMouseEnter(self, *args):
        return self.markerObject.OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        return self.markerObject.OnMouseExit(*args)

    def GetMenu(self):
        return self.markerObject.GetMenu()

    def GetTooltipDelay(self):
        return settings.user.ui.Get(TOOLTIP_SETTINGS_BRACKET, TOOLTIP_DELAY_BRACKET)

    @apply
    def opacity():
        doc = 'Opacity of map marker container, intended to override distance opacity if needed'

        def fget(self):
            return self._opacity

        def fset(self, value):
            self._opacity = value
            if self.markerObject and (self.markerObject.activeState or self.markerObject.hilightState):
                renderOpacity = 1.0
            else:
                renderOpacity = value
            self.renderObject.opacity = renderOpacity

        return property(**locals())

    def UpdateBackgrounds(self):
        for each in self.background:
            pl, pt, pr, pb = each.padding
            each.displayRect = (ScaleDpiF(pl),
             ScaleDpiF(pt),
             self._displayWidth - ScaleDpiF(pl + pr),
             self._displayHeight - ScaleDpiF(pt + pb))

    def GetDragData(self, *args):
        return self.markerObject.GetDragData(self, *args)

    @classmethod
    def PrepareDrag(cls, *args):
        return BaseLink.PrepareDrag(*args)


class MarkerBase(object):
    __metaclass__ = telemetry.ZONE_PER_METHOD
    isLoaded = False
    markerID = None
    position = (0, 0, 0)
    destroyed = False
    distanceFadeAlphaNearFar = (0.0, mapViewConst.MAX_MARKER_DISTANCE)
    displayStateOverride = None
    markerContainer = None
    parentContainer = None
    extraContainer = None
    curveSet = None
    eventHandler = None
    solarSystemID = None
    positionPickable = False
    hilightState = False
    activeState = False
    updated = False
    tooltipRowClass = None
    itemID = None
    typeID = None

    def __init__(self, markerID, markerHandler, parentContainer, position, curveSet, eventHandler = None, **kwds):
        self.markerID = markerID
        projectBracket = trinity.EveProjectBracket()
        if self.distanceFadeAlphaNearFar:
            projectBracket.maxDispRange = self.distanceFadeAlphaNearFar[1]
        self.projectBracket = projectBracket
        self.parentContainer = weakref.ref(parentContainer)
        self.curveSet = weakref.ref(curveSet)
        self.markerHandler = markerHandler
        self.eventHandler = eventHandler
        self.SetPosition(position)
        projectBracket.bracketUpdateCallback = self.OnMapMarkerUpdated
        projectBracket.displayChangeCallback = self.OnMapMarkerDisplayChange
        curveSet.curves.append(projectBracket)

    def Close(self):
        self.DestroyRenderObject()
        if self.curveSet:
            curveSet = self.curveSet()
            if curveSet:
                curveSet.curves.fremove(self.projectBracket)
        self.markerHandler = None
        self.eventHandler = None
        self.curveSet = None
        self.projectBracket = None
        self.parentContainer = None
        self.markerContainer = None

    def FadeOutAndClose(self):
        if self.markerContainer and not self.markerContainer.destroyed and self.markerContainer.opacity:
            uicore.animations.FadeTo(self.markerContainer, startVal=self.markerContainer.opacity, endVal=0.0, callback=self.Close)
        else:
            self.Close()

    def GetExtraMouseOverInfo(self):
        if self.markerHandler:
            return self.markerHandler.GetExtraMouseOverInfoForMarker(self.markerID)

    def SetHilightState(self, hilightState):
        if hilightState != self.hilightState:
            self.hilightState = hilightState
            self.lastUpdateCameraValues = None
            self.UpdateActiveAndHilightState()

    def SetActiveState(self, activeState):
        if activeState != self.activeState:
            self.activeState = activeState
            self.lastUpdateCameraValues = None
            self.UpdateActiveAndHilightState()

    def UpdateActiveAndHilightState(self, *args, **kwds):
        pass

    def MoveToFront(self):
        if self.parentContainer:
            parentContainer = self.parentContainer()
            if not parentContainer or parentContainer.destroyed:
                return
            if self.markerContainer and not self.markerContainer.destroyed:
                renderObject = self.markerContainer.renderObject
                parentContainer.renderObject.children.remove(renderObject)
                parentContainer.renderObject.children.insert(0, renderObject)
            if self.extraContainer and not self.extraContainer.destroyed:
                renderObject = self.extraContainer.renderObject
                parentContainer.renderObject.children.remove(renderObject)
                parentContainer.renderObject.children.insert(0, renderObject)

    def GetBoundaries(self):
        mx, my = self.projectBracket.rawProjectedPosition
        return (mx - 6 + self.projectBracket.offsetX,
         my - 6 + self.projectBracket.offsetY,
         mx + 6 + self.projectBracket.offsetX,
         my + 6 + self.projectBracket.offsetY)

    def GetDisplayText(self):
        return None

    def GetLabelText(self):
        return None

    def GetDragText(self):
        return self.GetDisplayText()

    def GetCameraDistance(self):
        return self.projectBracket.cameraDistance

    def SetPosition(self, position):
        self.position = position
        self.projectBracket.trackPosition = position

    def GetDisplayPosition(self):
        if self.projectBracket:
            return self.projectBracket.trackPosition

    def OnMapMarkerDisplayChange(self, projectBracket, displayState):
        if displayState == False and self.isLoaded:
            self.DestroyRenderObject()

    def OnMapMarkerUpdated(self, projectBracket):
        if self.displayStateOverride == False:
            if self.markerContainer:
                self.DestroyRenderObject()
        elif not self.distanceFadeAlphaNearFar:
            if self.markerContainer:
                self.markerContainer.opacity = 1.0
            else:
                self.CreateRenderObject()
        else:
            cameraTranslationFromParent = self.markerHandler.cameraTranslationFromParent
            if (cameraTranslationFromParent, projectBracket.cameraDistance) != getattr(self, 'lastUpdateCameraValues', None):
                self.lastUpdateCameraValues = (cameraTranslationFromParent, projectBracket.cameraDistance)
                if self.markerHandler.IsActiveOfHilighted(self.markerID):
                    opacity = 1.0
                    self.MoveToFront()
                else:
                    nearFadeDist, farFadeDist = self.distanceFadeAlphaNearFar
                    if projectBracket.cameraDistance < nearFadeDist:
                        baseOpacity = projectBracket.cameraDistance / nearFadeDist
                    elif projectBracket.cameraDistance < farFadeDist:
                        baseOpacity = min(1.0, max(0.0, 1.0 - projectBracket.cameraDistance / farFadeDist))
                    elif self.isLoaded:
                        self.DestroyRenderObject()
                        return
                    nearFactor = min(1.0, cameraTranslationFromParent / projectBracket.cameraDistance)
                    opacity = round(baseOpacity * nearFactor, 2)
                if opacity > 0.05:
                    self.CreateRenderObject()
                    self.markerContainer.opacity = opacity
                    self.UpdateExtraContainer()
                elif self.markerContainer and self.isLoaded:
                    self.DestroyRenderObject()
        self.updated = True

    def OnClick(self, *args, **kwds):
        self.clickTimer = AutoTimer(250, self.ClickMarker, uicore.uilib.Key(uiconst.VK_CONTROL))

    def OnDblClick(self, *args, **kwds):
        self.ClickMarker(True)

    def ClickMarker(self, zoomTo):
        self.clickTimer = None
        self.markerHandler.OnMarkerSelected(self, zoomTo)

    def OnMouseDown(self, *args):
        pass

    def OnMouseUp(self, *args):
        pass

    def OnMouseEnter(self, *args):
        if uicore.uilib.leftbtn or uicore.uilib.rightbtn:
            return
        if self.markerHandler.IsMarkerPickOverridden():
            return
        self.markerHandler.OnMarkerHilighted(self)

    def OnMouseExit(self, *args):
        pass

    def CreateRenderObject(self):
        if self.parentContainer and (not self.markerContainer or self.markerContainer.destroyed):
            parent = self.parentContainer()
            if not parent:
                return
            container = MarkerContainerBase(parent=parent, markerObject=self)
            self.markerContainer = container
            self.projectBracket.bracket = container.renderObject
            self.Load()

    def Reload(self):
        self.DestroyRenderObject()
        self.lastUpdateCameraValues = None

    def DestroyRenderObject(self):
        self.projectBracket.bracket = None
        if self.markerContainer and not self.markerContainer.destroyed:
            markerContainer = self.markerContainer
            self.markerContainer = None
            markerContainer.Close()
        if self.extraContainer and not self.extraContainer.destroyed:
            self.extraContainer.Close()
            self.extraContainer = None
        self.isLoaded = False
        self.lastUpdateCameraValues = None

    def UpdateExtraContainer(self):
        if not self.extraContainer or not self.markerContainer:
            return
        offsetX, offsetY = self.GetExtraContainerDisplayOffset()
        self.extraContainer.renderObject.displayX = self.markerContainer.renderObject.displayX + offsetX
        self.extraContainer.renderObject.displayY = self.markerContainer.renderObject.displayY + offsetY

    def GetExtraContainerDisplayOffset(self):
        return (0, self.markerContainer.renderObject.displayHeight)

    def Load(self):
        pass

    def GetMenu(self):
        try:
            objectID = int(self.markerID)
            return self.eventHandler.GetMenuForObjectID(objectID)
        except:
            pass

    def GetHint(self):
        return None

    def GetDragData(self, *args):
        displayText = self.GetDragText()
        if self.itemID and self.typeID and displayText:
            url = 'showinfo:%d//%d' % (self.typeID, self.itemID)
            entry = Bunch()
            entry.__guid__ = 'TextLink'
            entry.url = url
            entry.displayText = StripTags(displayText)
            return [entry]


class MarkerUniverseBased(MarkerBase):

    def __init__(self, *args, **kwds):
        MarkerBase.__init__(self, *args, **kwds)

    def SetYScaleFactor(self, yScaleFactor):
        x, y, z = self.position
        self.projectBracket.trackPosition = (x, y * yScaleFactor, z)


class MarkerSolarSystemBased(MarkerBase):
    inRangeIndicatorState = False
    itemID = None
    trackObjectID = None
    binding = None
    vectorSequencer = None

    def __init__(self, *args, **kwds):
        MarkerBase.__init__(self, *args, **kwds)
        self.mapPositionSolarSystem = kwds['mapPositionSolarSystem']
        self.mapPositionLocal = kwds['mapPositionLocal']
        self.solarSystemID = kwds['solarSystemID']
        trackObjectID = kwds.get('trackObjectID', None)
        if trackObjectID:
            self.trackObjectID = trackObjectID
            self.SetupTracking()

    def Close(self, *args, **kwds):
        self.TearDownTracking()
        MarkerBase.Close(self, *args, **kwds)

    def UpdateSolarSystemPosition(self, solarSystemPosition):
        self.mapPositionSolarSystem = solarSystemPosition
        self.position = solarSystemPosition
        self.projectBracket.trackPosition = self.position

    def SetInRangeIndicatorState(self, visibleState):
        self.inRangeIndicatorState = visibleState

    def GetDistance(self):
        if session.solarsystemid:
            if self.itemID:
                ballPark = sm.GetService('michelle').GetBallpark()
                if ballPark and self.itemID in ballPark.balls:
                    return ballPark.balls[self.itemID].surfaceDist
            if self.solarSystemID == session.solarsystemid:
                solarSystemPosition = MapPosToSolarSystemPos(self.mapPositionLocal)
                myPosition = GetMyPos()
                return geo2.Vec3Length(geo2.Vec3Subtract(solarSystemPosition, (myPosition.x, myPosition.y, myPosition.z)))

    def TearDownTracking(self):
        if self.vectorSequencer:
            if self.curveSet:
                curveSet = self.curveSet()
                if curveSet:
                    curveSet.curves.remove(self.vectorSequencer)
                    curveSet.bindings.remove(self.binding)
        self.binding = None
        self.vectorSequencer = None

    def SetupTracking(self):
        self.TearDownTracking()
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        sunBall = None
        if self.trackObjectID == session.shipid:
            for itemID, each in bp.slimItems.iteritems():
                if each.groupID == const.groupSun:
                    sunBall = bp.GetBall(itemID)
                    break

        trackBallID = self.trackObjectID
        ball = bp.GetBall(trackBallID)
        if ball is None or sunBall is None:
            return
        vectorCurve = trinity.TriVectorCurve()
        vectorCurve.value = (-SOLARSYSTEM_SCALE, -SOLARSYSTEM_SCALE, -SOLARSYSTEM_SCALE)
        invSunPos = trinity.TriVectorSequencer()
        invSunPos.operator = trinity.TRIOP_MULTIPLY
        invSunPos.functions.append(sunBall)
        invSunPos.functions.append(vectorCurve)
        vectorCurve = trinity.TriVectorCurve()
        vectorCurve.value = (SOLARSYSTEM_SCALE, SOLARSYSTEM_SCALE, SOLARSYSTEM_SCALE)
        ballPos = trinity.TriVectorSequencer()
        ballPos.operator = trinity.TRIOP_MULTIPLY
        ballPos.functions.append(ball)
        ballPos.functions.append(vectorCurve)
        vectorSequencer = trinity.TriVectorSequencer()
        vectorSequencer.operator = trinity.TRIOP_ADD
        vectorSequencer.functions.append(invSunPos)
        vectorSequencer.functions.append(ballPos)
        bind = trinity.TriValueBinding()
        bind.copyValueCallable = self.OnBallPositionUpdate
        bind.sourceObject = vectorSequencer
        bind.sourceAttribute = 'value'
        self.binding = bind
        self.vectorSequencer = vectorSequencer
        if self.curveSet:
            curveSet = self.curveSet()
            if curveSet:
                curveSet.curves.append(vectorSequencer)
                curveSet.bindings.append(bind)

    def OnBallPositionUpdate(self, curveSet, *args):
        if curveSet.value == (0, 0, 0):
            uthread.new(self.TearDownTracking)
        else:
            self.UpdateMapPositionLocal(curveSet.value)
