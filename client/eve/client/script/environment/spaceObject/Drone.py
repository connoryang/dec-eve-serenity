#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\Drone.py
import blue
import trinity
import eve.client.script.environment.spaceObject.ship as ship
import evegraphics.settings as gfxsettings
import eveSpaceObject
import eve.client.script.environment.model.turretSet as turretSet

class Drone(ship.Ship):

    def LoadModel(self, fileName = None, loadedModel = None):
        droneModel = None
        if not self.IsDroneModelEnabled():
            droneModel = trinity.EveShip2()
            loc = trinity.EveLocator2()
            loc.name = 'locator_turret_1a'
            droneModel.locators.append(loc)
        ship.Ship.LoadModel(self, fileName, droneModel)

    def Assemble(self):
        if not self.IsDroneModelEnabled():
            return
        self.FitBoosters(alwaysOn=True, enableTrails=False)
        self.SetupAmbientAudio()
        if hasattr(self.model, 'ChainAnimationEx'):
            self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)

    def FitHardpoints(self, blocking = False):
        if self.fitted:
            return
        if self.model is None:
            self.LogWarn('FitHardpoints - No model')
            return
        self.fitted = True
        if not gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
            return
        groupID = self.typeData.get('groupID', None)
        raceName = self.typeData.get('sofRaceName', None)
        droneGroup = eveSpaceObject.droneGroupFromTypeGroup.get(groupID, None)
        if droneGroup is None:
            self.LogError('FitHardpoints - no gfx drone group for groupID ' + str(groupID))
            return
        turretGfxIDs = eveSpaceObject.droneTurretGfxID.get(droneGroup, None)
        if turretGfxIDs is None:
            self.LogError('FitHardpoints - no turret gfxID info for drone group ' + str(droneGroup))
            return
        turretGraphicID = turretGfxIDs[1]
        if turretGfxIDs[0] is not None:
            if raceName is not None:
                turretGraphicID = turretGfxIDs[0].get(raceName, turretGfxIDs[1])
        if turretGraphicID is not None:
            ts = turretSet.TurretSet.AddTurretToModel(self.model, turretGraphicID)
            if ts is not None and self.modules is not None:
                self.modules[self.id] = ts

    def Explode(self):
        if not self.IsDroneModelEnabled() or not gfxsettings.Get(gfxsettings.UI_EXPLOSION_EFFECTS_ENABLED):
            return False
        return ship.Ship.Explode(self)

    def IsDroneModelEnabled(self):
        groupID = self.typeData.get('groupID', None)
        droneGroup = eveSpaceObject.droneGroupFromTypeGroup.get(groupID, None)
        if droneGroup == eveSpaceObject.gfxDroneGroupNpc:
            return True
        return gfxsettings.Get(gfxsettings.UI_DRONE_MODELS_ENABLED)
