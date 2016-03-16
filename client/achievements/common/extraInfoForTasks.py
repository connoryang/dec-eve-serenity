#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\common\extraInfoForTasks.py
from achievements.common.achievementConst import AchievementConsts
noobWeaponsByRaceID = {const.raceAmarr: 'res:/UI/Texture/Icons/13_64_13.png',
 const.raceCaldari: 'res:/UI/Texture/Icons/13_64_5.png',
 const.raceGallente: 'res:/UI/Texture/Icons/13_64_1.png',
 const.raceMinmatar: 'res:/UI/Texture/Icons/12_64_9.png'}

def GetWeaponTexturePathFromRace():
    return noobWeaponsByRaceID.get(session.raceID)


class TaskInfoEntry_ImageText(object):

    def __init__(self, text, imagePath, imageSize, imageColor = (1, 1, 1, 1), textColor = (1, 1, 1, 0.75), imagePathFetchFunc = None):
        self.textPath = text
        self.textColor = textColor
        self.imagePath = imagePath
        self.imageSize = imageSize
        self.imageColor = imageColor
        self.imagePathFetchFunc = imagePathFetchFunc

    def GetTexturePath(self):
        if self.imagePath:
            return self.imagePath
        if self.imagePathFetchFunc:
            return self.imagePathFetchFunc()


class TaskInfoEntry_Text(object):

    def __init__(self, text, textColor = (1, 1, 1, 0.75)):
        self.text = text
        self.textColor = textColor


ORBIT_TASKINFO = TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/OrbitCommand', imagePath='res:/UI/Texture/Icons/44_32_21.png', imageSize=32)
LOCK_TASKINFO = TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/LockCommand', imagePath='res:/UI/Texture/Icons/44_32_17.png', imageSize=32)
HOSTILE_NPC_TASKINFO = [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/HostileNPC', imagePath='res:/UI/Texture/Shared/Brackets/npcrookie_16.png', imageSize=16, imageColor=(1, 0, 0, 1)), TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/HostileNPC', imagePath='res:/UI/Texture/Shared/Brackets/npcfrigate_16.png', imageSize=16, imageColor=(1, 0, 0, 1))]
ACHIEVEMENT_TASK_EXTRAINFO = {AchievementConsts.UI_ROTATE_IN_SPACE: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/MoveCamRoundShip', imagePath='res:/UI/Texture/classes/Achievements/mouseBtnLeft.png', imageSize=32)],
 AchievementConsts.UI_ZOOM_IN_SPACE: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/ZoomCam', imagePath='res:/UI/Texture/classes/Achievements/mouseBtnMiddle.png', imageSize=32)],
 AchievementConsts.LOOK_AT_OBJECT: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/LookAtCommand', imagePath='res:/UI/Texture/Icons/44_32_20.png', imageSize=32)],
 AchievementConsts.APPROACH: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/ApproachCommand', imagePath='res:/UI/Texture/icons/44_32_23.png', imageSize=32)],
 AchievementConsts.ORBIT_NPC: HOSTILE_NPC_TASKINFO + [ORBIT_TASKINFO],
 AchievementConsts.LOCK_NPC: [LOCK_TASKINFO],
 AchievementConsts.ACTIVATE_GUN: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/Gun', imagePath=None, imagePathFetchFunc=GetWeaponTexturePathFromRace, imageSize=32)],
 AchievementConsts.KILL_NPC: HOSTILE_NPC_TASKINFO,
 AchievementConsts.LOOT_FROM_NPC_WRECK: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/WreckBracket', imagePath='res:/UI/Texture/Shared/Brackets/wreckNPC.png', imageSize=16), TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/OpenCargoCommand', imagePath='res:/UI/Texture/Icons/44_32_35.png', imageSize=32)],
 AchievementConsts.ORBIT_ASTEROID: [ORBIT_TASKINFO],
 AchievementConsts.LOCK_ASTEROID: [LOCK_TASKINFO],
 AchievementConsts.ACTIVATE_MINER: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/MiningLaser', imagePath='res:/UI/Texture/Icons/12_64_8.png', imageSize=32)],
 AchievementConsts.WARP: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/WarpCommand', imagePath='res:/UI/Texture/Icons/44_32_18.png', imageSize=32)],
 AchievementConsts.DOCK_IN_STATION: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/StationBracket', imagePath='res:/UI/Texture/Shared/Brackets/station.png', imageSize=16), TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/DockCommand', imagePath='res:/UI/Texture/Icons/44_32_9.png', imageSize=32)],
 AchievementConsts.MOVE_FROM_CARGO_TO_HANGAR: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/InventoryNeocom', imagePath='res:/ui/Texture/WindowIcons/items.png', imageSize=32)],
 AchievementConsts.FIT_ITEM: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/FittingNeocom', imagePath='res:/ui/Texture/WindowIcons/fitting.png', imageSize=32)],
 AchievementConsts.UNFIT_MODULE: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/FittingNeocom', imagePath='res:/ui/Texture/WindowIcons/fitting.png', imageSize=32)],
 AchievementConsts.FIT_LOSLOT: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/LowSlot', imagePath='res:/UI/Texture/Icons/8_64_9.png', imageSize=32)],
 AchievementConsts.FIT_MEDSLOT: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/MidSlot', imagePath='res:/UI/Texture/Icons/8_64_10.png', imageSize=32)],
 AchievementConsts.FIT_HISLOT: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/HighSlot', imagePath='res:/UI/Texture/Icons/8_64_11.png', imageSize=32)],
 AchievementConsts.FIT_CHARGES: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/ChargeMarket', imagePath='res:/UI/Texture/Icons/14_64_16.png', imageSize=16)],
 AchievementConsts.PLACE_BUY_ORDER: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/MarketNeocom', imagePath='res:/ui/Texture/WindowIcons/market.png', imageSize=32)],
 AchievementConsts.PLACE_SELL_ORDER: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/InventoryNeocom', imagePath='res:/ui/Texture/WindowIcons/items.png', imageSize=32)],
 AchievementConsts.UNDOCK_FROM_STATION: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/UndockStationServices', imagePath='res:/ui/Texture/classes/Achievements/undockIcon.png', imageSize=32)],
 AchievementConsts.USE_STARGATE: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/StargateBracket', imagePath='res:/UI/Texture/Shared/Brackets/stargate.png', imageSize=16), TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/JumpCommand', imagePath='res:/UI/Texture/Icons/44_32_39.png', imageSize=32)],
 AchievementConsts.JUMP_TO_NEXT_SYSTEM: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/StargateBracketNextSystem', imagePath='res:/UI/Texture/Shared/Brackets/stargate.png', imageSize=16, imageColor=(1, 1, 0, 1)), TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/JumpCommand', imagePath='res:/UI/Texture/Icons/44_32_39.png', imageSize=32)],
 AchievementConsts.OPEN_MAP: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/MapNeocom', imagePath='res:/ui/Texture/WindowIcons/map.png', imageSize=32)],
 AchievementConsts.ACTIVATE_AUTOPILOT: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/AutopilotCommand', imagePath='res:/UI/Texture/Icons/44_32_12.png', imageSize=32)],
 AchievementConsts.SEND_EVEMAIL: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/MailNeocom', imagePath='res:/ui/Texture/WindowIcons/evemail.png', imageSize=32)],
 AchievementConsts.CHAT_IN_LOCAL: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/ChatChannels', imagePath='res:/ui/Texture/WindowIcons/chatchannel.png', imageSize=32)],
 AchievementConsts.ADD_CONTACT: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/PeoplePlaces', imagePath='res:/ui/Texture/WindowIcons/peopleandplaces.png', imageSize=32)],
 AchievementConsts.REFINE_ORE: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/ReprocessingService', imagePath='res:/ui/Texture/WindowIcons/reprocessing.png', imageSize=32)],
 AchievementConsts.LOAD_BLUEPRINT: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/IndustryService', imagePath='res:/ui/Texture/WindowIcons/Industry.png', imageSize=32)],
 AchievementConsts.START_INDUSTRY_JOB: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/ManufacturingActivity', imagePath='res:/ui/Texture/classes/Industry/activity/manufacturing.png', imageSize=26)],
 AchievementConsts.FIT_PROBE_LAUNCHER: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/ProbeLauncher', imagePath='res:/ui/Texture/Icons/49_64_7.png', imageSize=32)],
 AchievementConsts.LAUNCH_PROBES: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/ScannersButton', imagePath='res:/ui/Texture/Icons/44_32_41.png', imageSize=32)],
 AchievementConsts.OPEN_CORP_FINDER: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/CorpNeocom', imagePath='res:/ui/Texture/WindowIcons/corporation.png', imageSize=32)],
 AchievementConsts.TALK_TO_AGENT: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/AgentFinderNeocom', imagePath='res:/ui/Texture/WindowIcons/agentfinder.png', imageSize=32)],
 AchievementConsts.CAREER_AGENT: [TaskInfoEntry_ImageText(text='UI/Achievements/TooltipExtraInfo/CareerAgentHelp', imagePath='res:/ui/Texture/WindowIcons/help.png', imageSize=32)]}
