#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sensorsuite\overlay\sitefilter.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from audioConst import BTNCLICK_DEFAULT
from eve.client.script.ui.util.uiComponents import HoverEffect, Component
from eve.common.lib.appConst import defaultPadding
import localization
import logging
from sensorsuite.overlay.brackets import OUTER_BRACKET_ORIENTATIONS, INNER_ICON_COLOR
logger = logging.getLogger(__name__)

@Component(HoverEffect(color=(1.0, 1.0, 1.0, 0.15)))

class SiteButton(Container):
    default_height = 36
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    opacityIdleIcon = 0.3
    opacityMouseDownIcon = 1.0
    opacityIdleLabel = 0.4
    opacityMouseDownLabel = 1.0
    exitDuration = 0.3

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sensorSuite = sm.GetService('sensorSuite')
        config = attributes.filterConfig
        self.iconCont = Container(parent=self, width=36, height=36, align=uiconst.TOLEFT, padding=(0, 0, 0, 0))
        iconData = config.siteIconData
        self.icon = Sprite(name='innerIcon', parent=self.iconCont, texturePath=iconData.icon, align=uiconst.CENTER, width=20, height=20, state=uiconst.UI_DISABLED, color=INNER_ICON_COLOR.GetRGBA())
        for n, (x, y) in enumerate(OUTER_BRACKET_ORIENTATIONS):
            Sprite(name='outerIcon_%d' % n, parent=self.iconCont, texturePath=iconData.outerTextures[n], align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(x * 11,
             y * 11,
             22,
             22), color=iconData.color.GetRGBA())

        textCont = Container(parent=self, align=uiconst.TOALL)
        self.label = EveLabelMedium(parent=textCont, align=uiconst.CENTERLEFT, text=localization.GetByLabel(config.label), padLeft=4)
        self.width = self.iconCont.width + defaultPadding + self.label.textwidth + defaultPadding
        self.config = config
        self.isActive = attributes.isActive
        if self.isActive:
            self.iconCont.opacity = self.opacityMouseDownIcon
            self.label.opacity = self.opacityMouseDownLabel
        else:
            self.iconCont.opacity = self.opacityIdleIcon
            self.label.opacity = self.opacityIdleLabel

    def OnClick(self, *args):
        self.Toggle()
        sm.GetService('audio').SendUIEvent(BTNCLICK_DEFAULT)

    def SetActive(self, isActive):
        self.isActive = isActive
        if self.isActive:
            animations.FadeTo(self.iconCont, self.icon.opacity, self.opacityMouseDownIcon, duration=0.1)
            animations.FadeTo(self.label, self.label.opacity, self.opacityMouseDownLabel, duration=0.1)
        else:
            animations.FadeTo(self.iconCont, self.icon.opacity, self.opacityIdleIcon, duration=self.exitDuration)
            animations.FadeTo(self.label, self.label.opacity, self.opacityIdleLabel, duration=self.exitDuration)
        self.sensorSuite.SetSiteFilter(self.config.siteType, self.isActive)

    def Toggle(self):
        self.SetActive(not self.isActive)
