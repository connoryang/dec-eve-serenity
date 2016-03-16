#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\form_tournament.py
import operator
import math
import dogma.effects
import evecamera
import evetypes
import uicontrols
import blue
import uthread
import carbonui.const as uiconst
import util
from collections import defaultdict
from service import ROLE_GML
import uiprimitives
import const
BACKGROUND = 'res:/UI/Texture/Tournament/Fancy_NoLogo_UI_Background.png'
shipTypeNicknames = {4363: 'Quafe Miasmos',
 4388: 'Quafe Miasmos',
 11936: 'I. Apocalypse',
 11938: 'I. Armageddon',
 29328: 'A. Shuttle',
 11134: 'A. Shuttle',
 27299: 'A. Shuttle',
 29330: 'C. Shuttle',
 672: 'C. Shuttle',
 27301: 'C. Shuttle',
 29332: 'G. Shuttle',
 11129: 'G. Shuttle',
 27303: 'G. Shuttle',
 29334: 'M. Shuttle',
 11132: 'M. Shuttle',
 27305: 'M. Shuttle',
 13202: 'F. Megathron',
 17812: 'Firetail',
 17841: 'Comet',
 17726: 'N. Apocalypse',
 17619: 'Hookbill',
 32305: 'N. Armageddon',
 17703: 'N. Slicer',
 17728: 'N. Megathron',
 26842: 'T. Tempest',
 17732: 'F. Tempest',
 12438: 'F. Stabber',
 32309: 'N. Scorpion',
 32311: 'F. Typhoon',
 29344: 'N. Exequror',
 32307: 'N. Dominix',
 17634: 'N. Caracal',
 29336: 'F. Scythe',
 29337: 'N. Augoror',
 26840: 'S. Raven',
 29340: 'N. Osprey',
 17636: 'N. Raven',
 12440: 'N. Vexor',
 17709: 'N. Omen',
 11942: 'S. Magnate',
 11011: 'G. Vexor',
 17707: 'M. Frigate',
 33677: 'Fuzzmobile',
 33153: 'N. Drake',
 33157: 'F. Hurricane',
 33155: 'N. Harbinger',
 33151: 'N. Brutix',
 34590: 'Victorieux',
 34151: 'V. Rattlesnake'}
barWidth = 40
barPadding = 4
statusIconWidth = 20
maxStatusIcons = 6
effectToIcon = {'warpScramblerMWD': const.iconModuleWarpScramblerMWD,
 'warpScrambler': const.iconModuleWarpScrambler,
 'focusedWarpScrambler': const.iconModuleFocusedWarpScrambler,
 'webify': const.iconModuleStasisWeb,
 'electronic': const.iconModuleECM,
 'ewRemoteSensorDamp': const.iconModuleSensorDamper,
 'ewTrackingDisrupt': const.iconModuleTrackingDisruptor,
 'ewGuidanceDisrupt': const.iconModuleGuidanceDisruptor,
 'ewTargetPaint': const.iconModuleTargetPainter,
 'ewEnergyVampire': const.iconModuleNosferatu,
 'ewEnergyNeut': const.iconModuleEnergyNeutralizer}

class DropShadowElement(object):

    def __init__(self, classOfThingToShadow, *args, **kwargs):
        self.main = classOfThingToShadow(*args, **kwargs)
        self.shad1 = classOfThingToShadow(*args, **kwargs)
        self.shad2 = classOfThingToShadow(*args, **kwargs)
        self.shad3 = classOfThingToShadow(*args, **kwargs)
        self.RePosition()
        self.ReColor()

    def RePosition(self):
        self.shad1.left = self.main.left + 2
        self.shad1.top = self.main.top + 2
        self.shad2.left = self.main.left + 2
        self.shad2.top = self.main.top + 1
        self.shad3.left = self.main.left + 1
        self.shad3.top = self.main.top + 2

    def ReColor(self):
        shadowColor = (0,
         0,
         0,
         self.main.color.a * 0.25)
        self.shad1.color = shadowColor
        self.shad2.color = shadowColor
        self.shad3.color = shadowColor

    @property
    def left(self):
        return self.main.left

    @left.setter
    def left(self, value):
        self.main.left = value
        self.RePosition()

    @property
    def top(self):
        return self.main.top

    @top.setter
    def top(self, value):
        self.main.top = value
        self.RePosition()

    @property
    def width(self):
        return self.main.width

    @property
    def height(self):
        return self.main.height

    @property
    def pos(self):
        return self.main.pos

    @pos.setter
    def pos(self, value):
        self.main.pos = value
        self.RePosition()

    @property
    def text(self):
        return self.main.text

    @text.setter
    def text(self, value):
        self.main.text = value
        self.shad1.text = value
        self.shad2.text = value
        self.shad3.text = value

    @property
    def color(self):
        return self.main.color

    @color.setter
    def color(self, value):
        self.main.color = value
        self.ReColor()


class TournamentWindow(uicontrols.Window):
    __guid__ = 'form.tournament'
    __neocommenuitem__ = (('Tournament Manager', 'tournament'), True, ROLE_GML)
    default_windowID = 'tournament'

    def ApplyAttributes(self, attributes):
        self.fancyUI = None
        self.warningLine = None
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.height = 180
        self.width = 300
        self.SetScope('all')
        self.SetWndIcon(None)
        self.SetCaption('Tournament Manager')
        self.SetTopparentHeight(0)
        self.SetMinSize([self.width, self.height])
        self.MakeUnResizeable()
        self.ConstructLayout()

    def ConstructLayout(self):
        self.tourneyMoniker = util.Moniker('tourneyMgr', session.solarsystemid)
        self.tourneys = self.tourneyMoniker.GetActiveTourneys()
        tourneyOptions = [ ('%s vs %s' % (tourney[1], tourney[2]), idx) for idx, tourney in enumerate(self.tourneys) ]
        self.startScreen = uiprimitives.Container(name='startScreen', parent=self.sr.main, align=uiconst.TOALL)
        self.matchSelect = uicontrols.Combo(label='Select Match', parent=self.startScreen, options=tourneyOptions, padding=(5, 15, 5, 5), align=uiconst.TOTOP)
        uicontrols.Button(label='Start Camera Client', parent=self.startScreen, padding=(5, 5, 5, 5), func=self.StartCameraClient, align=uiconst.TOTOP)
        uicontrols.Button(label='Start FancyUI Client', parent=self.startScreen, padding=(5, 5, 5, 5), func=self.StartFancyUIClient, align=uiconst.TOTOP)
        self.cameraClientScreen = uiprimitives.Container(name='cameraClientScreen', parent=self.sr.main, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        uicontrols.Button(label='Lock Dudes', parent=self.cameraClientScreen, padding=(5, 5, 5, 5), func=self.LockEveryone, align=uiconst.TOTOP)
        uicontrols.Button(label='Sort Locks', parent=self.cameraClientScreen, padding=(5, 5, 5, 5), func=self.SortLocks, align=uiconst.TOTOP)
        uicontrols.Button(label='Toggle Bracket Text', parent=self.cameraClientScreen, func=self.ToggleShipText, align=uiconst.TOPLEFT, top=85, left=5)
        uicontrols.Button(label='Toggle DronePod Bracks', parent=self.cameraClientScreen, func=self.ToggleDronePod, align=uiconst.TOPLEFT, top=110, left=5)
        uicontrols.Button(label='Toggle BrackBackground', parent=self.cameraClientScreen, func=self.ToggleBackground, align=uiconst.TOPLEFT, top=85, left=150)
        uicontrols.Button(label='Toggle Text Color Match', parent=self.cameraClientScreen, func=self.ToggleColor, align=uiconst.TOPLEFT, top=110, left=150)
        uicontrols.Button(label='Toggle Sorting By Points', parent=self.cameraClientScreen, func=self.ToggleBracketSort, align=uiconst.TOPLEFT, top=135, left=150)
        uicontrols.Button(label='Toggle CamWobble', parent=self.cameraClientScreen, padding=(5, 5, 5, 5), func=self.ToggleCamWobble, align=uiconst.TOTOP)
        self.fancyUIWindow = uiprimitives.Container(name='fancyUIWindow', parent=self.sr.main, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        self.fancyUI = uiprimitives.Container(name='AT-Fancy', parent=uicore.layer.inflight, pos=(0,
         746,
         1920,
         334), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)
        self.warningLine = uiprimitives.Fill(name='AT-Camera Warning', parent=uicore.layer.main, pos=(0,
         752,
         1920,
         2), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, color=(1, 0, 0, 0.85))

    def FetchTeams(self):
        self.teamComps = self.tourneyMoniker.GetTeamMembers(self.tourneys[self.matchSelect.GetValue()][0])
        for teamIdx in (0, 1):
            self.teamComps[teamIdx].sort(key=operator.itemgetter(3, 1), reverse=True)

    def StartCameraClient(self, *args):
        self.FetchTeams()
        charMgr = sm.RemoteSvc('charMgr')
        for charID, shipTypeID, shipID, points in self.teamComps[0]:
            charMgr.AddContact(charID, -10)

        for charID, shipTypeID, shipID, points in self.teamComps[1]:
            charMgr.AddContact(charID, 10)

        neocomLayer = uicore.layer.Get('sidePanels')
        if neocomLayer is not None and neocomLayer.state != uiconst.UI_HIDDEN:
            neocomLayer.state = uiconst.UI_HIDDEN
        sm.GetService('infoPanel').ShowHideSidePanel(hide=True)
        sm.GetService('sceneManager').GetActiveCamera().maxLookatRange = 300000.0
        sm.GetService('target').disableSpinnyReticule = True
        sm.GetService('target').overrideBarHeight = 120
        try:
            slashCmd = sm.RemoteSvc('slash').SlashCmd
            slashCmd('/dogma %d %d = 24' % (session.charid, const.attributeMaxLockedTargets))
            slashCmd('/dogma %d %d = 24' % (session.shipid, const.attributeMaxLockedTargets))
        except:
            pass

        self.startScreen.state = uiconst.UI_HIDDEN
        self.cameraClientScreen.state = uiconst.UI_NORMAL
        self.warningLine.state = uiconst.UI_NORMAL
        nebulaID = self.tourneys[self.matchSelect.GetValue()][3]
        scene = sm.GetService('sceneManager').GetActiveScene()
        for res in scene.backgroundEffect.resources:
            if res.name == 'NebulaMap':
                res.resourcePath = 'res:/dx9/scene/universe/%s_cube.dds' % (nebulaID,)

        scene.envMap1ResPath = 'res:/dx9/scene/universe/%s_cube.dds' % (nebulaID,)
        scene.envMap2ResPath = 'res:/dx9/scene/universe/%s_cube_blur.dds' % (nebulaID,)

    def StartFancyUIClient(self, *args):
        self.FetchTeams()
        neocomLayer = uicore.layer.Get('sidePanels')
        if neocomLayer is not None and neocomLayer.state != uiconst.UI_HIDDEN:
            neocomLayer.state = uiconst.UI_HIDDEN
        try:
            slashCmd = sm.RemoteSvc('slash').SlashCmd
            slashCmd('/dogma %d %d = 24' % (session.charid, const.attributeMaxLockedTargets))
            slashCmd('/dogma %d %d = 24' % (session.shipid, const.attributeMaxLockedTargets))
        except:
            pass

        self.startScreen.state = uiconst.UI_HIDDEN
        self.fancyUIWindow.state = uiconst.UI_NORMAL
        self.fancyUI.state = uiconst.UI_NORMAL
        teamOneName = DropShadowElement(uicontrols.Label, text=self.tourneys[self.matchSelect.GetValue()][1], parent=self.fancyUI, left=0, top=4, uppercase=True, fontsize=22, bold=True, color=(1, 1, 1, 1), shadowOffset=(3, 3), shadowColor=(0, 0, 0, 1))
        teamOneName.left = 760 - teamOneName.width
        self.leftTeamScore = DropShadowElement(uicontrols.Label, text='46', parent=self.fancyUI, left=0, top=2, fontsize=24, bold=True, color=(1, 1, 1, 1), shadowOffset=(3, 3))
        self.leftTeamScore.left = 812 - self.leftTeamScore.width
        DropShadowElement(uicontrols.Label, text=self.tourneys[self.matchSelect.GetValue()][2], parent=self.fancyUI, left=1160, top=4, uppercase=True, fontsize=22, bold=True, color=(1, 1, 1, 1), shadowOffset=(5, 5))
        self.rightTeamScore = DropShadowElement(uicontrols.Label, text='26', parent=self.fancyUI, left=1100, top=2, fontsize=24, bold=True, color=(1, 1, 1, 1))
        self.leftTeamBar = uiprimitives.Fill(name='redbar', parent=self.fancyUI, pos=(0, 0, 831, 5), align=uiconst.TOPLEFT, color=(199 / 255.0,
         72 / 255.0,
         72 / 255.0,
         1))
        self.rightTeamBar = uiprimitives.Fill(name='bluebar', parent=self.fancyUI, pos=(1089, 0, 831, 5), align=uiconst.TOPLEFT, color=(29 / 255.0,
         97 / 255.0,
         168 / 255.0,
         1))
        defBarY = 38
        offBarY = 52
        contBarY = 66
        barHeight = 12
        self.leftTeamRep = uiprimitives.Sprite(parent=self.fancyUI, pos=(500,
         defBarY,
         49,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarPurple.png')
        self.leftTeamEHP = uiprimitives.Sprite(parent=self.fancyUI, pos=(550,
         defBarY,
         281,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarBlue.png')
        self.leftTeamOffFill = uiprimitives.Sprite(parent=self.fancyUI, pos=(650,
         offBarY,
         181,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarRed.png')
        self.leftTeamOffBackground = uiprimitives.Sprite(parent=self.fancyUI, pos=(350,
         offBarY,
         299,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Bar_Full.png')
        self.leftTeamContFill = uiprimitives.Sprite(parent=self.fancyUI, pos=(710,
         contBarY,
         121,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarGreen.png')
        self.leftTeamContBackground = uiprimitives.Sprite(parent=self.fancyUI, pos=(630,
         contBarY,
         79,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Bar_Full.png')
        self.rightTeamRep = uiprimitives.Sprite(parent=self.fancyUI, pos=(1089 + 157 + 1,
         defBarY,
         60,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarPurple.png')
        self.rightTeamEHP = uiprimitives.Sprite(parent=self.fancyUI, pos=(1089,
         defBarY,
         157,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarBlue.png')
        self.rightTeamOffFill = uiprimitives.Sprite(parent=self.fancyUI, pos=(1089,
         offBarY,
         348,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarRed.png')
        self.rightTeamOffBackground = uiprimitives.Sprite(parent=self.fancyUI, pos=(1089 + 348 + 1,
         offBarY,
         62,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Bar_Full.png')
        self.rightTeamContFill = uiprimitives.Sprite(parent=self.fancyUI, pos=(1089,
         contBarY,
         284,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarGreen.png')
        self.rightTeamContBackground = uiprimitives.Sprite(parent=self.fancyUI, pos=(1089 + 284 + 1,
         contBarY,
         121,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Bar_Full.png')
        self.clockLabel = DropShadowElement(uicontrols.EveCaptionLarge, text='10:00', parent=self.fancyUI, left=0, top=0, color=(1, 1, 1, 1))
        self.clockLabel.left = 1920 / 2 - self.clockLabel.width / 2
        banContainer = uiprimitives.Container(parent=self.fancyUI, pos=(16, 40, 316, 214), align=uiconst.TOPLEFT, clipChildren=True)
        DropShadowElement(uicontrols.EveCaptionLarge, text='Ship Bans', parent=banContainer, left=0, top=0)
        self.bansLabel = DropShadowElement(uicontrols.EveCaptionLarge, text='bans', parent=banContainer, left=0, top=26)
        statusIconsWidth = 258 / 2
        shipOffset = statusIconsWidth
        shipWidth = 98
        barsOffset = shipOffset + shipWidth
        barsWidth = 142
        speedOffset = barsOffset + barsWidth
        speedWidth = 49
        nameOffset = speedOffset + speedWidth
        nameWidth = 149
        pointsOffset = nameOffset + nameWidth
        pointsWidth = 40
        headerY = 90
        rowStartY = 114
        rowHeight = 18
        self.statusIconContainers = {}
        self.updateElements = {}
        cfg.eveowners.Prime([ x[0] for x in self.teamComps[0] ] + [ x[0] for x in self.teamComps[1] ])
        for teamIdx, color in ((0, (1, 0, 0, 0.1)), (1, (0, 0, 1, 0.1))):
            for idx, pilot in enumerate(self.teamComps[teamIdx]):
                yOffset = rowStartY + idx * rowHeight
                pilotName = cfg.eveowners[pilot[0]].ownerName
                shipTypeID = pilot[1]
                shipName = shipTypeNicknames[shipTypeID] if shipTypeID in shipTypeNicknames else evetypes.GetName(shipTypeID)
                shipID = pilot[2]
                points = pilot[3]
                healthBarBackgroundColor = (143.0 / 255,
                 19.0 / 255,
                 19.0 / 255,
                 1)
                healthBarFillColor = (141.0 / 255,
                 141.0 / 255,
                 141.0 / 255,
                 1)
                if teamIdx == 0:
                    statusContainer = uiprimitives.Container(parent=self.fancyUI, left=1920 / 2 - statusIconsWidth, top=yOffset, width=statusIconWidth * maxStatusIcons, height=statusIconWidth, align=uiconst.TOPLEFT)
                    self.statusIconContainers[shipID] = (statusContainer, 0, operator.add)
                    barContainer = uiprimitives.Container(parent=self.fancyUI, left=1920 / 2 - barsOffset - barsWidth + 4, top=yOffset, width=barsWidth, height=rowHeight - 2, align=uiconst.TOPLEFT)
                    self.updateElements[shipID] = [0,
                     points,
                     DropShadowElement(uicontrols.EveLabelLarge, text='<b>0', parent=self.fancyUI, left=1920 / 2 - speedOffset - speedWidth + 4, top=yOffset, width=speedWidth, maxLines=1, color=(1, 1, 1, 0.95)),
                     barContainer,
                     uiprimitives.Container(parent=barContainer, pos=(0,
                      1,
                      barWidth,
                      rowHeight - 2), align=uiconst.TOPLEFT, clipChildren=True),
                     uiprimitives.Container(parent=barContainer, pos=(barWidth + barPadding,
                      1,
                      barWidth,
                      rowHeight - 2), align=uiconst.TOPLEFT, clipChildren=True),
                     uiprimitives.Container(parent=barContainer, pos=((barWidth + barPadding) * 2,
                      1,
                      barWidth,
                      rowHeight - 2), align=uiconst.TOPLEFT, clipChildren=True),
                     DropShadowElement(uicontrols.EveLabelLarge, text='<b>%d' % (points,), parent=self.fancyUI, left=1920 / 2 - pointsOffset - pointsWidth + 4, top=yOffset, width=pointsWidth, maxLines=1, color=(1, 1, 1, 0.95)),
                     DropShadowElement(uicontrols.EveLabelLarge, text='<b>%s' % (pilotName,), parent=self.fancyUI, left=1920 / 2 - nameOffset - nameWidth + 4, top=yOffset, width=nameWidth, maxLines=1, showEllipsis=True, color=(1, 1, 1, 0.95)),
                     DropShadowElement(uicontrols.EveLabelLarge, text='<b>%s' % (shipName,), parent=self.fancyUI, left=1920 / 2 - shipOffset - shipWidth + 4, top=yOffset, width=shipWidth, maxLines=1, color=(1, 1, 1, 0.95))]
                    self.updateElements[shipID].append(uiprimitives.Sprite(parent=self.updateElements[shipID][4], pos=(0,
                     0,
                     barWidth,
                     rowHeight - 2), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Block_Full.png'))
                    self.updateElements[shipID].append(uiprimitives.Sprite(parent=self.updateElements[shipID][5], pos=(0,
                     0,
                     barWidth,
                     rowHeight - 2), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Block_Full.png'))
                    self.updateElements[shipID].append(uiprimitives.Sprite(parent=self.updateElements[shipID][6], pos=(0,
                     0,
                     barWidth,
                     rowHeight - 2), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Block_Full.png'))
                    uiprimitives.Sprite(parent=barContainer, pos=(0,
                     1,
                     barWidth,
                     rowHeight - 2), texturePath='res:/UI/Texture/Tournament/Block_Back.png', align=uiconst.TOPLEFT)
                    uiprimitives.Sprite(parent=barContainer, pos=(barWidth + barPadding,
                     1,
                     barWidth,
                     rowHeight - 2), texturePath='res:/UI/Texture/Tournament/Block_Back.png', align=uiconst.TOPLEFT)
                    uiprimitives.Sprite(parent=barContainer, pos=((barWidth + barPadding) * 2,
                     1,
                     barWidth,
                     rowHeight - 2), texturePath='res:/UI/Texture/Tournament/Block_Back.png', align=uiconst.TOPLEFT)
                else:
                    statusContainer = uiprimitives.Container(parent=self.fancyUI, left=1920 / 2, top=yOffset, width=statusIconWidth * maxStatusIcons, height=statusIconWidth, align=uiconst.TOPLEFT)
                    self.statusIconContainers[shipID] = (statusContainer, statusIconsWidth - statusIconWidth, operator.sub)
                    barContainer = uiprimitives.Container(parent=self.fancyUI, left=1920 / 2 + barsOffset + 4 + 6, top=yOffset, width=barsWidth, height=rowHeight - 2, align=uiconst.TOPLEFT)
                    self.updateElements[shipID] = [1,
                     points,
                     DropShadowElement(uicontrols.EveLabelLarge, text='<b>0', parent=self.fancyUI, left=1920 / 2 + speedOffset + 4, top=yOffset, width=speedWidth, maxLines=1, color=(1, 1, 1, 0.95)),
                     barContainer,
                     uiprimitives.Container(parent=barContainer, pos=(0,
                      1,
                      barWidth,
                      rowHeight - 2), align=uiconst.TOPLEFT, clipChildren=True),
                     uiprimitives.Container(parent=barContainer, pos=(barWidth + barPadding,
                      1,
                      barWidth,
                      rowHeight - 2), align=uiconst.TOPLEFT, clipChildren=True),
                     uiprimitives.Container(parent=barContainer, pos=((barWidth + barPadding) * 2,
                      1,
                      barWidth,
                      rowHeight - 2), align=uiconst.TOPLEFT, clipChildren=True),
                     DropShadowElement(uicontrols.EveLabelLarge, text='<b>%d' % (points,), parent=self.fancyUI, left=1920 / 2 + pointsOffset + 4, top=yOffset, width=pointsWidth, maxLines=1, color=(1, 1, 1, 0.95)),
                     DropShadowElement(uicontrols.EveLabelLarge, text='<b>%s' % (pilotName,), parent=self.fancyUI, left=1920 / 2 + nameOffset + 4, top=yOffset, width=nameWidth, maxLines=1, showEllipsis=True, color=(1, 1, 1, 0.95)),
                     DropShadowElement(uicontrols.EveLabelLarge, text='<b>%s' % (shipName,), parent=self.fancyUI, left=1920 / 2 + shipOffset + 4, top=yOffset, width=shipWidth, maxLines=1, color=(1, 1, 1, 0.95))]
                    self.updateElements[shipID].append(uiprimitives.Sprite(parent=self.updateElements[shipID][4], pos=(0,
                     0,
                     barWidth,
                     rowHeight - 2), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Block_Full_Mirror.png'))
                    self.updateElements[shipID].append(uiprimitives.Sprite(parent=self.updateElements[shipID][5], pos=(0,
                     0,
                     barWidth,
                     rowHeight - 2), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Block_Full_Mirror.png'))
                    self.updateElements[shipID].append(uiprimitives.Sprite(parent=self.updateElements[shipID][6], pos=(0,
                     0,
                     barWidth,
                     rowHeight - 2), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Block_Full_Mirror.png'))
                    (uiprimitives.Sprite(parent=barContainer, pos=(0,
                      1,
                      barWidth,
                      rowHeight - 2), texturePath='res:/UI/Texture/Tournament/Block_Back_Mirror.png', align=uiconst.TOPLEFT),)
                    uiprimitives.Sprite(parent=barContainer, pos=(barWidth + barPadding,
                     1,
                     barWidth,
                     rowHeight - 2), texturePath='res:/UI/Texture/Tournament/Block_Back_Mirror.png', align=uiconst.TOPLEFT)
                    uiprimitives.Sprite(parent=barContainer, pos=((barWidth + barPadding) * 2,
                     1,
                     barWidth,
                     rowHeight - 2), texturePath='res:/UI/Texture/Tournament/Block_Back_Mirror.png', align=uiconst.TOPLEFT)
                left = 350 if teamIdx == 0 else 1089
                uiprimitives.Sprite(parent=self.fancyUI, pos=(left,
                 yOffset + 1,
                 481,
                 rowHeight - 2), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Player_Back.png')

        uiprimitives.Sprite(name='background', parent=self.fancyUI, texturePath=BACKGROUND, pos=(0, 0, 1920, 334))
        self.matchStartTime = None
        self.matchComplete = False
        self.shipDeathTimes = {}
        self.maxEHP = float(prefs.GetValue('maxFancyEHP', 500000))
        self.maxDPS = float(prefs.GetValue('maxFancyDPS', 4500))
        self.maxCont = float(prefs.GetValue('maxFancyCont', 50))
        uthread.new(self.FancyUIUpdate)

    def SortEffects(self, effectSet):
        desiredOrdering = [86,
         80,
         const.iconModuleECM,
         const.iconModuleSensorDamper,
         const.iconModuleTrackingDisruptor,
         const.iconModuleEnergyNeutralizer,
         const.iconModuleNosferatu,
         const.iconModuleTargetPainter,
         const.iconModuleStasisWeb,
         const.iconModuleWarpScrambler,
         const.iconModuleWarpScramblerMWD]
        return [ x for x in desiredOrdering if x in effectSet ]

    def HarvestStatusEffects(self):
        fx = sm.GetService('FxSequencer')
        clientDogmaStaticSvc = sm.GetService('clientDogmaStaticSvc')
        effects = defaultdict(set)
        for shipID in self.updateElements.iterkeys():
            activations = fx.GetAllBallActivations(shipID)
            for activation in activations:
                for trigger in activation.triggers:
                    try:
                        moduleTypeID = trigger.moduleTypeID
                        groupID = evetypes.GetGroupID(moduleTypeID)
                        if groupID == 325:
                            iconID = 80
                        elif groupID == 41:
                            iconID = 86
                        else:
                            effectID = clientDogmaStaticSvc.GetDefaultEffect(moduleTypeID)
                            iconID = effectToIcon[dogma.effects.GetEwarTypeByEffectID(effectID)]
                        effects[trigger.targetID].add(iconID)
                    except:
                        pass

        return effects

    def RandomStatusEffects(self):
        import random
        effects = {}
        possibleIcons = [86,
         80,
         const.iconModuleECM,
         const.iconModuleSensorDamper,
         const.iconModuleTrackingDisruptor,
         const.iconModuleEnergyNeutralizer,
         const.iconModuleNosferatu,
         const.iconModuleTargetPainter,
         const.iconModuleStasisWeb,
         const.iconModuleWarpScrambler,
         const.iconModuleWarpScramblerMWD]
        for shipID in self.updateElements.iterkeys():
            effects[shipID] = [ x for x in possibleIcons if random.random() > 0.5 ]

        return effects

    def UpdateFancyStatusEffects(self):
        for icon in self.iconsToCleanup:
            icon.Close()

        self.iconsToCleanup = []
        statusEffects = self.HarvestStatusEffects()
        for shipID in self.updateElements.iterkeys():
            effectSet = statusEffects[shipID]
            newList = self.SortEffects(effectSet)
            oldList = self.currentStatusIcons[shipID]
            iconContainerData = self.statusIconContainers[shipID]
            newIcons = {}
            for idx, (iconID, iconElement) in enumerate(oldList):
                try:
                    newIndex = newList.index(iconID)
                except ValueError:
                    uicore.animations.FadeOut(iconElement, duration=0.5)
                    self.iconsToCleanup.append(iconElement)
                    continue

                if newIndex != idx:
                    movement = iconContainerData[2](0, (newIndex - idx) * statusIconWidth)
                    uicore.animations.MoveOutRight(iconElement, amount=movement, duration=0.75)
                    if newIndex >= maxStatusIcons:
                        uicore.animations.FadeOut(iconElement, duration=0.5)
                        self.iconsToCleanup.append(iconElement)
                    else:
                        newIcons[newIndex] = (iconID, iconElement)
                else:
                    newIcons[idx] = (iconID, iconElement)

            oldIcons = set([ x[0] for x in oldList ])
            for idx, iconID in enumerate(newList):
                if idx >= maxStatusIcons:
                    break
                if iconID not in oldIcons:
                    iconLocation = iconContainerData[2](iconContainerData[1], idx * statusIconWidth) - 2
                    newIcon = uicontrols.Icon(parent=iconContainerData[0], align=uiconst.TOPLEFT, pos=(iconLocation,
                     -4,
                     24,
                     24), graphicID=iconID, ignoreSize=True, opacity=0)
                    uicore.animations.FadeIn(newIcon, duration=0.5)
                    newIcons[idx] = (iconID, newIcon)

            self.currentStatusIcons[shipID] = [ newIcons[idx] for idx in xrange(len(newIcons)) ]

    def UpdateFancyBars(self):
        barDetails = self.tourneyMoniker.GetFancyDetails(self.tourneys[self.matchSelect.GetValue()][0])
        barWidth = 481
        ehpPerPixel = barWidth / self.maxEHP
        repPerPixel = 60 * ehpPerPixel
        dpsPerPixel = barWidth / self.maxDPS
        contPerPixel = barWidth / self.maxCont
        leftTeamX = 350
        rightTeamX = 1089
        totalEHP, totalReps, fleetMaxDPS, fleetAppliedDPS, fleetMaxControl, fleetAppliedControl = barDetails[0] or (0, 0, 0, 0, 0, 0)
        ehpWidth = min(barWidth, math.ceil(totalEHP * ehpPerPixel))
        self.leftTeamEHP.width = ehpWidth
        self.leftTeamEHP.left = leftTeamX + barWidth - ehpWidth
        repWidth = math.ceil(totalReps * repPerPixel)
        repWidth = min(repWidth, barWidth - ehpWidth - 1)
        self.leftTeamRep.width = repWidth
        self.leftTeamRep.left = leftTeamX + barWidth - ehpWidth - 1 - repWidth
        curDPSWidth = min(barWidth, math.ceil(fleetAppliedDPS * dpsPerPixel))
        maxDPSWidth = max(0, min(barWidth, math.ceil(fleetMaxDPS * dpsPerPixel)) - curDPSWidth - 1)
        self.leftTeamOffFill.width = curDPSWidth
        self.leftTeamOffFill.left = leftTeamX + barWidth - curDPSWidth
        self.leftTeamOffBackground.width = maxDPSWidth
        self.leftTeamOffBackground.left = leftTeamX + barWidth - curDPSWidth - 1 - maxDPSWidth
        curControlWidth = min(barWidth, math.ceil(fleetAppliedControl * contPerPixel))
        maxControlWidth = max(0, min(barWidth, math.ceil(fleetMaxControl * contPerPixel)) - curControlWidth - 1)
        self.leftTeamContFill.width = curControlWidth
        self.leftTeamContFill.left = leftTeamX + barWidth - curControlWidth
        self.leftTeamContBackground.width = maxControlWidth
        self.leftTeamContBackground.left = leftTeamX + barWidth - curControlWidth - 1 - maxControlWidth
        totalEHP, totalReps, fleetMaxDPS, fleetAppliedDPS, fleetMaxControl, fleetAppliedControl = barDetails[1] or (0, 0, 0, 0, 0, 0)
        ehpWidth = min(barWidth, math.ceil(totalEHP * ehpPerPixel))
        self.rightTeamEHP.width = ehpWidth
        self.rightTeamEHP.left = rightTeamX
        repWidth = math.ceil(totalReps * repPerPixel)
        repWidth = min(repWidth, barWidth - ehpWidth - 1)
        self.rightTeamRep.width = repWidth
        self.rightTeamRep.left = rightTeamX + ehpWidth + 1
        curDPSWidth = min(barWidth, math.ceil(fleetAppliedDPS * dpsPerPixel))
        maxDPSWidth = max(0, min(barWidth, math.ceil(fleetMaxDPS * dpsPerPixel)) - curDPSWidth - 1)
        self.rightTeamOffFill.width = curDPSWidth
        self.rightTeamOffFill.left = rightTeamX
        self.rightTeamOffBackground.width = maxDPSWidth
        self.rightTeamOffBackground.left = rightTeamX + curDPSWidth + 1
        curControlWidth = min(barWidth, math.ceil(fleetAppliedControl * contPerPixel))
        maxControlWidth = max(0, min(barWidth, math.ceil(fleetMaxControl * contPerPixel)) - curControlWidth - 1)
        self.rightTeamContFill.width = curControlWidth
        self.rightTeamContFill.left = rightTeamX
        self.rightTeamContBackground.width = maxControlWidth
        self.rightTeamContBackground.left = rightTeamX + curControlWidth + 1
        matchState, startTime = barDetails[2]
        STATE_BANNING = 0
        STATE_PREGAME = 1
        STATE_WARPIN = 2
        STATE_COUNTDOWN = 3
        STATE_STARTING = 4
        STATE_INPROGRESS = 5
        STATE_COMPLETE = 6
        STATE_CLOSED = 7
        if matchState >= STATE_COMPLETE:
            self.matchComplete = True
        else:
            if matchState < STATE_INPROGRESS:
                elapsedTimeSec = 0
            else:
                self.matchStartTime = startTime
                elapsedTimeSec = blue.os.TimeDiffInMs(startTime, blue.os.GetWallclockTime()) / 1000.0
            displayTimeSec = max(0, 600 - elapsedTimeSec)
            self.clockLabel.text = '%d:%02d' % (displayTimeSec / 60, displayTimeSec % 60)
            self.clockLabel.left = 1920 / 2 - self.clockLabel.width / 2
        redBans = '   ' + '\n   '.join((evetypes.GetName(x) for x in barDetails[3][0]))
        blueBans = '   ' + '\n   '.join((evetypes.GetName(x) for x in barDetails[3][1]))
        self.bansLabel.text = 'Red Team:\n%s\n\nBlue Team:\n%s' % (redBans, blueBans)

    def FancyUIUpdate(self):
        michelle = sm.GetService('michelle')
        target = sm.GetService('target')
        ballsIHaveAnimatedDeathFor = {}
        self.currentStatusIcons = defaultdict(list)
        self.iconsToCleanup = []
        while not self.destroyed:
            with util.ExceptionEater('FancyStatus update'):
                self.UpdateFancyStatusEffects()
            with util.ExceptionEater('FancyBar update'):
                self.UpdateFancyBars()
            teamScores = [100, 100]
            bp = michelle.GetBallpark()
            for shipID, (teamIdx, points, speedLabel, barContainer, bar1Cont, bar2Cont, bar3Cont, ptsLabel, nameLabel, shipLabel, bar1, bar2, bar3) in self.updateElements.iteritems():
                uthread.new(target.TryLockTarget, shipID)
                ball = michelle.GetBall(shipID)
                if ball and not (hasattr(ball, 'explodeOnRemove') and ball.explodeOnRemove):
                    teamScores[0 if teamIdx == 1 else 1] -= points
                    speedLabel.text = '<b>%d' % (math.sqrt(ball.vx ** 2 + ball.vy ** 2 + ball.vz ** 2),)
                    damageState = bp.GetDamageState(shipID)
                    ptsLabel.color = (1, 1, 1, 0.95)
                    nameLabel.color = (1, 1, 1, 0.95)
                    shipLabel.color = (1, 1, 1, 0.95)
                    if shipID in ballsIHaveAnimatedDeathFor:
                        ballsIHaveAnimatedDeathFor[shipID].Stop()
                        del ballsIHaveAnimatedDeathFor[shipID]
                        barContainer.opacity = 1
                        if shipID in self.shipDeathTimes:
                            del self.shipDeathTimes[shipID]
                else:
                    speedLabel.text = ''
                    damageState = (0, 0, 0)
                    if shipID not in ballsIHaveAnimatedDeathFor:
                        ballsIHaveAnimatedDeathFor[shipID] = uicore.animations.FadeOut(barContainer, duration=2)
                    ptsLabel.color = (1, 1, 1, 0.4)
                    nameLabel.color = (1, 1, 1, 0.4)
                    shipLabel.color = (1, 1, 1, 0.4)
                    if shipID not in self.shipDeathTimes:
                        self.shipDeathTimes[shipID] = blue.os.GetSimTime()
                if damageState is None:
                    continue
                if teamIdx == 0:
                    bar1Cont.width = int(math.ceil(damageState[2] * (barWidth - 4))) + 2
                    if damageState[2] < 0.3:
                        bar1.texturePath = 'res:/UI/Texture/Tournament/Block_Damage.png'
                    else:
                        bar1.texturePath = 'res:/UI/Texture/Tournament/Block_Full.png'
                    bar2Cont.width = int(math.ceil(damageState[1] * (barWidth - 4))) + 2
                    if damageState[1] < 0.3:
                        bar2.texturePath = 'res:/UI/Texture/Tournament/Block_Damage.png'
                    else:
                        bar2.texturePath = 'res:/UI/Texture/Tournament/Block_Full.png'
                    bar3Cont.width = int(math.ceil(damageState[0] * (barWidth - 4))) + 2
                    if damageState[0] < 0.3:
                        bar3.texturePath = 'res:/UI/Texture/Tournament/Block_Damage.png'
                    else:
                        bar3.texturePath = 'res:/UI/Texture/Tournament/Block_Full.png'
                else:
                    bar1Cont.width = int(math.ceil(damageState[0] * (barWidth - 4))) + 2
                    bar1Cont.left = barWidth - bar1Cont.width
                    bar1.left = bar1Cont.width - barWidth
                    if damageState[0] < 0.3:
                        bar1.texturePath = 'res:/UI/Texture/Tournament/Block_Damage_Mirror.png'
                    else:
                        bar1.texturePath = 'res:/UI/Texture/Tournament/Block_Full_Mirror.png'
                    bar2Cont.width = int(math.ceil(damageState[1] * (barWidth - 4))) + 2
                    bar2Cont.left = barWidth + barPadding + (barWidth - bar2Cont.width)
                    bar2.left = bar2Cont.width - barWidth
                    if damageState[1] < 0.3:
                        bar2.texturePath = 'res:/UI/Texture/Tournament/Block_Damage_Mirror.png'
                    else:
                        bar2.texturePath = 'res:/UI/Texture/Tournament/Block_Full_Mirror.png'
                    bar3Cont.width = int(math.ceil(damageState[2] * (barWidth - 4))) + 2
                    bar3Cont.left = (barWidth + barPadding) * 2 + (barWidth - bar3Cont.width)
                    bar3.left = bar3Cont.width - barWidth
                    if damageState[2] < 0.3:
                        bar3.texturePath = 'res:/UI/Texture/Tournament/Block_Damage_Mirror.png'
                    else:
                        bar3.texturePath = 'res:/UI/Texture/Tournament/Block_Full_Mirror.png'

            self.leftTeamScore.text = str(teamScores[0])
            self.rightTeamScore.text = str(teamScores[1])
            leftTeamRemainingPointsWidth = int(831 * ((100 - teamScores[1]) / 100.0))
            rightTeamRemainingPointsWidth = int(831 * ((100 - teamScores[0]) / 100.0))
            self.leftTeamBar.left = 831 - leftTeamRemainingPointsWidth
            self.leftTeamBar.width = leftTeamRemainingPointsWidth
            self.rightTeamBar.width = rightTeamRemainingPointsWidth
            blue.synchro.SleepSim(220)

    def Close(self, *args, **kwds):
        if self.fancyUI:
            self.fancyUI.Close()
        if self.warningLine:
            self.warningLine.Close()
        sm.GetService('target').disableSpinnyReticule = False
        sm.GetService('target').overrideBarHeight = None
        neocomLayer = uicore.layer.Get('sidePanels')
        if neocomLayer is not None:
            neocomLayer.state = uiconst.UI_PICKCHILDREN
        sm.GetService('infoPanel').ShowHideSidePanel(hide=False)
        uicontrols.Window.Close(self, *args, **kwds)

    def LockEveryone(self, *args):
        target = sm.GetService('target')
        for teamIdx in (0, 1):
            for charID, shipTypeID, shipID, points in self.teamComps[teamIdx]:
                uthread.new(target.TryLockTarget, shipID)

    def SortLocks(self, *args):
        target = sm.GetService('target')
        target.rowDict = defaultdict(list)
        for teamIdx in (0, 1):
            for charID, shipTypeID, shipID, points in self.teamComps[teamIdx]:
                if shipID in target.targetsByID:
                    target.rowDict[teamIdx].append(shipID)

        target.ArrangeTargets()

    def ToggleCamWobble(self, *args):
        cam = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SPACE_PRIMARY)
        cam.idleMove = not cam.idleMove

    def ToggleBackground(*args):
        prefs.SetValue('bracketBackground', not prefs.GetValue('bracketBackground', True))
        sm.GetService('bracket').Reload()

    def ToggleDronePod(*args):
        prefs.SetValue('bracketDronePodFuntimes', not prefs.GetValue('bracketDronePodFuntimes', True))
        sm.GetService('bracket').Reload()

    def ToggleColor(*args):
        prefs.SetValue('bracketTextColor', not prefs.GetValue('bracketTextColor', True))
        sm.GetService('bracket').Reload()

    def ToggleShipText(*args):
        prefs.SetValue('bracketsAlwaysShowShipText', not prefs.GetValue('bracketsAlwaysShowShipText', True))
        sm.GetService('bracket').Reload()

    def ToggleBracketSort(*args):
        prefs.SetValue('sortBracketsByPoints', not prefs.GetValue('sortBracketsByPoints', True))
        sm.GetService('bracket').Reload()
