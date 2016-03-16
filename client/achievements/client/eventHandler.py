#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\client\eventHandler.py
import weakref
from achievements.common.achievementConst import AchievementEventConst as eventConst
from achievements.common.eventHandlerUtil import ListContainsTypeInGivenGroups
from eve.common.script.sys.idCheckers import IsStation
import inventorycommon.const as invConst

class EventHandler(object):
    __notifyevents__ = ['OnClientEvent_LockItem',
     'OnClientEvent_MoveWithDoubleClick',
     'OnClientEvent_Orbit',
     'OnClientEvent_MoveFromCargoToHangar',
     'OnClientEvent_ActivateModule',
     'OnClientEvent_Approach',
     'OnClientEvent_ChattedInLocal',
     'OnClientEvent_OpenMap',
     'OnClientEvent_DestinationSet',
     'OnAutoPilotOn',
     'OnClientEvent_JumpedToNextSystemInRoute',
     'OnClientMouseZoomInSpace',
     'OnClientMouseSpinInSpace',
     'OnModuleUnfitted',
     'OnLookAtMyShip',
     'OnLookAtOther',
     'OnClient_ShipActivated',
     'OnClientEvent_OpenCorpFinder',
     'OnClientEvent_BlueprintLoaded',
     'OnProbeAdded',
     'OnClientEvent_PerfectScanResultReached',
     'OnBookmarkCreated']

    def __init__(self, achievementSvc):
        sm.RegisterNotify(self)
        self.achievementSvc = weakref.proxy(achievementSvc)

    def LogAchievementEvent(self, eventType, amount = 1):
        self.achievementSvc.LogClientEvent(eventType, amount)

    def OnClientEvent_LockItem(self, slimItem):
        if slimItem.categoryID == const.categoryAsteroid:
            self.LogAchievementEvent(eventConst.ASTEROIDS_LOCK_CLIENT)
        elif self.IsHostileNPC(slimItem):
            self.LogAchievementEvent(eventConst.HOSTILE_NPC_LOCK_CLIENT)

    def OnClientEvent_MoveWithDoubleClick(self):
        self.LogAchievementEvent(eventConst.DOUBLE_CLICK_COUNT_CLIENT)

    def OnClientEvent_Orbit(self, slimItem):
        if slimItem.categoryID == const.categoryAsteroid:
            self.LogAchievementEvent(eventConst.ASTEROIDS_ORBIT_CLIENT)
        elif self.IsHostileNPC(slimItem):
            self.LogAchievementEvent(eventConst.HOSTILE_NPC_ORBIT_CLIENT)

    def OnClientEvent_Approach(self):
        self.LogAchievementEvent(eventConst.APPROACH_CLIENT)

    def OnClientEvent_MoveFromCargoToHangar(self, sourceID, destinationID, destinationFlag = None):
        if sourceID > const.minFakeItem:
            self.LogAchievementEvent(eventConst.ITEMS_LOOT_CLIENT)
            return
        if session.stationid2:
            sourceLocationItem = sm.GetService('invCache').FetchItem(sourceID, session.stationid2)
            if not sourceLocationItem:
                return
            if sourceLocationItem.categoryID == const.categoryShip and (IsStation(destinationID) or destinationFlag == const.flagHangar):
                self.LogAchievementEvent(eventConst.ITEMS_MOVE_FROM_CARGO_TO_HANGAR_CLIENT)

    def OnClientEvent_ActivateModule(self, effectID):
        if effectID in (const.effectProjectileFired, const.effectTargetAttack):
            self.LogAchievementEvent(eventConst.ACTIVATE_GUN_CLIENT)
        elif effectID == const.effectSalvaging:
            self.LogAchievementEvent(eventConst.ACTIVATE_SALVAGER_CLIENT)

    def OnClientEvent_ChattedInLocal(self):
        self.LogAchievementEvent(eventConst.SOCIAL_CHAT_IN_LOCAL_CLIENT)

    def OnClientEvent_OpenMap(self):
        self.LogAchievementEvent(eventConst.UI_OPEN_MAP_CLIENT)

    def OnClientEvent_DestinationSet(self):
        self.LogAchievementEvent(eventConst.TRAVEL_SET_DESTINATION_CLIENT)

    def OnAutoPilotOn(self, *args):
        self.LogAchievementEvent(eventConst.TRAVEL_ACTIVATE_AUTOPILOT_CLIENT)

    def OnClientEvent_JumpedToNextSystemInRoute(self):
        self.LogAchievementEvent(eventConst.TRAVEL_JUMP_TO_NEXT_SYSTEM_CLIENT)

    def OnClientMouseZoomInSpace(self, amount):
        if amount > 0:
            self.LogAchievementEvent(eventConst.UI_MOUSEZOOM_OUT_CLIENT)
        else:
            self.LogAchievementEvent(eventConst.UI_MOUSEZOOM_IN_CLIENT)

    def OnClientMouseSpinInSpace(self):
        self.LogAchievementEvent(eventConst.UI_MOUSE_ROTATE_CLIENT)

    def OnModuleUnfitted(self):
        self.LogAchievementEvent(eventConst.FITTING_UNFIT_MODULE_CLIENT)

    def OnLookAtMyShip(self, itemID):
        self.LogAchievementEvent(eventConst.LOOK_AT_OWN_SHIP)

    def OnLookAtOther(self, itemID):
        self.LogAchievementEvent(eventConst.LOOK_AT_OBJECT)

    def OnClient_ShipActivated(self):
        self.LogAchievementEvent(eventConst.ACTIVATE_SHIP_CLIENT)

    def UnregisterForEvents(self):
        sm.UnregisterNotify(self)

    def IsHostileNPC(self, slimItem):
        if slimItem.categoryID == const.categoryEntity and slimItem.typeID:
            val = sm.GetService('clientDogmaStaticSvc').GetTypeAttribute2(slimItem.typeID, const.attributeEntityBracketColour)
            if val >= 1:
                return True
        return False

    def OnClientEvent_OpenCorpFinder(self):
        self.LogAchievementEvent(eventConst.OPEN_CORP_FINDER)

    def OnClientEvent_BlueprintLoaded(self):
        self.LogAchievementEvent(eventConst.INDUSTRY_LOAD_BLUEPRINT)

    def OnProbeAdded(self, probe):
        self.LogAchievementEvent(eventConst.LAUNCH_PROBES)

    def OnClientEvent_PerfectScanResultReached(self):
        self.LogAchievementEvent(eventConst.REACH_PERFECT_SCAN_RESULTS)

    def OnBookmarkCreated(self, bookmarkID, comment, typeID = None):
        if typeID and ListContainsTypeInGivenGroups([typeID], [invConst.groupWormhole]):
            self.LogAchievementEvent(eventConst.CREATE_WORMHOLE_BOOKMARK)
