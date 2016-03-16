#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\fightersSvc.py
from appConst import defaultPadding
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_GML
import uicontrols
import uiprimitives
from carbonui.const import TOPLEFT
import geo2
from eve.client.script.ui.inflight.squadrons.shipFighterState import ShipFighterState
from eve.common.script.mgt import fighterConst
import evetypes
from fighters import ABILITY_SLOT_0, ABILITY_SLOT_1, ABILITY_SLOT_2
from inventorycommon.const import categoryFighter
from spacecomponents.client.components.behavior import EnableDebugging, DisableDebugging

class FighterDebugWindow(uicontrols.Window):
    default_windowID = 'FighterDebugWindow'
    default_width = 250
    default_height = 400
    default_caption = 'Fighter debug prototype'
    default_icon = '41_13'
    currentFighterID = None

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(0)
        self.SetMinSize([250, 400])
        self.MakeUnResizeable()
        mainCont = uiprimitives.Container(name='mainCont', parent=self.sr.main, pos=(defaultPadding,
         defaultPadding,
         defaultPadding,
         defaultPadding))
        uicontrols.Button(parent=mainCont, name='CreateFighter', label='Create Fighter', pos=(10, 10, 0, 0), func=self.OnCreateFighterButton, align=TOPLEFT)
        uicontrols.Button(parent=mainCont, name='DebugFighter', label='DBG', pos=(110, 10, 100, 0), fixedwidth=20, func=self.OnDebugFighterButton, align=TOPLEFT)
        uicontrols.Button(parent=mainCont, name='DestroyFighter', label='Destroy Fighter', pos=(140, 10, 0, 0), func=self.OnDestroyFighterButton, align=TOPLEFT)
        uicontrols.Label(text='Fighter ID', parent=mainCont, pos=(10, 40, 0, 0), align=TOPLEFT)
        self.fighterIDBox = uicontrols.SinglelineEdit(name='fighterID', parent=mainCont, pos=(80, 40, 160, 20), align=TOPLEFT, OnChange=self.OnFighterIDBoxChange)
        self.fighterIDBox.SetText(self._GetFighterID())
        uicontrols.Label(text='Target ID', parent=mainCont, pos=(10, 80, 0, 0), align=TOPLEFT)
        self.targetIDBox = uicontrols.SinglelineEdit(name='targetID', parent=mainCont, pos=(80, 80, 160, 20), align=TOPLEFT)
        self.targetIDBox.SetText(session.shipid)
        uicontrols.Button(parent=mainCont, name='OrbitTarget', label='Orbit Target', pos=(10, 110, 0, 0), fixedwidth=110, func=self.OnOrbitTargetButton)
        uicontrols.Button(parent=mainCont, name='OrbitMe', label='Orbit Me', pos=(130, 110, 0, 0), fixedwidth=110, func=self.OnOrbitMeButton)
        uicontrols.Button(parent=mainCont, name='StopMovement', label='Stop movement', pos=(10, 140, 0, 0), fixedwidth=110, func=self.OnMoveStopButton)
        uicontrols.Button(parent=mainCont, name='Kamikaze', label='Kamikaze', pos=(130, 140, 0, 0), fixedwidth=110, func=self.OnKamikazeButton)
        uicontrols.Label(text='x,y,z', parent=mainCont, pos=(10, 170, 0, 0), align=TOPLEFT)
        self.gotoPosBox = uicontrols.SinglelineEdit(name='gotoPos', parent=mainCont, pos=(40, 170, 190, 20), align=TOPLEFT)
        uicontrols.ButtonIcon(name='pickXYZ', parent=mainCont, pos=(230, 170, 16, 16), align=TOPLEFT, width=16, iconSize=16, texturePath='res:/UI/Texture/Icons/38_16_150.png', hint='Pick random position near target', func=self.OnPickXYZ)
        uicontrols.Button(parent=mainCont, name='GotoPoint', label='Goto this point', pos=(130, 190, 0, 0), fixedwidth=110, func=self.OnGotoPointButton)
        uicontrols.Button(parent=mainCont, name='ToggleMoveMode', label='Toggle Movement', pos=(10, 190, 0, 0), fixedwidth=110, func=self.OnToggleMoveButton)
        uicontrols.Label(text='Ability 0', parent=mainCont, pos=(10, 220, 0, 0), align=TOPLEFT)
        uicontrols.Button(parent=mainCont, name='ActivateAbilityOnTarget', label='Activate (target)', pos=(10, 240, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnTarget, args=(ABILITY_SLOT_0,))
        uicontrols.Button(parent=mainCont, name='ActivateAbilityOnSelf', label='Activate (self)', pos=(95, 240, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnSelf, args=(ABILITY_SLOT_0,))
        uicontrols.Button(parent=mainCont, name='DeactivateAbility', label='Deactivate', pos=(180, 240, 0, 0), fixedwidth=60, func=self.OnDeactivateAbility, args=(ABILITY_SLOT_0,))
        uicontrols.Label(text='Ability 1', parent=mainCont, pos=(10, 270, 0, 0), align=TOPLEFT)
        uicontrols.Button(parent=mainCont, name='ActivateAbilityOnTarget', label='Activate (target)', pos=(10, 290, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnTarget, args=(ABILITY_SLOT_1,))
        uicontrols.Button(parent=mainCont, name='ActivateAbilityOnSelf', label='Activate (self)', pos=(95, 290, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnSelf, args=(ABILITY_SLOT_1,))
        uicontrols.Button(parent=mainCont, name='DeactivateAbility', label='Deactivate', pos=(180, 290, 0, 0), fixedwidth=60, func=self.OnDeactivateAbility, args=(ABILITY_SLOT_1,))
        uicontrols.Label(text='Ability 2', parent=mainCont, pos=(10, 320, 0, 0), align=TOPLEFT)
        uicontrols.Button(parent=mainCont, name='ActivateAbilityOnTarget', label='Activate (target)', pos=(10, 340, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnTarget, args=(ABILITY_SLOT_2,))
        uicontrols.Button(parent=mainCont, name='ActivateAbilityOnSelf', label='Activate (self)', pos=(95, 340, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnSelf, args=(ABILITY_SLOT_2,))
        uicontrols.Button(parent=mainCont, name='DeactivateAbility', label='Deactivate', pos=(180, 340, 0, 0), fixedwidth=60, func=self.OnDeactivateAbility, args=(ABILITY_SLOT_2,))

    def _GetFighterID(self):
        return self.currentFighterID

    def _GetTargetID(self):
        try:
            return int(self.targetIDBox.text.strip())
        except ValueError:
            return None

    def OnFighterIDBoxChange(self, *args):
        try:
            self.currentFighterID = int(self.fighterIDBox.text.strip())
        except ValueError:
            pass

    def OnCreateFighterButton(self, *args):
        self._OnCreateFighterButton(*args)

    def _OnCreateFighterButton(self, *args):
        fighterTypeID = 37599
        self.currentFighterID = sm.GetService('fighters').SpawnTestFighter(fighterTypeID)
        self.fighterIDBox.SetText(self.currentFighterID)

    def OnDestroyFighterButton(self, *args):
        self._OnDestroyFighterButton(*args)

    def _OnDestroyFighterButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            DisableDebugging(fighterID)
            sm.GetService('fighters').DestroyTestFighter(fighterID)
            self.fighterIDBox.SetText('')
            self.currentFighterID = None

    def OnDebugFighterButton(self, *args):
        self._OnDebugFighterButton(*args)

    def _OnDebugFighterButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            EnableDebugging(fighterID)

    def OnPickXYZ(self, *args):
        self._OnPickXYZ(*args)

    def _OnPickXYZ(self, *args):
        michelle = sm.GetService('michelle')
        targetID = self._GetTargetID() or session.shipid
        ball = michelle.GetBall(targetID)
        if ball:
            import random
            shipPos = geo2.VectorD(ball.x, ball.y, ball.z)
            offsetRange = ball.radius + 2000
            offset = geo2.Vector(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
            targetPos = geo2.Vec3AddD(shipPos, geo2.Vec3Scale(geo2.Vec3Normalize(offset), offsetRange))
            self.gotoPosBox.SetText('%.0f, %.0f, %0.f' % (targetPos[0], targetPos[1], targetPos[2]))

    def OnGotoPointButton(self, *args):
        self._OnGotoPointButton(*args)

    def _OnGotoPointButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            point = geo2.VectorD([ float(v.strip()) for v in self.gotoPosBox.text.strip().split(',') ])
            sm.GetService('fighters').CmdGotoPoint(fighterID, list(point))

    def OnToggleMoveButton(self, *args):
        self._OnOnToggleMoveButton(*args)

    def _OnOnToggleMoveButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            uicore.layer.inflight.positionalControl.StartFighterMoveCommand([fighterID])

    def OnOrbitTargetButton(self, *args):
        self._OnOrbitTargetButton(*args)

    def _OnOrbitTargetButton(self, *args):
        fighterID = self._GetFighterID()
        targetID = self._GetTargetID()
        if fighterID is not None and targetID is not None:
            sm.GetService('fighters').CmdMovementOrbit(fighterID, targetID)

    def OnOrbitMeButton(self, *args):
        self._OnOrbitMeButton(*args)

    def _OnOrbitMeButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').CmdMovementOrbit(fighterID, session.shipid)

    def OnMoveStopButton(self, *args):
        self._OnMoveStopButton(*args)

    def _OnMoveStopButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').CmdMovementStop(fighterID)

    def OnKamikazeButton(self, *args):
        self._OnKamikazeButton(*args)

    def _OnKamikazeButton(self, *args):
        fighterID = self._GetFighterID()
        targetID = self._GetTargetID()
        if fighterID is not None:
            sm.GetService('fighters').CmdKamikaze(fighterID, targetID)

    def OnActivateAbilityOnTarget(self, abilitySlotID):
        self._OnActivateAbilityOnTarget(abilitySlotID)

    def _OnActivateAbilityOnTarget(self, abilitySlotID):
        fighterID = self._GetFighterID()
        targetID = self._GetTargetID()
        if fighterID is not None and targetID is not None:
            sm.GetService('fighters').ActivateAbilitySlot(fighterID, abilitySlotID, targetID)

    def OnActivateAbilityOnSelf(self, abilitySlotID):
        self._OnActivateAbilityOnSelf(abilitySlotID)

    def _OnActivateAbilityOnSelf(self, abilitySlotID):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').ActivateAbilitySlot(fighterID, abilitySlotID)

    def OnDeactivateAbility(self, abilitySlotID):
        self._OnDeactivateAbility(abilitySlotID)

    def _OnDeactivateAbility(self, abilitySlotID):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').DeactivateAbilitySlot(fighterID, abilitySlotID)


class FightersSvc(Service):
    __dependencies__ = ['michelle']
    __guid__ = 'svc.fighters'
    __servicename__ = 'fighters'
    __displayname__ = 'Fighters service'
    __neocommenuitem__ = (('Fighter debug [prototype]', None), 'ShowDebugWindow', ROLE_GML)
    shipFighterState = None

    def Run(self, memStream = None):
        self.LogInfo('Starting fighters service')
        self.shipFighterState = ShipFighterState(self)

    def ShowDebugWindow(self):
        wnd = FighterDebugWindow.GetIfOpen()
        if wnd:
            wnd.Maximize()
        else:
            FighterDebugWindow.Open()

    def FightersMenu(self):

        def SpawnFighterInBay(fighterTypeID):
            self.LogInfo('Spawning fighter via /fit', fighterTypeID, evetypes.GetEnglishName(fighterTypeID))
            sm.RemoteSvc('slash').SlashCmd('/fit me %d %d' % (fighterTypeID, 1))

        groupMenu = []
        for fighterGroupID in evetypes.GetGroupIDsByCategory(categoryFighter):
            groupName = evetypes.GetGroupNameByGroup(fighterGroupID)
            typeMenu = []
            for fighterTypeID in evetypes.GetTypeIDsByGroup(fighterGroupID):
                fighterName = evetypes.GetEnglishName(fighterTypeID)
                typeMenu.append((fighterName, SpawnFighterInBay, (fighterTypeID,)))

            typeMenu.sort()
            groupMenu.append((groupName, typeMenu))

        groupMenu.sort()
        return [('NEW FIGHTERS', groupMenu)]

    def CmdMovementOrbit(self, fighterID, targetID):
        self._ExecuteFighterCommand(fighterConst.COMMAND_ORBIT, fighterID, targetID, 2000)

    def CmdMovementStop(self, fighterID):
        self._ExecuteFighterCommand(fighterConst.COMMAND_STOP, fighterID)

    def CmdKamikaze(self, fighterID, targetID):
        self._ExecuteFighterCommand(fighterConst.COMMAND_KAMIKAZE, fighterID, targetID)

    def CmdGotoPoint(self, fighterID, point):
        self._ExecuteFighterCommand(fighterConst.COMMAND_GOTO_POINT, fighterID, point)

    def _ExecuteFighterCommand(self, command, fighterID, *args, **kwargs):
        sm.RemoteSvc('fighterMgr').ExecuteFighterCommand(command, fighterID, *args, **kwargs)

    def SpawnTestFighter(self, typeID):
        return sm.RemoteSvc('fighterMgr').SpawnTestFighter(typeID)

    def DestroyTestFighter(self, fighterID):
        sm.RemoteSvc('fighterMgr').DestroyTestFighter(fighterID)

    def GetFightersForShip(self):
        if not session.role & ROLE_GML:
            return ([], [])
        return sm.RemoteSvc('fighterMgr').GetFightersForShip()

    def LoadFightersToTube(self, fighterID, tubeFlagID):
        return sm.RemoteSvc('fighterMgr').LoadFightersToTube(fighterID, tubeFlagID)

    def UnloadTubeToFighterBay(self, tubeFlagID):
        return sm.RemoteSvc('fighterMgr').UnloadTubeToFighterBay(tubeFlagID)

    def LaunchFightersFromTube(self, tubeFlagID):
        return sm.RemoteSvc('fighterMgr').LaunchFightersFromTube(tubeFlagID)

    def ScoopFightersToTube(self, fighterID, tubeFlagID):
        return sm.RemoteSvc('fighterMgr').ScoopFightersToTube(fighterID, tubeFlagID)

    def ActivateAbilitySlot(self, fighterID, abilitySlotID, *abilityArgs, **abilityKwargs):
        return sm.RemoteSvc('fighterMgr').ActivateAbilitySlot(fighterID, abilitySlotID, *abilityArgs, **abilityKwargs)

    def DeactivateAbilitySlot(self, fighterID, abilitySlotID):
        return sm.RemoteSvc('fighterMgr').DeactivateAbilitySlot(fighterID, abilitySlotID)
