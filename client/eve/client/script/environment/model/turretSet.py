#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\model\turretSet.py
import remotefilecache
import inventorycommon.typeHelpers
import trinity
import blue
import log
import audio2
import util
import evetypes
import evegraphics.settings as gfxsettings
from stacklesslib.util import block_trap

class TurretSet:
    __guid__ = 'turretSet.TurretSet'
    turretsEnabled = [False]

    def Initialize(self, graphics, locator, overrideBeamGraphicID = None, count = 1):
        self.inWarp = False
        self.isShooting = False
        self.targetsAvailable = False
        self.online = True
        self.targetID = None
        self.turretTypeID = 0
        self.turretGroupID = 0
        self.turretSets = []
        if not hasattr(graphics, 'graphicFile'):
            log.LogError('No turret redfile defined for: ' + str(graphics))
            return self.turretSets
        turretPath = graphics.graphicFile
        for i in range(count):
            tSet = trinity.Load(turretPath)
            if tSet is None:
                continue
            if len(tSet.locatorName) == 0:
                tSet.locatorName = 'locator_turret_'
            elif tSet.locatorName[-1].isdigit():
                tSet.locatorName = tSet.locatorName[:-1]
            if locator < 0:
                tSet.slotNumber = i + 1
            else:
                tSet.slotNumber = locator
            self.turretSets.append(tSet)

        for turretSet in self.turretSets:
            turretFxPath = turretSet.firingEffectResPath
            try:
                effect = blue.recycler.RecycleOrLoad(turretFxPath)
            except RuntimeError:
                log.LogError('Could not load firing effect ' + turretFxPath + ' for turret: ' + turretPath)
                effect = None

            turretSet.firingEffect = effect

        return self.turretSets

    def GetTurretSet(self, index = 0):
        return self.turretSets[index]

    def GetTurretSets(self):
        return self.turretSets

    def Release(self):
        pass

    def SetTargetsAvailable(self, available):
        if self.targetsAvailable and not available:
            self.Rest()
        self.targetsAvailable = available

    def SetTarget(self, shipID, targetID):
        self.targetID = targetID
        targetBall = sm.GetService('michelle').GetBall(targetID)
        if targetBall is not None:
            if hasattr(targetBall, 'model'):
                for turretSet in self.turretSets:
                    turretSet.targetObject = targetBall.model

    def SetAmmoColorByTypeID(self, ammoTypeID):
        gfx = inventorycommon.typeHelpers.GetGraphic(ammoTypeID)
        if hasattr(gfx, 'ammoColor'):
            color = tuple(gfx.ammoColor)
            self.SetAmmoColor(color)

    def SetAmmoColor(self, color):
        if color is None:
            return
        for turretSet in self.turretSets:
            if turretSet.firingEffect is not None:
                for curve in turretSet.firingEffect.Find('trinity.TriColorCurve'):
                    if curve.name == 'Ammo':
                        curve.value = color

    def IsShooting(self):
        return self.isShooting

    def StartShooting(self, ammoGFXid = None):
        if self.inWarp:
            return
        for turretSet in self.turretSets:
            turretSet.EnterStateFiring()

        self.isShooting = True

    def StopShooting(self):
        for turretSet in self.turretSets:
            if self.inWarp:
                turretSet.EnterStateDeactive()
            elif self.targetsAvailable:
                turretSet.EnterStateTargeting()
            else:
                turretSet.EnterStateIdle()

        self.isShooting = False

    def Rest(self):
        if self.inWarp or not self.online:
            return
        for turretSet in self.turretSets:
            turretSet.EnterStateIdle()

    def Offline(self):
        if self.online == False:
            return
        self.online = False
        for turretSet in self.turretSets:
            turretSet.isOnline = False
            turretSet.EnterStateDeactive()

    def Online(self):
        if self.online:
            return
        self.online = True
        for turretSet in self.turretSets:
            turretSet.isOnline = True
            turretSet.EnterStateIdle()

    def Reload(self):
        for turretSet in self.turretSets:
            turretSet.EnterStateReloading()

    def EnterWarp(self):
        self.inWarp = True
        for turretSet in self.turretSets:
            turretSet.EnterStateDeactive()

    def ExitWarp(self):
        self.inWarp = False
        if self.online:
            for turretSet in self.turretSets:
                turretSet.EnterStateIdle()

    def TakeAim(self, targetID):
        if self.targetID != targetID:
            log.LogWarn('target ids mismatch!')
            return
        if not self.online:
            return
        for turretSet in self.turretSets:
            turretSet.EnterStateTargeting()

    @staticmethod
    def AddTurretToModel(model, turretGraphicsID, turretFaction = None, locatorID = 1, count = 1):
        if model.__bluetype__ not in ('trinity.EveShip2', 'trinity.EveMobile'):
            log.LogError('Wrong object is trying to get turret attached due to wrong authored content! model:' + model.name + ' bluetype:' + model.__bluetype__)
            return
        graphics = cfg.graphics.GetIfExists(turretGraphicsID)
        newTurretSet = TurretSet()
        eveTurretSets = newTurretSet.Initialize(graphics, locatorID, None, count=count)
        spaceObjectFactory = sm.GetService('sofService').spaceObjectFactory
        for tSet in eveTurretSets:
            if model.dna:
                spaceObjectFactory.SetupTurretMaterialFromDNA(tSet, model.dna)
            elif turretFaction is not None:
                spaceObjectFactory.SetupTurretMaterialFromFaction(tSet, turretFaction)
            model.turretSets.append(tSet)

        return newTurretSet

    @staticmethod
    def FitTurret(model, turretTypeID, locatorID, turretFaction = None, count = 1, online = True, checkSettings = True):
        if not evetypes.Exists(turretTypeID):
            return
        if checkSettings and not gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
            return
        groupID = evetypes.GetGroupID(turretTypeID)
        if model is None:
            log.LogError('FitTurret() called with NoneType, so there is no model to fit the turret to!')
            return
        if groupID not in const.turretModuleGroups:
            return
        newTurretSet = None
        graphicID = evetypes.GetGraphicID(turretTypeID)
        if graphicID is not None:
            newTurretSet = TurretSet.AddTurretToModel(model, graphicID, turretFaction, locatorID, count)
            if newTurretSet is None:
                return
            if not online:
                newTurretSet.Offline()
            newTurretSet.turretTypeID = turretTypeID
            newTurretSet.turretGroupID = groupID
        return newTurretSet

    @staticmethod
    def PrefetchGraphicsForModules(modules):
        prefetch_set = set()
        for moduleID, typeID, slot, isOnline in modules:
            if evetypes.Exists(typeID) and evetypes.GetGroupID(typeID) not in const.turretModuleGroups:
                continue
            turretPath = inventorycommon.typeHelpers.GetGraphicFile(typeID)
            if turretPath:
                prefetch_set.add(turretPath)

        remotefilecache.prefetch_files(prefetch_set)

    @staticmethod
    def FitTurrets(shipID, model, shipFaction = None):
        if not gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
            return {}
        turretsFitted = {}
        modules = []
        if shipID == util.GetActiveShip():
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            if not dogmaLocation.IsItemLoaded(shipID):
                return {}
            dogmaLocation.LoadItem(shipID)
            ship = dogmaLocation.GetDogmaItem(shipID)
            modules = []
            for module in ship.GetFittedItems().itervalues():
                if module.groupID in const.turretModuleGroups:
                    modules.append([module.itemID,
                     module.typeID,
                     module.flagID - const.flagHiSlot0 + 1,
                     module.IsOnline()])

        else:
            slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(shipID)
            if slimItem is not None:
                moduleItems = slimItem.modules
                modules = [ [module[0],
                 module[1],
                 module[2] - const.flagHiSlot0 + 1,
                 True] for module in moduleItems ]
        TurretSet.PrefetchGraphicsForModules(modules)
        with block_trap():
            del model.turretSets[:]
            modules = sorted(modules, key=lambda x: x[2])
            locatorCounter = 1
            for moduleID, typeID, slot, isOnline in modules:
                slot = slot or locatorCounter
                ts = TurretSet.FitTurret(model, typeID, slot, shipFaction, online=isOnline)
                if ts is not None:
                    turretsFitted[moduleID] = ts
                    locatorCounter += 1

            return turretsFitted
