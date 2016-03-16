#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\fightersHealthGaugeCont.py
from math import cos, sin
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from eve.client.script.ui.control.eveIcon import Icon
from eve.common.script.mgt.fighterConst import HEALTHY_FIGTHER, DAMAGED_FIGTHER, DEAD_FIGHTER
import mathUtil
import trinity
import carbonui.const as uiconst
import util

class FightersHealthGauge(Container):
    default_height = 86
    default_width = 86
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    isDragObject = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = None
        self.squadronSize = None
        self.squadronState = attributes.get('state', None)
        self.tubeFlagID = attributes.get('tubeFlagID', None)
        dashColors = self.GetDashColors()
        self.fightersGauge = FighterHealthGaugeLine(parent=self, dashColors=dashColors, align=uiconst.CENTER)
        Sprite(parent=self, align=uiconst.CENTER, width=86, height=86, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/fighterItemOverlay.png', state=uiconst.UI_DISABLED)
        self.fighterIcon = Icon(parent=self, align=uiconst.CENTER, width=52, height=52, state=uiconst.UI_DISABLED, blendMode=1, textureSecondaryPath='res:/UI/Texture/classes/ShipUI/Fighters/fighterItemMask.png', spriteEffect=trinity.TR2_SFX_MODULATE)
        Sprite(parent=self, align=uiconst.CENTER, width=86, height=86, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/fighterItemUnderlay.png', state=uiconst.UI_DISABLED)

    def LoadFighterIcon(self, typeID):
        if typeID == self.typeID:
            return
        self.typeID = typeID
        self.fighterIcon.LoadIconByTypeID(typeID=typeID)

    def SetSquadronSize(self, squadronSize):
        self.squadronSize = squadronSize
        self.UpdateFighters()

    def GetDashColors(self):
        dashColors = []
        for i in xrange(1, 13):
            if i <= self.squadronSize:
                dashColor = HEALTHY_FIGTHER
            else:
                dashColor = DEAD_FIGHTER
            dashColors.append(dashColor)

        return dashColors

    def GetDragData(self):
        if self.squadronState is not None:
            squadronData = util.KeyVal()
            squadronData.tubeFlagID = self.tubeFlagID
            squadronData.squadronState = self.squadronState
            squadronData.typeID = self.typeID
            squadronData.__guid__ = 'uicls.FightersHealthGauge'
            return [squadronData]
        else:
            return []

    def UpdateFighters(self):
        dashColors = self.GetDashColors()
        self.fightersGauge.UpdateFighterColors(dashColors)


class FighterHealthGaugeLine(VectorLineTrace):
    __notifyevents__ = ['OnUIScalingChange']
    demoCount = 0
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        VectorLineTrace.ApplyAttributes(self, attributes)
        self.dashSizeFactor = attributes.dashSizeFactor or 2.0
        self.startAngle = attributes.startAngle or mathUtil.DegToRad(135)
        self.range = attributes.range or mathUtil.DegToRad(265)
        self.radius = attributes.radius or 31
        self.lineWidth = attributes.lineWidth or 2.5
        self.gapEnds = attributes.gapEnds or True
        self.dashColors = attributes.dashColors or [(1, 1, 1, 1)]
        self.PlotFighters()
        sm.RegisterNotify(self)

    def UpdateFighterColors(self, dashColors):
        self.dashColors = dashColors
        self.Flush()
        self.PlotFighters()

    def PlotFighters(self):
        dashCount = len(self.dashColors)
        circum = self.radius * self.range
        if self.gapEnds:
            gapStepRad = self.range / (dashCount * (self.dashSizeFactor + 1))
        else:
            gapStepRad = self.range / (dashCount * (self.dashSizeFactor + 1) - 1)
        dashStepRad = gapStepRad * self.dashSizeFactor
        pixelRad = self.range / circum
        centerOffset = self.radius + self.lineWidth * 0.5
        jointOffset = min(gapStepRad / 3, pixelRad / 2)
        rot = self.startAngle
        if self.gapEnds:
            rot += gapStepRad / 2
        for i, color in enumerate(self.dashColors):
            r, g, b, a = color
            point = (centerOffset + self.radius * cos(rot - jointOffset), centerOffset + self.radius * sin(rot - jointOffset))
            self.AddPoint(point, (r,
             g,
             b,
             0.0))
            point = (centerOffset + self.radius * cos(rot + jointOffset), centerOffset + self.radius * sin(rot + jointOffset))
            self.AddPoint(point, color)
            smoothRad = pixelRad * 4 + jointOffset
            while smoothRad < dashStepRad - jointOffset:
                point = (centerOffset + self.radius * cos(rot + smoothRad), centerOffset + self.radius * sin(rot + smoothRad))
                self.AddPoint(point, color)
                smoothRad += pixelRad * 4

            rot += dashStepRad
            point = (centerOffset + self.radius * cos(rot - jointOffset), centerOffset + self.radius * sin(rot - jointOffset))
            self.AddPoint(point, color)
            point = (centerOffset + self.radius * cos(rot + jointOffset), centerOffset + self.radius * sin(rot + jointOffset))
            self.AddPoint(point, (r,
             g,
             b,
             0.0))
            rot += gapStepRad

        self.width = self.height = centerOffset * 2

    def OnUIScalingChange(self, *args):
        if not self.destroyed:
            self.Flush()
            self.PlotFighters()
