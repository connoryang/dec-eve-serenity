#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\common\achievementGroups.py
from achievements.common.achievementConst import AchievementConsts
from localization import GetByLabel

class AchievementGroup(object):
    achievementTasks = None

    def __init__(self, groupID, nameLabelPath, descriptionLabelPath, notificationPath, achievementTaskIDs, groupConnections, treePosition = None, triggeredBy = None, suggestedGroup = True, *args, **kwargs):
        self.groupID = groupID
        self.groupName = GetByLabel(nameLabelPath)
        self.groupDescription = GetByLabel(descriptionLabelPath)
        self.groupConnections = groupConnections
        self.achievementTaskIDs = achievementTaskIDs
        self.notificationPath = notificationPath
        self.triggeredBy = triggeredBy
        self.suggestedGroup = suggestedGroup
        if treePosition:
            self.SetTreePosition(treePosition)
        else:
            self.treePosition = (1, 1)

    def SetTreePosition(self, treePosition):
        self.treePosition = treePosition

    def GetAchievementTaskIDs(self):
        return self.achievementTaskIDs

    def GetAchievementTasks(self):
        if self.achievementTasks is None:
            self.achievementTasks = []
            allAchievements = sm.GetService('achievementSvc').allAchievements
            for achievementTaskID in self.achievementTaskIDs:
                self.achievementTasks.append(allAchievements[achievementTaskID])

        return self.achievementTasks

    def IsCompleted(self):
        groupTasks = self.GetAchievementTasks()
        totalNum = len(groupTasks)
        completed = len([ x for x in groupTasks if x.completed ])
        return totalNum == completed

    def HasAchievement(self, achievementID):
        return achievementID in self.achievementTaskIDs

    def GetNextIncompleteTask(self, currentAchievementTaskID = None):
        tasks = self.GetAchievementTasks()
        foundCurrent = currentAchievementTaskID is None
        for each in tasks:
            if each.achievementID == currentAchievementTaskID:
                foundCurrent = True
                continue
            if foundCurrent and not each.completed:
                return each

    def GetFirstCompletedTask(self):
        tasks = self.GetAchievementTasks()
        for each in tasks:
            if each.completed:
                return each

    def GetProgressProportion(self):
        tasks = self.GetAchievementTasks()
        total = len(tasks)
        completed = 0
        for each in tasks:
            if each.completed:
                completed += 1

        return completed / float(total)


_achievementGroups = [AchievementGroup(nameLabelPath='Achievements/GroupNameText/fly', descriptionLabelPath='Achievements/GroupDescriptionText/fly', notificationPath='Achievements/GroupNotificationText/fly', groupID=11, achievementTaskIDs=[AchievementConsts.DOUBLE_CLICK, AchievementConsts.APPROACH], groupConnections=[12], treePosition=(3, 1)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/kill', descriptionLabelPath='Achievements/GroupDescriptionText/kill', notificationPath='Achievements/GroupNotificationText/kill', groupID=12, achievementTaskIDs=[AchievementConsts.ORBIT_NPC,
  AchievementConsts.LOCK_NPC,
  AchievementConsts.ACTIVATE_GUN,
  AchievementConsts.KILL_NPC,
  AchievementConsts.LOOT_FROM_NPC_WRECK], groupConnections=[13], treePosition=(4, 1)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/mine', descriptionLabelPath='Achievements/GroupDescriptionText/mine', notificationPath='Achievements/GroupNotificationText/mine', groupID=13, achievementTaskIDs=[AchievementConsts.ORBIT_ASTEROID,
  AchievementConsts.LOCK_ASTEROID,
  AchievementConsts.ACTIVATE_MINER,
  AchievementConsts.MINE_ORE], groupConnections=[14], treePosition=(5, 1)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/warp', descriptionLabelPath='Achievements/GroupDescriptionText/warp', notificationPath='Achievements/GroupNotificationText/warp', groupID=14, achievementTaskIDs=[AchievementConsts.WARP], groupConnections=[15], treePosition=(5, 2)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/station', descriptionLabelPath='Achievements/GroupDescriptionText/station', notificationPath='Achievements/GroupNotificationText/station', groupID=15, achievementTaskIDs=[AchievementConsts.DOCK_IN_STATION,
  AchievementConsts.MOVE_FROM_CARGO_TO_HANGAR,
  AchievementConsts.FIT_ITEM,
  AchievementConsts.PLACE_BUY_ORDER,
  AchievementConsts.UNDOCK_FROM_STATION], groupConnections=[16], treePosition=(4, 3)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/stargate', descriptionLabelPath='Achievements/GroupDescriptionText/stargate', notificationPath='Achievements/GroupNotificationText/stargate', groupID=16, achievementTaskIDs=[AchievementConsts.USE_STARGATE], groupConnections=[17], treePosition=(3, 2)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/skill', descriptionLabelPath='Achievements/GroupDescriptionText/skill', notificationPath='Achievements/GroupNotificationText/skill', groupID=17, achievementTaskIDs=[AchievementConsts.START_TRAINING, AchievementConsts.INJECT_SKILL], groupConnections=[18], treePosition=(4, 2))]
_achievementGroups2 = [AchievementGroup(nameLabelPath='Achievements/GroupNameText/look', descriptionLabelPath='Achievements/GroupDescriptionText/look', notificationPath='Achievements/GroupNotificationText/look', groupID=100, achievementTaskIDs=[AchievementConsts.UI_ROTATE_IN_SPACE,
  AchievementConsts.UI_ZOOM_IN_SPACE,
  AchievementConsts.LOOK_AT_OBJECT,
  AchievementConsts.LOOK_AT_OWN_SHIP], groupConnections=[101], treePosition=(1, 1)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/fly', descriptionLabelPath='Achievements/GroupDescriptionText/fly', notificationPath='Achievements/GroupNotificationText/fly', groupID=101, achievementTaskIDs=[AchievementConsts.DOUBLE_CLICK, AchievementConsts.APPROACH], groupConnections=[102], treePosition=(1, 2)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/kill', descriptionLabelPath='Achievements/GroupDescriptionText/kill', notificationPath='Achievements/GroupNotificationText/kill', groupID=102, achievementTaskIDs=[AchievementConsts.ORBIT_NPC,
  AchievementConsts.LOCK_NPC,
  AchievementConsts.ACTIVATE_GUN,
  AchievementConsts.KILL_NPC,
  AchievementConsts.LOOT_FROM_NPC_WRECK], groupConnections=[103], treePosition=(1, 3)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/skill', descriptionLabelPath='Achievements/GroupDescriptionText/skill', notificationPath='Achievements/GroupNotificationText/skill', groupID=103, achievementTaskIDs=[AchievementConsts.START_TRAINING], groupConnections=[104], treePosition=(2, 3)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/warp', descriptionLabelPath='Achievements/GroupDescriptionText/warp', notificationPath='Achievements/GroupNotificationText/warp', groupID=104, achievementTaskIDs=[AchievementConsts.WARP], groupConnections=[105], treePosition=(2, 2)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/station', descriptionLabelPath='Achievements/GroupDescriptionText/station', notificationPath='Achievements/GroupNotificationText/station', groupID=105, achievementTaskIDs=[AchievementConsts.DOCK_IN_STATION, AchievementConsts.MOVE_FROM_CARGO_TO_HANGAR, AchievementConsts.UNDOCK_FROM_STATION], groupConnections=[106], treePosition=(2, 1)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/mine', descriptionLabelPath='Achievements/GroupDescriptionText/mine', notificationPath='Achievements/GroupNotificationText/mine', groupID=106, achievementTaskIDs=[AchievementConsts.ORBIT_ASTEROID,
  AchievementConsts.LOCK_ASTEROID,
  AchievementConsts.ACTIVATE_MINER,
  AchievementConsts.MINE_ORE], groupConnections=[107], treePosition=(3, 1)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/market', descriptionLabelPath='Achievements/GroupDescriptionText/market', notificationPath='Achievements/GroupNotificationText/market', groupID=107, achievementTaskIDs=[AchievementConsts.PLACE_SELL_ORDER, AchievementConsts.PLACE_BUY_ORDER], groupConnections=[108], treePosition=(3, 2)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/fitting', descriptionLabelPath='Achievements/GroupDescriptionText/fitting', notificationPath='Achievements/GroupNotificationText/fitting', groupID=108, achievementTaskIDs=[AchievementConsts.UNFIT_MODULE,
  AchievementConsts.FIT_LOSLOT,
  AchievementConsts.FIT_MEDSLOT,
  AchievementConsts.FIT_HISLOT], groupConnections=[109], treePosition=(3, 3)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/social', descriptionLabelPath='Achievements/GroupDescriptionText/social', notificationPath='Achievements/GroupNotificationText/social', groupID=109, achievementTaskIDs=[AchievementConsts.CHAT_IN_LOCAL, AchievementConsts.INVITE_TO_CONVO, AchievementConsts.ADD_CONTACT], groupConnections=[110], treePosition=(4, 3)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/stargate', descriptionLabelPath='Achievements/GroupDescriptionText/stargate', notificationPath='Achievements/GroupNotificationText/stargate', groupID=110, achievementTaskIDs=[AchievementConsts.USE_STARGATE], groupConnections=[111], treePosition=(4, 2)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/route', descriptionLabelPath='Achievements/GroupDescriptionText/route', notificationPath='Achievements/GroupNotificationText/route', groupID=111, achievementTaskIDs=[AchievementConsts.OPEN_MAP,
  AchievementConsts.SET_DESTINATION,
  AchievementConsts.JUMP_TO_NEXT_SYSTEM,
  AchievementConsts.ACTIVATE_AUTOPILOT], groupConnections=[112], treePosition=(4, 1)),
 AchievementGroup(nameLabelPath='Achievements/GroupNameText/death', descriptionLabelPath='Achievements/GroupDescriptionText/death', notificationPath='Achievements/GroupNotificationText/death', groupID=112, achievementTaskIDs=[AchievementConsts.LOSE_SHIP, AchievementConsts.ACTIVATE_SHIP], groupConnections=[112], treePosition=(5, 1), triggeredBy=AchievementConsts.LOSE_SHIP)]
group100 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/look', descriptionLabelPath='Achievements/GroupDescriptionText/look', notificationPath='Achievements/GroupNotificationText/look', groupID=100, achievementTaskIDs=[AchievementConsts.UI_ROTATE_IN_SPACE,
 AchievementConsts.UI_ZOOM_IN_SPACE,
 AchievementConsts.LOOK_AT_OBJECT,
 AchievementConsts.LOOK_AT_OWN_SHIP], groupConnections=[101], treePosition=(1, 1))
group101 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/fly', descriptionLabelPath='Achievements/GroupDescriptionText/fly', notificationPath='Achievements/GroupNotificationText/fly', groupID=101, achievementTaskIDs=[AchievementConsts.DOUBLE_CLICK, AchievementConsts.APPROACH], groupConnections=[102], treePosition=(1, 2))
group102 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/kill', descriptionLabelPath='Achievements/GroupDescriptionText/kill', notificationPath='Achievements/GroupNotificationText/kill', groupID=102, achievementTaskIDs=[AchievementConsts.ORBIT_NPC,
 AchievementConsts.LOCK_NPC,
 AchievementConsts.ACTIVATE_GUN,
 AchievementConsts.KILL_NPC,
 AchievementConsts.LOOT_FROM_NPC_WRECK], groupConnections=[103], treePosition=(1, 3))
group103 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/skill', descriptionLabelPath='Achievements/GroupDescriptionText/skill', notificationPath='Achievements/GroupNotificationText/skill', groupID=103, achievementTaskIDs=[AchievementConsts.START_TRAINING], groupConnections=[104], treePosition=(2, 3))
group104 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/warp', descriptionLabelPath='Achievements/GroupDescriptionText/warp', notificationPath='Achievements/GroupNotificationText/warp', groupID=104, achievementTaskIDs=[AchievementConsts.WARP], groupConnections=[105], treePosition=(2, 2))
group105 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/station', descriptionLabelPath='Achievements/GroupDescriptionText/station', notificationPath='Achievements/GroupNotificationText/station', groupID=105, achievementTaskIDs=[AchievementConsts.DOCK_IN_STATION, AchievementConsts.MOVE_FROM_CARGO_TO_HANGAR, AchievementConsts.UNDOCK_FROM_STATION], groupConnections=[106], treePosition=(2, 1))
group106 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/mine', descriptionLabelPath='Achievements/GroupDescriptionText/mine', notificationPath='Achievements/GroupNotificationText/mine', groupID=106, achievementTaskIDs=[AchievementConsts.ORBIT_ASTEROID,
 AchievementConsts.LOCK_ASTEROID,
 AchievementConsts.ACTIVATE_MINER,
 AchievementConsts.MINE_ORE], groupConnections=[107], treePosition=(3, 1))
group107 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/market', descriptionLabelPath='Achievements/GroupDescriptionText/market', notificationPath='Achievements/GroupNotificationText/market', groupID=107, achievementTaskIDs=[AchievementConsts.PLACE_SELL_ORDER, AchievementConsts.PLACE_BUY_ORDER], groupConnections=[108], treePosition=(3, 2))
group108 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/fitting', descriptionLabelPath='Achievements/GroupDescriptionText/fitting', notificationPath='Achievements/GroupNotificationText/fitting', groupID=108, achievementTaskIDs=[AchievementConsts.UNFIT_MODULE,
 AchievementConsts.FIT_LOSLOT,
 AchievementConsts.FIT_MEDSLOT,
 AchievementConsts.FIT_HISLOT], groupConnections=[109], treePosition=(3, 3))
group109 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/social', descriptionLabelPath='Achievements/GroupDescriptionText/social', notificationPath='Achievements/GroupNotificationText/social', groupID=109, achievementTaskIDs=[AchievementConsts.CHAT_IN_LOCAL, AchievementConsts.INVITE_TO_CONVO, AchievementConsts.ADD_CONTACT], groupConnections=[110], treePosition=(4, 3))
group110 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/stargate', descriptionLabelPath='Achievements/GroupDescriptionText/stargate', notificationPath='Achievements/GroupNotificationText/stargate', groupID=110, achievementTaskIDs=[AchievementConsts.USE_STARGATE], groupConnections=[111], treePosition=(4, 2))
group111 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/route', descriptionLabelPath='Achievements/GroupDescriptionText/route', notificationPath='Achievements/GroupNotificationText/route', groupID=111, achievementTaskIDs=[AchievementConsts.OPEN_MAP,
 AchievementConsts.SET_DESTINATION,
 AchievementConsts.JUMP_TO_NEXT_SYSTEM,
 AchievementConsts.ACTIVATE_AUTOPILOT], groupConnections=[112], treePosition=(4, 1))
group112 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/industry', descriptionLabelPath='Achievements/GroupDescriptionText/industry', notificationPath='Achievements/GroupNotificationText/industry', groupID=112, achievementTaskIDs=[AchievementConsts.REFINE_ORE,
 AchievementConsts.LOAD_BLUEPRINT,
 AchievementConsts.START_INDUSTRY_JOB,
 AchievementConsts.DELIVER_INDUSTRY_JOB], groupConnections=[113], treePosition=(5, 1))
group113 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/exploration', descriptionLabelPath='Achievements/GroupDescriptionText/exploration', notificationPath='Achievements/GroupNotificationText/exploration', groupID=113, achievementTaskIDs=[AchievementConsts.ENTER_DISTRIBUTION_SITE,
 AchievementConsts.FIT_PROBE_LAUNCHER,
 AchievementConsts.LAUNCH_PROBES,
 AchievementConsts.GET_PERFECT_SCAN_RESULTS], groupConnections=[114], treePosition=(5, 2))
group114 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/agents', descriptionLabelPath='Achievements/GroupDescriptionText/agents', notificationPath='Achievements/GroupNotificationText/agents', groupID=114, achievementTaskIDs=[AchievementConsts.TALK_TO_AGENT, AchievementConsts.ACCEPT_MISSION, AchievementConsts.COMPLETE_MISSION], groupConnections=[115], treePosition=(5, 3))
group115 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/death', descriptionLabelPath='Achievements/GroupDescriptionText/death', notificationPath='Achievements/GroupNotificationText/death', groupID=115, achievementTaskIDs=[AchievementConsts.LOSE_SHIP, AchievementConsts.ACTIVATE_SHIP], groupConnections=[116], treePosition=(6, 3), triggeredBy=AchievementConsts.LOSE_SHIP, suggestedGroup=False)
group116 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/corp', descriptionLabelPath='Achievements/GroupDescriptionText/corp', notificationPath='Achievements/GroupNotificationText/corp', groupID=116, achievementTaskIDs=[AchievementConsts.OPEN_CORP_FINDER, AchievementConsts.JOIN_CORP], groupConnections=[117], treePosition=(6, 2), suggestedGroup=False)
group117 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/wormhole', descriptionLabelPath='Achievements/GroupDescriptionText/wormhole', notificationPath='Achievements/GroupNotificationText/wormhole', groupID=117, achievementTaskIDs=[AchievementConsts.ENTER_WORMHOLE, AchievementConsts.BOOKMARK_WORMHOLE], groupConnections=[118], treePosition=(6, 1), triggeredBy=AchievementConsts.ENTER_WORMHOLE, suggestedGroup=False)
group118 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/salvage', descriptionLabelPath='Achievements/GroupDescriptionText/salvage', notificationPath='Achievements/GroupNotificationText/salvage', groupID=118, achievementTaskIDs=[AchievementConsts.USE_SALVAGER, AchievementConsts.SALVAGE], groupConnections=[119], treePosition=(7, 1), suggestedGroup=False)
group119 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/podded', descriptionLabelPath='Achievements/GroupDescriptionText/podded', notificationPath='Achievements/GroupNotificationText/podded', groupID=119, achievementTaskIDs=[AchievementConsts.LOSE_POD], groupConnections=[], treePosition=(7, 2), triggeredBy=AchievementConsts.LOSE_POD, suggestedGroup=False)
group120 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/agents', descriptionLabelPath='Achievements/GroupDescriptionText/career', notificationPath='Achievements/GroupNotificationText/agents', groupID=120, achievementTaskIDs=[AchievementConsts.CAREER_AGENT, AchievementConsts.ACCEPT_MISSION, AchievementConsts.COMPLETE_MISSION], groupConnections=[115], treePosition=(8, 7))
group119.SetTreePosition((13, 10))
group118.SetTreePosition((10, 9))
group117.SetTreePosition((15, 7))
group116.SetTreePosition((13, 8))
group115.SetTreePosition((14, 10))
group114.SetTreePosition((9, 8))
group113.SetTreePosition((16, 7))
group112.SetTreePosition((16, 5))
group111.SetTreePosition((13, 4))
group110.SetTreePosition((12, 4))
group109.SetTreePosition((12, 8))
group108.SetTreePosition((7, 9))
group107.SetTreePosition((6, 10))
group106.SetTreePosition((16, 4))
group105.SetTreePosition((6, 9))
group104.SetTreePosition((9, 5))
group103.SetTreePosition((12, 6))
group102.SetTreePosition((9, 7))
group101.SetTreePosition((10, 5))
group100.SetTreePosition((9, 4))
group120.SetTreePosition((10, 8))
_achievementGroups3 = [group100,
 group101,
 group102,
 group103,
 group104,
 group105,
 group106,
 group107,
 group108,
 group109,
 group110,
 group111,
 group112,
 group113,
 group114,
 group115,
 group116,
 group117,
 group118,
 group119]
_achievementGroups4 = [group100,
 group101,
 group104,
 group103,
 group110,
 group120,
 group105,
 group102,
 group106,
 group107,
 group108,
 group109,
 group111,
 group112,
 group113,
 group115,
 group116,
 group117,
 group118,
 group119]
import gatekeeper

def GetAchievementGroups():
    return _achievementGroups3


def GetTaskIds():
    allTaskIds = set()
    for group in GetAchievementGroups():
        allTaskIds.update(group.GetAchievementTaskIDs())

    return allTaskIds


def GetFirstIncompleteAchievementGroup():
    alreadyActivated = settings.char.ui.Get('opportunities_aura_activated', [])
    for each in GetAchievementGroups():
        if not each.suggestedGroup:
            continue
        if each.groupID not in alreadyActivated and not each.IsCompleted():
            return each


def GroupTriggeredByTask(task):
    alreadyActivated = settings.char.ui.Get('opportunities_aura_activated', [])
    for each in GetAchievementGroups():
        if each.triggeredBy == task and each.groupID not in alreadyActivated and not each.IsCompleted():
            return each


def GetAchievementGroup(groupID):
    for each in GetAchievementGroups():
        if each.groupID == groupID:
            return each


def GetGroupForAchievement(achievementID):
    for eachGroup in GetAchievementGroups():
        if achievementID in eachGroup.achievementTaskIDs:
            return eachGroup


def GetActiveAchievementGroup():
    activeGroupID = sm.GetService('achievementSvc').GetActiveAchievementGroupID()
    return GetAchievementGroup(activeGroupID)


def HasCompletedAchievementGroup():
    for each in GetAchievementGroups():
        if each.IsCompleted():
            return True

    return False


def HasCompletedAchievementTask():
    for each in GetAchievementGroups():
        if each.GetFirstCompletedTask():
            return True

    return False
