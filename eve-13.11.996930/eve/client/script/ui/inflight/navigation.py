#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\navigation.py
from itertools import chain
from carbonui.uianimations import animations
from eve.client.script.parklife import states
from eve.client.script.ui.camera.cameraUtil import IsNewCameraActive
from eve.client.script.ui.camera.dungeonEditorCameraController import DungeonEditorCameraController
from eve.client.script.ui.camera.farLookCameraController import FarLookCameraController
from eve.client.script.ui.camera.shipOrbitCameraController import ShipOrbitCameraController
from eve.client.script.ui.camera.shipPOVCameraController import ShipPOVCameraController
from eve.client.script.ui.camera.spaceCameraController import SpaceCameraController
from eve.client.script.ui.camera.tacticalCameraController import TacticalCameraController
from eve.client.script.ui.control.marqueeCont import MarqueeCont
from eve.client.script.ui.inflight.bracketsAndTargets.bracketVarious import GetOverlaps
from eve.client.script.ui.shared.infoPanels.infoPanelLocationInfo import ListSurroundingsBtn
from eve.client.script.ui.tooltips.tooltipHandler import TOOLTIP_SETTINGS_BRACKET, TOOLTIP_DELAY_BRACKET
import evecamera
from sensorsuite.overlay.brackets import SensorSuiteBracket
from spacecomponents.client.components import deploy
from spacecomponents.common.helper import HasDeployComponent
import uiprimitives
import uiutil
import uicls
import carbonui.const as uiconst
from eve.client.script.ui.inflight.drone import DropDronesInSpace
from eve.client.script.ui.inflight.bracketsAndTargets.inSpaceBracketTooltip import PersistentInSpaceBracketTooltip
import uthread

class InflightLayer(uicls.LayerCore):
    __guid__ = 'uicls.InflightLayer'
    __notifyevents__ = ['OnActiveCameraChanged', 'OnRadialMenuExpanded']

    def ApplyAttributes(self, attributes):
        uicls.LayerCore.ApplyAttributes(self, attributes)
        self.locked = 0
        self.sr.tcursor = None
        self.hoverbracket = None
        self.sr.spacemenu = None
        self.marqueeCont = None
        self.locks = {}
        self.cameraController = None
        self.sr.tcursor = uiprimitives.Container(name='targetingcursor', parent=self, align=uiconst.ABSOLUTE, width=1, height=1, state=uiconst.UI_HIDDEN)
        uiprimitives.Line(parent=self.sr.tcursor, align=uiconst.RELATIVE, left=10, width=3000, height=1)
        uiprimitives.Line(parent=self.sr.tcursor, align=uiconst.TOPRIGHT, left=10, width=3000, height=1)
        uiprimitives.Line(parent=self.sr.tcursor, align=uiconst.RELATIVE, top=10, width=1, height=3000)
        uiprimitives.Line(parent=self.sr.tcursor, align=uiconst.BOTTOMLEFT, top=10, width=1, height=3000)

    def OnOpenView(self):
        camera = sm.GetService('sceneManager').GetActiveCamera()
        if camera:
            self.OnActiveCameraChanged(camera.cameraID)

    def OnActiveCameraChanged(self, cameraID):
        if cameraID == evecamera.CAM_SPACE_PRIMARY:
            self.cameraController = SpaceCameraController()
        elif cameraID == evecamera.CAM_SHIPORBIT:
            self.cameraController = ShipOrbitCameraController()
        elif cameraID == evecamera.CAM_TACTICAL:
            self.cameraController = TacticalCameraController()
        elif cameraID == evecamera.CAM_SHIPPOV:
            self.cameraController = ShipPOVCameraController()
        elif cameraID == evecamera.CAM_FARLOOK:
            self.cameraController = FarLookCameraController()
        elif cameraID == evecamera.CAM_DUNGEONEDIT:
            self.cameraController = DungeonEditorCameraController()
        else:
            self.cameraController = None

    def GetSpaceMenu(self):
        if self.sr.spacemenu:
            if self.sr.spacemenu.solarsystemid == eve.session.solarsystemid2:
                return self.sr.spacemenu
            m = self.sr.spacemenu
            self.sr.spacemenu = None
            m.Close()
        solarsystemitems = sm.GetService('map').GetSolarsystemItems(session.solarsystemid2)
        listbtn = ListSurroundingsBtn(name='gimp', parent=self, state=uiconst.UI_HIDDEN, pos=(0, 0, 0, 0))
        listbtn.sr.mapitems = solarsystemitems
        listbtn.sr.groupByType = 1
        listbtn.filterCurrent = 1
        listbtn.solarsystemid = eve.session.solarsystemid2
        self.sr.spacemenu = listbtn
        return self.sr.spacemenu

    def _OnClose(self):
        uiprimitives.Container._OnClose(self)
        if not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN

    def PrepareTooltipLoad(self, bracket):
        if uicore.uilib.leftbtn or uicore.uilib.rightbtn:
            return None
        currentPos = (uicore.uilib.x, uicore.uilib.y)
        lastPos = getattr(self, 'lastLoadPos', (None, None))
        if lastPos == currentPos:
            return None
        self.lastLoadPos = currentPos
        self.tooltipBracket = bracket
        currentTooltip = uicore.uilib.tooltipHandler.GetPersistentTooltipByOwner(self)
        if currentTooltip and not (currentTooltip.destroyed or currentTooltip.beingDestroyed):
            if currentTooltip.IsOverlapBracket(bracket):
                return None
            currentTooltip.Close()
        isFloating = bracket.IsFloating()
        overlaps, boundingBox = GetOverlaps(bracket, useMousePosition=isinstance(bracket, SensorSuiteBracket), customBracketParent=uicore.layer.bracket)
        overlapSites = sm.GetService('sensorSuite').GetOverlappingSites()
        if isFloating and len(overlaps) + len(overlapSites) == 1:
            return None
        overlapSites.sort(key=lambda x: x.data.GetSortKey())
        self.tooltipPositionRect = bracket.GetAbsolute()
        ro = bracket.renderObject
        self.bracketPosition = (ro.displayX,
         ro.displayY,
         ro.displayWidth,
         ro.displayHeight)
        for bracket in chain(overlaps, overlapSites):
            bracket.opacity = 2.0

        for layer in (uicore.layer.inflight, uicore.layer.sensorSuite):
            animations.FadeTo(layer, startVal=layer.opacity, endVal=0.5, duration=0.5)

        uicore.uilib.tooltipHandler.LoadPersistentTooltip(self, loadArguments=(bracket,
         overlaps,
         boundingBox,
         overlapSites), customTooltipClass=PersistentInSpaceBracketTooltip, customPositionRect=boundingBox)

    def OnRadialMenuExpanded(self, *args):
        self.StopMarqueeSelection()

    def GetTooltipDelay(self):
        return settings.user.ui.Get(TOOLTIP_SETTINGS_BRACKET, TOOLTIP_DELAY_BRACKET)

    def GetTooltipPosition(self, *args, **kwds):
        return self.tooltipPositionRect

    def GetTooltipPointer(self):
        tooltipPanel = uicore.uilib.tooltipHandler.GetPersistentTooltipByOwner(self)
        if not tooltipPanel:
            return
        x, y, width, height = self.bracketPosition
        bracketLayerWidth = uicore.layer.bracket.displayWidth
        bracketLayerHeight = uicore.layer.bracket.displayHeight
        width = uicore.ReverseScaleDpi(width)
        height = uicore.ReverseScaleDpi(height)
        overlapAmount = len(tooltipPanel.overlaps)
        isCompact = tooltipPanel.isCompact
        if x <= 0:
            if isCompact and overlapAmount == 1:
                return uiconst.POINT_LEFT_2
            else:
                return uiconst.POINT_LEFT_3
        elif x + width >= bracketLayerWidth:
            if isCompact and overlapAmount == 1:
                return uiconst.POINT_RIGHT_2
            else:
                return uiconst.POINT_RIGHT_3
        elif y <= 0:
            if isCompact:
                return uiconst.POINT_TOP_2
            else:
                return uiconst.POINT_TOP_1
        elif y + height >= bracketLayerHeight:
            if isCompact:
                return uiconst.POINT_BOTTOM_2
            else:
                return uiconst.POINT_BOTTOM_1
        if isCompact:
            return uiconst.POINT_BOTTOM_2
        else:
            return uiconst.POINT_BOTTOM_1

    def GetTooltipPositionFallbacks(self):
        tooltipPanel = uicore.uilib.tooltipHandler.GetPersistentTooltipByOwner(self)
        if tooltipPanel:
            isCompact = tooltipPanel.isCompact
        else:
            isCompact = False
        if isCompact:
            return [uiconst.POINT_TOP_2,
             uiconst.POINT_TOPLEFT,
             uiconst.POINT_TOPRIGHT,
             uiconst.POINT_BOTTOMLEFT,
             uiconst.POINT_BOTTOMRIGHT]
        else:
            return [uiconst.POINT_TOP_1,
             uiconst.POINT_TOPLEFT,
             uiconst.POINT_TOPRIGHT,
             uiconst.POINT_BOTTOMLEFT,
             uiconst.POINT_BOTTOMRIGHT]

    def ShowTargetingCursor(self):
        self.sr.tcursor.left = uicore.uilib.x - 1
        self.sr.tcursor.top = uicore.uilib.y
        self.sr.tcursor.state = uiconst.UI_DISABLED

    def HideTargetingCursor(self):
        self.sr.tcursor.state = uiconst.UI_HIDDEN

    def GetMenu(self, itemID = None):
        if self.locked:
            return []
        m = []
        if not itemID and self.cameraController:
            picktype, pickobject = self.cameraController.GetPick()
            if pickobject and hasattr(pickobject, 'translationCurve') and hasattr(pickobject.translationCurve, 'id'):
                itemID = pickobject.translationCurve.id
            if pickobject:
                if sm.GetService('posAnchor').IsActive():
                    if pickobject.name[:6].lower() == 'cursor':
                        m.append((uiutil.MenuLabel('UI/Inflight/POS/AnchorHere'), sm.GetService('posAnchor').SubmitAnchorPosSelect, ()))
                        m.append(None)
                        m.append((uiutil.MenuLabel('UI/Inflight/POS/CancelAnchoring'), sm.GetService('posAnchor').CancelAchorPosSelect, ()))
                        return m
        if not itemID:
            mm = []
            if not (eve.rookieState and eve.rookieState < 32):
                mm = self.GetSpaceMenu().GetMenu()
            m += [(uiutil.MenuLabel('UI/Inflight/ResetCamera'), sm.GetService('sceneManager').GetActiveCamera().ResetCamera, ())]
            m += [None, [uiutil.MenuLabel('UI/Inflight/ShowSystemInMapBrowser'), sm.GetService('menu').ShowInMapBrowser, (eve.session.solarsystemid2,)], None]
            return m + mm
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return m
        slimItem = bp.GetInvItem(itemID)
        if slimItem is None:
            return m
        pickid = slimItem.itemID
        groupID = slimItem.groupID
        categoryID = slimItem.categoryID
        if eve.session.shipid is None:
            return m
        m += sm.GetService('menu').CelestialMenu(slimItem.itemID, slimItem=slimItem)
        return m

    def ShowRadialMenuIndicator(self, slimItem, *args):
        if not slimItem:
            return
        bracket = sm.GetService('bracket').GetBracket(slimItem.itemID)
        if bracket is None:
            return
        bracket.ShowRadialMenuIndicator()

    def HideRadialMenuIndicator(self, slimItem, *args):
        if slimItem is None:
            return
        bracket = sm.GetService('bracket').GetBracket(slimItem.itemID)
        if bracket is None:
            return
        bracket.HideRadialMenuIndicator()

    def OnDropData(self, dragObj, nodes):
        if dragObj.__guid__ in ('listentry.DroneMainGroup', 'listentry.DroneSubGroup', 'listentry.DroneEntry'):
            DropDronesInSpace(dragObj, nodes)
        elif dragObj.__guid__ in ('xtriui.InvItem', 'listentry.InvItem'):
            deployItems = []
            for node in nodes:
                if node.item.ownerID != session.charid:
                    return
                if node.item.locationID != session.shipid:
                    return
                if HasDeployComponent(node.item.typeID):
                    deployItems.append(node.item)

            if deployItems:
                deploy.DeployAction(deployItems)

    def ResetAchievementVariables(self):
        self.cameraController.ResetAchievementVariables()

    def OnMouseDown(self, *args):
        if not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_DISABLED
        if not self.cameraController:
            return
        pickObject = self.cameraController.OnMouseDown(*args)
        self.TryExpandActionMenu(pickObject)
        uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
        if IsNewCameraActive():
            if uicore.uilib.leftbtn and uicore.cmd.IsSomeCombatCommandLoaded():
                self.StopMarqueeSelection()
                self.marqueeCont = MarqueeCont(parent=self)

    def OnMouseUp(self, *args):
        if not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN
        if not uicore.uilib.leftbtn and not uicore.uilib.rightbtn:
            uicore.uilib.UnclipCursor()
            if uicore.uilib.GetCapture() == self:
                uicore.uilib.ReleaseCapture()
        elif uicore.uilib.leftbtn or uicore.uilib.rightbtn:
            uicore.uilib.SetCapture(self)
        if not self.cameraController:
            return
        marqueeActive = self.IsMarqueeActivated()
        if self.marqueeCont:
            selected = self.GetMarqueeSelection()
            if selected and marqueeActive:
                itemID = selected[0]
                sm.GetService('state').SetState(itemID, states.selected, True)
                uicore.cmd.ExecuteCombatCommand(itemID, uiconst.UI_CLICK)
        if not marqueeActive:
            self.cameraController.OnMouseUp(*args)
        else:
            self.cameraController.mouseDownPos = None

    def IsMarqueeActivated(self):
        if not self.cameraController:
            return False
        return self.cameraController.GetMouseTravel() >= 5 and self.marqueeCont and IsNewCameraActive()

    def GetMarqueeSelection(self):
        try:
            ret = []
            for bracket in sm.GetService('bracket').brackets.values():
                if self.IsMarqueeSelected(bracket):
                    ret.append(bracket)

            if not ret and self.cameraController:
                x, y = self.marqueeCont.GetCenterPoint()
                pickType, pickObj = self.cameraController.GetPick(x, y)
                if pickObj:
                    return [int(pickObj.name)]
            return [ bracket.itemID for bracket in ret ]
        finally:
            self.marqueeCont.Close()
            self.marqueeCont = None

    def IsMarqueeSelected(self, bracket):
        if not bracket.display:
            return False
        try:
            x = bracket.left + bracket.width / 2
            y = bracket.top + bracket.height / 2
        except:
            print bracket
            return

        if x < self.marqueeCont.left:
            return False
        elif x > self.marqueeCont.left + self.marqueeCont.width:
            return False
        elif y < self.marqueeCont.top:
            return False
        elif y > self.marqueeCont.top + self.marqueeCont.height:
            return False
        else:
            return True

    def OnDblClick(self, *args):
        if self.cameraController:
            self.cameraController.OnDblClick(*args)

    def OnMouseWheel(self, *args):
        if self.cameraController:
            self.cameraController.OnMouseWheel(*args)

    def OnMouseEnter(self, *args):
        if self.destroyed or self.parent is None or self.parent.destroyed:
            return
        if not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN
        if sm.IsServiceRunning('tactical'):
            uthread.new(sm.GetService('tactical').ResetTargetingRanges)
        uiutil.SetOrder(self, -1)

    def OnMouseMove(self, *args):
        if uicore.IsDragging():
            return
        self.sr.hint = ''
        self.sr.tcursor.left = uicore.uilib.x - 1
        self.sr.tcursor.top = uicore.uilib.y
        if self.cameraController:
            if self.cameraController.CheckMoveSceneCursor():
                self.StopMarqueeSelection()
            elif not self.marqueeCont:
                self.cameraController.OnMouseMove(*args)

    def StopMarqueeSelection(self):
        if self.marqueeCont:
            self.marqueeCont.Close()
            self.marqueeCont = None

    def TryExpandActionMenu(self, pickObj):
        if pickObj and hasattr(pickObj, 'translationCurve') and hasattr(pickObj.translationCurve, 'id'):
            uthread.new(sm.GetService('radialmenu').TryExpandActionMenu, pickObj.translationCurve.id, self)

    def ZoomBy(self, amount):
        if IsNewCameraActive():
            camera = self.cameraController.GetCamera()
            camera.Zoom(0.001 * amount)
        else:
            self.cameraController.ZoomBy(amount)
