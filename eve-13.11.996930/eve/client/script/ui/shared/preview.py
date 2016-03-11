#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\preview.py
from brennivin.itertoolsext import first, first_or_default
from carbon.common.lib.GameWorld import GWAnimation
from carbon.common.script.util.commonutils import Clamp
from carbon.common.script.util.format import FmtDist
from carbonui.uicore import uicorebase as uicore
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.environment.model.turretSet import TurretSet
from eve.client.script.ui.control.buttonGroup import ButtonGroup
from eve.client.script.ui.control.eveLabel import EveCaptionMedium, EveHeaderSmall, Label
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.control.scenecontainer import SceneContainerBaseNavigation, SceneContainer
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.login.charcreation.ccUtil import GenderIDToPaperDollGender
from eve.client.script.ui.shared.skins.controller import SkinPanelController
from eve.client.script.ui.shared.skins.skinPanel import SkinPanel
from eve.client.script.ui.station.assembleModularShip import AssembleShip
from eve.client.script.ui.util.uiComponents import Component, ButtonEffect
from eve.common.script.sys.eveCfg import IsPreviewable
import evetypes
from inventorycommon.util import IsModularShip
from locks import Lock
from utillib import KeyVal
import carbon.common.script.sys.service as service
import carbonui.const as uiconst
import charactercreator.const as ccConst
import eve.common.lib.appConst as appConst
import evegraphics.settings as gfxsettings
import evegraphics.utils as gfxutils
import eveSpaceObject.spaceobjanimation as soanimation
import geo2
import inventorycommon.const as invconst
import itertools
import localization
import log
import math
import paperDoll as pd
import re
import sys
import trinity
import uthread
import inventorycommon.typeHelpers
import const
MESH_NAMES_BY_GROUPID = {invconst.groupApparelEyewear: [pd.ACCESSORIES_CATEGORIES.ACCESSORIES],
 invconst.groupApparelProsthetics: [pd.ACCESSORIES_CATEGORIES.SLEEVESLOWER],
 invconst.groupApparelTattoos: [pd.ACCESSORIES_CATEGORIES.SLEEVESLOWER],
 invconst.groupApparelPiercings: [],
 invconst.groupApparelScars: [pd.BODY_CATEGORIES.SCARS],
 invconst.groupApparelMidLayer: [pd.BODY_CATEGORIES.TOPINNER],
 invconst.groupApparelOuter: [pd.BODY_CATEGORIES.OUTER],
 invconst.groupApparelTops: [pd.BODY_CATEGORIES.TOPINNER],
 invconst.groupApparelBottoms: [pd.BODY_CATEGORIES.BOTTOMOUTER],
 invconst.groupApparelFootwear: [pd.BODY_CATEGORIES.FEET],
 invconst.groupApparelHairStyles: [pd.DOLL_PARTS.HAIR, pd.DOLL_PARTS.HEAD],
 invconst.groupApparelMakeup: [pd.HEAD_CATEGORIES.MAKEUP]}
MANNEQUIN_RES_BY_GENDER = {pd.GENDER.MALE: 'res:/Graphics/Character/DNAFiles/Mannequin/MaleMannequin.prs',
 pd.GENDER.FEMALE: 'res:/Graphics/Character/DNAFiles/Mannequin/FemaleMannequin.prs'}
PAPERDOLL_CATEGORIES_COVERING = {ccConst.bottommiddle: [ccConst.bottomouter]}

def GetPaperDollResource(typeID, gender = None):
    assets = filter(lambda a: a.typeID == typeID, cfg.paperdollResources)
    if len(assets) == 0:
        log.LogWarn('PreviewWnd::PreviewType - No asset matched the typeID {}'.format(typeID))
        return None
    default_asset = first(assets)
    unisex_asset = first_or_default(assets, lambda a: a.resGender is None, default_asset)
    return first_or_default(assets, lambda a: a.resGender == gender, unisex_asset)


def SetupAnimations(model, typeID):
    animationStates = inventorycommon.typeHelpers.GetAnimationStates(typeID)
    for animationState in animationStates:
        gfxState = cfg.graphicStates.GetIfExists(animationState)
        if gfxState is not None:
            soanimation.SetUpAnimation(model, gfxState.file, trinity)

    if len(animationStates) == 0:
        model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
    else:
        soanimation.TriggerDefaultStates(model)


class Preview(service.Service):
    __guid__ = 'svc.preview'
    __servicename__ = 'preview'
    __displayname__ = 'Preview Service'
    __exportedcalls__ = {'PreviewType': [],
     'PreviewCharacter': []}
    __dependencies__ = []

    def Run(self, memStream = None):
        service.Service.Run(self, memStream=memStream)
        self.state = service.SERVICE_RUNNING

    def PreviewType(self, typeID, subsystems = None, itemID = None, animate = True):
        wnd = PreviewWnd.GetIfOpen()
        if wnd:
            wnd.PreviewType(typeID=typeID, subsystems=subsystems, itemID=itemID, animate=animate)
        else:
            wnd = PreviewWnd.Open(typeID=typeID, subsystems=subsystems, itemID=itemID, animate=animate)
        return wnd

    def PreviewCharacter(self, charID):
        if charID in appConst.auraAgentIDs:
            return
        dna = sm.RemoteSvc('paperDollServer').GetPaperDollData(charID)
        if dna is None:
            raise UserError('CharacterHasNoDNA', {'charID': charID})
        wnd = PreviewCharacterWnd.GetIfOpen()
        if wnd:
            wnd.PreviewCharacter(charID=charID, dna=dna)
        else:
            wnd = PreviewCharacterWnd.Open(charID=charID, dna=dna)
        return wnd


@Component(ButtonEffect(opacityIdle=0.0, opacityHover=0.5, opacityMouseDown=1.0, bgElementFunc=lambda parent, _: parent.hilite, audioOnEntry='wise:/msg_ListEntryEnter_play', audioOnClick='wise:/msg_ListEntryClick_play'))

class SidePanelButton(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(SidePanelButton, self).ApplyAttributes(attributes)
        self.onClick = attributes.onClick
        self.expanded = attributes.get('expanded', False)
        Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/preview/tab.png', width=20, height=80)
        self.hilite = Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/preview/tab-hilite.png', width=20, height=80, opacity=0.0)
        rotation = 0 if self.expanded else math.pi
        self.tabIcon = Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, left=2, top=32, texturePath='res:/UI/Texture/classes/preview/tab-icon.png', width=16, height=16, rotation=rotation)

    def OnClick(self, *args):
        self.expanded = not self.expanded
        self.AnimClick()
        self.onClick()

    def AnimClick(self):
        rotation = 0 if self.expanded else math.pi
        uicore.animations.MorphScalar(self.tabIcon, 'rotation', startVal=self.tabIcon.rotation, endVal=rotation, duration=0.3)


class PreviewWnd(Window):
    __guid__ = 'form.PreviewWnd'
    default_windowID = 'previewWnd'
    default_topParentHeight = 0
    default_minSize = (420, 320)
    default_caption = localization.GetByLabel('UI/Preview/PreviewCaption')
    PANEL_WIDTH = 280

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        itemID = attributes.itemID
        self.typeID = attributes.typeID
        subsystems = attributes.subsystems
        animate = attributes.animate
        width = self.PANEL_WIDTH if self.IsPanelExpanded() else 0
        self.sidePanel = Container(parent=self.sr.main, align=uiconst.TOLEFT, width=width, clipChildren=True)
        self.skinController = SkinPanelController(typeID=None)
        SkinPanel(parent=self.sidePanel, align=uiconst.TOLEFT, width=self.PANEL_WIDTH - 10, left=10, controller=self.skinController, settingsPrefix='Preview_SkinPanel', logContext='PreviewWindow')
        mainCont = Container(parent=self.sr.main, align=uiconst.TOALL, padding=(2, 0, 2, 2))
        opacity = 1.0 if self.IsPanelEnabled() else 0.0
        self.sidePanelButton = SidePanelButton(parent=mainCont, align=uiconst.CENTERLEFT, opacity=opacity, onClick=self.ToggleSidePanel, expanded=self.IsPanelExpanded())
        self.loadingWheel = LoadingWheel(parent=mainCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.previewContFill = FillThemeColored(parent=mainCont, align=uiconst.TOALL)
        overlayCont = Container(name='overlayCont', parent=mainCont, padding=2, clipChildren=1)
        self.title = EveCaptionMedium(text='', parent=overlayCont, align=uiconst.TOTOP, padding=(17, 4, 17, 0), state=uiconst.UI_NORMAL)
        self.title.GetMenu = self.GetShipMenu
        self.title.expandOnLeft = 1
        self.subtitle = EveHeaderSmall(text='', parent=overlayCont, align=uiconst.TOTOP, padding=(19, 0, 17, 0), state=uiconst.UI_DISABLED)
        descLayer = Container(parent=mainCont)
        self.descCont = ContainerAutoSize(parent=descLayer, align=uiconst.TOBOTTOM, bgColor=(0.0, 0.0, 0.0, 0.3), padding=6, state=uiconst.UI_HIDDEN)
        self.desc = Label(parent=self.descCont, padding=6, fontsize=12, align=uiconst.TOBOTTOM)
        self.previewContainer = PreviewContainer(parent=mainCont, OnStartLoading=self.OnStartLoading, OnStopLoading=self.OnStopLoading)
        self.previewContainer.navigation.OnDropData = self.OnDropData
        self.PreviewType(self.typeID, subsystems, itemID, animate)

    def IsPanelExpanded(self):
        return self.IsPanelEnabled() and settings.user.ui.Get('previewPanel', 1)

    def IsPanelEnabled(self):
        return evetypes.GetCategoryID(self.typeID) == invconst.categoryShip or evetypes.GetGroupID(self.typeID) == invconst.groupShipSkins

    def ToggleSidePanel(self):
        isExpanded = not self.IsPanelExpanded()
        settings.user.ui.Set('previewPanel', isExpanded)
        self.UpdateSidePanel(isExpanded)

    def UpdateSidePanel(self, expanded = None):
        if expanded is None:
            expanded = settings.user.ui.Get('previewPanel', 1)
        width = self.PANEL_WIDTH if expanded else 0
        uicore.animations.MorphScalar(self.sidePanel, 'width', startVal=self.sidePanel.width, endVal=width, duration=0.3)

    def OnStartLoading(self, previewCont):
        uicore.animations.FadeIn(self.loadingWheel, duration=0.4)
        uicore.animations.FadeIn(self.previewContFill, duration=0.2, sleep=True)
        self.ClearText()

    def OnStopLoading(self, previewCont, success):
        uicore.animations.FadeOut(self.loadingWheel, duration=0.2)
        if success:
            uicore.animations.FadeOut(self.previewContFill, duration=0.4)
            self.UpdateText()

    def UpdateText(self):
        context = self.previewContainer.context
        if not hasattr(context, 'typeID'):
            return
        groupID = evetypes.GetGroupID(context.typeID)
        categoryID = evetypes.GetCategoryID(context.typeID)
        title = evetypes.GetName(context.typeID)
        if hasattr(context, 'itemID'):
            bp = sm.GetService('michelle').GetBallpark()
            if bp:
                slim = bp.GetInvItem(context.itemID)
                if slim:
                    title = slim.name
        self.title.text = title
        subtitle = ''
        if categoryID != invconst.categoryApparel:
            scene = self.previewContainer.sceneContainer.scene
            model = first_or_default(getattr(scene, 'objects', []), None)
            if model:
                radius = round(model.GetBoundingSphereRadius() * 2, 0)
                if groupID in invconst.turretModuleGroups or groupID in invconst.turretAmmoGroups:
                    subtitle = localization.GetByLabel('UI/Preview/ShipSubLabelNoRace', groupName=evetypes.GetGroupName(context.typeID), length=FmtDist(radius))
                else:
                    raceID = evetypes.GetRaceID(context.typeID)
                    race = cfg.races.Get(raceID) if raceID in cfg.races else None
                    if race is None:
                        subtitle = localization.GetByLabel('UI/Preview/ShipSubLabelNoRace', groupName=evetypes.GetGroupName(context.typeID), length=FmtDist(radius))
                    else:
                        raceName = localization.GetByMessageID(race.raceNameID)
                        subtitle = localization.GetByLabel('UI/Preview/ShipSubLabel', raceName=raceName, groupName=evetypes.GetGroupName(context.typeID), length=FmtDist(radius))
        self.subtitle.text = subtitle
        if categoryID == invconst.categoryApparel:
            self.descCont.Show()
            description = evetypes.GetDescription(context.typeID) or ''
            description = re.sub('<b>|</b>|\\r', '', description)
            description = re.sub('\\n', '<br>', description)
            self.desc.text = description

    def GetShipMenu(self, *args):
        return sm.GetService('menu').GetMenuFormItemIDTypeID(None, self.typeID, ignoreMarketDetails=False, filterFunc=[localization.GetByLabel('UI/Preview/Preview')])

    def OnDropData(self, dragObj, nodes):
        super(PreviewWnd, self).OnDropData(dragObj, nodes)
        node = first(nodes)
        typeID = None
        if hasattr(node, 'item') and hasattr(node.item, 'typeID'):
            typeID = node.item.typeID
        elif hasattr(node, 'typeID'):
            typeID = node.typeID
        itemID = None
        if hasattr(node, 'item') and hasattr(node.item, 'itemID'):
            itemID = node.item.itemID
        elif hasattr(node, 'itemID'):
            itemID = node.itemID
        if typeID:
            self.PreviewType(typeID, itemID=itemID)

    def PreviewType(self, typeID, subsystems = None, itemID = None, animate = True):
        uthread.new(self._PreviewType, typeID, subsystems, itemID, animate)

    def _PreviewType(self, typeID, subsystems, itemID, animate):
        self.typeID = typeID
        self.BringToFront()
        if evetypes.GetCategoryID(typeID) == invconst.categoryApparel:
            self.SetMinSize([320, 470])
            self.SetMaxSize([800, 950])
        else:
            self.SetMinSize([660, 320])
            self.SetMaxSize([None, None])
        if not self.IsPanelEnabled():
            uicore.animations.FadeOut(self.sidePanelButton, duration=0.3)
            self.UpdateSidePanel(expanded=False)
        newScene = self.previewContainer.PreviewType(typeID, subsystems=subsystems, itemID=itemID, controller=getattr(self, 'skinController', None))
        if self.IsPanelEnabled():
            uicore.animations.FadeIn(self.sidePanelButton, duration=0.3)
            self.UpdateSidePanel()
        if IsModularShip(typeID):
            kv = KeyVal(typeID=typeID)
            wnd = AssembleShip.GetIfOpen('PreviewSubSystems')
            if wnd:
                wnd.UpdateShip(kv, self.previewContainer.context.subsystems)
            else:
                AssembleShip.Open(windowID='PreviewSubSystems', ship=kv, groupIDs=None, isPreview=True, setselected=self.previewContainer.context.subsystems)
        else:
            self.CloseSubSystemWnd()
        if newScene and animate:
            self.previewContainer.AnimEntry(-1.8, 0.2, -0.7, -0.3)

    def ClearText(self):
        self.title.text = ''
        self.subtitle.text = ''
        self.desc.SetText('')
        self.descCont.Hide()

    def BringToFront(self):
        self.Maximize()
        wnd = AssembleShip.GetIfOpen(windowID='PreviewSubSystems')
        if wnd and wnd.parent.children.index(wnd) > 1:
            wnd.Maximize()

    def _OnResize(self, *args, **kw):
        self.previewContainer.UpdateViewPort()

    def CloseSubSystemWnd(self):
        AssembleShip.CloseIfOpen(windowID='PreviewSubSystems')

    def Close(self, setClosed = False, *args, **kwds):
        Window.Close(self, setClosed, *args, **kwds)
        self.CloseSubSystemWnd()


class PreviewCharacterWnd(Window):
    __guid__ = 'form.PreviewCharacterWnd'
    default_windowID = 'previewCharacterWnd'
    default_topParentHeight = 0
    default_minSize = (420, 320)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.charID = attributes.charID
        self.dna = attributes.dna
        self.btnGroup = ButtonGroup(parent=self.sr.main, idx=0)
        self.btnGroup.AddButton(localization.GetByLabel('UI/Preview/ViewPortrait'), self.SwitchToPortrait, (self.charID,))
        self.previewContainer = PreviewContainer(parent=self.sr.main)
        self.PreviewCharacter(self.charID, dna=self.dna)

    def PreviewCharacter(self, charID, dna):
        self.charID = charID
        self.dna = dna
        caption = localization.GetByLabel('UI/InfoWindow/PortraitCaption', character=charID)
        self.SetCaption(caption)
        uthread.new(self.previewContainer.PreviewCharacter, charID, dna=dna)
        self.Maximize()

    def SwitchToPortrait(self, charID):
        from eve.client.script.ui.shared.info.infoWindow import PortraitWindow
        PortraitWindow.CloseIfOpen()
        portraitWnd = PortraitWindow.Open(charID=charID)
        portraitWnd.Maximize()
        self.CloseByUser()

    def _OnResize(self, *args, **kw):
        self.previewContainer.UpdateViewPort()


class InvalidPreviewType(Exception):
    pass


class PreviewContainerClosing(Exception):
    pass


class PreviewNavigation(SceneContainerBaseNavigation):
    default_cursor = uiconst.UICURSOR_CCALLDIRECTIONS
    default_state = uiconst.UI_NORMAL

    def UpdateCursor(self):
        if uicore.uilib.rightbtn and not uicore.uilib.leftbtn and self.sr.sceneContainer.verticalPanEnabled:
            self.cursor = uiconst.UICURSOR_CCUPDOWN
        else:
            self.cursor = uiconst.UICURSOR_CCALLDIRECTIONS

    def OnMouseDown(self, *args):
        SceneContainerBaseNavigation.OnMouseDown(self, *args)
        self.UpdateCursor()

    def OnMouseUp(self, *args):
        SceneContainerBaseNavigation.OnMouseUp(self, *args)
        self.UpdateCursor()

    def OnMouseMove(self, *args):
        SceneContainerBaseNavigation.OnMouseMove(self, *args)
        if uicore.uilib.leftbtn and not uicore.uilib.rightbtn:
            cameraDistance = self.sr.sceneContainer.camera.translationFromParent
            delta = uicore.uilib.dy * 0.0006 * cameraDistance
            y = self.sr.sceneContainer.verticalPan
            self.sr.sceneContainer.verticalPan = y + delta


class PreviewSceneContainer(SceneContainer):
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        super(PreviewSceneContainer, self).ApplyAttributes(attributes)
        self._minY = None
        self._maxY = None

    @property
    def verticalPanLimits(self):
        return (self._minY, self._maxY)

    @verticalPanLimits.setter
    def verticalPanLimits(self, limits):
        if limits is None:
            limits = (None, None)
        minY, maxY = limits
        if minY > maxY:
            minY, maxY = maxY, minY
        self._minY = minY
        self._maxY = maxY

    @property
    def verticalPanEnabled(self):
        return self._minY is not None and self._maxY is not None

    @property
    def verticalPan(self):
        return self.cameraParent.value[1]

    @verticalPan.setter
    def verticalPan(self, y):
        if self.verticalPanEnabled:
            y = Clamp(y, self._minY, self._maxY)
            x, _, z = self.cameraParent.value
            self.cameraParent.value = (x, y, z)


class PreviewContainer(Container):
    __notifyevents__ = ['OnGraphicSettingsChanged', 'OnSetDevice']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.context = None
        self.loadingThread = None
        self.startLoadingCallback = attributes.get('OnStartLoading', None)
        self.stopLoadingCallback = attributes.get('OnStopLoading', None)
        self.loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.loadingWheel.opacity = 0.0
        self.sceneContainer = PreviewSceneContainer(parent=self, align=uiconst.TOALL)
        self.sceneContainer.Startup()
        self.navigation = PreviewNavigation(parent=self)
        self.navigation.Startup(self.sceneContainer)

    def Close(self):
        super(PreviewContainer, self).Close()
        self._Cleanup()

    def _OnStartLoading(self):
        if self.startLoadingCallback:
            self.startLoadingCallback(self)
        else:
            uicore.animations.FadeIn(self.loadingWheel, duration=0.4)

    def _OnStopLoading(self, success):
        if self.stopLoadingCallback:
            self.stopLoadingCallback(self, success)
        else:
            uicore.animations.FadeOut(self.loadingWheel, duration=0.4)

    def PreviewType(self, typeID, **kwargs):
        if not IsPreviewable(typeID):
            raise InvalidPreviewType('%s (%s) is not previewable' % (evetypes.GetName(typeID), typeID))
        groupID = evetypes.GetGroupID(typeID)
        categoryID = evetypes.GetCategoryIDByGroup(groupID)
        if IsModularShip(typeID):
            return self.PreviewTech3Ship(typeID, subsystems=kwargs.get('subsystems'), scenePath=kwargs.get('scenePath'))
        if categoryID == invconst.categoryApparel:
            return self.PreviewApparel(typeID, gender=kwargs.get('gender'), background=kwargs.get('background'))
        if groupID in invconst.turretModuleGroups:
            return self.PreviewTurret(typeID, scenePath=kwargs.get('scenePath'))
        if groupID in invconst.turretAmmoGroups:
            return self.PreviewAmmo(typeID, scenePath=kwargs.get('scenePath'))
        if groupID == invconst.groupShipSkins or categoryID == invconst.categoryShip:
            controller = kwargs.get('controller')
            if controller is None:
                return self.PreviewSkin(typeID, scenePath=kwargs.get('scenePath'))
            else:
                return self.PreviewSkinnedEntity(typeID, controller=kwargs.get('controller'), scenePath=kwargs.get('scenePath'))
        else:
            return self.PreviewSpaceEntity(typeID, itemID=kwargs.get('itemID'), scenePath=kwargs.get('scenePath'))

    def PreviewAmmo(self, typeID, scenePath = None):
        context = AmmoSceneContext(typeID, scenePath=scenePath)
        return self.LoadScene(context)

    def PreviewApparel(self, typeID, gender = None, background = None):
        context = ApparelSceneContext(typeID, gender=gender, background=background)
        return self.LoadScene(context)

    def PreviewCharacter(self, charID, dna = None, apparel = None, background = None):
        context = CharacterSceneContext(charID, dna=dna, apparel=apparel, background=background)
        return self.LoadScene(context)

    def PreviewSkinnedEntity(self, typeID, controller, scenePath = None):
        if evetypes.GetCategoryID(typeID) == invconst.categoryShip:
            controller.typeID = typeID
            materialSetID = None
        else:
            skin = sm.GetService('skinSvc').GetSkinByLicenseType(typeID)
            controller.typeID = skin.types[0]
            for s in controller.skins:
                if s.materialID == skin.materialID:
                    controller.PickSkin(s)
                    break

            materialSetID = skin.materialSetID
        self.skinController = controller
        self.scenePath = scenePath
        controller.onChange.connect(self.UpdateSkinnedEntity)
        return self.PreviewSpaceEntity(controller.typeID, materialSetID=materialSetID, scenePath=scenePath)

    def UpdateSkinnedEntity(self):
        typeID = self.skinController.typeID
        materialSetID = None
        if self.skinController.previewed is not None:
            materialSetID = self.skinController.previewed.materialSetID
        uthread.new(self.PreviewSpaceEntity, typeID, materialSetID=materialSetID, scenePath=self.scenePath)

    def PreviewSkin(self, typeID, scenePath = None):
        if evetypes.GetCategoryID(typeID) == invconst.categoryShip:
            return self.PreviewSpaceEntity(typeID, scenePath=scenePath)
        else:
            skin = sm.GetService('skinSvc').GetSkinByLicenseType(typeID)
            entityTypeID = skin.types[0]
            return self.PreviewSpaceEntity(entityTypeID, materialSetID=skin.materialSetID, scenePath=scenePath)

    def PreviewSpaceEntity(self, typeID, itemID = None, materialSetID = None, scenePath = None):
        context = SpaceEntitySceneContext(typeID, itemID=itemID, materialSetID=materialSetID, scenePath=scenePath)
        return self.LoadScene(context)

    def PreviewSofDna(self, dna, dirt = None, scenePath = None):
        context = SofDnaSceneContext(dna, dirt=dirt, scenePath=scenePath)
        return self.LoadScene(context)

    def PreviewTech3Ship(self, typeID, subsystems = None, scenePath = None):
        context = T3ShipSceneContext(typeID, subsystems=subsystems, scenePath=scenePath)
        return self.LoadScene(context)

    def PreviewTurret(self, typeID, scenePath = None):
        context = TurretSceneContext(typeID, scenePath=scenePath)
        return self.LoadScene(context)

    def LoadScene(self, context, force = False):
        if context == self.context and not force:
            return False
        success = True
        try:
            self._OnStartLoading()
            self._Cleanup()
            self.context = context
            self.loadingThread = uthread.newJoinable(self.context.LoadScene, self.sceneContainer)
            uthread.waitForJoinable(self.loadingThread, timeout=None)
            self.UpdateViewPort()
            self.loadingThread = None
        except Exception:
            if not self.destroyed:
                log.LogException('Exception raised while loading preview for {context}'.format(context=str(context)))
                sys.exc_clear()
                success = False

        self._OnStopLoading(success)
        return success

    def Reload(self):
        if self.context:
            self.LoadScene(self.context, force=True)

    def _Cleanup(self):
        try:
            if self.loadingThread:
                self.loadingThread.kill()
                self.loadingThread = None
            if self.context:
                self.context.Cleanup()
                self.context = None
        except Exception:
            log.LogException('Exception raised during preview container cleanup', severity=log.INFO)
            sys.exc_clear()

    def AnimEntry(self, yaw0 = 0.0, pitch0 = 0.0, yaw1 = -0.5, pitch1 = -0.5, duration = 2.0):
        self.sceneContainer.AnimEntry(yaw0, pitch0, yaw1, pitch1, duration)

    def UpdateViewPort(self):
        if self.sceneContainer:
            self.sceneContainer.UpdateViewPort()

    def OnSetDevice(self):
        uthread.new(self.Reload)

    def OnGraphicSettingsChanged(self, changes):
        if self.context and any((setting in self.context.relevantSettings for setting in changes)):
            uthread.new(self.Reload)


class SceneContext(object):
    relevantSettings = []

    def LoadScene(self, sceneContainer):
        raise NotImplementedError('SceneContexts must override the LoadScene method')

    def Cleanup(self):
        pass


class AmmoSceneContext(SceneContext):

    def __init__(self, typeID, scenePath = None):
        if evetypes.GetGroupID(typeID) not in invconst.turretAmmoGroups:
            raise InvalidPreviewType('%s (%s) is not a previewable ammo type' % (evetypes.GetName(typeID), typeID))
        self.typeID = typeID
        self.scenePath = scenePath or 'res:/dx9/scene/fitting/previewAmmo.red'

    def __eq__(self, other):
        return isinstance(other, AmmoSceneContext) and self.typeID == other.typeID and self.scenePath == other.scenePath

    def LoadScene(self, sceneContainer):
        sceneContainer.PrepareSpaceScene(maxPitch=0.0, scenePath=self.scenePath)
        model = trinity.Load('res:/dx9/model/ship/IconPreview/PreviewAmmoShip.red')
        sceneContainer.AddToScene(model)
        ammoRedFile = inventorycommon.typeHelpers.GetGraphicFile(self.typeID)
        ammoRedFile = ammoRedFile[:-4] + '_hi' + ammoRedFile[-4:]
        ammo = trinity.Load(ammoRedFile)
        if ammo.__bluetype__ != 'trinity.EveMissile':
            raise InvalidPreviewType('{%s (%s) is not a trinity.EveMissile' % (evetypes.GetName(self.typeID), self.typeID))
        warhead = ammo.warheads[0]
        floatHeight = ammo.boundingSphereRadius - ammo.boundingSphereCenter[2]
        floatHeight += 0.2 * ammo.boundingSphereRadius
        warhead.translation = (0.0, floatHeight, 0.0)
        warhead.rotation = geo2.QuaternionRotationAxis((1.0, 0.0, 0.0), -0.5 * math.pi)
        warhead.startDataValid = True
        model.children.append(warhead)
        del warhead.children[:]
        reflection = warhead.CopyTo()
        reflection.translation = (0.0, -floatHeight, 0.0)
        reflection.rotation = geo2.QuaternionRotationAxis((1.0, 0.0, 0.0), 0.5 * math.pi)
        reflection.startDataValid = True
        model.children.append(reflection)
        boundingCenterY = ammo.boundingSphereRadius + 0.5 * floatHeight
        model.boundingSphereCenter = (0.0, boundingCenterY, 0.0)
        model.boundingSphereRadius = ammo.boundingSphereRadius + floatHeight
        SetupSpaceCamera(sceneContainer, model)


class ApparelSceneContext(SceneContext):
    relevantSettings = [gfxsettings.GFX_CHAR_TEXTURE_QUALITY]

    def __init__(self, typeID, gender = None, background = None):
        if evetypes.GetCategoryID(typeID) != invconst.categoryApparel:
            raise InvalidPreviewType('%s (%s) is not an apparel item' % (evetypes.GetName(typeID), typeID))
        self.typeID = typeID
        self.gender = gender
        self.background = background
        self.mannequin = None

    def __eq__(self, other):
        return isinstance(other, ApparelSceneContext) and self.typeID == other.typeID and self.gender == other.gender and self.background == other.background

    def LoadScene(self, sceneContainer):
        sceneContainer.PrepareInteriorScene(backgroundImage=self.background)
        apparel = GetPaperDollResource(self.typeID, gender=self.gender)
        if apparel is None:
            raise InvalidPreviewType('%s (%s) does not have an associated paper doll resource' % (evetypes.GetName(self.typeID), self.typeID))
        factory = pd.Factory()
        mannequin = pd.PaperDollCharacter(factory)
        self.mannequin = mannequin
        dollGender = GenderIDToPaperDollGender(apparel.resGender)
        mannequin.doll = pd.Doll('mannequin', gender=dollGender)
        mannequin.doll.Load(MANNEQUIN_RES_BY_GENDER[dollGender], factory)
        mannequin.WaitForUpdate()
        textureQuality = gfxsettings.Get(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
        resolution = ccConst.TEXTURE_RESOLUTIONS[textureQuality]
        mannequin.doll.textureResolution = resolution
        mannequin.doll.overrideLod = 0
        mannequin.Spawn(sceneContainer.scene, usePrepass=False)
        mannequin.WaitForUpdate()
        with CaptureDollMeshChanges(mannequin.doll) as meshes:
            mannequin.doll.SetItemType(factory, apparel.resPath)
            typeData = factory.GetItemType(apparel.resPath, gender=dollGender)
            apparelCategory = sm.GetService('character').GetCategoryFromResPath(typeData[0])
            coveringCategories = PAPERDOLL_CATEGORIES_COVERING.get(apparelCategory, [])
            for category in coveringCategories:
                mannequin.doll.buildDataManager.RemoveMeshContainingModifiers(category)

            mannequin.Update()
            mannequin.WaitForUpdate()
        newMeshes = set(filter(lambda m: m not in meshes.before, meshes.after))
        assetGroupID = evetypes.GetGroupID(self.typeID)
        meshNameCheck = lambda mesh: any(map(lambda name: mesh.name.startswith(name), MESH_NAMES_BY_GROUPID[assetGroupID]))
        groupMeshes = set(filter(meshNameCheck, meshes.after))
        boundingBoxes = map(lambda m: m.geometry.GetBoundingBox(0), newMeshes | groupMeshes)
        if len(boundingBoxes) == 0:
            aabb = mannequin.visualModel.GetBoundingBoxInLocalSpace()
        else:
            aabb = reduce(MergeBoundingBoxes, boundingBoxes)
        animationRes = 'res:/Animation/MorphemeIncarna/Export/Mannequin/Mannequin.mor'
        animationUpdater = GWAnimation(animationRes)
        if animationUpdater is not None:
            animationSetIndex = 0 if dollGender == pd.GENDER.FEMALE else 1
            animationUpdater.network.SetAnimationSetIndex(animationSetIndex)
            mannequin.avatar.animationUpdater = animationUpdater
        floorShadow = trinity.Load(ccConst.CUSTOMIZATION_FLOOR)
        sceneContainer.scene.dynamics.append(floorShadow)
        SetupInteriourCamera(sceneContainer, aabb)

    def Cleanup(self):
        self.mannequin = None


class CharacterSceneContext(SceneContext):
    relevantSettings = [gfxsettings.GFX_CHAR_TEXTURE_QUALITY, gfxsettings.UI_NCC_GREEN_SCREEN, gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION]

    def __init__(self, charID, dna = None, apparel = None, background = None):
        dna = dna or sm.RemoteSvc('paperDollServer').GetPaperDollData(charID)
        if dna is None:
            raise UserError('CharacterHasNoDNA', {'charID': charID})
        self.charID = charID
        self.dna = dna
        self.apparel = apparel or []
        self.background = background

    def __eq__(self, other):
        return isinstance(other, CharacterSceneContext) and self.charID == other.charID and self.dna == other.dna and self.apparel == other.apparel and self.background == other.background

    def LoadScene(self, sceneContainer):
        background = self.background
        if gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            background = 'res:/UI/Texture/CharacterCreation/backdrops/Background_1001.dds'
        sceneContainer.PrepareInteriorScene(addShadowStep=True, backgroundImage=background)
        owner = cfg.eveowners.Get(self.charID)
        bloodlineID = const.typeIDToBloodlineID[owner.typeID]
        gender = getattr(owner, 'gender', None)
        if gender is None:
            raise RuntimeError('{0.name} ({0.charID}) does not have a defined gender'.format(owner))
        charSvc = sm.GetService('character')
        character = charSvc.AddCharacterToScene(charID=self.charID, scene=sceneContainer.scene, gender=GenderIDToPaperDollGender(gender), bloodlineID=bloodlineID, dna=self.dna, lod=pd.LOD_SKIN, updateDoll=False)
        textureQuality = gfxsettings.Get(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
        textureResolution = ccConst.DOLL_VIEWER_TEXTURE_RESOLUTIONS[textureQuality]
        character.doll.textureResolution = textureResolution
        useFastShader = gfxsettings.Get(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION)
        character.doll.useFastShader = useFastShader
        for typeID in self.apparel:
            apparel = GetPaperDollResource(typeID, gender=gender)
            if apparel is None:
                log.LogError('Unable to preview %s (%s) since it has no associated resource' % (evetypes.GetName(typeID), typeID))
                continue
            charSvc.ApplyTypeToDoll(self.charID, apparel.resPath, doUpdate=False)

        character.Update()
        character.WaitForUpdate()
        if useFastShader:
            sceneContainer.scene.ambientColor = (0.25, 0.25, 0.25)
        if not gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            floor = trinity.Load(ccConst.CUSTOMIZATION_FLOOR)
            sceneContainer.scene.dynamics.append(floor)
        if sceneContainer.scene.apexScene is not None:
            sceneContainer.scene.apexScene.CreatePlane((0, 0, 0), (0, 1, 0), 0)
        aabb = character.visualModel.GetBoundingBoxInLocalSpace()
        SetupInteriourCamera(sceneContainer, aabb)

    def Cleanup(self):
        sm.GetService('character').RemoveCharacter(self.charID)


class SpaceEntitySceneContext(SceneContext):

    def __init__(self, typeID, itemID = None, materialSetID = None, scenePath = None):
        if scenePath is None:
            raceID = evetypes.GetRaceID(typeID)
            scenePath = gfxutils.GetPreviewScenePath(raceID)
        self.typeID = typeID
        self.itemID = itemID
        self.materialSetID = materialSetID
        self.scenePath = scenePath

    def __eq__(self, other):
        return isinstance(other, SpaceEntitySceneContext) and self.typeID == other.typeID and self.itemID == other.itemID and self.materialSetID == other.materialSetID and self.scenePath == other.scenePath

    def LoadScene(self, sceneContainer):
        sceneContainer.PrepareSpaceScene(scenePath=self.scenePath)
        resFile = inventorycommon.typeHelpers.GetGraphicFile(self.typeID)
        modelDNA = None
        if evetypes.GetCategoryID(self.typeID) == invconst.categoryStation and self.itemID:
            stations = cfg.mapSolarSystemContentCache.npcStations
            npcStation = stations.get(self.itemID, None)
            if npcStation:
                graphicID = npcStation.graphicID
                modelDNA = gfxutils.BuildSOFDNAFromGraphicID(graphicID)
        if modelDNA is None:
            modelDNA = gfxutils.BuildSOFDNAFromTypeID(self.typeID, materialSetID=self.materialSetID)
        if modelDNA is not None:
            spaceObjectFactory = sm.GetService('sofService').spaceObjectFactory
            model = spaceObjectFactory.BuildFromDNA(modelDNA)
        else:
            model = trinity.Load(resFile)
        if model is None:
            raise InvalidPreviewType('%s (%s) failed to load associated model' % (evetypes.GetName(self.typeID), self.typeID))
        if getattr(model, 'boosters', None) is not None:
            model.boosters = None
        if getattr(model, 'modelRotationCurve', None) is not None:
            model.modelRotationCurve = None
        if getattr(model, 'modelTranslationCurve', None) is not None:
            model.modelTranslationCurve = None
        SetupAnimations(model, self.typeID)
        model.FreezeHighDetailMesh()
        trinity.WaitForResourceLoads()
        sceneContainer.AddToScene(model)
        SetupSpaceCamera(sceneContainer, model)


class SofDnaSceneContext(SceneContext):

    def __init__(self, dna, dirt = None, scenePath = None):
        if scenePath is None:
            scenePath = gfxutils.GetResPathFromGraphicID(20413)
        self.dna = dna
        self.dirt = dirt
        self.scenePath = scenePath

    def __eq__(self, other):
        return isinstance(other, SofDnaSceneContext) and self.dna == other.dna and self.scenePath == other.scenePath and self.dirt == other.dirt

    def LoadScene(self, sceneContainer):
        sceneContainer.PrepareSpaceScene(scenePath=self.scenePath)
        spaceObjectFactory = sm.GetService('sofService').spaceObjectFactory
        model = spaceObjectFactory.BuildFromDNA(self.dna)
        if model is None:
            raise InvalidPreviewType('failed to load associated model: ' + self.dna)
        if self.dirt is not None:
            model.dirtLevel = self.dirt
        sceneContainer.AddToScene(model)
        SetupSpaceCamera(sceneContainer, model)


class T3ShipSceneContext(SceneContext):

    def __init__(self, typeID, subsystems = None, scenePath = None):
        if not IsModularShip(typeID):
            raise InvalidPreviewType('%s (%s) is not a tech 3 ship' % (evetypes.GetName(typeID), typeID))
        subsystems = subsystems or {}
        randomSubsystems = sm.GetService('t3ShipSvc').GetRandomSubsystems(typeID)
        subsystems = {k:subsystems.get(k, v) for k, v in randomSubsystems.iteritems()}
        if scenePath is None:
            raceID = evetypes.GetRaceID(typeID)
            scenePath = gfxutils.GetPreviewScenePath(raceID)
        self.typeID = typeID
        self.subsystems = subsystems
        self.scenePath = scenePath

    def __eq__(self, other):
        return isinstance(other, T3ShipSceneContext) and self.typeID == other.typeID and self.subsystems == other.subsystems and self.scenePath == other.scenePath

    def LoadScene(self, sceneContainer):
        sceneContainer.PrepareSpaceScene(scenePath=self.scenePath)
        t3ShipSvc = sm.GetService('t3ShipSvc')
        model = t3ShipSvc.GetTech3ShipFromDict(self.typeID, self.subsystems)
        SetupAnimations(model, self.typeID)
        sceneContainer.AddToScene(model)
        SetupSpaceCamera(sceneContainer, model)


class TurretSceneContext(SceneContext):

    def __init__(self, typeID, scenePath = None):
        if evetypes.GetGroupID(typeID) not in invconst.turretModuleGroups:
            raise InvalidPreviewType('%s (%s) is not a turret module' % (evetypes.GetName(typeID), typeID))
        self.typeID = typeID
        self.scenePath = scenePath or 'res:/dx9/scene/fitting/previewTurrets.red'

    def __eq__(self, other):
        return isinstance(other, TurretSceneContext) and self.typeID == other.typeID and self.scenePath == other.scenePath

    def LoadScene(self, sceneContainer):
        sceneContainer.PrepareSpaceScene(maxPitch=0.0, scenePath=self.scenePath)
        model = trinity.Load('res:/dx9/model/ship/IconPreview/PreviewTurretShip.red')
        turretSet = TurretSet.FitTurret(model, self.typeID, 1, evetypes.GetSofFactionNameOrNone(self.typeID), checkSettings=False)
        if turretSet is None:
            raise RuntimeError('Failed to load preview for %s (%s)' % (evetypes.GetName(self.typeID), self.typeID))
        boundingSphere = turretSet.turretSets[0].boundingSphere
        model.boundingSphereRadius = boundingSphere[3]
        model.boundingSphereCenter = boundingSphere[:3]
        if model.boundingSphereCenter[1] < 2.0:
            model.boundingSphereCenter = (boundingSphere[0], 2.0, boundingSphere[2])
        for turret in turretSet.turretSets:
            turret.bottomClipHeight = 0.0
            turret.FreezeHighDetailLOD()
            turret.ForceStateDeactive()
            turret.EnterStateIdle()

        sceneContainer.AddToScene(model)
        SetupSpaceCamera(sceneContainer, model)


def SetupSpaceCamera(sceneContainer, model):
    sceneContainer.verticalPanLimits = None
    alpha = sceneContainer.fieldOfView / 2.0
    radius = model.GetBoundingSphereRadius()
    maxZoom = max(radius * (1 / math.tan(alpha)) * 2, 1.0)
    minZoom = radius + sceneContainer.frontClip
    sceneContainer.SetMinMaxZoom(minZoom, maxZoom)


def SetupInteriourCamera(sceneContainer, boundingBox):
    p0, p1 = geo2.Vector(boundingBox[0]), geo2.Vector(boundingBox[1])
    center = 0.5 * (p1 - p0) + p0
    sceneContainer.cameraParent.parent = None
    sceneContainer.cameraParent.value = center
    sceneContainer.verticalPanLimits = (p0.y, p1.y)
    rad = max(geo2.Vec3Length(p0 - p1), 0.3)
    alpha = sceneContainer.fieldOfView * 1.5 / 2.0
    maxZoom = min(rad * (1 / math.tan(alpha)), 9.0)
    minZoom = rad + sceneContainer.frontClip
    sceneContainer.SetMinMaxZoom(minZoom, maxZoom)
    sceneContainer.zoom = 0.6
    sceneContainer.camera.maxPitch = 0.0


class CaptureDollMeshChanges(object):

    def __init__(self, doll):
        self.doll = doll

    def __enter__(self):
        self.before = self.doll.buildDataManager.GetMeshes(includeClothMeshes=True)
        return self

    def __exit__(self, type, value, traceback):
        self.after = self.doll.buildDataManager.GetMeshes(includeClothMeshes=True)


def MergeBoundingBoxes(a, b):
    merged = ((min(a[0][0], b[0][0]), min(a[0][1], b[0][1]), min(a[0][2], b[0][2])), (max(a[1][0], b[1][0]), max(a[1][1], b[1][1]), max(a[1][2], b[1][2])))
    return merged
