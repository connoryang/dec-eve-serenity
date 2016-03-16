#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\stationView.py
import sys
from eveSpaceObject import spaceobjaudio
import evetypes
import inventorycommon.typeHelpers
from inventorycommon.util import IsShipFittingFlag
from eve.common.script.net import eveMoniker
import log
import trinity
import util
import uthread
import blue
from eve.client.script.ui.services.viewStateSvc import View
from eve.client.script.ui.inflight import shipstance
from eveSpaceObject import spaceobjanimation
import evegraphics.utils as gfxutils

class StationView(View):
    __guid__ = 'viewstate.StationView'
    __notifyevents__ = ['OnDogmaItemChange',
     'ProcessActiveShipChanged',
     'OnActiveShipSkinChange',
     'OnDamageStateChanged']
    __dependencies__ = ['godma',
     'loading',
     'station',
     'invCache',
     't3ShipSvc',
     'sceneManager',
     'clientDogmaIM']
    __overlays__ = {'sidePanels'}

    def __init__(self):
        View.__init__(self)
        self.activeshipmodel = None

    def ShowShip(self, shipID, maintainZoomLevel = False):
        self.WaitForShip(shipID)
        hangarInv = self.invCache.GetInventory(const.containerHangar)
        hangarItems = hangarInv.List()
        for each in hangarItems:
            if each.itemID == shipID:
                self.activeShipItem = each
                try:
                    uthread.new(self.ShowActiveShip, maintainZoomLevel)
                except Exception as e:
                    log.LogException('Failed to show ship')
                    sys.exc_clear()

                break

    def HideView(self):
        interiorScene = sm.GetService('sceneManager').GetActiveScene()
        if interiorScene:
            for cs in interiorScene.curveSets:
                for binding in cs.bindings:
                    binding.copyValueCallable = None

                del cs.bindings[:]
                del cs.curves[:]

        View.HideView(self)

    def WaitForShip(self, shipID):
        maximumWait = 10000
        sleepUnit = 100
        iterations = maximumWait / sleepUnit
        while util.GetActiveShip() != shipID and iterations:
            iterations -= 1
            blue.pyos.synchro.SleepWallclock(sleepUnit)

        if util.GetActiveShip() != shipID:
            raise RuntimeError('Ship never came :(')
        self.LogInfo('Waited for ship for %d iterations.' % (maximumWait / sleepUnit - iterations))

    def SetupAnimation(self, model, shipItem):
        if model is None:
            return
        if not evetypes.Exists(shipItem.typeID):
            return
        animationStates = inventorycommon.typeHelpers.GetAnimationStates(shipItem.typeID)
        spaceobjanimation.LoadAnimationStates(animationStates, cfg.graphicStates, model, trinity)
        if model.animationSequencer is not None:
            model.animationSequencer.GoToState('normal')
            spaceobjanimation.SetShipAnimationStance(model, shipstance.get_ship_stance(shipItem.itemID, shipItem.typeID))

    def OnDogmaItemChange(self, item, change):
        if item.locationID == change.get(const.ixLocationID, None) and item.flagID == change.get(const.ixFlag):
            return
        activeShipID = util.GetActiveShip()
        if item.locationID == activeShipID and IsShipFittingFlag(item.flagID) and item.categoryID == const.categorySubSystem:
            self.ShowShip(activeShipID)

    def OnActiveShipSkinChange(self, itemID, skinID):
        if session.stationid2 is None:
            return
        if not hasattr(self, 'activeShipItem'):
            return
        if itemID == self.activeShipItem.itemID:
            self.ShowShip(self.activeShipItem.itemID, maintainZoomLevel=True)

    def OnDamageStateChanged(self, itemID):
        if self.activeShipItem.itemID == itemID:
            shieldState, armorState, hullState = self.GetDamageState(self.activeShipItem.itemID)
            self.activeshipmodel.SetImpactDamageState(shieldState, armorState, hullState, False)

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        if oldShipID != shipID:
            self.ShowShip(shipID)

    def SetupAnimationUpdaterAudio(self, newModel):
        if hasattr(newModel, 'animationUpdater'):
            newModel.animationUpdater.eventListener = self.generalAudioEntity

    def GetDamageState(self, itemID):
        shieldState, armorState, hullState = sm.GetService('clientDogmaIM').GetDogmaLocation().GetDamageStateEx(itemID)
        if isinstance(shieldState, tuple):
            shieldState = shieldState[0]
        return (shieldState, armorState, hullState)

    def SetupShipModel(self, newModel):
        itemID = self.activeShipItem.itemID
        dirtTimeStamp = eveMoniker.GetShipAccess().GetDirtTimestamp(itemID)
        dirtLevel = gfxutils.CalcDirtLevelFromAge(dirtTimeStamp)
        newModel.dirtLevel = dirtLevel
        killCounter = sm.RemoteSvc('shipKillCounter').GetItemKillCountPlayer(itemID)
        newModel.displayKillCounterValue = min(killCounter, 999)
        shieldState, armorState, hullState = self.GetDamageState(itemID)
        newModel.SetImpactDamageState(shieldState, armorState, hullState, True)

    def SetupGeneralAudioEntity(self, newModel):
        if newModel is not None and hasattr(newModel, 'observers'):
            self.generalAudioEntity = spaceobjaudio.SetupAudioEntity(newModel)
