#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\shipSceneContainer.py
import math
from eve.client.script.ui.control.scenecontainer import SceneContainer
from eve.client.script.ui.inflight.shipstance import get_ship_stance
from eveSpaceObject import spaceobjanimation
import evetypes
from iconrendering.photo import _ApplyIsisEffect
import log
import turretSet
import trinity
import uthread
from uthread2.callthrottlers import CallCombiner
import telemetry
import inventorycommon.typeHelpers

class ShipSceneContainer(SceneContainer):
    __notifyevents__ = ['ProcessFittingWindowStartMinimize', 'ProcessFittingWindowEndMinimize']

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        SceneContainer.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.controller.on_new_itemID.connect(self.ReloadShipModel)
        self.controller.on_subsystem_fitted.connect(self.ReloadShipModel)
        self.controller.on_hardpoints_fitted.connect(self.UpdateHardpoints)
        self.controller.on_module_online_state.connect(self.ProcessOnlineStateChange)
        self.controller.on_skin_material_changed.connect(self.OnSkinChanged)
        self.controller.on_stance_activated.connect(self.OnStanceActive)
        self.CreateActiveShipModelThrottled = CallCombiner(self.CreateActiveShipModel, 1.0)
        sm.RegisterNotify(self)
        uthread.new(self.ReloadShipModel)

    def OnSkinChanged(self):
        self.ReloadShipModel(animate=False)

    @telemetry.ZONE_METHOD
    def ReloadShipModel(self, throttle = False, animate = True):
        if self.destroyed:
            return
        with self._reloadLock:
            if throttle:
                newModel = self.CreateActiveShipModelThrottled()
            else:
                newModel = self.CreateActiveShipModel()
            if not newModel:
                return
            newModel.FreezeHighDetailMesh()
            trinity.WaitForResourceLoads()
            self.AddToScene(newModel)
            if animate:
                self.AnimEntry()
            if isinstance(self.controller.dogmaLocation.GetCurrentShipID(), basestring):
                _ApplyIsisEffect(newModel, isSkinned=False)
                grid = trinity.Load('res:/dx9/model/UI/ScanGrid.red')
                grid.scaling = (4, 4, 4)
                self.scene.objects.append(grid)
            camera = self.camera
            rad = newModel.GetBoundingSphereRadius()
            minZoom = rad + camera.frontClip
            alpha = camera.fieldOfView / 2.0
            maxZoom = rad * (1 / math.tan(alpha)) * 2
            oldZoomDistance = self.minZoom + (self.maxZoom - self.minZoom) * self.zoom
            defaultZoom = minZoom / (maxZoom - minZoom)
            self.SetMinMaxZoom(minZoom, maxZoom)
            if animate or oldZoomDistance < minZoom or oldZoomDistance > maxZoom:
                self.zoom = defaultZoom
            shipTypeID = self.controller.GetTypeID()
            if self.controller.IsSimulated():
                stanceID = None
            else:
                stanceID = get_ship_stance(self.controller.GetItemID(), shipTypeID)
            animationStates = []
            if evetypes.Exists(shipTypeID):
                animationStates = inventorycommon.typeHelpers.GetAnimationStates(shipTypeID)
            spaceobjanimation.LoadAnimationStates(animationStates, cfg.graphicStates, newModel, trinity)
            if newModel.animationSequencer is not None:
                newModel.animationSequencer.GoToState('normal')
                spaceobjanimation.SetShipAnimationStance(newModel, stanceID)
            if not self.controller.IsSimulated():
                self.UpdateHardpoints(newModel)

    @telemetry.ZONE_METHOD
    def CreateActiveShipModel(self):
        newModel = self.controller.GetModel()
        if not newModel:
            return
        if hasattr(newModel, 'ChainAnimationEx'):
            newModel.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        newModel.display = 1
        newModel.name = str(self.controller.GetItemID())
        return newModel

    @telemetry.ZONE_METHOD
    def UpdateHardpoints(self, newModel = None):
        if newModel is None:
            newModel = self.GetSceneShip()
        if newModel is None:
            log.LogError('UpdateHardpoints - No model!')
            return
        factionName = None
        graphicInfo = cfg.graphics.GetIfExists(evetypes.GetGraphicID(self.controller.GetTypeID()))
        if graphicInfo is not None:
            factionName = getattr(graphicInfo, 'sofFactionName', None)
        turretSet.TurretSet.FitTurrets(self.controller.GetItemID(), newModel, factionName)

    @telemetry.ZONE_METHOD
    def GetSceneShip(self):
        for model in self.scene.objects:
            if getattr(model, 'name', None) == str(self.controller.GetItemID()):
                return model

    @telemetry.ZONE_METHOD
    def PlayDeploymentAnimation(self, slot, dogmaItem):
        sceneShip = self.GetSceneShip()
        if sceneShip is not None:
            for turret in sceneShip.turretSets:
                if turret.slotNumber != slot:
                    continue
                if dogmaItem.IsOnline():
                    turret.EnterStateIdle()
                else:
                    turret.EnterStateDeactive()
                    break

    def OnStanceActive(self, stanceID):
        spaceobjanimation.SetShipAnimationStance(self.GetSceneShip(), stanceID)

    def _OnClose(self, *args):
        sm.UnregisterNotify(self)
        SceneContainer._OnClose(self)

    def ProcessOnlineStateChange(self, dogmaItem):
        if self.destroyed:
            return
        slot = dogmaItem.flagID - const.flagHiSlot0 + 1
        if slot is not None:
            self.PlayDeploymentAnimation(slot, dogmaItem)

    def ProcessFittingWindowStartMinimize(self):
        self.Hide()

    def ProcessFittingWindowEndMinimize(self):
        self.Show()
