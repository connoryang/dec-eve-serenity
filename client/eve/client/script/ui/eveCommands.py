#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\eveCommands.py
from carbonui.control.menu import ClearMenuLayer
from eve.client.script.ui.inflight.overviewSettings import OverviewSettings
from eve.client.script.ui.inflight.probeScannerWindow import ProbeScannerWindow
from eve.client.script.parklife.dungeonHelper import IsJessicaOpen
from eve.client.script.ui.camera.cameraUtil import IsNewCameraActive, IsAutoTrackingEnabled
from eve.client.script.ui.inflight.scannerFiles.directionalScanner import DirectionalScanner
from eve.client.script.ui.inflight.shipstance import set_stance
from eve.client.script.ui.shared.fitting.fittingWnd import FittingWindow2
from eve.client.script.ui.shared.fittingGhost.fittingWndGhost import FittingWindowGhost
from eve.client.script.ui.shared.mapView.dockPanelUtil import GetDockPanelManager
from eve.client.script.ui.shared.mapView.mapViewNavigation import MapViewNavigation
from eve.client.script.ui.shared.mapView.mapViewUtil import IsMapBetaEnabled
from eve.client.script.ui.shared.planet.planetWindow import PlanetWindow
from achievements.client.achievementTreeWindow import AchievementTreeWindow
from eve.client.script.ui.shared.systemMenu.betaOptions import IsBetaScannersEnabled
from eve.client.script.ui.view import viewStateConst
import evecamera
from projectdiscovery import IsProjectDiscoveryEnabled
from projectdiscovery.client.window import ProjectDiscoveryWindow
import evetypes
import uicontrols
import uicls
import carbonui.const as uiconst
import uthread
import form
import blue
from eve.client.script.ui.view.viewStateConst import ViewState
import trinity
import sys
import service
import eve.client.script.parklife.fxSequencer as FxSequencer
import moniker
import const
import appUtils
import svc
import destiny
import uix
import localization
import bluepy
import eve.common.script.sys.eveCfg as eveCfg
import carbonui.services.command as command
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import KeepAtRange
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import Orbit
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import DockOrJumpOrActivateGate
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToItem
import evegraphics.settings as gfxsettings
from eve.client.script.ui.shared.industry.industryWnd import Industry
from reprocessing.ui.reprocessingWnd import ReprocessingWnd
import shipmode.data
import urlparse
from eveexceptions.exceptionEater import ExceptionEater
from inventorycommon.util import IsModularShip
from uthread2.callthrottlers import CallCombiner
from eveNewCommands.client.escapeCommand import EscapeCommand
from eveNewCommands.client.escapeCommandAdapter import EscapeCommandAdapter
from eve.devtools.script.enginetools import EngineToolsLauncher
contextFiS = 1
contextIncarna = 2
labelsByFuncName = {'CmdAccelerate': 'UI/Commands/CmdAccelerate',
 'CmdActivateHighPowerSlot1': 'UI/Commands/CmdActivateHighPowerSlot1',
 'CmdActivateHighPowerSlot2': 'UI/Commands/CmdActivateHighPowerSlot2',
 'CmdActivateHighPowerSlot3': 'UI/Commands/CmdActivateHighPowerSlot3',
 'CmdActivateHighPowerSlot4': 'UI/Commands/CmdActivateHighPowerSlot4',
 'CmdActivateHighPowerSlot5': 'UI/Commands/CmdActivateHighPowerSlot5',
 'CmdActivateHighPowerSlot6': 'UI/Commands/CmdActivateHighPowerSlot6',
 'CmdActivateHighPowerSlot7': 'UI/Commands/CmdActivateHighPowerSlot7',
 'CmdActivateHighPowerSlot8': 'UI/Commands/CmdActivateHighPowerSlot8',
 'CmdActivateLowPowerSlot1': 'UI/Commands/CmdActivateLowPowerSlot1',
 'CmdActivateLowPowerSlot2': 'UI/Commands/CmdActivateLowPowerSlot2',
 'CmdActivateLowPowerSlot3': 'UI/Commands/CmdActivateLowPowerSlot3',
 'CmdActivateLowPowerSlot4': 'UI/Commands/CmdActivateLowPowerSlot4',
 'CmdActivateLowPowerSlot5': 'UI/Commands/CmdActivateLowPowerSlot5',
 'CmdActivateLowPowerSlot6': 'UI/Commands/CmdActivateLowPowerSlot6',
 'CmdActivateLowPowerSlot7': 'UI/Commands/CmdActivateLowPowerSlot7',
 'CmdActivateLowPowerSlot8': 'UI/Commands/CmdActivateLowPowerSlot8',
 'CmdActivateMediumPowerSlot1': 'UI/Commands/CmdActivateMediumPowerSlot1',
 'CmdActivateMediumPowerSlot2': 'UI/Commands/CmdActivateMediumPowerSlot2',
 'CmdActivateMediumPowerSlot3': 'UI/Commands/CmdActivateMediumPowerSlot3',
 'CmdActivateMediumPowerSlot4': 'UI/Commands/CmdActivateMediumPowerSlot4',
 'CmdActivateMediumPowerSlot5': 'UI/Commands/CmdActivateMediumPowerSlot5',
 'CmdActivateMediumPowerSlot6': 'UI/Commands/CmdActivateMediumPowerSlot6',
 'CmdActivateMediumPowerSlot7': 'UI/Commands/CmdActivateMediumPowerSlot7',
 'CmdActivateMediumPowerSlot8': 'UI/Commands/CmdActivateMediumPowerSlot8',
 'CmdAlignToItem': 'UI/Commands/CmdAlignToItem',
 'CmdApproachItem': 'UI/Commands/CmdApproachItem',
 'CmdCycleFleetBroadcastScope': 'UI/Commands/CmdCycleFleetBroadcastScope',
 'CmdDecelerate': 'UI/Commands/CmdDecelerate',
 'CmdDockOrJumpOrActivateGate': 'UI/Commands/CmdDockOrJumpOrActivateGate',
 'CmdDronesEngage': 'UI/Commands/CmdDronesEngage',
 'CmdDronesReturnAndOrbit': 'UI/Commands/CmdDronesReturnAndOrbit',
 'CmdDronesReturnToBay': 'UI/Commands/CmdDronesReturnToBay',
 'CmdExitStation': 'UI/Commands/CmdExitStation',
 'CmdEnterCQ': 'UI/Commands/EnterCQ',
 'CmdEnterHangar': 'UI/Commands/EnterHangar',
 'CmdFleetBroadcast_EnemySpotted': 'UI/Fleet/FleetBroadcast/Commands/EnemySpotted',
 'CmdFleetBroadcast_HealArmor': 'UI/Fleet/FleetBroadcast/Commands/HealArmor',
 'CmdFleetBroadcast_HealCapacitor': 'UI/Fleet/FleetBroadcast/Commands/HealCapacitor',
 'CmdFleetBroadcast_HealShield': 'UI/Fleet/FleetBroadcast/Commands/HealShield',
 'CmdFleetBroadcast_HoldPosition': 'UI/Fleet/FleetBroadcast/Commands/HoldPosition',
 'CmdFleetBroadcast_InPosition': 'UI/Fleet/FleetBroadcast/Commands/InPosition',
 'CmdFleetBroadcast_JumpBeacon': 'UI/Fleet/FleetBroadcast/Commands/JumpBeacon',
 'CmdFleetBroadcast_Location': 'UI/Fleet/FleetBroadcast/Commands/Location',
 'CmdFleetBroadcast_NeedBackup': 'UI/Fleet/FleetBroadcast/Commands/NeedBackup',
 'CmdForceFadeFromBlack': 'UI/Commands/CmdForceFadeFromBlack',
 'CmdHideCursor': 'UI/Commands/CmdHideCursor',
 'CmdHideUI': 'UI/Commands/CmdHideUI',
 'CmdKeepItemAtRange': 'UI/Commands/CmdKeepItemAtRange',
 'CmdLockTargetItem': 'UI/Commands/CmdLockTargetItem',
 'CmdSelectTargetItem': 'UI/Commands/CmdSelectTargetItem',
 'CmdLogOff': 'UI/Commands/CmdLogOff',
 'CmdMoveBackward': 'UI/Commands/CmdMoveBackward',
 'CmdMoveForward': 'UI/Commands/CmdMoveForward',
 'CmdMoveLeft': 'UI/Commands/CmdMoveLeft',
 'CmdMoveRight': 'UI/Commands/CmdMoveRight',
 'CmdNextStackedWindow': 'UI/Commands/CmdNextStackedWindow',
 'CmdNextTab': 'UI/Commands/CmdNextTab',
 'CmdOpenNewMessage': 'UI/Commands/CmdOpenNewMessage',
 'CmdOrbitItem': 'UI/Commands/CmdOrbitItem',
 'CmdOverloadHighPowerRack': 'UI/Commands/CmdOverloadHighPowerRack',
 'CmdOverloadHighPowerSlot1': 'UI/Commands/CmdOverloadHighPowerSlot1',
 'CmdOverloadHighPowerSlot2': 'UI/Commands/CmdOverloadHighPowerSlot2',
 'CmdOverloadHighPowerSlot3': 'UI/Commands/CmdOverloadHighPowerSlot3',
 'CmdOverloadHighPowerSlot4': 'UI/Commands/CmdOverloadHighPowerSlot4',
 'CmdOverloadHighPowerSlot5': 'UI/Commands/CmdOverloadHighPowerSlot5',
 'CmdOverloadHighPowerSlot6': 'UI/Commands/CmdOverloadHighPowerSlot6',
 'CmdOverloadHighPowerSlot7': 'UI/Commands/CmdOverloadHighPowerSlot7',
 'CmdOverloadHighPowerSlot8': 'UI/Commands/CmdOverloadHighPowerSlot8',
 'CmdOverloadLowPowerRack': 'UI/Commands/CmdOverloadLowPowerRack',
 'CmdOverloadLowPowerSlot1': 'UI/Commands/CmdOverloadLowPowerSlot1',
 'CmdOverloadLowPowerSlot2': 'UI/Commands/CmdOverloadLowPowerSlot2',
 'CmdOverloadLowPowerSlot3': 'UI/Commands/CmdOverloadLowPowerSlot3',
 'CmdOverloadLowPowerSlot4': 'UI/Commands/CmdOverloadLowPowerSlot4',
 'CmdOverloadLowPowerSlot5': 'UI/Commands/CmdOverloadLowPowerSlot5',
 'CmdOverloadLowPowerSlot6': 'UI/Commands/CmdOverloadLowPowerSlot6',
 'CmdOverloadLowPowerSlot7': 'UI/Commands/CmdOverloadLowPowerSlot7',
 'CmdOverloadLowPowerSlot8': 'UI/Commands/CmdOverloadLowPowerSlot8',
 'CmdOverloadMediumPowerRack': 'UI/Commands/CmdOverloadMediumPowerRack',
 'CmdOverloadMediumPowerSlot1': 'UI/Commands/CmdOverloadMediumPowerSlot1',
 'CmdOverloadMediumPowerSlot2': 'UI/Commands/CmdOverloadMediumPowerSlot2',
 'CmdOverloadMediumPowerSlot3': 'UI/Commands/CmdOverloadMediumPowerSlot3',
 'CmdOverloadMediumPowerSlot4': 'UI/Commands/CmdOverloadMediumPowerSlot4',
 'CmdOverloadMediumPowerSlot5': 'UI/Commands/CmdOverloadMediumPowerSlot5',
 'CmdOverloadMediumPowerSlot6': 'UI/Commands/CmdOverloadMediumPowerSlot6',
 'CmdOverloadMediumPowerSlot7': 'UI/Commands/CmdOverloadMediumPowerSlot7',
 'CmdOverloadMediumPowerSlot8': 'UI/Commands/CmdOverloadMediumPowerSlot8',
 'CmdPickPortrait0': 'UI/Commands/PickPortrait0',
 'CmdPickPortrait1': 'UI/Commands/PickPortrait1',
 'CmdPickPortrait2': 'UI/Commands/PickPortrait2',
 'CmdPickPortrait3': 'UI/Commands/PickPortrait3',
 'CmdPrevStackedWindow': 'UI/Commands/CmdPrevStackedWindow',
 'CmdPrevTab': 'UI/Commands/CmdPrevTab',
 'CmdQuitGame': 'UI/Commands/CmdQuitGame',
 'CmdReconnectToDrones': 'UI/Commands/ReconnectToLostDrones',
 'CmdReloadAmmo': 'UI/Commands/CmdReloadAmmo',
 'CmdResetMonitor': 'UI/Commands/CmdResetMonitor',
 'CmdSelectNextTarget': 'UI/Commands/CmdSelectNextTarget',
 'CmdSelectPrevTarget': 'UI/Commands/CmdSelectPrevTarget',
 'CmdSendBroadcast_Target': 'UI/Commands/CmdSendBroadcast_Target',
 'CmdSetChatChannelFocus': 'UI/Commands/CmdSetChatChannelFocus',
 'CmdSetOverviewFocus': 'UI/Commands/CmdSetOverviewFocus',
 'CmdSetShipFullSpeed': 'UI/Commands/CmdSetShipFullSpeed',
 'CmdShowItemInfo': 'UI/Commands/CmdShowItemInfo',
 'CmdStopShip': 'UI/Commands/CmdStopShip',
 'CmdToggleAggressivePassive': 'UI/Commands/CmdToggleAggressivePassive',
 'CmdToggleAutopilot': 'UI/Commands/CmdToggleAutopilot',
 'CmdToggleCombatView': 'UI/Commands/CmdToggleCombatView',
 'CmdToggleDroneFocusFire': 'UI/Commands/CmdToggleDroneFocusFire',
 'CmdToggleEffects': 'UI/Commands/CmdToggleEffects',
 'CmdToggleEffectTurrets': 'UI/Commands/CmdToggleEffectTurrets',
 'CmdToggleFighterAttackAndFollow': 'UI/Commands/CmdToggleFighterAttackAndFollow',
 'CmdToggleLookAtItem': 'UI/Commands/CmdToggleLookAtItem',
 'CmdToggleCameraTracking': 'UI/Commands/CmdToggleCameraTracking',
 'CmdToggleShowAllBrackets': 'UI/Commands/CmdToggleShowAllBrackets',
 'CmdToggleShowNoBrackets': 'UI/Commands/CmdToggleShowNoBrackets',
 'CmdToggleShowSpecialBrackets': 'UI/Commands/CmdToggleShowSpecialBrackets',
 'CmdToggleTacticalOverlay': 'UI/Commands/CmdToggleTacticalOverlay',
 'CmdToggleTargetItem': 'UI/Commands/CmdToggleTargetItem',
 'CmdUnlockTargetItem': 'UI/Commands/CmdUnlockTargetItem',
 'CmdWarpToItem': 'UI/Commands/CmdWarpToItem',
 'CmdOpenRadialMenu': 'UI/Commands/CmdOpenRadialMenu',
 'CmdRefreshDirectionalScan': 'UI/Commands/CmdRefreshDirectionalScan',
 'CmdToggleAutoTracking': 'UI/Commands/CmdToggleAutoTracking',
 'WinCmdToggleWindowed': 'UI/Commands/WinCmdToggleWindowed',
 'CmdToggleTrackSelectedItem': 'UI/Commands/CmdToggleTrackSelectedItem',
 'CmdTrackingCameraCenterPosition': 'UI/Commands/CmdTrackingCameraCenterPosition',
 'CmdTrackingCameraCustomPosition': 'UI/Commands/CmdTrackingCameraCustomPosition',
 'CmdTrackingCameraTogglePosition': 'UI/Commands/CmdTrackingCameraTogglePosition',
 'CmdSetCameraPOV': 'UI/Commands/CmdSetCameraPOV',
 'CmdSetCameraOrbit': 'UI/Commands/CmdSetCameraOrbit',
 'CmdSetCameraTactical': 'UI/Commands/CmdSetCameraTactical',
 'CmdTagItem_1': 'UI/Commands/CmdTagItem_1',
 'CmdTagItem_2': 'UI/Commands/CmdTagItem_2',
 'CmdTagItem_3': 'UI/Commands/CmdTagItem_3',
 'CmdTagItem_A': 'UI/Commands/CmdTagItem_A',
 'CmdTagItem_B': 'UI/Commands/CmdTagItem_B',
 'CmdTagItem_C': 'UI/Commands/CmdTagItem_C',
 'CmdTagItem_X': 'UI/Commands/CmdTagItem_X',
 'CmdTagItem_Y': 'UI/Commands/CmdTagItem_Y',
 'CmdTagItem_Z': 'UI/Commands/CmdTagItem_Z',
 'CmdTagItem_123': 'UI/Commands/CmdTagItem_123',
 'CmdTagItem_ABC': 'UI/Commands/CmdTagItem_ABC',
 'CmdTagItem_XYZ': 'UI/Commands/CmdTagItem_XYZ',
 'CmdTagItem_123456789': 'UI/Commands/CmdTagItem_123456789',
 'CmdTagItem_ABCDEFGHI': 'UI/Commands/CmdTagItem_ABCDEFGHI',
 'CmdToggleSensorOverlay': 'UI/Commands/CmdToggleSensorOverlay',
 'CmdCreateBookmark': 'UI/Inflight/BookmarkLocation',
 'ToggleAurumStore': 'UI/Commands/OpenStore',
 'ToggleRedeemItems': 'UI/Commands/RedeemItems',
 'CmdFlightControlsUp': 'UI/Commands/CmdFlightControlsUp',
 'CmdFlightControlsDown': 'UI/Commands/CmdFlightControlsDown',
 'CmdFlightControlsLeft': 'UI/Commands/CmdFlightControlsLeft',
 'CmdFlightControlsRight': 'UI/Commands/CmdFlightControlsRight',
 'CmdToggleSystemMenu': 'UI/Commands/CmdToggleSystemMenu',
 'CmdSetDefenceStance': 'UI/Commands/CmdSetDefenceStance',
 'CmdSetSniperStance': 'UI/Commands/CmdSetSniperStance',
 'CmdSetSpeedStance': 'UI/Commands/CmdSetSpeedStance',
 'CmdToggleProjectDiscovery': 'UI/Commands/CmdToggleProjectDiscovery'}
CATEGORIES = {'window': 'UI/SystemMenu/Shortcuts/WindowTab',
 'combat': 'UI/SystemMenu/Shortcuts/CombatTab',
 'general': 'UI/SystemMenu/Shortcuts/GeneralTab',
 'navigation': 'UI/SystemMenu/Shortcuts/NavigationTab',
 'modules': 'UI/SystemMenu/Shortcuts/ModulesTab',
 'drones': 'UI/SystemMenu/Shortcuts/DronesTab',
 'charactercreator': 'UI/CharacterCreation',
 'movement': 'UI/SystemMenu/Shortcuts/CharacterMovementTab'}

class EveCommandService(svc.cmd):
    __guid__ = 'svc.eveCmd'
    __displayname__ = 'Command service'
    __replaceservice__ = 'cmd'
    __notifyevents__ = ['OnSessionChanged']
    __exportedcalls__ = {'OpenMilitia': [service.ROLE_IGB]}
    __categoryToContext__ = {'general': (contextFiS, contextIncarna),
     'window': (contextFiS, contextIncarna),
     'combat': (contextFiS,),
     'drones': (contextFiS,),
     'modules': (contextFiS,),
     'navigation': (contextFiS,),
     'movement': (contextIncarna,),
     'charactercreator': (contextIncarna,)}
    __dependencies__ = svc.cmd.__dependencies__ + ['menu']

    def Run(self, memStream = None):
        svc.cmd.Run(self, memStream)
        self.combatFunctionLoaded = None
        self.combatCmdLoaded = None
        self.combatCmdCurrentHasExecuted = False
        self.combatCmdUnloadFunc = None
        self.contextToCommand = {}
        self.labelsByFuncName.update(labelsByFuncName)
        self._telemetrySessionActive = False
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_ACTIVE, self.OnApplicationFocusChanged)
        self.isCmdQuitPending = False
        self.commandMemory = {}
        self.openingWndsAutomatically = False
        self.SetSpeedFractionThrottled = CallCombiner(self.SetSpeedFraction, 0.3)

    def Reload(self, forceGenericOnly = False):
        svc.cmd.Reload(self, forceGenericOnly)
        change = {}
        self.contextToCommand = {}
        self.LoadAllAccelerators()
        self.commandMemory = {}

    def OnSessionChanged(self, isRemote, sess, change):
        svc.cmd.OnSessionChanged(self, isRemote, sess, change)
        if 'locationid' in change:
            self.LoadAllAccelerators()

    def LoadAllAccelerators(self):
        self.commandMap.UnloadAllAccelerators()
        self.commandMap.LoadAcceleratorsByCategory('general')
        self.commandMap.LoadAcceleratorsByCategory('window')
        if getattr(session, 'locationid', None):
            if eveCfg.IsWorldSpace(session.locationid) or eveCfg.IsStation(session.locationid):
                self.commandMap.LoadAcceleratorsByCategory('movement')
            else:
                self.commandMap.LoadAcceleratorsByCategory('combat')
                self.commandMap.LoadAcceleratorsByCategory('drones')
                self.commandMap.LoadAcceleratorsByCategory('modules')
                self.commandMap.LoadAcceleratorsByCategory('navigation')

    def OnApplicationFocusChanged(self, obj, eventID, params):
        if not obj:
            return True
        if getattr(session, 'locationid', None) and eveCfg.IsSolarSystem(session.locationid):
            cmds = self.commandMap.GetAllCommands()
            combatCmds = [ cmd for cmd in cmds if cmd.category == 'combat' ]
            for cmd in combatCmds:
                allPressed = True
                if not cmd.shortcut:
                    continue
                for key in cmd.shortcut:
                    if not uicore.uilib.Key(key):
                        allPressed = False

                if allPressed:
                    cmd.callback()
                    return True

        return True

    def GetCategoryContext(self, category):
        return self.__categoryToContext__[category]

    def CheckContextIntersection(self, context1, context2):
        for context in context1:
            if context in context2:
                return True

        return False

    def CheckDuplicateShortcuts(self):
        for cmd in self.defaultShortcutMapping:
            for cmdCheck in self.defaultShortcutMapping:
                if cmdCheck.shortcut:
                    sameName = cmdCheck.name == cmd.name
                    sameShortcut = cmdCheck.shortcut == cmd.shortcut
                    cmdCheckContext = self.__categoryToContext__[cmdCheck.category]
                    cmdContext = self.__categoryToContext__[cmd.category]
                    sameContext = self.CheckContextIntersection(cmdCheckContext, cmdContext)
                    if sameShortcut and sameContext and not sameName:
                        self.LogError('Same default shortcut used for multiple commands:', cmd)

    def SetDefaultShortcutMappingGAME(self):
        ret = []
        c = command.CommandMapping
        CTRL = uiconst.VK_CONTROL
        ALT = uiconst.VK_MENU
        SHIFT = uiconst.VK_SHIFT
        m = [c(self.CmdOverloadLowPowerRack, (CTRL, uiconst.VK_1)),
         c(self.CmdOverloadMediumPowerRack, (CTRL, uiconst.VK_2)),
         c(self.CmdOverloadHighPowerRack, (CTRL, uiconst.VK_3)),
         c(self.CmdReloadAmmo, (CTRL, uiconst.VK_R))]
        for i in xrange(1, 9):
            key = getattr(uiconst, 'VK_F%s' % i)
            m.extend([c(getattr(self, 'CmdActivateHighPowerSlot%s' % i), key),
             c(getattr(self, 'CmdActivateMediumPowerSlot%s' % i), (ALT, key)),
             c(getattr(self, 'CmdActivateLowPowerSlot%s' % i), (CTRL, key)),
             c(getattr(self, 'CmdOverloadHighPowerSlot%s' % i), (SHIFT, key)),
             c(getattr(self, 'CmdOverloadMediumPowerSlot%s' % i), (ALT, SHIFT, key)),
             c(getattr(self, 'CmdOverloadLowPowerSlot%s' % i), (CTRL, SHIFT, key))])

        for cm in m:
            cm.category = 'modules'
            ret.append(cm)

        m = [c(self.CmdSelectPrevTarget, (ALT, uiconst.VK_LEFT)),
         c(self.CmdSelectNextTarget, (ALT, uiconst.VK_RIGHT)),
         c(self.CmdToggleAutopilot, (CTRL, uiconst.VK_S)),
         c(self.CmdToggleTacticalOverlay, (CTRL, uiconst.VK_D)),
         c(self.CmdDecelerate, uiconst.VK_SUBTRACT, repeatable=True),
         c(self.CmdAccelerate, uiconst.VK_ADD, repeatable=True),
         c(self.CmdStopShip, (CTRL, uiconst.VK_SPACE)),
         c(self.CmdSetShipFullSpeed, (ALT, CTRL, uiconst.VK_SPACE)),
         c(self.CmdFlightControlsUp, uiconst.VK_UP),
         c(self.CmdFlightControlsDown, uiconst.VK_DOWN),
         c(self.CmdFlightControlsLeft, uiconst.VK_LEFT),
         c(self.CmdFlightControlsRight, uiconst.VK_RIGHT),
         c(self.CmdToggleShowAllBrackets, (ALT, uiconst.VK_Z)),
         c(self.CmdToggleShowNoBrackets, (ALT, SHIFT, uiconst.VK_Z)),
         c(self.CmdToggleShowSpecialBrackets, (ALT, SHIFT, uiconst.VK_X)),
         c(self.CmdFleetBroadcast_EnemySpotted, uiconst.VK_Z),
         c(self.CmdFleetBroadcast_NeedBackup, None),
         c(self.CmdFleetBroadcast_HealArmor, None),
         c(self.CmdFleetBroadcast_HealShield, None),
         c(self.CmdFleetBroadcast_HealCapacitor, None),
         c(self.CmdFleetBroadcast_InPosition, None),
         c(self.CmdFleetBroadcast_HoldPosition, None),
         c(self.CmdFleetBroadcast_JumpBeacon, None),
         c(self.CmdFleetBroadcast_Location, None),
         c(self.CmdSendBroadcast_Target, uiconst.VK_X),
         c(self.CmdCycleFleetBroadcastScope, None),
         c(self.CmdToggleTrackSelectedItem, uiconst.VK_C if not IsNewCameraActive() else None),
         c(self.CmdTrackingCameraCenterPosition, None),
         c(self.CmdTrackingCameraCustomPosition, None),
         c(self.CmdTrackingCameraTogglePosition, None),
         c(self.CmdSetCameraTactical, (ALT, uiconst.VK_1)),
         c(self.CmdSetCameraOrbit, (ALT, uiconst.VK_2)),
         c(self.CmdSetCameraPOV, (ALT, uiconst.VK_3)),
         c(self.CmdToggleSensorOverlay, (CTRL, uiconst.VK_O)),
         c(self.CmdCreateBookmark, (CTRL, uiconst.VK_B))]
        for cm in m:
            cm.category = 'navigation'
            ret.append(cm)

        m = [c(self.CmdDronesEngage, uiconst.VK_F),
         c(self.CmdDronesReturnAndOrbit, (SHIFT, ALT, uiconst.VK_R)),
         c(self.CmdDronesReturnToBay, (SHIFT, uiconst.VK_R)),
         c(self.CmdReconnectToDrones, None),
         c(self.CmdToggleAggressivePassive, None),
         c(self.CmdToggleDroneFocusFire, None),
         c(self.CmdToggleFighterAttackAndFollow, None)]
        for cm in m:
            cm.category = 'drones'
            ret.append(cm)

        m = [c(self.CmdPrevStackedWindow, (CTRL, SHIFT, uiconst.VK_PRIOR)),
         c(self.CmdNextStackedWindow, (CTRL, SHIFT, uiconst.VK_NEXT)),
         c(self.CmdPrevTab, (CTRL, uiconst.VK_PRIOR)),
         c(self.CmdNextTab, (CTRL, uiconst.VK_NEXT)),
         c(self.CmdExitStation, None),
         c(self.CmdEnterCQ, None),
         c(self.CmdEnterHangar, None),
         c(self.CmdHideUI, (CTRL, uiconst.VK_F9)),
         c(self.CmdHideCursor, (ALT, uiconst.VK_F9)),
         c(self.CmdToggleEffects, (CTRL,
          ALT,
          SHIFT,
          uiconst.VK_E)),
         c(self.CmdToggleEffectTurrets, (CTRL,
          ALT,
          SHIFT,
          uiconst.VK_T)),
         c(self.CmdOpenRadialMenu, None),
         c(self.CmdZoomIn, None, repeatable=True),
         c(self.CmdZoomOut, None, repeatable=True),
         c(self.CmdToggleSystemMenu, None, enabled=False)]
        ret.extend(m)
        if bool(session.role & service.ROLE_CONTENT):
            ret.append(c(self.OpenDungeonEditor, (CTRL, SHIFT, uiconst.VK_D)))
        if bool(session.role & service.ROLEMASK_ELEVATEDPLAYER):
            ret.append(c(self.CmdToggleCombatView, (CTRL, ALT, uiconst.VK_T)))
        m = [c(self.CmdToggleTargetItem, None),
         c(self.CmdLockTargetItem, CTRL),
         c(self.CmdSelectTargetItem, SHIFT),
         c(self.CmdUnlockTargetItem, (CTRL, SHIFT)),
         c(self.CmdToggleLookAtItem, ALT),
         c(self.CmdToggleCameraTracking, uiconst.VK_C if IsNewCameraActive() else None),
         c(self.CmdApproachItem, uiconst.VK_Q),
         c(self.CmdAlignToItem, uiconst.VK_A),
         c(self.CmdOrbitItem, uiconst.VK_W),
         c(self.CmdKeepItemAtRange, uiconst.VK_E),
         c(self.CmdShowItemInfo, uiconst.VK_T),
         c(self.CmdDockOrJumpOrActivateGate, uiconst.VK_D),
         c(self.CmdWarpToItem, uiconst.VK_S),
         c(self.MakeCmdTagItem('1'), uiconst.VK_1),
         c(self.MakeCmdTagItem('2'), uiconst.VK_2),
         c(self.MakeCmdTagItem('3'), uiconst.VK_3),
         c(self.MakeCmdTagItem('A'), uiconst.VK_4),
         c(self.MakeCmdTagItem('B'), uiconst.VK_5),
         c(self.MakeCmdTagItem('C'), uiconst.VK_6),
         c(self.MakeCmdTagItem('X'), None),
         c(self.MakeCmdTagItem('Y'), None),
         c(self.MakeCmdTagItem('Z'), None),
         c(self.MakeCmdTagItemFromSequence(['1', '2', '3']), uiconst.VK_7),
         c(self.MakeCmdTagItemFromSequence(['A', 'B', 'C']), uiconst.VK_8),
         c(self.MakeCmdTagItemFromSequence(['X', 'Y', 'Z']), uiconst.VK_9),
         c(self.MakeCmdTagItemFromSequence(['1',
          '2',
          '3',
          '4',
          '5',
          '6',
          '7',
          '8',
          '9']), None),
         c(self.MakeCmdTagItemFromSequence(['A',
          'B',
          'C',
          'D',
          'E',
          'F',
          'G',
          'H',
          'I']), None),
         c(self.CmdSetDefenceStance, (SHIFT, uiconst.VK_1)),
         c(self.CmdSetSniperStance, (SHIFT, uiconst.VK_2)),
         c(self.CmdSetSpeedStance, (SHIFT, uiconst.VK_3)),
         c(self.CmdIncreaseProbeScanRange, None),
         c(self.CmdDecreaseProbeScanRange, None),
         c(self.CmdRefreshProbeScan, None),
         c(self.CmdRefreshDirectionalScan, uiconst.VK_V),
         c(self.CmdToggleAutoTracking, (SHIFT, uiconst.VK_C))]
        for cm in m:
            cm.category = 'combat'
            ret.append(cm)

        m = [c(self.CmdOpenNewMessage, None),
         c(self.CmdSetChatChannelFocus, uiconst.VK_SPACE),
         c(self.CmdSetOverviewFocus, (ALT, uiconst.VK_SPACE)),
         c(self.CmdToggleMap, uiconst.VK_F10),
         c(self.CmdToggleSolarSystemMap, uiconst.VK_F9),
         c(self.CmdToggleMapBeta, (CTRL, uiconst.VK_F10)),
         c(self.CmdToggleShipTree, None),
         c(self.OpenAssets, (ALT, uiconst.VK_T)),
         c(self.OpenBrowser, (ALT, uiconst.VK_B)),
         c(self.OpenCalculator, None),
         c(self.OpenCalendar, None),
         c(self.OpenCapitalNavigation, None),
         c(self.OpenCargoHoldOfActiveShip, None),
         c(self.OpenOreHoldOfActiveShip, None),
         c(self.OpenMineralHoldOfActiveShip, None),
         c(self.OpenPlanetaryCommoditiesHoldOfActiveShip, None),
         c(self.OpenFuelBayOfActiveShip, None),
         c(self.OpenChannels, None),
         c(self.OpenCharactersheet, (ALT, uiconst.VK_A)),
         c(self.OpenConfigMenu, None),
         c(self.OpenContracts, None),
         c(self.OpenCorpDeliveries, None),
         c(self.OpenCorpHangar, None),
         c(self.OpenCorporationPanel, None),
         c(self.OpenDroneBayOfActiveShip, None),
         c(self.OpenIndustry, (ALT, uiconst.VK_S)),
         c(self.OpenFitting, (ALT, uiconst.VK_F)),
         c(self.OpenFleet, None),
         c(self.OpenFpsMonitor, (CTRL, uiconst.VK_F)),
         c(self.OpenHangarFloor, (ALT, uiconst.VK_G)),
         c(self.OpenHelp, uiconst.VK_F12),
         c(self.OpenInsurance, None),
         c(self.OpenJournal, (ALT, uiconst.VK_J)),
         c(self.OpenLog, None),
         c(self.OpenLpstore, None),
         c(self.OpenMail, (ALT, uiconst.VK_I)),
         c(self.OpenMapBrowser, uiconst.VK_F11),
         c(self.OpenMarket, (ALT, uiconst.VK_R)),
         c(self.OpenMedical, None),
         c(self.OpenMilitia, None),
         c(self.OpenBountyOffice, None),
         c(self.OpenMoonMining, None),
         c(self.OpenNotepad, None),
         c(self.OpenOverviewSettings, None),
         c(self.OpenPeopleAndPlaces, (ALT, uiconst.VK_E)),
         c(self.OpenCharacterCustomization, None),
         c(self.OpenRepairshop, None),
         c(self.OpenReprocessingPlant, None),
         c(self.OpenScanner, (ALT, uiconst.VK_P)),
         c(self.OpenDirectionalScanner, (ALT, uiconst.VK_D)),
         c(self.OpenSecurityOffice, None),
         c(self.OpenShipConfig, None),
         c(self.OpenShipHangar, (ALT, uiconst.VK_N)),
         c(self.OpenInventory, (ALT, uiconst.VK_C)),
         c(self.OpenSkillQueueWindow, (ALT, uiconst.VK_X)),
         c(self.OpenStationManagement, None),
         c(self.OpenTutorial, None),
         c(self.OpenWallet, (ALT, uiconst.VK_W)),
         c(self.CmdForceFadeFromBlack, (SHIFT, uiconst.VK_BACK)),
         c(self.OpenAgentFinder, None),
         c(self.OpenCompare, None),
         c(self.OpenEveMenu, uiconst.VK_OEM_5),
         c(self.OpenFittingMgmt, None),
         c(self.ToggleAurumStore, (ALT, uiconst.VK_4)),
         c(self.ToggleRedeemItems, (ALT, uiconst.VK_Y)),
         c(self.OpenPlanets, None),
         c(self.ToggleOpportunity, None)]
        if IsProjectDiscoveryEnabled():
            m.append(c(self.ToggleProjectDiscovery, None))
        if not blue.sysinfo.isTransgaming:
            m.append(c(self.OpenTwitchStreaming, None))
        if bool(session.role & service.ROLE_PROGRAMMER):
            m.append(c(self.OpenUIDebugger, None))
            m.append(c(self.ToggleTelemetryRecord, None))
        for cm in m:
            cm.category = 'window'
            ret.append(cm)

        m = [c(self.CmdMoveForward, uiconst.VK_W),
         c(self.CmdMoveBackward, uiconst.VK_S),
         c(self.CmdMoveLeft, uiconst.VK_A),
         c(self.CmdMoveRight, uiconst.VK_D)]
        for cm in m:
            cm.category = 'movement'
            ret.append(cm)

        m = [c(self.CmdPickPortrait0, uiconst.VK_F1),
         c(self.CmdPickPortrait1, uiconst.VK_F2),
         c(self.CmdPickPortrait2, uiconst.VK_F3),
         c(self.CmdPickPortrait3, uiconst.VK_F4)]
        for cm in m:
            cm.category = 'charactercreator'
            ret.append(cm)

        return ret

    def CmdActivateHighPowerSlot1(self, *args):
        self._cmdshipui(0, 0)

    def CmdActivateHighPowerSlot2(self, *args):
        self._cmdshipui(1, 0)

    def CmdActivateHighPowerSlot3(self, *args):
        self._cmdshipui(2, 0)

    def CmdActivateHighPowerSlot4(self, *args):
        self._cmdshipui(3, 0)

    def CmdActivateHighPowerSlot5(self, *args):
        self._cmdshipui(4, 0)

    def CmdActivateHighPowerSlot6(self, *args):
        self._cmdshipui(5, 0)

    def CmdActivateHighPowerSlot7(self, *args):
        self._cmdshipui(6, 0)

    def CmdActivateHighPowerSlot8(self, *args):
        self._cmdshipui(7, 0)

    def CmdActivateMediumPowerSlot1(self, *args):
        self._cmdshipui(0, 1)

    def CmdActivateMediumPowerSlot2(self, *args):
        self._cmdshipui(1, 1)

    def CmdActivateMediumPowerSlot3(self, *args):
        self._cmdshipui(2, 1)

    def CmdActivateMediumPowerSlot4(self, *args):
        self._cmdshipui(3, 1)

    def CmdActivateMediumPowerSlot5(self, *args):
        self._cmdshipui(4, 1)

    def CmdActivateMediumPowerSlot6(self, *args):
        self._cmdshipui(5, 1)

    def CmdActivateMediumPowerSlot7(self, *args):
        self._cmdshipui(6, 1)

    def CmdActivateMediumPowerSlot8(self, *args):
        self._cmdshipui(7, 1)

    def CmdActivateLowPowerSlot1(self, *args):
        self._cmdshipui(0, 2)

    def CmdActivateLowPowerSlot2(self, *args):
        self._cmdshipui(1, 2)

    def CmdActivateLowPowerSlot3(self, *args):
        self._cmdshipui(2, 2)

    def CmdActivateLowPowerSlot4(self, *args):
        self._cmdshipui(3, 2)

    def CmdActivateLowPowerSlot5(self, *args):
        self._cmdshipui(4, 2)

    def CmdActivateLowPowerSlot6(self, *args):
        self._cmdshipui(5, 2)

    def CmdActivateLowPowerSlot7(self, *args):
        self._cmdshipui(6, 2)

    def CmdActivateLowPowerSlot8(self, *args):
        self._cmdshipui(7, 2)

    def CmdOverloadHighPowerSlot1(self, *args):
        self._cmdoverload(0, 0)

    def CmdOverloadHighPowerSlot2(self, *args):
        self._cmdoverload(1, 0)

    def CmdOverloadHighPowerSlot3(self, *args):
        self._cmdoverload(2, 0)

    def CmdOverloadHighPowerSlot4(self, *args):
        self._cmdoverload(3, 0)

    def CmdOverloadHighPowerSlot5(self, *args):
        self._cmdoverload(4, 0)

    def CmdOverloadHighPowerSlot6(self, *args):
        self._cmdoverload(5, 0)

    def CmdOverloadHighPowerSlot7(self, *args):
        self._cmdoverload(6, 0)

    def CmdOverloadHighPowerSlot8(self, *args):
        self._cmdoverload(7, 0)

    def CmdOverloadMediumPowerSlot1(self, *args):
        self._cmdoverload(0, 1)

    def CmdOverloadMediumPowerSlot2(self, *args):
        self._cmdoverload(1, 1)

    def CmdOverloadMediumPowerSlot3(self, *args):
        self._cmdoverload(2, 1)

    def CmdOverloadMediumPowerSlot4(self, *args):
        self._cmdoverload(3, 1)

    def CmdOverloadMediumPowerSlot5(self, *args):
        self._cmdoverload(4, 1)

    def CmdOverloadMediumPowerSlot6(self, *args):
        self._cmdoverload(5, 1)

    def CmdOverloadMediumPowerSlot7(self, *args):
        self._cmdoverload(6, 1)

    def CmdOverloadMediumPowerSlot8(self, *args):
        self._cmdoverload(7, 1)

    def CmdOverloadLowPowerSlot1(self, *args):
        self._cmdoverload(0, 2)

    def CmdOverloadLowPowerSlot2(self, *args):
        self._cmdoverload(1, 2)

    def CmdOverloadLowPowerSlot3(self, *args):
        self._cmdoverload(2, 2)

    def CmdOverloadLowPowerSlot4(self, *args):
        self._cmdoverload(3, 2)

    def CmdOverloadLowPowerSlot5(self, *args):
        self._cmdoverload(4, 2)

    def CmdOverloadLowPowerSlot6(self, *args):
        self._cmdoverload(5, 2)

    def CmdOverloadLowPowerSlot7(self, *args):
        self._cmdoverload(6, 2)

    def CmdOverloadLowPowerSlot8(self, *args):
        self._cmdoverload(7, 2)

    def CmdOverloadHighPowerRack(self, *args):
        self._cmdoverloadrack('Hi')

    def CmdOverloadMediumPowerRack(self, *args):
        self._cmdoverloadrack('Med')

    def CmdOverloadLowPowerRack(self, *args):
        self._cmdoverloadrack('Lo')

    def CmdSelectPrevTarget(self, *args):
        sm.GetService('target').SelectPrevTarget()
        self.CmdSetOverviewFocus()

    def CmdSelectNextTarget(self, *args):
        sm.GetService('target').SelectNextTarget()
        self.CmdSetOverviewFocus()

    def CmdZoomIn(self, *args):
        self._Zoom(direction=-1)

    CmdZoomIn.nameLabelPath = 'UI/Inflight/ZoomIn'

    def CmdZoomOut(self, *args):
        self._Zoom(direction=1)

    CmdZoomOut.nameLabelPath = 'UI/Inflight/ZoomOut'

    def _Zoom(self, direction):
        viewSvc = sm.GetService('viewState')
        simulatedMouseScroll = 120
        activeWindow = uicore.registry.GetActiveStackOrWindow()
        if activeWindow and hasattr(activeWindow, 'CmdZoomInOut'):
            activeWindow.CmdZoomInOut(direction * simulatedMouseScroll)
        elif viewSvc.IsViewActive('planet', 'starmap', 'systemmap', 'shiptree', 'inflight', 'station', 'hangar'):
            view = viewSvc.GetCurrentView()
            view.ZoomBy(direction * simulatedMouseScroll)

    def CmdToggleAutopilot(self, *args):
        if session.solarsystemid:
            if sm.GetService('autoPilot').GetState():
                sm.GetService('autoPilot').SetOff()
            else:
                sm.GetService('autoPilot').SetOn()

    CmdToggleAutopilot.nameLabelPath = 'Tooltips/Hud/Autopilot'
    CmdToggleAutopilot.descriptionLabelPath = 'Tooltips/Hud/Autopilot_description'

    def CmdToggleTacticalOverlay(self, *args):
        if session.solarsystemid is not None:
            sm.GetService('tactical').ToggleOnOff()

    CmdToggleTacticalOverlay.nameLabelPath = 'Tooltips/Hud/Tactical'
    CmdToggleTacticalOverlay.descriptionLabelPath = 'Tooltips/Hud/Tactical_description'

    def SetSpeedFraction(self, speed):
        remote = sm.GetService('michelle').GetRemotePark()
        if remote:
            remote.CmdSetSpeedFraction(speed)

    def CmdDecelerate(self, *args):
        if eve.session.shipid and eve.session.solarsystemid:
            bp = sm.GetService('michelle').GetBallpark()
            ownBall = bp.GetBall(eve.session.shipid)
            if ownBall is not None:
                self.SetSpeedFractionThrottled(min(1.0, ownBall.speedFraction - 0.1))

    def CmdAccelerate(self, *args):
        if eve.session.shipid and eve.session.solarsystemid:
            rp = sm.GetService('michelle').GetRemotePark()
            bp = sm.GetService('michelle').GetBallpark()
            ownBall = bp.GetBall(eve.session.shipid)
            if rp is not None and ownBall is not None:
                if ownBall.mode == destiny.DSTBALL_STOP and not sm.GetService('autoPilot').GetState():
                    direction = trinity.TriVector(0.0, 0.0, 1.0)
                    currentDirection = ownBall.GetQuaternionAt(blue.os.GetSimTime())
                    direction.TransformQuaternion(currentDirection)
                    rp.CmdGotoDirection(direction.x, direction.y, direction.z)
                    sm.GetService('menu').ClearAlignTargets()
                self.SetSpeedFractionThrottled(min(1.0, ownBall.speedFraction + 0.1))

    def CmdStopShip(self, *args):
        if eve.session.shipid and eve.session.solarsystemid:
            autoPilot = sm.GetService('autoPilot')
            if not sm.GetService('machoNet').GetGlobalConfig().get('newAutoNavigationKillSwitch', False):
                autoPilot.CancelSystemNavigation()
            else:
                autoPilot.AbortApproachAndTryCommand()
                autoPilot.AbortWarpAndTryCommand()
            if session.IsItSafe():
                bp = sm.GetService('michelle').GetRemotePark()
                if bp and session.IsItSafe():
                    bp.CmdStop()
            sm.GetService('logger').AddText(localization.GetByLabel('UI/Commands/ShipStopping'), 'notify')
            sm.GetService('space').DoSetIndicationTextForcefully(localization.GetByLabel('UI/Inflight/Messages/ShipStoppingHeader'), '')
            if autoPilot.GetState():
                autoPilot.SetOff()

    def CmdSetShipFullSpeed(self, *args):
        bp = sm.GetService('michelle').GetBallpark()
        rbp = sm.GetService('michelle').GetRemotePark()
        if bp is None or rbp is None:
            return
        ownBall = bp.GetBall(eve.session.shipid)
        if ownBall and rbp is not None and ownBall.mode == destiny.DSTBALL_STOP:
            if not sm.GetService('autoPilot').GetState():
                direction = trinity.TriVector(0.0, 0.0, 1.0)
                currentDirection = ownBall.GetQuaternionAt(blue.os.GetSimTime())
                direction.TransformQuaternion(currentDirection)
                rbp.CmdGotoDirection(direction.x, direction.y, direction.z)
                sm.GetService('menu').ClearAlignTargets()
        if rbp is not None:
            rbp.CmdSetSpeedFraction(1.0)
            speedText = self._FormatSpeed(ownBall.maxVelocity)
            sm.GetService('logger').AddText(speedText, 'notify')
            sm.GetService('gameui').Say(speedText)

    def _FormatSpeed(self, speed):
        if speed >= 100:
            speed = long(speed)
        return localization.GetByLabel('UI/Commands/SpeedChangedTo', speed=speed)

    def CmdToggleShowAllBrackets(self, *args):
        if session.solarsystemid:
            bracketMgr = sm.GetService('bracket')
            if bracketMgr.ShowingAll():
                bracketMgr.StopShowingAll()
            else:
                bracketMgr.ShowAll()

    def CmdToggleShowNoBrackets(self, *args):
        if session.solarsystemid:
            bracketMgr = sm.GetService('bracket')
            if bracketMgr.ShowingNone():
                bracketMgr.StopShowingNone()
            else:
                bracketMgr.ShowNone()

    def CmdToggleShowSpecialBrackets(self, *args):
        if session.solarsystemid:
            bracketMgr = sm.GetService('bracket')
            bracketMgr.ToggleShowSpecials()

    def CmdReloadAmmo(self, *args):
        if uicore.layer.shipui.isopen:
            uicore.layer.shipui.OnReloadAmmo()

    def _cmdshipui(self, sidx, gidx):
        if uicore.layer.shipui.isopen:
            uicore.layer.shipui.OnF(sidx, gidx)

    def _cmdoverload(self, sidx, gidx):
        if uicore.layer.shipui.isopen:
            uicore.layer.shipui.OnFKeyOverload(sidx, gidx)

    def _cmdoverloadrack(self, what):
        if uicore.layer.shipui.isopen:
            uicore.layer.shipui.ToggleRackOverload(what)

    def CmdQuitGame(self, *args):
        if self.isCmdQuitPending:
            return
        self.isCmdQuitPending = True
        try:
            if sm.GetService('gameui').HasDisconnectionNotice() or uicore.Message('AskQuitGame', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                self.DoQuitGame()
        finally:
            self.isCmdQuitPending = False

    def DoQuitGame(self):
        try:
            sm.GetService('tutorial').OnCloseApp()
            self.settings.SaveSettings()
            if boot.region == 'optic' and not blue.sysinfo.isTransgaming:
                blue.os.ShellExecute('bin:\\eveBanner.exe', const.tianCityBannerUrl)
            sm.GetService('clientStatsSvc').OnProcessExit()
        except:
            self.LogException()
        finally:
            bluepy.Terminate('User requesting close')

    def CmdLogOff(self, *args):
        modalWnd = uicore.registry.GetModalWindow()
        if modalWnd and modalWnd.__guid__ == 'form.MessageBox':
            return
        if uicore.Message('AskLogoffGame', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.settings.SaveSettings()
            appUtils.Reboot('Generic Logoff')

    def CmdDronesEngage(self, *args):
        drones = sm.GetService('michelle').GetDrones()
        if drones is None:
            return
        salvageDroneIDs = []
        droneIDs = []
        for droneID, drone in drones.iteritems():
            typeID = drone[4]
            if evetypes.GetGroupID(typeID) == const.groupSalvageDrone:
                salvageDroneIDs.append(droneID)
            else:
                droneIDs.append(droneID)

        entity = moniker.GetEntityAccess()
        if entity:
            if droneIDs:
                sm.GetService('menu').EngageTarget(droneIDs)
            if salvageDroneIDs:
                sm.GetService('menu').Salvage(salvageDroneIDs)

    def CmdDronesReturnAndOrbit(self, *args):
        drones = sm.GetService('michelle').GetDrones()
        if not drones:
            return
        droneIDs = drones.keys()
        targetID = sm.GetService('target').GetActiveTargetID()
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdReturnHome(droneIDs)
            sm.GetService('menu').HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')
            if droneIDs and targetID:
                eve.Message('Command', {'command': localization.GetByLabel('UI/Commands/DronesReturningAndOrbiting')})

    def CmdDronesReturnToBay(self, *args):
        drones = sm.GetService('michelle').GetDrones()
        if not drones:
            return
        droneIDs = drones.keys()
        targetID = sm.GetService('target').GetActiveTargetID()
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdReturnBay(droneIDs)
            sm.GetService('menu').HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')
            if droneIDs and targetID:
                eve.Message('Command', {'command': localization.GetByLabel('UI/Commands/DronesReturningToDroneBay')})

    def CmdReconnectToDrones(self, *args):
        sm.GetService('menu').ReconnectToDrones()

    def CmdToggleAggressivePassive(self, *args):
        isAggressive = settings.char.ui.Get('droneAggression', cfg.dgmattribs.Get(const.attributeDroneIsAggressive).defaultValue)
        newIsAggressive = (isAggressive + 1) % 2
        droneSettings = {const.attributeDroneIsAggressive: newIsAggressive}
        settings.char.ui.Set('droneAggression', newIsAggressive)
        sm.GetService('godma').GetStateManager().ChangeDroneSettings(droneSettings)

    def CmdToggleDroneFocusFire(self, *args):
        isFocusFire = settings.char.ui.Get('droneFocusFire', cfg.dgmattribs.Get(const.attributeDroneFocusFire).defaultValue)
        newIsFocusFire = (isFocusFire + 1) % 2
        droneSettings = {const.attributeDroneFocusFire: newIsFocusFire}
        settings.char.ui.Set('droneFocusFire', newIsFocusFire)
        sm.GetService('godma').GetStateManager().ChangeDroneSettings(droneSettings)

    def CmdToggleFighterAttackAndFollow(self, *args):
        isFaf = settings.char.ui.Get('fighterAttackAndFollow', cfg.dgmattribs.Get(const.attributeFighterAttackAndFollow).defaultValue)
        newIsFaf = (isFaf + 1) % 2
        droneSettings = {const.attributeFighterAttackAndFollow: newIsFaf}
        settings.char.ui.Set('fighterAttackAndFollow', newIsFaf)
        sm.GetService('godma').GetStateManager().ChangeDroneSettings(droneSettings)

    def WinCmdToggleWindowed(self, *args):
        lastTimeToggled = settings.user.ui.Get('LastTimeToggleWindowed', 0)
        if blue.os.GetWallclockTime() - lastTimeToggled > 2 * const.SEC:
            settings.user.ui.Set('LastTimeToggleWindowed', blue.os.GetWallclockTime())
            sm.GetService('device').ToggleWindowed()

    def CmdResetMonitor(self, *args):
        sm.GetService('device').ResetMonitor()

    def CmdToggleSolarSystemMap(self, *args):
        if eve.session.charid:
            from eve.client.script.ui.shared.mapView.mapViewUtil import ToggleSolarSystemMap
            ToggleSolarSystemMap()

    CmdToggleSolarSystemMap.nameLabelPath = 'UI/Map/MapPallet/btnSolarsystemMap'
    CmdToggleSolarSystemMap.descriptionLabelPath = ''

    def CmdToggleMap(self, *args):
        if eve.session.charid is not None and not getattr(self, 'loadingCharacterCustomization', False):
            ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
            from eve.client.script.ui.shared.mapView.mapViewUtil import IsMapBetaExplicit
            if IsMapBetaExplicit() or ctrl and session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
                self.CmdToggleMapBeta()
            else:
                uthread.new(sm.GetService('map').Toggle).context = 'svc.map.Toggle'
                sm.ScatterEvent('OnClientEvent_OpenMap')

    CmdToggleMap.nameLabelPath = 'UI/Neocom/MapBtn'
    CmdToggleMap.descriptionLabelPath = 'Tooltips/Neocom/Map_description'

    def CmdToggleMapBeta(self, *args):
        if eve.session.charid is not None and not getattr(self, 'loadingCharacterCustomization', False):
            if not IsMapBetaEnabled():
                return
            from eve.client.script.ui.shared.mapView.mapViewPanel import MapViewPanel
            if not MapViewPanel.ClosePanel():
                MapViewPanel.OpenPanel(parent=uicore.layer.main)

    CmdToggleMapBeta.nameString = 'Map Beta'
    CmdToggleMapBeta.descriptionLabelPath = 'Tooltips/Neocom/Map_description'

    def CmdToggleShipTree(self):
        sm.GetService('viewState').ToggleSecondaryView('shiptree')

    CmdToggleShipTree.nameLabelPath = 'UI/Neocom/ShipTreeBtn'
    CmdToggleShipTree.descriptionLabelPath = 'Tooltips/Neocom/ISIS_description'

    def CmdPrevStackedWindow(self, *args):
        wnd = uicore.registry.GetActive()
        if wnd is None or wnd.sr.stack is None:
            return
        tabGroup = wnd.sr.stack.sr.tabs.children[0]
        tabGroup.SelectPrev()

    def CmdNextStackedWindow(self, *args):
        wnd = uicore.registry.GetActive()
        if wnd is None or wnd.sr.stack is None:
            return
        tabGroup = wnd.sr.stack.sr.tabs.children[0]
        tabGroup.SelectNext()

    def CmdPrevTab(self, *args):
        tabGroup = self._GetTabgroup()
        if tabGroup:
            tabGroup.SelectPrev()

    def CmdNextTab(self, *args):
        tabGroup = self._GetTabgroup()
        if tabGroup:
            tabGroup.SelectNext()

    def _GetTabgroup(self):
        wnd = uicore.registry.GetActive()
        if not wnd:
            return
        MAXRECURS = 10
        tabGroup = self._FindTabGroup(wnd.sr.maincontainer, MAXRECURS)
        if not tabGroup and wnd.sr.stack and len(wnd.sr.stack.sr.content.children) > 1:
            tabGroup = self._FindTabGroup(wnd.sr.stack.sr.tabs, MAXRECURS)
        return tabGroup

    def _FindTabGroup(self, parent, maxLevel):
        if isinstance(parent, uicontrols.TabGroup) and not parent.destroyed:
            return parent
        if not hasattr(parent, 'children') or not parent.children or maxLevel == 0:
            return
        blue.pyos.BeNice()
        for c in parent.children:
            tabGroup = self._FindTabGroup(c, maxLevel - 1)
            if tabGroup:
                return tabGroup

    def CmdExitStation(self, *args):
        if session.stationid2 and not uicore.registry.GetModalWindow():
            ccLayer = uicore.layer.Get('charactercreation')
            if ccLayer is not None and ccLayer.isopen:
                return
            if sm.GetService('viewState').HasActiveTransition():
                return
            sm.GetService('station').Exit()

    def CmdEnterCQ(self, *args):
        if sm.GetService('viewState').IsViewActive('station') or session.stationid2 is None:
            return
        change = {'worldspaceid': (session.worldspaceid, session.worldspaceid)}
        uthread.pool('eveCommands::CmdEnterCQ', sm.GetService('viewState').ChangePrimaryView, 'station', change=change)

    def CmdEnterHangar(self, *args):
        if sm.GetService('viewState').IsViewActive('hangar') or session.stationid2 is None:
            return
        change = {'stationid': (session.stationid2, session.stationid2)}
        uthread.pool('eveCommands::CmdEnterHangar', sm.GetService('viewState').ChangePrimaryView, 'hangar', change=change)

    def CmdSetChatChannelFocus(self, *args):
        sm.GetService('focus').SetChannelFocus()

    def CmdSetOverviewFocus(self, *args):
        wnd = form.OverView.GetIfOpen()
        if wnd:
            uicore.registry.SetFocus(wnd)

    def GetWndMenu(self, *args):
        if uicore.registry.GetModalWindow() or not session.charid:
            return
        if not getattr(eve, 'chooseWndMenu', None) or eve.chooseWndMenu.destroyed or eve.chooseWndMenu.state == uiconst.UI_HIDDEN:
            ClearMenuLayer()
            form.CtrlTabWindow.CloseIfOpen()
            mv = form.CtrlTabWindow.Open()
            mv.left = (uicore.desktop.width - mv.width) / 2
            mv.top = (uicore.desktop.height - mv.height) / 2
            eve.chooseWndMenu = mv
        return eve.chooseWndMenu

    def CmdFleetBroadcast_EnemySpotted(self):
        sm.GetService('fleet').SendBroadcast_EnemySpotted()

    def CmdFleetBroadcast_NeedBackup(self):
        sm.GetService('fleet').SendBroadcast_NeedBackup()

    def CmdFleetBroadcast_HealArmor(self):
        sm.GetService('fleet').SendBroadcast_HealArmor()

    def CmdFleetBroadcast_HealShield(self):
        sm.GetService('fleet').SendBroadcast_HealShield()

    def CmdFleetBroadcast_HealCapacitor(self):
        sm.GetService('fleet').SendBroadcast_HealCapacitor()

    def CmdFleetBroadcast_InPosition(self):
        sm.GetService('fleet').SendBroadcast_InPosition()

    def CmdFleetBroadcast_HoldPosition(self):
        sm.GetService('fleet').SendBroadcast_HoldPosition()

    def CmdFleetBroadcast_JumpBeacon(self):
        sm.GetService('fleet').SendBroadcast_JumpBeacon()

    def CmdFleetBroadcast_Location(self):
        sm.GetService('fleet').SendBroadcast_Location()

    def CmdToggleTrackSelectedItem(self):
        sm.GetService('targetTrackingService').ToggleActiveTracking()

    def CmdTrackingCameraCenterPosition(self):
        sm.GetService('targetTrackingService').SetCenteredTrackingState(True)
        sm.GetService('targetTrackingService').EnableTrackingCamera()

    def CmdTrackingCameraCustomPosition(self):
        sm.GetService('targetTrackingService').SetCenteredTrackingState(False)
        sm.GetService('targetTrackingService').EnableTrackingCamera()

    def CmdTrackingCameraTogglePosition(self):
        sm.GetService('targetTrackingService').ToggleCenteredTracking()
        sm.GetService('targetTrackingService').EnableTrackingCamera()

    def CmdSetCameraPOV(self):
        if not self._IsSpaceCameraSwitchAllowed():
            return
        sm.GetService('sceneManager').SetActiveCameraByID(evecamera.CAM_SHIPPOV)

    CmdSetCameraPOV.nameLabelPath = 'Tooltips/Hud/POVCamera'
    CmdSetCameraPOV.descriptionLabelPath = 'Tooltips/Hud/POVCamera_description'

    def CmdSetCameraOrbit(self):
        if not self._IsSpaceCameraSwitchAllowed():
            return
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if cam.cameraID == evecamera.CAM_SHIPORBIT:
            if cam.GetItemID() != session.shipid:
                cam.LookAt(session.shipid)
            elif cam.isManualFovEnabled:
                cam.DisableManualFov()
            else:
                cam.Track(session.shipid)
        else:
            sm.GetService('sceneManager').SetActiveCameraByID(evecamera.CAM_SHIPORBIT)

    CmdSetCameraOrbit.nameLabelPath = 'Tooltips/Hud/OrbitCamera'
    CmdSetCameraOrbit.descriptionLabelPath = 'Tooltips/Hud/OrbitCamera_description'

    def CmdSetCameraTactical(self):
        if not self._IsSpaceCameraSwitchAllowed():
            return
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if cam.cameraID == evecamera.CAM_TACTICAL:
            cam.LookAt(session.shipid, allowSwitchCamera=False)
        else:
            sm.GetService('sceneManager').SetActiveCameraByID(evecamera.CAM_TACTICAL)

    CmdSetCameraTactical.nameLabelPath = 'Tooltips/Hud/TacticalCamera'
    CmdSetCameraTactical.descriptionLabelPath = 'Tooltips/Hud/TacticalCamera_description'

    def _IsSpaceCameraSwitchAllowed(self):
        if not IsNewCameraActive():
            return False
        if not sm.GetService('viewState').IsViewActive(ViewState.Space):
            return
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if not cam or cam.IsLocked():
            return False
        return True

    def OpenCapitalNavigation(self, *args):
        if eveCfg.GetActiveShip():
            form.CapitalNav.ToggleOpenClose()

    OpenCapitalNavigation.nameLabelPath = form.CapitalNav.default_captionLabelPath

    def OpenMonitor(self, *args):
        EngineToolsLauncher.Open()

    OpenMonitor.nameLabelPath = 'UI/Commands/OpenMonitor'

    def OpenFpsMonitor(self, *args):
        uicls.FpsMonitor.ToggleOpenClose(parent=uicore.layer.alwaysvisible)

    OpenFpsMonitor.nameLabelPath = 'UI/Commands/OpenFpsMonitor'

    def OpenConfigMenu(self, *args):
        sysMenu = uicore.layer.systemmenu
        if sysMenu.isopen:
            uthread.new(sysMenu.CloseMenu)
        else:
            sysMenu.OpenView()

    OpenConfigMenu.nameLabelPath = 'UI/Commands/OpenConfigMenu'

    def OpenMail(self, *args):
        if session.charid:
            return form.MailWindow.ToggleOpenClose()

    OpenMail.nameLabelPath = form.MailWindow.default_captionLabelPath
    OpenMail.descriptionLabelPath = form.MailWindow.default_descriptionLabelPath

    def OpenAgentFinder(self, *args):
        if session.charid:
            form.AgentFinderWnd.ToggleOpenClose()

    OpenAgentFinder.nameLabelPath = form.AgentFinderWnd.default_captionLabelPath
    OpenAgentFinder.descriptionLabelPath = form.AgentFinderWnd.default_descriptionLabelPath

    def CmdOpenNewMessage(self, *args):
        if session.charid:
            sm.GetService('mailSvc').SendMsgDlg()

    def OpenWallet(self, *args):
        if eve.session.solarsystemid2:
            form.Wallet.ToggleOpenClose()

    OpenWallet.nameLabelPath = form.Wallet.default_captionLabelPath

    def OpenCorporationPanel(self, *args):
        if eve.session.solarsystemid2:
            wnd = form.Corporation.GetIfOpen()
            if wnd:
                form.Corporation.ToggleOpenClose()
            elif eveCfg.IsNPC(session.corpid):
                sm.GetService('corpui').Show(localization.GetByLabel('UI/Corporations/BaseCorporationUI/Recruitment'))
            else:
                sm.GetService('corpui').Show()

    OpenCorporationPanel.nameLabelPath = form.Corporation.default_captionLabelPath
    OpenCorporationPanel.descriptionLabelPath = form.Corporation.default_descriptionLabelPath

    def OpenCorporationPanel_RecruitmentPane(self, *args):
        if eve.session.solarsystemid2:
            sm.GetService('corpui').Show(localization.GetByLabel('UI/Corporations/BaseCorporationUI/Recruitment'))

    def OpenAssets(self, *args):
        if eve.session.solarsystemid2:
            form.AssetsWindow.ToggleOpenClose()

    OpenAssets.nameLabelPath = form.AssetsWindow.default_captionLabelPath
    OpenAssets.descriptionLabelPath = form.AssetsWindow.default_descriptionLabelPath

    def OpenChannels(self, *args):
        if eve.session.solarsystemid2:
            sm.GetService('channels').Show()

    OpenChannels.nameLabelPath = form.Channels.default_captionLabelPath
    OpenChannels.descriptionLabelPath = form.Channels.default_descriptionLabelPath

    def OpenJournal(self, *args):
        if eve.session.solarsystemid2:
            form.Journal.ToggleOpenClose()

    OpenJournal.nameLabelPath = form.Journal.default_captionLabelPath
    OpenJournal.descriptionLabelPath = form.Journal.default_descriptionLabelPath

    def OpenSkillQueueWindow(self, *args):
        if session.charid:
            form.SkillQueue.ToggleOpenClose()

    OpenSkillQueueWindow.nameLabelPath = form.SkillQueue.default_captionLabelPath
    OpenSkillQueueWindow.descriptionLabelPath = form.SkillQueue.default_descriptionLabelPath

    def OpenEveMenu(self, *args):
        sm.GetService('neocom').ToggleEveMenu()

    OpenEveMenu.nameLabelPath = 'Tooltips/Neocom/NeocomMenu'
    OpenEveMenu.descriptionLabelPath = 'Tooltips/Neocom/NeocomMenu_description'

    def OpenTwitchStreaming(self, *args):
        form.TwitchStreaming.ToggleOpenClose()

    OpenTwitchStreaming.nameLabelPath = form.TwitchStreaming.default_captionLabelPath
    OpenTwitchStreaming.descriptionLabelPath = form.TwitchStreaming.default_descriptionLabelPath

    def ToggleAurumStore(self, *args):
        sm.GetService('viewState').ToggleSecondaryView(ViewState.VirtualGoodsStore)

    ToggleAurumStore.nameLabelPath = 'UI/VirtualGoodsStore/VgsName'
    ToggleAurumStore.descriptionLabelPath = 'Tooltips/Neocom/Vgs_description'

    def ToggleProjectDiscovery(self, *args):
        ProjectDiscoveryWindow.ToggleOpenClose()

    ToggleProjectDiscovery.nameLabelPath = 'UI/ProjectDiscovery/ProjectName'
    ToggleProjectDiscovery.descriptionLabelPath = 'Tooltips/Neocom/ProjectDiscoveryDescription'

    def ToggleRedeemItems(self, *args):
        if session.charid is not None:
            sm.StartService('redeem').ToggleRedeemWindow()

    ToggleRedeemItems.nameLabelPath = 'UI/Commands/RedeemItems'
    ToggleRedeemItems.descriptionLabelPath = 'Tooltips/Neocom/RedeemItems_description'

    def OpenLog(self, *args):
        uthread.new(self.__OpenLog_thread).context = 'cmd.OpenLog'

    OpenLog.nameLabelPath = form.Logger.default_captionLabelPath
    OpenLog.descriptionLabelPath = form.Logger.default_descriptionLabelPath

    def ToggleOpportunity(self, *args):
        AchievementTreeWindow.ToggleOpenClose()

    ToggleOpportunity.nameLabelPath = 'Achievements/UI/OpportunitiesTreeHeader'

    def __OpenLog_thread(self, *args):
        form.Logger.ToggleOpenClose()

    def OpenDroneBayOfActiveShip(self, *args):
        if eveCfg.GetActiveShip() is not None:
            uthread.new(self.__OpenDroneBayOfActiveShip_thread).context = 'cmd.OpenDroneBayOfActiveShip'

    OpenDroneBayOfActiveShip.nameLabelPath = 'UI/Commands/OpenDroneBayOfActiveShip'

    def __OpenDroneBayOfActiveShip_thread(self, *args):
        shipID = eveCfg.GetActiveShip()
        if shipID is None:
            return
        shipItem = sm.GetService('clientDogmaIM').GetDogmaLocation().GetDogmaItemWithWait(shipID)
        godmaType = sm.GetService('godma').GetType(shipItem.typeID)
        if godmaType.droneCapacity or IsModularShip(shipItem.typeID):
            invID = ('ShipDroneBay', shipID)
            form.Inventory.OpenOrShow(invID=invID, usePrimary=False, toggle=True)
        else:
            raise UserError('ShipHasNoDroneBay')

    def OpenCargoHoldOfActiveShip(self, *args):
        if eveCfg.GetActiveShip() is not None:
            uthread.new(self.__OpenCargoHoldOfActiveShip_thread).context = 'cmd.OpenCargoHoldOfActiveShip'

    OpenCargoHoldOfActiveShip.nameLabelPath = 'Tooltips/Hud/CargoHold'
    OpenCargoHoldOfActiveShip.descriptionLabelPath = 'Tooltips/Hud/CargoHold_description'

    def __OpenCargoHoldOfActiveShip_thread(self, *args):
        shipID = eveCfg.GetActiveShip()
        if shipID is None:
            return
        shipItem = sm.GetService('clientDogmaIM').GetDogmaLocation().GetDogmaItemWithWait(shipID)
        if shipItem is None:
            return
        invID = ('ShipCargo', shipID)
        form.Inventory.OpenOrShow(invID=invID, usePrimary=False, toggle=True)

    def OpenFuelBayOfActiveShip(self):
        self._OpenSpecialHoldOfActiveship(const.attributeSpecialFuelBayCapacity, 'ShipFuelBay')

    OpenFuelBayOfActiveShip.nameLabelPath = 'UI/Commands/OpenFuelBayOfActiveShip'

    def OpenOreHoldOfActiveShip(self):
        self._OpenSpecialHoldOfActiveship(const.attributeSpecialOreHoldCapacity, 'ShipOreHold')

    OpenOreHoldOfActiveShip.nameLabelPath = 'UI/Commands/OpenOreHoldOfActiveShip'

    def OpenMineralHoldOfActiveShip(self):
        self._OpenSpecialHoldOfActiveship(const.attributeSpecialMineralHoldCapacity, 'ShipMineralHold')

    OpenMineralHoldOfActiveShip.nameLabelPath = 'UI/Commands/OpenMineralHoldOfActiveShip'

    def OpenPlanetaryCommoditiesHoldOfActiveShip(self):
        self._OpenSpecialHoldOfActiveship(const.attributeSpecialPlanetaryCommoditiesHoldCapacity, 'ShipPlanetaryCommoditiesHold')

    OpenPlanetaryCommoditiesHoldOfActiveShip.nameLabelPath = 'UI/Commands/OpenPlanetaryCommoditiesHoldOfActiveShip'

    def _OpenSpecialHoldOfActiveship(self, attr, invCtrlName):
        itemID = eveCfg.GetActiveShip()
        if itemID is None:
            return
        ship = sm.GetService('clientDogmaIM').GetDogmaLocation().GetDogmaItemWithWait(itemID)
        if bool(sm.GetService('godma').GetTypeAttribute(ship.typeID, attr)):
            invID = (invCtrlName, itemID)
            form.Inventory.OpenOrShow(invID=invID, usePrimary=False, toggle=True)

    def OpenCharactersheet(self, *args):
        if eve.session.solarsystemid2:
            form.CharacterSheet.ToggleOpenClose()

    OpenCharactersheet.nameLabelPath = form.CharacterSheet.default_captionLabelPath
    OpenCharactersheet.descriptionLabelPath = form.CharacterSheet.default_descriptionLabelPath

    def OpenFleet(self, *args):
        form.FleetWindow.ToggleOpenClose()

    OpenFleet.nameLabelPath = form.FleetWindow.default_captionLabelPath
    OpenFleet.descriptionLabelPath = form.FleetWindow.default_descriptionLabelPath

    def OpenPeopleAndPlaces(self, *args):
        if eve.session.solarsystemid2:
            form.AddressBook.ToggleOpenClose()

    OpenPeopleAndPlaces.nameLabelPath = form.AddressBook.default_captionLabelPath
    OpenPeopleAndPlaces.descriptionLabelPath = form.AddressBook.default_descriptionLabelPath

    def OpenHelp(self, *args):
        if eve.session.charid:
            form.HelpWindow.ToggleOpenClose()

    OpenHelp.nameLabelPath = form.HelpWindow.default_captionLabelPath
    OpenHelp.descriptionLabelPath = form.HelpWindow.default_descriptionLabelPath

    def OpenReportBug(self, *args):
        form.BugReportingWindow.ToggleOpenClose()

    def OpenStationManagement(self, *args):
        if eve.session.solarsystemid2:
            form.StationManagement().Startup()

    OpenStationManagement.nameLabelPath = 'UI/Commands/OpenStationManagement'

    def OpenScanner(self, *args):
        if eve.session.solarsystemid:
            if IsBetaScannersEnabled():
                from eve.client.script.ui.inflight.probeScannerWindow import ProbeScannerWindow
                ProbeScannerWindow.ToggleOpenClose()
            else:
                from eve.client.script.ui.inflight.scanner import Scanner
                Scanner.ToggleOpenClose()

    OpenScanner.nameLabelPath = ProbeScannerWindow.default_captionLabelPath
    OpenScanner.descriptionLabelPath = ProbeScannerWindow.default_descriptionLabelPath

    def OpenDirectionalScanner(self, *args):
        if session.solarsystemid:
            if IsBetaScannersEnabled():
                from eve.client.script.ui.inflight.scannerFiles.directionalScannerWindow import DirectionalScanner
            else:
                from eve.client.script.ui.inflight.scannerFiles.directionalScanner import DirectionalScanner
            DirectionalScanner.ToggleOpenClose()

    OpenDirectionalScanner.nameLabelPath = DirectionalScanner.default_captionLabelPath
    OpenDirectionalScanner.descriptionLabelPath = DirectionalScanner.default_descriptionLabelPath

    def OpenMapBrowser(self, locationID = None):
        if eve.session.solarsystemid2:
            wnd = form.MapBrowserWnd.GetIfOpen()
            if wnd and not wnd.destroyed:
                if locationID is None:
                    if wnd.state == uiconst.UI_HIDDEN:
                        wnd.Show()
                    else:
                        wnd.Hide()
                else:
                    if wnd.state == uiconst.UI_HIDDEN:
                        wnd.Show()
                    wnd.DoLoad(locationID)
                return
            form.MapBrowserWnd.Open(locationID=locationID)

    OpenMapBrowser.nameLabelPath = form.MapBrowserWnd.default_captionLabelPath
    OpenMapBrowser.descriptionLabelPath = form.MapBrowserWnd.default_descriptionLabelPath

    def OpenHangarFloor(self, *args):
        if session.stationid2 is None:
            return
        invID = ('StationItems', session.stationid2)
        form.Inventory.OpenOrShow(invID=invID, usePrimary=False, toggle=True)

    OpenHangarFloor.nameLabelPath = 'UI/Commands/OpenHangarFloor'

    def OpenShipHangar(self, *args, **kwds):
        if session.stationid2 is None:
            return
        invID = ('StationShips', session.stationid2)
        form.Inventory.OpenOrShow(invID=invID, usePrimary=False, toggle=True)

    OpenShipHangar.nameLabelPath = 'UI/Commands/OpenShipHangar'

    def OpenInventory(self, *args):
        if not session.charid:
            return
        form.Inventory.OpenOrShow(toggle=True)

    OpenInventory.nameLabelPath = 'UI/Neocom/InventoryBtn'
    OpenInventory.descriptionLabelPath = 'Tooltips/Neocom/Inventory_description'

    def OpenCalculator(self, *args):
        form.Calculator.ToggleOpenClose()

    OpenCalculator.nameLabelPath = form.Calculator.default_captionLabelPath
    OpenCalculator.descriptionLabelPath = form.Calculator.default_descriptionLabelPath

    def OpenOverviewSettings(self, *args):
        OverviewSettings.Open()

    OpenOverviewSettings.nameLabelPath = OverviewSettings.default_captionLabelPath
    OpenOverviewSettings.descriptionLabelPath = OverviewSettings.default_descriptionLabelPath

    def OpenCorpHangar(self, *args):
        office = sm.GetService('corp').GetOffice()
        if office:
            invID = ('StationCorpHangars', office.itemID)
            form.Inventory.OpenOrShow(invID=invID, usePrimary=False, toggle=True)

    OpenCorpHangar.nameLabelPath = 'UI/Commands/OpenCorpHangar'

    def OpenCorpDeliveries(self, *args):
        deliveryRoles = const.corpRoleAccountant | const.corpRoleJuniorAccountant | const.corpRoleTrader
        if session.corprole & deliveryRoles == 0:
            eve.Message('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Commands/CorpRoleMissing')})
            allOpen = settings.char.windows.Get('openWindows', {})
            allOpen.pop('CorpMarketHangar', None)
            settings.char.windows.Set('openWindows', allOpen)
            return
        if session.stationid2:
            uthread.new(self.__OpenCorpDeliveries_thread)

    OpenCorpDeliveries.nameLabelPath = 'UI/Commands/OpenCorpDeliveries'

    def __OpenCorpDeliveries_thread(self, *args):
        if session.stationid2:
            invID = ('StationCorpDeliveries', session.stationid2)
            form.Inventory.OpenOrShow(invID=invID, usePrimary=False, toggle=True)

    def ShowVgsOffer(self, offerId, suppressFullScreen = False):
        self.LogInfo('ShowVgsOffer', offerId)
        sm.GetService('vgsService').GetUiController().ShowOffer(offerId, suppressFullScreen=suppressFullScreen)

    def BuyPlexOnline(self, *args):
        if boot.region == 'optic':
            plexUrl = 'http://eve.tiancity.com/client/evemall.html'
        else:
            plexUrl = 'https://secure.eveonline.com/PLEX/'
        blue.os.ShellExecute(plexUrl)

    def BuyAurumOnline(self, *args):
        if boot.region == 'optic':
            aurumUrl = 'http://eve.tiancity.com/client/evemall.html'
        else:
            token = sm.RemoteSvc('userSvc').GetSSOExchangeToken()
            if token:
                aurumUrl = 'https://secure.eveonline.com/AurStore/?token=%s' % token
            else:
                aurumUrl = 'https://secure.eveonline.com/AurStore/'
        blue.os.ShellExecute(aurumUrl)

    def OpenAccountManagement(self, *args):
        if boot.region == 'optic':
            accountUrl = 'http://pay.tiancity.com/eve/EveExchangeMain.aspx'
        else:
            accountUrl = 'https://secure.eveonline.com/'
        blue.os.ShellExecute(accountUrl)

    def OpenSubscriptionPage(self, origin = None, reason = None, *args):
        if boot.region == 'optic':
            accountUrl = 'http://pay.tiancity.com/eve/EveExchangeMain.aspx'
        else:
            token = sm.RemoteSvc('userSvc').GetSSOExchangeToken()
            if origin and reason and token:
                accountUrl = 'https://secure.eveonline.com/upgrade/?origin=%s&reason=%s&token=%s' % (origin, reason, token)
            elif origin and reason:
                accountUrl = 'https://secure.eveonline.com/upgrade/?origin=%s&reason=%s' % (origin, reason)
            else:
                accountUrl = 'https://secure.eveonline.com/upgrade/'
        blue.os.ShellExecute(accountUrl)
        with ExceptionEater('eventLog'):
            uthread.new(sm.ProxySvc('eventLog').LogClientEvent, 'trial', ['origin', 'reason'], 'OpenSubscriptionPage', origin, reason)

    def OpenTrialUpsell(self, origin = None, reason = None, message = None, *args):
        form.TrialPopup.Open(origin=origin, reason=reason, message=message)

    def OpenBrowser(self, url = None, windowName = 'virtualbrowser', args = {}, data = None, newTab = False):
        parsedUrl = urlparse.urlparse(url or '')
        if not session.charid:
            if url is not None and url != 'home' and parsedUrl.scheme in ('http', 'https'):
                blue.os.ShellExecute(url)
            return
        if parsedUrl.hostname and parsedUrl.hostname.count('secure.eveonline.com') > 0:
            if parsedUrl.path.lower().count('plex') > 0:
                self.BuyPlexOnline()
            else:
                self.OpenAccountManagement()
            return
        browserWindow = uicls.BrowserWindow.GetIfOpen(windowID=windowName)
        if browserWindow is None:
            return uicls.BrowserWindow.Open(initialUrl=url, windowID=windowName)
        browserWindow.Maximize()
        if url == 'home':
            uthread.new(browserWindow.GoHome)
        elif url:
            if newTab:
                uthread.new(browserWindow.AddTab, url)
            else:
                uthread.new(browserWindow.BrowseTo, url, args=args, data=data)
        return browserWindow

    OpenBrowser.nameLabelPath = 'UI/Neocom/BrowserBtn'

    def OpenNotepad(self, *args):
        form.Notepad.ToggleOpenClose()

    OpenNotepad.nameLabelPath = form.Notepad.default_captionLabelPath
    OpenNotepad.descriptionLabelPath = form.Notepad.default_descriptionLabelPath

    def OpenMoonMining(self, id = None):
        bp = sm.GetService('michelle').GetBallpark()
        if not id:
            for itemID in bp.slimItems:
                if bp.slimItems[itemID].groupID == const.groupControlTower:
                    id = bp.slimItems[itemID]
                    break

        if not id:
            return
        form.MoonMining.ToggleOpenClose(slimItem=id)

    OpenMoonMining.nameLabelPath = form.MoonMining.default_captionLabelPath
    OpenMoonMining.descriptionLabelPath = form.MoonMining.default_descriptionLabelPath

    def OpenShipConfig(self, id = None):
        activeShipID = eveCfg.GetActiveShip()
        if activeShipID is not None:
            ship = sm.GetService('clientDogmaIM').GetDogmaLocation().GetShip()
            typeObj = sm.GetService('godma').GetType(ship.typeID)
            if bool(typeObj.canReceiveCloneJumps):
                form.ShipConfig.ToggleOpenClose()

    OpenShipConfig.nameLabelPath = form.ShipConfig.default_captionLabelPath
    OpenShipConfig.descriptionLabelPath = form.ShipConfig.default_descriptionLabelPath

    def ToggleTutorialOverlay(self, *args):
        if not session.solarsystemid or uicore.layer.tutorialOverlay.isopen:
            uicore.layer.tutorialOverlay.CloseView()
        else:
            uicore.layer.tutorialOverlay.OpenView()

    def OpenTutorial(self, *args):
        if eve.session.charid:
            tutorialSvc = sm.GetService('tutorial')
            browser = tutorialSvc.GetTutorialBrowser(create=False)
            if browser is None:
                tutorialSvc.OpenCurrentTutorial()
            else:
                browser.ToggleMinimize()

    OpenTutorial.nameLabelPath = 'UI/Shared/Tutorial'
    OpenTutorial.detailedDescription = 'Tooltips/Neocom/Aura_description'

    def HasServiceAccess(self, serviceName, onlyCheckFacWarSystems = False):
        if onlyCheckFacWarSystems and session.solarsystemid2 not in sm.GetService('facwar').GetFacWarSystems():
            return True
        lobby = form.Lobby.GetIfOpen()
        if lobby is None:
            return False
        lobby.CheckCanAccessService(serviceName)
        return True

    def OpenMarket(self, *args):
        if session.stationid2 is None or self.HasServiceAccess('market', True):
            form.RegionalMarket.ToggleOpenClose()

    OpenMarket.nameLabelPath = form.RegionalMarket.default_captionLabelPath
    OpenMarket.descriptionLabelPath = form.RegionalMarket.default_descriptionLabelPath

    def OpenContracts(self, *args):
        wnd = form.ContractsWindow.ToggleOpenClose()
        if wnd:
            sm.GetService('tutorial').OpenTutorialSequence_Check(uix.tutorialInformativeContracts)

    OpenContracts.nameLabelPath = form.ContractsWindow.default_captionLabelPath
    OpenContracts.descriptionLabelPath = form.ContractsWindow.default_descriptionLabelPath

    def OpenIndustry(self, *args):
        if eve.session.solarsystemid2:
            Industry.ToggleOpenClose()

    OpenIndustry.nameLabelPath = Industry.default_captionLabelPath
    OpenIndustry.descriptionLabelPath = Industry.default_descriptionLabelPath

    def OpenPlanets(self, *args):
        if eve.session.solarsystemid2:
            PlanetWindow.ToggleOpenClose()

    OpenPlanets.nameLabelPath = PlanetWindow.default_captionLabelPath
    OpenPlanets.descriptionLabelPath = PlanetWindow.default_descriptionLabelPath

    def OpenFitting(self, *args):
        shipID = eveCfg.GetActiveShip()
        if shipID is None:
            uicore.Message('CannotPerformActionWithoutShip')
        elif session.stationid2 is None or self.HasServiceAccess('fitting'):
            FittingWindow2.ToggleOpenClose(shipID=shipID)

    OpenFitting.nameLabelPath = FittingWindow2.default_captionLabelPath
    OpenFitting.descriptionLabelPath = FittingWindow2.default_descriptionLabelPath

    def OpenGhostFitting(self, *args):
        if not sm.GetService('machoNet').GetGlobalConfig().get('enableGhostFitting'):
            return
        shipID = sm.GetService('fittingSvc').GetShipIDForFittingWindow()
        if shipID is None:
            uicore.Message('CannotPerformActionWithoutShip')
        elif session.stationid2 is None or self.HasServiceAccess('fitting'):
            FittingWindowGhost.ToggleOpenClose(shipID=shipID)

    def OpenMedical(self, *args):
        if session.stationid2:
            if eve.stationItem.serviceMask & const.stationServiceCloning == const.stationServiceCloning or eve.stationItem.serviceMask & const.stationServiceSurgery == const.stationServiceSurgery or eve.stationItem.serviceMask & const.stationServiceDNATherapy == const.stationServiceDNATherapy:
                if self.HasServiceAccess('medical'):
                    form.MedicalWindow.ToggleOpenClose()

    OpenMedical.nameLabelPath = form.MedicalWindow.default_captionLabelPath
    OpenMedical.descriptionLabelPath = form.MedicalWindow.default_descriptionLabelPath

    def OpenRepairshop(self, *args):
        if session.stationid2:
            if eve.stationItem.serviceMask & const.stationServiceRepairFacilities == const.stationServiceRepairFacilities:
                if self.HasServiceAccess('repairshop'):
                    form.RepairShopWindow.ToggleOpenClose()

    OpenRepairshop.nameLabelPath = form.RepairShopWindow.default_captionLabelPath
    OpenRepairshop.descriptionLabelPath = form.RepairShopWindow.default_descriptionLabelPath

    def OpenInsurance(self, *args):
        if session.stationid2:
            if eve.stationItem.serviceMask & const.stationServiceInsurance == const.stationServiceInsurance:
                if self.HasServiceAccess('insurance'):
                    form.InsuranceWindow.ToggleOpenClose()

    OpenInsurance.nameLabelPath = form.InsuranceWindow.default_captionLabelPath
    OpenInsurance.descriptionLabelPath = form.InsuranceWindow.default_descriptionLabelPath

    def OpenBountyOffice(self, *args):
        form.BountyWindow.ToggleOpenClose()

    OpenBountyOffice.nameLabelPath = form.BountyWindow.default_captionLabelPath
    OpenBountyOffice.descriptionLabelPath = form.BountyWindow.default_descriptionLabelPath

    def OpenSecurityOffice(self, *args):
        if session.stationid2:
            if sm.GetService('securityOfficeSvc').CanAccessServiceInStation(session.stationid2):
                uicls.SecurityOfficeWindow.ToggleOpenClose()

    OpenSecurityOffice.nameLabelPath = uicls.SecurityOfficeWindow.default_captionLabelPath
    OpenSecurityOffice.descriptionLabelPath = uicls.SecurityOfficeWindow.default_descriptionLabelPath

    def OpenMilitia(self, *args):
        if session.stationid2 is None or self.HasServiceAccess('navyoffices'):
            form.MilitiaWindow.ToggleOpenClose()

    OpenMilitia.nameLabelPath = form.MilitiaWindow.default_captionLabelPath
    OpenMilitia.descriptionLabelPath = form.MilitiaWindow.default_descriptionLabelPath

    def OpenReprocessingPlant(self, items = None):
        if session.stationid2 and self.HasServiceAccess('reprocessingPlant'):
            if eve.stationItem.serviceMask & const.stationServiceReprocessingPlant == const.stationServiceReprocessingPlant:
                if ReprocessingWnd.IsOpen() and items:
                    wnd = ReprocessingWnd.GetIfOpen()
                    wnd.AddPreselectedItems(items)
                else:
                    ReprocessingWnd.ToggleOpenClose(selectedItems=items)

    OpenReprocessingPlant.nameLabelPath = ReprocessingWnd.default_captionLabelPath
    OpenReprocessingPlant.descriptionLabelPath = ReprocessingWnd.default_descriptionLabelPath

    def OpenLpstore(self, *args):
        if session.stationid2:
            corpID = eve.stationItem.ownerID
            if eveCfg.IsNPC(corpID) and self.HasServiceAccess('lpstore'):
                sm.GetService('lpstore').OpenLPStore(corpID)

    OpenLpstore.nameLabelPath = form.LPStore.default_captionLabelPath
    OpenLpstore.descriptionLabelPath = form.LPStore.default_descriptionLabelPath

    def OpenCharacterCustomization(self, *args):
        if getattr(sm.GetService('map'), 'busy', False):
            return
        if sm.GetService('cc').NoExistingCustomization():
            raise UserError('CantRecustomizeCharacterWithoutDoll')
        if session.stationid:
            try:
                self.loadingCharacterCustomization = True
                if self.HasServiceAccess('charcustomization'):
                    sm.GetService('gameui').GoCharacterCreationCurrentCharacter()
            finally:
                self.loadingCharacterCustomization = False

    OpenCharacterCustomization.nameLabelPath = 'Tooltips/StationServices/CharacterCustomization'
    OpenCharacterCustomization.descriptionLabelPath = 'Tooltips/StationServices/CharacterCustomization_description'

    def OpenCalendar(self, *args):
        sm.GetService('neocom').BlinkOff('clock')
        if session.charid:
            form.eveCalendarWnd.ToggleOpenClose()

    OpenCalendar.nameLabelPath = form.eveCalendarWnd.default_captionLabelPath
    OpenCalendar.descriptionLabelPath = form.eveCalendarWnd.default_descriptionLabelPath

    def OpenAuraInteraction(self, *args):
        agentService = sm.GetService('agents')
        auraID = agentService.GetAuraAgentID()
        agentService.InteractWith(auraID)

    def CmdHideUI(self, force = 0):
        sys = uicore.layer.systemmenu
        if sys.isopen and not force:
            return
        if eve.hiddenUIState:
            self.ShowUI()
        else:
            self.HideUI()

    def HideUI(self):
        sm.GetService('tutorial').ChangeTutorialWndState(visible=0)
        layersToHide = ('abovemain', 'main', 'login', 'intro', 'charsel', 'shipui', 'bracket', 'target', 'tactical')
        hiddenUIState = []
        for each in layersToHide:
            layer = uicore.layer.Get(each)
            if layer is None:
                continue
            layer.state = uiconst.UI_HIDDEN
            hiddenUIState.append(each)

        sm.ScatterEvent('OnHideUI')
        eve.hiddenUIState = hiddenUIState

    def ShowUI(self, *args):
        if eve.hiddenUIState:
            for each in eve.hiddenUIState:
                layer = uicore.layer.Get(each)
                layer.state = uiconst.UI_PICKCHILDREN

        sm.GetService('tutorial').ChangeTutorialWndState(visible=1)
        eve.hiddenUIState = None
        sm.ScatterEvent('OnShowUI')

    def IsUIHidden(self, *args):
        return bool(eve.hiddenUIState)

    def CmdHideCursor(self, *args):
        uicore.uilib.SetCursor(uiconst.UICURSOR_NONE)

    def OpenDungeonEditor(self, *args):
        if session.solarsystemid and eve.session.role & service.ROLE_CONTENT:
            form.DungeonEditor.Open()
            if IsJessicaOpen():
                form.DungeonObjectProperties.Open()
                import panel
                panel.LoadDungeonListViewer()

    OpenDungeonEditor.nameLabelPath = 'UI/Commands/OpenDungeonEditor'

    def OpenFittingMgmt(self):
        form.FittingMgmt.Open()

    OpenFittingMgmt.nameLabelPath = form.FittingMgmt.default_captionLabelPath

    def OpenCompare(self, *args):
        form.TypeCompare.ToggleOpenClose()

    OpenCompare.nameLabelPath = form.TypeCompare.default_captionLabelPath
    OpenCompare.descriptionLabelPath = form.TypeCompare.default_descriptionLabelPath

    def OpenUIDebugger(self, *args):
        form.UIDebugger.ToggleOpenClose()

    OpenUIDebugger.nameLabelPath = 'UI/Commands/OpenUIDebugger'

    def ToggleTelemetryRecord(self):
        if self._telemetrySessionActive:
            blue.statistics.StopTelemetry()
            self._telemetrySessionActive = False
            print '*** Telemetry session stopped ***'
        else:
            blue.statistics.StartTelemetry('localhost')
            self._telemetrySessionActive = True
            print '*** Telemetry session started ***'

    def CmdToggleEffects(self, *args):
        candidateEffects = []
        for guid in cfg.GetEffectGuids():
            if guid not in FxSequencer.fxTurretGuids and guid not in FxSequencer.fxProtectedGuids:
                candidateEffects.append(guid)

        disabledGuids = sm.GetService('FxSequencer').GetDisabledGuids()
        if len(candidateEffects) > 0:
            if candidateEffects[0] in disabledGuids:
                gfxsettings.Set(gfxsettings.UI_EFFECTS_ENABLED, 1, pending=False)
                sm.GetService('FxSequencer').EnableGuids(candidateEffects)
                uicore.Message('CustomNotify', {'notify': 'All effects - On'})
            else:
                gfxsettings.Set(gfxsettings.UI_EFFECTS_ENABLED, 0, pending=False)
                sm.GetService('FxSequencer').DisableGuids(candidateEffects)
                uicore.Message('CustomNotify', {'notify': 'All effects - Off'})

    def CmdToggleEffectTurrets(self, *args):
        disabledGuids = sm.GetService('FxSequencer').GetDisabledGuids()
        if FxSequencer.fxTurretGuids[0] in disabledGuids:
            gfxsettings.Set(gfxsettings.UI_TURRETS_ENABLED, 1, pending=False)
            sm.GetService('FxSequencer').EnableGuids(FxSequencer.fxTurretGuids)
            uicore.Message('CustomNotify', {'notify': 'All Turret effects - On'})
        else:
            gfxsettings.Set(gfxsettings.UI_TURRETS_ENABLED, 0, pending=False)
            sm.GetService('FxSequencer').DisableGuids(FxSequencer.fxTurretGuids)
            uicore.Message('CustomNotify', {'notify': 'All Turret effects - Off'})

    def CmdToggleCombatView(self, *args):
        if eve.session.solarsystemid and eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            sm.GetService('target').ToggleViewMode()

    def CmdCycleFleetBroadcastScope(self, *args):
        sm.GetService('fleet').CycleBroadcastScope()

    def CmdTrackSelectedItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdTrackSelectedItem')
        camera = sm.GetService('sceneManager').GetActiveCamera()
        self.LoadCombatCommand(camera.targetTracker.TrackItem, cmd)

    def CmdToggleTargetItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdToggleTargetItem')
        self.LoadCombatCommand(sm.GetService('target').ToggleLockTarget, cmd)

    def CmdLockTargetItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdLockTargetItem')
        self.LoadCombatCommand(sm.GetService('target').TryLockTarget, cmd)

    def CmdSelectTargetItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdSelectTargetItem')
        self.LoadCombatCommand(sm.GetService('menu').SelectTarget, cmd)

    def CmdUnlockTargetItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdUnlockTargetItem')
        self.LoadCombatCommand(sm.GetService('target').UnlockTarget, cmd)

    def CmdToggleLookAtItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdToggleLookAtItem')
        self.LoadCombatCommand(sm.GetService('menu').ToggleLookAt, cmd)

    def CmdToggleCameraTracking(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdToggleCameraTracking')
        self.LoadCombatCommand(sm.GetService('menu').SetInterest, cmd)

    def CmdApproachItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdApproachItem')
        self.LoadCombatCommand(sm.GetService('menu').Approach, cmd)

    def CmdAlignToItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdAlignToItem')
        self.LoadCombatCommand(sm.GetService('menu').AlignTo, cmd)

    def CmdOrbitItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdOrbitItem')
        self.LoadCombatCommand(Orbit, cmd)

    def CmdKeepItemAtRange(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdKeepItemAtRange')
        self.LoadCombatCommand(KeepAtRange, cmd)

    def CmdShowItemInfo(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdShowItemInfo')
        self.LoadCombatCommand(sm.GetService('menu').ShowInfoForItem, cmd)

    def CmdDockOrJumpOrActivateGate(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdDockOrJumpOrActivateGate')
        self.LoadCombatCommand(DockOrJumpOrActivateGate, cmd)

    def CmdWarpToItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdWarpToItem')
        self.LoadCombatCommand(WarpToItem, cmd)

    def CmdOpenRadialMenu(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdOpenRadialMenu')
        self.LoadCombatCommand(None, cmd)

    def CmdSendBroadcast_Target(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdSendBroadcast_Target')
        self.LoadCombatCommand(sm.GetService('fleet').SendBroadcast_Target, cmd)

    def MakeCmdTagItem(self, tag):
        functionName = 'CmdTagItem_%s' % tag

        def CmdTagItem():
            if session.fleetid is None:
                return
            cmd = uicore.cmd.commandMap.GetCommandByName(functionName)

            def DoTagItem(itemID):
                if session.fleetid is None:
                    return
                self.menu.TagItem(itemID, tag)

            self.LoadCombatCommand(DoTagItem, cmd)

        CmdTagItem.__name__ = functionName
        return CmdTagItem

    def MakeCmdTagItemFromSequence(self, tagSequence):
        functionName = 'CmdTagItem_%s' % ''.join(tagSequence)

        def CmdTagItem():
            if session.fleetid is None:
                return
            cmd = uicore.cmd.commandMap.GetCommandByName(functionName)

            def DoTagItemFromSequence(itemID):
                if session.fleetid is None:
                    return
                index = self.commandMemory.get(functionName, 0)
                tag = tagSequence[index]
                index = (index + 1) % len(tagSequence)
                self.commandMemory[functionName] = index
                self.menu.TagItem(itemID, tag)

            self.LoadCombatCommand(DoTagItemFromSequence, cmd)

        CmdTagItem.__name__ = functionName
        return CmdTagItem

    def CmdToggleSensorOverlay(self):
        if session.solarsystemid is not None:
            sm.GetService('sensorSuite').ToggleOverlay()

    CmdToggleSensorOverlay.nameLabelPath = 'UI/Inflight/Scanner/SensorOverlay'

    def CmdCreateBookmark(self):
        if session.solarsystemid is not None:
            sm.GetService('addressbook').BookmarkCurrentLocation()

    def CmdFlightControlsUp(self):
        pass

    CmdFlightControlsUp.nameLabelPath = 'UI/Commands/CmdFlightControlsUp'

    def CmdFlightControlsDown(self):
        pass

    CmdFlightControlsDown.nameLabelPath = 'UI/Commands/CmdFlightControlsDown'

    def CmdFlightControlsLeft(self):
        pass

    CmdFlightControlsLeft.nameLabelPath = 'UI/Commands/CmdFlightControlsLeft'

    def CmdFlightControlsRight(self):
        pass

    CmdFlightControlsRight.nameLabelPath = 'UI/Commands/CmdFlightControlsRight'

    def LoadCombatCommand(self, function, cmd):
        if not session.solarsystemid:
            return
        sm.GetService('ui').SetFreezeOverview(freeze=True)
        self.combatFunctionLoaded = function
        self.combatCmdLoaded = cmd
        uicore.event.RegisterForTriuiEvents((uiconst.UI_KEYUP,
         uiconst.UI_KEYDOWN,
         uiconst.UI_ACTIVE,
         uiconst.UI_MOUSEUP), self.CombatKeyUnloadListener)
        delayMs = 300
        for key in cmd.shortcut:
            if key not in uiconst.MODKEYS:
                delayMs = 0
                break

        sm.GetService('space').SetShortcutText(cmd.GetDescription(), localization.GetByLabel('UI/Commands/ClickTarget'), delayMs)
        sm.GetService('flightPredictionSvc').CommandKeyDown(cmd.name)

    def UnloadCombatCommand(self):
        uthread.new(self._UnloadCombatCommand)

    def _UnloadCombatCommand(self):
        sm.GetService('flightPredictionSvc').CommandKeyUp()
        sm.GetService('space').ClearShortcutText()
        sm.GetService('ui').SetFreezeOverview(freeze=False)
        self.combatFunctionLoaded = None
        self.combatCmdLoaded = None
        if self.combatCmdUnloadFunc:
            self.combatCmdUnloadFunc(self.combatCmdCurrentHasExecuted)
            self.combatCmdUnloadFunc = None
        self.combatCmdCurrentHasExecuted = False

    def CombatKeyUnloadListener(self, wnd, eventID, keyChange):
        if eventID == uiconst.UI_MOUSEUP and keyChange[0] in (uiconst.MOUSELEFT, uiconst.MOUSERIGHT):
            return True
        if eventID == uiconst.UI_ACTIVE:
            self.UnloadCombatCommand()
            return
        if self.combatCmdLoaded is None:
            return True
        vk, id = keyChange
        if vk not in self.combatCmdLoaded.shortcut:
            self.UnloadCombatCommand()
            return
        for key in self.combatCmdLoaded.shortcut:
            if not uicore.uilib.Key(key):
                self.UnloadCombatCommand()
                return

        return True

    def ExecuteCombatCommand(self, itemID, eventID, **kwargs):
        if itemID is None or self.combatFunctionLoaded is None:
            return False
        if eventID == uiconst.UI_KEYUP and self.combatCmdCurrentHasExecuted:
            self.UnloadCombatCommand()
            return True
        self.combatCmdCurrentHasExecuted = True
        self.ExecuteActiveCombatCommand(itemID, **kwargs)
        return True

    def ExecuteActiveCombatCommand(self, itemID, **kwargs):
        uthread.new(self.combatFunctionLoaded, itemID, **kwargs)

    def IsSomeCombatCommandLoaded(self):
        return self.combatFunctionLoaded is not None

    def IsCombatCommandLoaded(self, cmdName):
        return self.combatCmdLoaded == self.commandMap.GetCommandByName(cmdName)

    def GetCombatCmdLoadedName(self):
        return self.combatCmdLoaded

    def CmdForceFadeFromBlack(self, *args):
        loadSvc = sm.GetService('loading')
        if loadSvc.IsLoading():
            loadSvc.FadeOut(100)

    def CmdMoveForward(self, *args):
        return self._UpdateMovement(const.MOVDIR_FORWARD)

    def CmdMoveBackward(self, *args):
        return self._UpdateMovement(const.MOVDIR_BACKWARD)

    def CmdMoveLeft(self, *args):
        return self._UpdateMovement(const.MOVDIR_LEFT)

    def CmdMoveRight(self, *args):
        return self._UpdateMovement(const.MOVDIR_RIGHT)

    def _UpdateMovement(self, direction):
        if sm.GetService('viewState').IsViewActive('station'):
            sm.GetService('navigation').UpdateMovement(direction)
        return False

    def Reset(self, resetKey):
        if resetKey == 'windows':
            sm.GetService('window').ResetWindowSettings()
            GetDockPanelManager().ResetAllPanelSettings()
        elif resetKey == 'window color':
            sm.GetService('uiColor').LoadUIColors(reset=True)
        elif resetKey == 'clear cache':
            sm.GetService('gameui').ClearCacheFiles()
        elif resetKey == 'clear iskspammers':
            try:
                delattr(sm.GetService('LSC'), 'spammerList')
            except:
                sys.exc_clear()

        elif resetKey == 'clear settings':
            sm.GetService('gameui').ClearSettings()
        elif resetKey == 'clear mail':
            sm.GetService('mailSvc').ClearMailCache()
        elif resetKey == 'reset neocom':
            sm.GetService('neocom').ResetButtons()

    def CmdToggleSystemMenu(self):
        systemMenu = uicore.layer.systemmenu
        if systemMenu.isopen:
            sm.GetService('uipointerSvc').ShowPointer()
            uthread.new(systemMenu.CloseMenu)
        else:
            sm.GetService('uipointerSvc').HidePointer()
            uthread.new(systemMenu.OpenView)

    CmdToggleSystemMenu.nameLabelPath = 'UI/Login/Settings'

    def OnEsc(self, *args):
        escapeAdaptor = EscapeCommandAdapter()
        escCommand = EscapeCommand(viewStateSrvc=sm.GetService('viewState'), adaptor=escapeAdaptor)
        escCommand.Execute()

    def OnTab(self):
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            uicore.registry.FindFocus(-1)
        else:
            uicore.registry.FindFocus(1)

    def MapCmd(self, cmdname, context):
        self.commandMap.UnloadAllAccelerators()
        wnd = form.MapCmdWindow.Open(cmdname=cmdname)
        modalResult = wnd.ShowModal()
        self.LoadAllAccelerators()
        if modalResult == 1:
            retval = wnd.result
            shortcut = retval['shortcut']
        else:
            return
        errorMsg = self.MapCmdErrorCheck(cmdname, shortcut, context)
        if errorMsg:
            eve.Message('CustomInfo', {'info': errorMsg})
            return
        alreadyUsing = self.commandMap.GetCommandByShortcut(shortcut)
        if alreadyUsing is not None:
            alreadyUsingContext = self.__categoryToContext__[alreadyUsing.category]
            if alreadyUsingContext not in self.contextToCommand:
                self.contextToCommand[alreadyUsingContext] = {}
            self.contextToCommand[alreadyUsingContext][shortcut] = alreadyUsing
        self.commandMap.RemapCommand(cmdname, shortcut)
        if context not in self.contextToCommand:
            self.contextToCommand[context] = {}
        self.ClearContextToCommandMapping(context, cmdname)
        self.contextToCommand[context][shortcut] = self.commandMap.GetCommandByName(cmdname)
        sm.ScatterEvent('OnMapShortcut', cmdname, shortcut)

    def ClearContextToCommandMapping(self, context, cmdname):
        toDeleteShortcut = None
        for shortcutKey, command in self.contextToCommand[context].iteritems():
            if command.name == cmdname:
                toDeleteShortcut = shortcutKey

        if toDeleteShortcut is not None:
            del self.contextToCommand[context][toDeleteShortcut]

    def MapCmdErrorCheck(self, cmdname, shortcut, context):
        if not shortcut:
            return localization.GetByLabel('UI/Commands/ChooseAKeyPrompt')
        for key in shortcut:
            keyName = self.GetKeyNameFromVK(key)
            if not getattr(uiconst, 'VK_%s' % keyName.upper(), None):
                eve.Message('UnknownKey', {'key': keyName})
                return

        alreadyUsing = self.commandMap.GetCommandByShortcut(shortcut)
        if alreadyUsing:
            cmdEdit = self.commandMap.GetCommandByName(cmdname)
            alreadyUsingContext = self.__categoryToContext__[alreadyUsing.category]
            cmdEditContext = self.__categoryToContext__[cmdEdit.category]
            sameContext = self.CheckContextIntersection(alreadyUsingContext, cmdEditContext)
            if sameContext and alreadyUsing.name != cmdname:
                return localization.GetByLabel('UI/Commands/ShortcutAlreadyUsedByCmd', cmd=alreadyUsing.GetShortcutAsString(), category=localization.GetByLabel(CATEGORIES[alreadyUsing.category]), func=alreadyUsing.GetDescription())
        if context in self.contextToCommand and shortcut in self.contextToCommand[context]:
            alreadyUsing = self.contextToCommand[context][shortcut]
            return localization.GetByLabel('UI/Commands/ShortcutAlreadyUsedByCmd', cmd=alreadyUsing.GetShortcutAsString(), category=localization.GetByLabel(CATEGORIES[alreadyUsing.category]), func=alreadyUsing.GetDescription())
        return ''

    def ClearMappedCmd(self, cmdname, showMsg = 1):
        command = self.commandMap.GetCommandByName(cmdname)
        context = self.__categoryToContext__[command.category]
        if context in self.contextToCommand:
            self.ClearContextToCommandMapping(context, cmdname)
        svc.cmd.ClearMappedCmd(self, cmdname, showMsg)

    def CmdPickPortrait0(self, *args):
        self.PickPortrait(0)

    def CmdPickPortrait1(self, *args):
        self.PickPortrait(1)

    def CmdPickPortrait2(self, *args):
        self.PickPortrait(2)

    def CmdPickPortrait3(self, *args):
        self.PickPortrait(3)

    def PickPortrait(self, portraitID):
        uicore.layer.charactercreation.PickPortrait(portraitID)

    def ExecuteCommand(self, cmd):
        return cmd.callback()

    def CmdSetDefenceStance(self, *args):
        self._SetStance(shipmode.data.shipStanceDefense)

    def CmdSetSniperStance(self, *args):
        self._SetStance(shipmode.data.shipStanceSniper)

    def CmdSetSpeedStance(self, *args):
        self._SetStance(shipmode.data.shipStanceSpeed)

    def _SetStance(self, stanceID):
        set_stance(stanceID, eveCfg.GetActiveShip())

    def CmdIncreaseProbeScanRange(self, *args):
        if session.solarsystemid:
            probeScanWindow = ProbeScannerWindow.GetIfOpen()
            if probeScanWindow:
                sm.GetService('scanSvc').ScaleFormation(2.0)
            return True

    CmdIncreaseProbeScanRange.nameLabelPath = 'UI/Commands/CmdIncreaseProbeScanRange'

    def CmdDecreaseProbeScanRange(self, *args):
        if session.solarsystemid:
            probeScanWindow = ProbeScannerWindow.GetIfOpen()
            if probeScanWindow:
                sm.GetService('scanSvc').ScaleFormation(0.5)
            return True

    CmdDecreaseProbeScanRange.nameLabelPath = 'UI/Commands/CmdDecreaseProbeScanRange'

    def CmdRefreshProbeScan(self, *args):
        if session.solarsystemid:
            from eve.client.script.ui.inflight.probeScannerWindow import ProbeScannerWindow
            probeScanWindow = ProbeScannerWindow.GetIfOpen()
            if probeScanWindow:
                probeScanWindow.Confirm()
            return True

    CmdRefreshProbeScan.nameLabelPath = 'UI/Commands/CmdRefreshProbeScan'

    def CmdRefreshDirectionalScan(self, *args):
        if not session.solarsystemid:
            return
        from eve.client.script.ui.inflight.scannerFiles.directionalScannerWindow import DirectionalScanner
        if IsNewCameraActive() and IsBetaScannersEnabled():
            wnd = DirectionalScanner.GetIfOpen()
            if not wnd:
                wnd = DirectionalScanner.Open(scanOnOpen=False)
            cmd = uicore.cmd.commandMap.GetCommandByName('CmdRefreshDirectionalScan')
            self.LoadCombatCommand(wnd.ScanTowardsItem, cmd)
            self.combatCmdUnloadFunc = wnd.OnCmdDirectionalScanUnload
            wnd.OnCmdDirectionalScanLoad()
        else:
            wnd = DirectionalScanner.GetIfOpen()
            if wnd:
                wnd.Confirm()

    CmdRefreshDirectionalScan.nameLabelPath = 'UI/Commands/CmdRefreshDirectionalScan'

    def CmdToggleAutoTracking(self, *args):
        if not session.solarsystemid:
            return
        if not IsNewCameraActive():
            return
        settings.char.ui.Set('orbitCameraAutoTracking', not IsAutoTrackingEnabled())
        sm.ScatterEvent('OnAutoTrackingChanged')

    CmdToggleAutoTracking.nameLabelPath = 'UI/Commands/CmdToggleAutoTracking'
