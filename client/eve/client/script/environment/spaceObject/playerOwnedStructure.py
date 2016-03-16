#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\playerOwnedStructure.py
from carbon.common.lib.const import SEC
import blue
import uthread
import eve.common.lib.appConst as const
from eve.client.script.environment.spaceObject.buildableStructure import BuildableStructure, TEARDOWN_OVERLAY_EFFECT_GRAPHIC_ID, CONSTRUCTION_OVERLAY_EFFECT_GRAPHIC_ID, STATE_BUILDING, STATE_TEARDOWN
import eve.common.script.mgt.posConst as pos
CONSTRUCTION_MATERIAL = 'res:/Texture/MinmatarShared/Gradientbuild.dds'
ONLINE_GLOW_OFF = (0.0, 0.0, 0.0)
ONLINE_GLOW_MID = (0.004, 0.0, 0.0)
CONTROL_TOWER = 'control_tower_type'
PLAYER_OWNED_STRUCTURE = 'player_owned_structure_type'
PLAY_EVENT = 'play_event_type'
STOP_EVENT = 'stop_event_type'
STATE_NONE = None
STATE_UNBUILT = 'Unbuilt'
STATE_OFFLINE = 'Offline'
STATE_ONLINING = 'Onlining'
STATE_ONLINE = 'Online'
POS_STATES_TO_STATE = {pos.STRUCTURE_UNANCHORED: STATE_NONE,
 pos.STRUCTURE_ANCHORED: STATE_OFFLINE,
 pos.STRUCTURE_ONLINING: STATE_ONLINING,
 pos.STRUCTURE_REINFORCED: STATE_ONLINE,
 pos.STRUCTURE_ONLINE: STATE_ONLINE,
 pos.STRUCTURE_OPERATING: STATE_ONLINE,
 pos.STRUCTURE_VULNERABLE: STATE_ONLINE,
 pos.STRUCTURE_SHIELD_REINFORCE: STATE_ONLINE,
 pos.STRUCTURE_ARMOR_REINFORCE: STATE_ONLINE,
 pos.STRUCTURE_INVULNERABLE: STATE_ONLINE}
POS_STATE_SOUNDS = {STATE_ONLINE: {CONTROL_TOWER: 'wise:/msg_ct_online_play',
                PLAYER_OWNED_STRUCTURE: 'wise:/msg_pos_online_play'},
 STATE_OFFLINE: {CONTROL_TOWER: 'wise:/msg_ct_offline_play',
                 PLAYER_OWNED_STRUCTURE: 'wise:/msg_pos_offline_play'},
 STATE_BUILDING: {PLAY_EVENT: 'wise:/building_effect_play',
                  STOP_EVENT: 'wise:/building_effect_stop'},
 STATE_TEARDOWN: {PLAY_EVENT: 'wise:/building_teardown_effect_play',
                  STOP_EVENT: 'wise:/building_teardown_effect_stop'}}

class PlayerOwnedStructure(BuildableStructure):

    def OnSlimItemUpdated(self, slimItem):
        oldPosState = self.GetPosState()
        newPosState = getattr(slimItem, 'posState', STATE_NONE)
        if newPosState is None or oldPosState == newPosState:
            return
        self.typeData['slimItem'].posState = newPosState
        self.PlaySounds(oldPosState, newPosState)
        if oldPosState == pos.STRUCTURE_ANCHORED and newPosState == pos.STRUCTURE_UNANCHORED or oldPosState == pos.STRUCTURE_UNANCHORED and newPosState == pos.STRUCTURE_ANCHORED:
            return
        uthread.new(self.LoadModel)

    def GetAnimationState(self, posState):
        return POS_STATES_TO_STATE.get(posState, STATE_NONE)

    def GetPosState(self):
        slimItem = self.typeData['slimItem']
        return getattr(slimItem, 'posState', None)

    def PlayStateSound(self, state, eventType):
        event = None
        state_events = POS_STATE_SOUNDS.get(state, None)
        if state_events is not None:
            event = state_events.get(eventType, None)
        if event is not None:
            self.PlayGeneralAudioEvent(event)
        else:
            self.LogWarn('PlayerOwnedStructure: No event found for state: %s of type: %s' % (state, eventType))

    def PlaySounds(self, oldState, posState):
        structure_type = CONTROL_TOWER if self.IsControlTower() else PLAYER_OWNED_STRUCTURE
        if oldState == pos.STRUCTURE_ONLINING and posState == pos.STRUCTURE_ONLINE:
            self.PlayStateSound(STATE_ONLINE, structure_type)
        elif oldState == pos.STRUCTURE_ONLINE and posState == pos.STRUCTURE_ANCHORED:
            self.PlayStateSound(STATE_OFFLINE, structure_type)

    def LoadModel(self, fileName = None, loadedModel = None):
        animationState = self.GetAnimationState(self.GetPosState())
        self.SetupModel(animationState is STATE_NONE and not self.IsAnchored())
        self.Assemble()
        if animationState is not STATE_NONE and not self.isConstructing:
            self.TriggerAnimation(animationState)
        self.SetStaticRotation()

    def Assemble(self):
        slimItem = self.typeData.get('slimItem')
        if slimItem.groupID == const.groupMoonMining:
            direction = self.FindClosestMoonDir()
            self.AlignToDirection(direction)

    def Release(self, origin = None):
        self.PlayGeneralAudioEvent('fade_out')
        BuildableStructure.Release(self, origin)

    def StartBuildingEffect(self, state, dogmaBuildingLength, elapsedTime, overlayGraphicID):
        curveLength = 1.0 * dogmaBuildingLength / 1000.0
        elapsedTime = 1.0 * elapsedTime / SEC
        self.PreBuildingSteps(overlayGraphicID)
        uthread.new(self.EndBuildingEffect, state, int((curveLength - elapsedTime) * 1000))
        self.TriggerAnimation(state, curveLength=curveLength, elapsedTime=elapsedTime)
        self.PlayStateSound(state, PLAY_EVENT)

    def EndBuildingEffect(self, state, delay):
        blue.pyos.synchro.SleepSim(delay)
        if self.released or self.exploded:
            return
        requiredFreeValue = state != STATE_TEARDOWN
        while self.isFree == requiredFreeValue:
            self.LogInfo('PlayerOwnedStructure: Yielding until self.isFree is correct')
            blue.synchro.Yield()

        if state == STATE_TEARDOWN:
            overlayEffectIdToRemove = TEARDOWN_OVERLAY_EFFECT_GRAPHIC_ID
        else:
            overlayEffectIdToRemove = CONSTRUCTION_OVERLAY_EFFECT_GRAPHIC_ID
        self.PostBuildingSteps(overlayEffectIdToRemove)
        self.PlayStateSound(state, STOP_EVENT)
        self.LoadModel()

    def BeginStructureAnchoring(self, timeSinceStart):
        self.LoadUnLoadedModels()
        self.LogInfo('PlayerOwnedStructure: BeginStructureAnchoring', self.GetTypeID())
        buildingLength = sm.GetService('godma').GetType(self.GetTypeID()).anchoringDelay
        self.StartBuildingEffect(STATE_BUILDING, buildingLength, timeSinceStart, CONSTRUCTION_OVERLAY_EFFECT_GRAPHIC_ID)
        self.PlaySounds(pos.STRUCTURE_UNANCHORED, pos.STRUCTURE_ANCHORED)

    def BeginStructureUnAnchoring(self, timeSinceStart):
        self.LoadUnLoadedModels()
        self.LogInfo('PlayerOwnedStructure: BeginStructureUnAnchoring', self.GetTypeID())
        godmaType = sm.GetService('godma').GetType(self.GetTypeID())
        if godmaType.AttributeExists('unanchoringDelay'):
            buildingLength = godmaType.unanchoringDelay
        else:
            buildingLength = godmaType.anchoringDelay
        self.StartBuildingEffect(STATE_TEARDOWN, buildingLength, timeSinceStart, TEARDOWN_OVERLAY_EFFECT_GRAPHIC_ID)
        self.PlaySounds(pos.STRUCTURE_ANCHORED, pos.STRUCTURE_UNANCHORED)

    def IsControlTower(self):
        slimItem = self.typeData.get('slimItem')
        if slimItem is not None:
            groupID = self.typeData.get('groupID')
            return groupID == const.groupControlTower
        return False

    def IsAnchored(self):
        self.LogInfo('PlayerOwnedStructure: Anchor State = ', not self.isFree)
        return not self.isFree

    def IsOnline(self):
        slimItem = self.typeData.get('slimItem')
        res = self.sm.GetService('pwn').GetStructureState(slimItem)[0] in ('online', 'invulnerable', 'vulnerable', 'reinforced')
        self.LogInfo('PlayerOwnedStructure: Online State = ', res)
        return res

    def OnlineAnimation(self, animate = 0):
        pass

    def OfflineAnimation(self, animate = 0):
        pass
