#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\common\opportunityTaskMap.py
from achievements.common.achievementConst import AchievementConsts

class OpportunityConst:
    LOOK = 100
    FLY = 101
    KILL = 102
    SKILL = 103
    WARP = 104
    STATION = 105
    MINE = 106
    MARKET = 107
    FITTING = 108
    SOCIAL = 109
    STARGATE = 110
    ROUTE = 111
    INDUSTRY = 112
    EXPLORATION = 113
    AGENTS = 114
    DEATH = 115
    CORP = 116
    WORMHOLE = 117
    SALVAGE = 118
    PODDED = 119
    AGENTSEXP = 120


GROUP_TO_TASK_IDS = {OpportunityConst.LOOK: [AchievementConsts.UI_ROTATE_IN_SPACE,
                         AchievementConsts.UI_ZOOM_IN_SPACE,
                         AchievementConsts.LOOK_AT_OBJECT,
                         AchievementConsts.LOOK_AT_OWN_SHIP],
 OpportunityConst.FLY: [AchievementConsts.DOUBLE_CLICK, AchievementConsts.APPROACH],
 OpportunityConst.KILL: [AchievementConsts.ORBIT_NPC,
                         AchievementConsts.LOCK_NPC,
                         AchievementConsts.ACTIVATE_GUN,
                         AchievementConsts.KILL_NPC,
                         AchievementConsts.LOOT_FROM_NPC_WRECK],
 OpportunityConst.SKILL: [AchievementConsts.START_TRAINING],
 OpportunityConst.WARP: [AchievementConsts.WARP],
 OpportunityConst.STATION: [AchievementConsts.DOCK_IN_STATION, AchievementConsts.MOVE_FROM_CARGO_TO_HANGAR, AchievementConsts.UNDOCK_FROM_STATION],
 OpportunityConst.MINE: [AchievementConsts.ORBIT_ASTEROID,
                         AchievementConsts.LOCK_ASTEROID,
                         AchievementConsts.ACTIVATE_MINER,
                         AchievementConsts.MINE_ORE],
 OpportunityConst.MARKET: [AchievementConsts.PLACE_SELL_ORDER, AchievementConsts.PLACE_BUY_ORDER],
 OpportunityConst.FITTING: [AchievementConsts.UNFIT_MODULE,
                            AchievementConsts.FIT_LOSLOT,
                            AchievementConsts.FIT_MEDSLOT,
                            AchievementConsts.FIT_HISLOT],
 OpportunityConst.SOCIAL: [AchievementConsts.CHAT_IN_LOCAL, AchievementConsts.INVITE_TO_CONVO, AchievementConsts.ADD_CONTACT],
 OpportunityConst.STARGATE: [AchievementConsts.USE_STARGATE],
 OpportunityConst.ROUTE: [AchievementConsts.OPEN_MAP,
                          AchievementConsts.SET_DESTINATION,
                          AchievementConsts.JUMP_TO_NEXT_SYSTEM,
                          AchievementConsts.ACTIVATE_AUTOPILOT],
 OpportunityConst.INDUSTRY: [AchievementConsts.REFINE_ORE,
                             AchievementConsts.LOAD_BLUEPRINT,
                             AchievementConsts.START_INDUSTRY_JOB,
                             AchievementConsts.DELIVER_INDUSTRY_JOB],
 OpportunityConst.EXPLORATION: [AchievementConsts.ENTER_DISTRIBUTION_SITE,
                                AchievementConsts.FIT_PROBE_LAUNCHER,
                                AchievementConsts.LAUNCH_PROBES,
                                AchievementConsts.GET_PERFECT_SCAN_RESULTS],
 OpportunityConst.AGENTS: [AchievementConsts.TALK_TO_AGENT, AchievementConsts.ACCEPT_MISSION, AchievementConsts.COMPLETE_MISSION],
 OpportunityConst.DEATH: [AchievementConsts.LOSE_SHIP, AchievementConsts.ACTIVATE_SHIP],
 OpportunityConst.CORP: [AchievementConsts.OPEN_CORP_FINDER, AchievementConsts.JOIN_CORP],
 OpportunityConst.WORMHOLE: [AchievementConsts.ENTER_WORMHOLE, AchievementConsts.BOOKMARK_WORMHOLE],
 OpportunityConst.SALVAGE: [AchievementConsts.USE_SALVAGER, AchievementConsts.SALVAGE],
 OpportunityConst.PODDED: [AchievementConsts.LOSE_POD],
 OpportunityConst.AGENTSEXP: [AchievementConsts.CAREER_AGENT, AchievementConsts.ACCEPT_MISSION, AchievementConsts.COMPLETE_MISSION]}
REWARD_1 = 50000
REWARD_2 = 75000
REWARD_3 = 100000
REWARD_4 = 150000
REWARD_5 = 250000
GROUP_TO_REWARD = {OpportunityConst.LOOK: REWARD_1,
 OpportunityConst.FLY: REWARD_1,
 OpportunityConst.KILL: REWARD_1,
 OpportunityConst.SKILL: REWARD_1,
 OpportunityConst.WARP: REWARD_1,
 OpportunityConst.STATION: REWARD_1,
 OpportunityConst.MINE: REWARD_1,
 OpportunityConst.MARKET: REWARD_2,
 OpportunityConst.FITTING: REWARD_2,
 OpportunityConst.SOCIAL: REWARD_3,
 OpportunityConst.STARGATE: REWARD_1,
 OpportunityConst.ROUTE: REWARD_4,
 OpportunityConst.INDUSTRY: REWARD_4,
 OpportunityConst.EXPLORATION: REWARD_4,
 OpportunityConst.AGENTS: REWARD_4,
 OpportunityConst.DEATH: REWARD_5,
 OpportunityConst.CORP: REWARD_5,
 OpportunityConst.WORMHOLE: REWARD_5,
 OpportunityConst.SALVAGE: REWARD_5,
 OpportunityConst.PODDED: REWARD_5,
 OpportunityConst.AGENTSEXP: REWARD_1}

def BuildIndex(idArrayDict):
    index = {}
    for key, taskList in idArrayDict.iteritems():
        for value in taskList:
            index[value] = key

    return index


TASK_ID_TO_GROUP = BuildIndex(GROUP_TO_TASK_IDS)
