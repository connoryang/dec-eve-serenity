#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\bracketMgr.py
from eve.client.script.parklife.dungeonHelper import IsJessicaOpen
import evetypes
import service
from spacecomponents.client.messages import MSG_ON_BRACKET_CREATED
import uicontrols
import form
import blue
import uix
import uiutil
import xtriui
import base
import uthread
import states as state
import util
import sys
import math
import stackless
import log
import carbonui.const as uiconst
import localization
import telemetry
import uicls
import bracketUtils
import collections
import fsdSchemas.binaryLoader as fsdBinaryLoader
from eve.client.script.ui.inflight.bracketsAndTargets.timedBracket import TimedBracket
from eve.client.script.ui.inflight.bracketsAndTargets.siphonBracket import SiphonSiloBracket
from spacecomponents.common.helper import HasBountyEscrowComponent
from spacecomponents.client.components.bountyEscrow import GetSubLabel as GetBountyEscrowSubLabel
SHOW_NONE = -1
SHOW_DEFAULT = 0
SHOW_ALL = 1
RED = (0.8, 0, 0, 1.0)
ORANGE = (0.75, 0.4, 0, 1.0)
YELLOW = (1.0, 1.0, 0, 0.3)
RECORDED_DAMAGE_PERIOD_SECONDS = 120
NUMBER_OF_DAMAGEDEALERS = 5
INF = 1e+32

class BracketMgr(service.Service):
    __guid__ = 'svc.bracket'
    __update_on_reload__ = 0
    __exportedcalls__ = {'GetBracketName': [],
     'GetBracketName2': [],
     'ResetOverlaps': [],
     'CheckOverlaps': [],
     'CleanUp': [],
     'ClearBracket': [],
     'ShowAll': [],
     'ShowNone': [],
     'ShowingAll': [],
     'ShowingNone': [],
     'GetBracketProps': [],
     'Reload': [],
     'GetScanSpeed': [],
     'GetCaptureData': []}
    __notifyevents__ = ['DoBallsAdded',
     'DoBallRemove',
     'DoBallClear',
     'ProcessSessionChange',
     'OnFleetStateChange',
     'OnStateChange',
     'OnDestinationSet',
     'OnPostCfgDataChanged',
     'OnBallparkCall',
     'OnSlimItemChange',
     'OnAttribute',
     'OnAttributes',
     'OnCaptureChanged',
     'OnBSDTablesChanged',
     'ProcessShipEffect',
     'ProcessBountyInfoUpdated',
     'OnUIScalingChange',
     'OnFleetJoin_Local',
     'OnFleetLeave_Local',
     'OnDamageMessage',
     'OnDamageMessages',
     'DoBallsRemove']
    __startupdependencies__ = ['wreck']
    __dependencies__ = ['michelle',
     'tactical',
     'map',
     'settings',
     'target']

    def __init__(self):
        service.Service.__init__(self)
        self.wantedGroupsWhenSelectedOnly = (const.groupHarvestableCloud,)
        self.wantedCategoriesWhenSelectedOnly = (const.categoryAsteroid,)
        self.specials = (const.groupLargeCollidableStructure, const.groupMoon)
        self.filterLCS = ['wall_x',
         'wall_z',
         ' wall',
         ' barricade',
         ' fence',
         ' barrier',
         ' junction',
         ' elevator',
         ' lookout',
         ' neon sign']
        self.showState = SHOW_DEFAULT
        self.showingSpecials = False

    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        self.scenarioMgr = sm.StartService('scenario')
        self.Reload()
        self.CreateBracketIndexes()

    def CreateBracketIndexes(self):
        self.bracketDataByCategoryID = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/bracketsByCategory.static', optimize=False)
        self.bracketDataByGroupID = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/bracketsByGroup.static', optimize=False)
        self.bracketDataByTypeID = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/bracketsByType.static', optimize=False)
        self.bracketsData = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/brackets.static', optimize=False)

    def GetBrackeDatatByID(self, bracketID):
        return self.bracketsData.get(bracketID, None)

    def GetBracketDataByTypeID(self, typeID):
        try:
            bracketID = self.bracketDataByTypeID[typeID]
        except KeyError:
            try:
                bracketID = self.bracketDataByGroupID[evetypes.GetGroupID(typeID)]
            except KeyError:
                try:
                    bracketID = self.bracketDataByCategoryID[evetypes.GetCategoryID(typeID)]
                except KeyError:
                    return None

        return self.GetBrackeDatatByID(bracketID)

    def GetBracketDataByGroupID(self, groupID):
        if groupID in self.bracketDataByGroupID:
            bracketID = self.bracketDataByGroupID[groupID]
            return self.GetBrackeDatatByID(bracketID)
        categoryID = evetypes.GetCategoryIDByGroup(groupID)
        if categoryID in self.bracketDataByCategoryID:
            bracketID = self.bracketDataByCategoryID[categoryID]
            return self.GetBrackeDatatByID(bracketID)

    def GetBracketIcon(self, typeID, isEmpty = None):
        bracket = self.GetBracketDataByTypeID(typeID)
        if bracket:
            if isEmpty and hasattr(bracket, 'texturePathEmpty'):
                return bracket.texturePathEmpty
            else:
                return bracket.texturePath

    def Stop(self, stream):
        self.CleanUp()

    def CleanUp(self):
        self.brackets = {}
        self.updateBrackets = {}
        self.damageByBracketID = {}
        self.biggestDamageDealers = []
        self.shipLabels = None
        self.overlaps = []
        self.overlapsHidden = []
        self.checkingOverlaps = 0
        self.showHiddenTimer = None
        self.hairlinesTimer = None
        self.inTargetRangeTimer = None
        self.damageDealerTimer = None
        uicore.layer.bracket.Flush()

    def Hide(self):
        l_bracket = uicore.layer.bracket
        if l_bracket:
            l_bracket.state = uiconst.UI_HIDDEN

    def Show(self):
        l_bracket = uicore.layer.bracket
        if l_bracket:
            l_bracket.state = uiconst.UI_PICKCHILDREN

    @telemetry.ZONE_METHOD
    def Reload(self, *args, **kwds):
        self.CleanUp()
        overviewPresetSvc = sm.GetService('overviewPresetSvc')
        showInTargetRange = overviewPresetSvc.GetSettingValueOrDefaultFromName('showInTargetRange', True)
        if showInTargetRange:
            self.inTargetRangeTimer = base.AutoTimer(1000, self.ShowInTargetRange)
        showBiggestDamageDealers = overviewPresetSvc.GetSettingValueOrDefaultFromName('showBiggestDamageDealers', True)
        if showBiggestDamageDealers:
            self.damageDealerTimer = base.AutoTimer(1000, self.ShowBiggestDamageDealers_thread)
        uthread.new(self.SoftReload)

    @telemetry.ZONE_METHOD
    def SoftReload(self, showSpecials = None, bracketShowState = None):
        if bracketShowState is not None:
            self.showState = bracketShowState
        if showSpecials is not None:
            self.showingSpecials = showSpecials
        ballPark = sm.GetService('michelle').GetBallpark(doWait=True)
        if not ballPark:
            return
        for slimItem in ballPark.slimItems.itervalues():
            self.AddBracketIfWanted(slimItem)

    def ShowAll(self):
        if self.showState != SHOW_ALL:
            self.showState = SHOW_ALL
            self.SoftReload()
        self.UpdateOverviewSettings()

    def UpdateOverviewSettings(self):
        overview = form.OverView.GetIfOpen()
        if overview:
            selectedTabKey = overview.GetSelectedTabKey()
            tabsettings = sm.GetService('overviewPresetSvc').GetTabSettingsForOverview()
            tabsetting = tabsettings.get(selectedTabKey, None)
            if tabsetting:
                tabsetting['showAll'] = self.showState == SHOW_ALL
                tabsetting['showNone'] = self.showState == SHOW_NONE
                tabsetting['showSpecials'] = self.showingSpecials

    def ShowNone(self):
        if self.showState != SHOW_NONE:
            self.showState = SHOW_NONE
            self.SoftReload()
        self.UpdateOverviewSettings()

    def ShowAllHidden(self):
        if not self.showHiddenTimer:
            bracket = self.brackets.get(session.shipid, None)
            if bracket:
                bracket.ShowOwnShip()
                self.showHiddenTimer = base.AutoTimer(100, self.StopShowingHidden)

    def StopShowingHidden(self):
        alt = uicore.uilib.Key(uiconst.VK_MENU)
        if not alt:
            self.showHiddenTimer = None
            bracket = self.brackets.get(session.shipid, None)
            if bracket:
                bracket.SetNormalInvisibleStateForOwnShip()

    def ToggleShowSpecials(self):
        self.showingSpecials = not self.showingSpecials
        self.UpdateOverviewSettings()
        self.SoftReload()

    def ShowingAll(self):
        return self.showState == SHOW_ALL

    def ShowingNone(self):
        return self.showState == SHOW_NONE

    def StopShowingAll(self):
        self.showState = SHOW_DEFAULT
        self.UpdateOverviewSettings()
        self.SoftReload()

    def StopShowingNone(self):
        self.showState = SHOW_DEFAULT
        self.UpdateOverviewSettings()
        self.SoftReload()

    @telemetry.ZONE_METHOD
    def IsWanted(self, ballID, typeID = None, groupID = None, categoryID = None, slimItem = None, filtered = None):
        if typeID and not self.GetBracketDataByTypeID(typeID):
            return False
        else:
            if typeID is None or groupID is None or categoryID is None:
                slimItem = slimItem or sm.GetService('michelle').GetBallpark().GetInvItem(ballID)
                if slimItem is None:
                    log.LogWarn('IsWanted - ball', ballID, 'not found in park')
                    return False
                typeID = slimItem.typeID
                groupID = slimItem.groupID
                categoryID = slimItem.categoryID
            if groupID == const.groupDeadspaceOverseersStructure:
                checkName = evetypes.GetName(typeID).lower()
                if checkName in self.filterLCS:
                    return False
            if groupID in self.wantedGroupsWhenSelectedOnly or categoryID in self.wantedCategoriesWhenSelectedOnly:
                return self.IsSelectedOrTargeted(ballID)
            isSpecial = groupID in self.specials
            if isSpecial:
                if getattr(self, 'showingSpecials', False):
                    return True
                return self.IsSelectedOrTargeted(ballID)
            if self.showState == SHOW_ALL:
                return True
            isSelectedOrTargeted = self.IsSelectedOrTargeted(ballID)
            if self.showState == SHOW_NONE:
                return isSelectedOrTargeted
            if isSelectedOrTargeted:
                return True
            slimItem = slimItem or sm.GetService('michelle').GetBallpark().GetInvItem(ballID)
            filtered = filtered or sm.GetService('tactical').GetFilteredStatesFunctionNames(isBracket=True)
            alwaysShown = sm.GetService('tactical').GetAlwaysShownStatesFunctionNames()
            return sm.GetService('tactical').WantIt(slimItem, filtered, alwaysShown, isBracket=True)

    @telemetry.ZONE_METHOD
    def IsSelectedOrTargeted(self, ballID):
        stateMgr = sm.GetService('state')
        for isWanted in stateMgr.GetStates(ballID, [state.selected,
         state.targeted,
         state.targeting,
         state.activeTarget]):
            if isWanted:
                return True

        return sm.GetService('target').IsTarget(ballID)

    def GetBracketName(self, objectID):
        if objectID in self.brackets:
            return self.brackets[objectID].displayName
        return ''

    def GetBracket(self, objectID):
        return self.brackets.get(objectID, None)

    def GetBracketName2(self, objectID):
        if not objectID:
            return ''
        ret = self.GetBracketName(objectID)
        if ret != '':
            return ret
        slimItem = sm.GetService('michelle').GetBallpark().slimItems.get(objectID, None)
        if slimItem is None:
            return ''
        return self.GetDisplayNameForBracket(slimItem)

    def DisplayName(self, slimItem, displayName):
        shiplabel = []
        if not getattr(self, 'shipLabels', None):
            self.shipLabels = sm.GetService('state').GetShipLabels()
            self.hideCorpTicker = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName('hideCorpTicker', True)
        for label in self.shipLabels:
            if label['state']:
                type, pre, post = label['type'], label['pre'], label['post']
                if type is None and slimItem.corpID and not util.IsNPC(slimItem.corpID):
                    shiplabel.append(pre)
                if type == 'corporation' and slimItem.corpID and not util.IsNPC(slimItem.corpID) and not (self.hideCorpTicker and slimItem.allianceID):
                    shiplabel += [pre, cfg.corptickernames.Get(slimItem.corpID).tickerName, post]
                if type == 'alliance' and slimItem.allianceID:
                    try:
                        shiplabel += [pre, cfg.allianceshortnames.Get(slimItem.allianceID).shortName, post]
                    except:
                        log.LogError('Failed to get allianceName, itemID:', slimItem.itemID, 'allianceID:', slimItem.allianceID)

                if type == 'pilot name':
                    shiplabel += [pre, displayName, post]
                if type == 'ship type':
                    shiplabel += [pre, evetypes.GetName(slimItem.typeID), post]
                if type == 'ship name':
                    name = cfg.evelocations.Get(slimItem.itemID).name
                    if name:
                        shiplabel += [pre, name, post]

        return ''.join(shiplabel)

    def OnSlimItemChange(self, oldSlim, newSlim):
        bracket = self.GetBracket(newSlim.itemID)
        if not bracket:
            return
        if hasattr(bracket, 'OnSlimItemChange'):
            bracket.OnSlimItemChange(oldSlim, newSlim)
        bracket.slimItem = newSlim
        bracket.displayName = None
        if util.IsStarbase(newSlim.categoryID):
            if newSlim.posState == oldSlim.posState and newSlim.posTimestamp == oldSlim.posTimestamp and newSlim.incapacitated == oldSlim.incapacitated and newSlim.controllerID == oldSlim.controllerID and newSlim.ownerID == oldSlim.ownerID:
                return
            bracket.UpdateStructureState(newSlim)
        elif util.IsOrbital(newSlim.categoryID):
            if newSlim.orbitalState == oldSlim.orbitalState and newSlim.orbitalTimestamp == oldSlim.orbitalTimestamp and newSlim.ownerID == oldSlim.ownerID and newSlim.orbitalHackerID == oldSlim.orbitalHackerID and newSlim.orbitalHackerProgress == oldSlim.orbitalHackerProgress:
                return
            bracket.UpdateOrbitalState(newSlim)
        elif newSlim.groupID == const.groupPlanet and newSlim.corpID != oldSlim.corpID:
            if newSlim.corpID is not None:
                bracket.displaySubLabel = localization.GetByLabel('UI/DustLink/ControlledBy', corpName=cfg.eveowners.Get(newSlim.corpID).name)
            else:
                bracket.displaySubLabel = None
        elif HasBountyEscrowComponent(newSlim.typeID):
            bracket.displaySubLabel = GetBountyEscrowSubLabel(newSlim)
        if newSlim.corpID != oldSlim.corpID:
            uthread.pool('BracketMgr::OnSlimItemChange --> UpdateStates', bracket.UpdateFlagAndBackground, newSlim)
        if newSlim.groupID in const.environmentContainers:
            if newSlim.groupID == const.groupWreck and newSlim.isEmpty and not oldSlim.isEmpty:
                sm.GetService('state').SetState(newSlim.itemID, state.flagWreckEmpty, True)
            bracket.Load_update(newSlim)
        self.UpdateCaptureFromSlim(newSlim)

    def UpdateCaptureFromSlim(self, slimItem):
        if getattr(slimItem, 'capturePoint', None):
            if not hasattr(self, 'capturePoints'):
                self.capturePoints = {}
            slimItem.capturePoint['lastIncident'] = blue.os.GetSimTime()
            self.capturePoints[slimItem.itemID] = slimItem.capturePoint
            bracket = self.GetBracket(slimItem.itemID)
            if bracket:
                bracket.UpdateCaptureProgress(slimItem.capturePoint)

    def ProcessSessionChange(self, isremote, session, change):
        if not sm.GetService('connection').IsConnected() or session.stationid is not None or session.worldspaceid is not None or session.charid is None:
            self.CleanUp()
        elif not change.has_key('solarsystemid') and change.has_key('shipid') and change['shipid'][0] is not None:
            oldShipID, shipID = change['shipid']
            bp = sm.GetService('michelle').GetBallpark()
            slimItem = bp.GetInvItem(oldShipID)
            if slimItem is not None:
                self.RemoveBracket(slimItem.itemID)
                self.AddBracketIfWanted(slimItem)
            slimItem = bp.GetInvItem(shipID)
            if slimItem is not None:
                self.RemoveBracket(slimItem.itemID)
                self.AddBracketIfWanted(slimItem)

    def GetBracketProps(self, slimItem, ball):
        bracketData = self.GetBracketDataByTypeID(slimItem.typeID)
        if getattr(slimItem, 'isEmpty', False) and hasattr(bracketData, 'texturePathEmpty'):
            texturePath = bracketData.texturePathEmpty
        else:
            texturePath = bracketData.texturePath
        minVisibleDistance = getattr(bracketData, 'minVisibleDistance', 0.0)
        maxVisibleDistance = getattr(bracketData, 'maxVisibleDistance', INF)
        iconOffset = getattr(bracketData, 'iconOffset', 0)
        return (texturePath,
         1,
         minVisibleDistance,
         maxVisibleDistance,
         iconOffset,
         0)

    @telemetry.ZONE_METHOD
    def SlimItemIsDungeonObjectWithTriggers(self, slimItem):
        if self.scenarioMgr.editDungeonID:
            if IsJessicaOpen():
                import dungeon
                objectID = slimItem.dunObjectID
                if objectID:
                    obj = dungeon.Object.Get(objectID)
                    if obj is not None:
                        return obj.HasAnyTriggers()

    def PrimeLocations(self, slimItem):
        locations = []
        for each in slimItem.jumps:
            if each.locationID not in locations:
                locations.append(each.locationID)
            if each.toCelestialID not in locations:
                locations.append(each.toCelestialID)

        if len(locations):
            cfg.evelocations.Prime(locations)

    def DoBallsAdded(self, balls_slimItems, *args, **kw):
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::BracketMgr')
        try:
            uthread.new(self._AddBrackets, balls_slimItems).context = blue.pyos.taskletTimer.GetCurrent() + '::_AddBrackets'
        finally:
            t.PopTimer(timer)

    @telemetry.ZONE_METHOD
    def _AddBrackets(self, balls_slimItems):
        for ball, slimItem in balls_slimItems:
            self.AddBracketIfWanted(slimItem, ball)

    @telemetry.ZONE_METHOD
    def RemoveBracket(self, itemID):
        if itemID in self.brackets:
            bracket = self.brackets[itemID]
            if bracket is not None and not bracket.destroyed:
                bracket.Close()
            del self.brackets[itemID]
        if itemID in self.updateBrackets:
            del self.updateBrackets[itemID]

    @telemetry.ZONE_METHOD
    def AddBracketIfWanted(self, slimItem, ball = None):
        try:
            itemID = slimItem.itemID
            groupID = slimItem.groupID
            categoryID = slimItem.categoryID
            typeID = slimItem.typeID
            if not self.IsWanted(itemID, typeID=typeID, groupID=groupID, categoryID=categoryID, slimItem=slimItem):
                bracket = self.brackets.get(itemID, None)
                if bracket:
                    bracket.Hide()
                return
            bracket = self.brackets.get(itemID, None)
            if bracket:
                if not bracket.display:
                    bracket.Show()
                return
            ball = ball or sm.GetService('michelle').GetBall(itemID)
            if not ball:
                return
            panel = self.GetNewBracket(itemID=itemID, groupID=groupID, typeID=slimItem.typeID)
            self.brackets[itemID] = panel
            if self.SlimItemIsDungeonObjectWithTriggers(slimItem):
                bracket.name = 'bracketForTriggerObject%d' % slimItem.dunObjectID
                bracket.displayName = self.GetDisplayNameForBracket(slimItem) + ' (Trigger)'
                props = self.GetBracketProps(slimItem, ball)
                props = ('res:/UI/Texture/Icons/38_16_139.png',) + props[1:]
                self.SetupBracketProperties(bracket, ball, slimItem, props)
                panel.updateItem = False
            else:
                if typeID == const.typeAsteroidBelt:
                    panel.name = 'bracketAsteroidBelt'
                elif categoryID == const.categoryAsteroid:
                    panel.name = 'bracketAsteroid'
                elif categoryID == const.categoryStation:
                    panel.name = 'bracketStation'
                elif hasattr(slimItem, 'ownerID'):
                    if slimItem.ownerID == const.factionUnknown and groupID == const.groupPirateDrone:
                        panel.name = 'bracketNPCPirateDrone1'
                panel.displayName = None
                if groupID == const.groupPlanet and slimItem.corpID:
                    panel.displaySubLabel = localization.GetByLabel('UI/DustLink/ControlledBy', corpName=cfg.eveowners.Get(slimItem.corpID).name)
                elif HasBountyEscrowComponent(slimItem.typeID):
                    panel.displaySubLabel = GetBountyEscrowSubLabel(slimItem)
                else:
                    panel.displaySubLabel = None
                self.SetupBracketProperties(panel, ball, slimItem)
                panel.updateItem = sm.GetService('state').CheckIfUpdateItem(slimItem) and itemID != eve.session.shipid
            panel.Startup(slimItem, ball)
            if panel.updateItem:
                self.updateBrackets[itemID] = panel
            if hasattr(self, 'capturePoints') and itemID in self.capturePoints.keys():
                panel.UpdateCaptureProgress(self.capturePoints[itemID])
            else:
                self.UpdateCaptureFromSlim(slimItem)
            if util.IsOrbital(categoryID):
                panel.UpdateOrbitalState(slimItem)
            self.michelle.GetBallpark().componentRegistry.SendMessageToItem(itemID, MSG_ON_BRACKET_CREATED, panel, slimItem)
        except AttributeError as e:
            log.LogException(e)
            sys.exc_clear()

    def GetBracketClass(self, groupID, typeID):
        if typeID == const.typeMobileShippingUnit:
            return TimedBracket
        elif groupID == const.groupSiphonPseudoSilo:
            return SiphonSiloBracket
        else:
            return uicls.InSpaceBracket

    @telemetry.ZONE_METHOD
    def GetNewBracket(self, itemID = '', groupID = None, typeID = None):
        bracketCls = self.GetBracketClass(groupID, typeID)
        bracket = bracketCls(parent=uicore.layer.bracket, name='__inflightbracket_%s' % itemID, align=uiconst.NOALIGN, state=uiconst.UI_NORMAL)
        return bracket

    @telemetry.ZONE_METHOD
    def GetDisplayNameForBracket(self, slimItem):
        try:
            displayName = uix.GetSlimItemName(slimItem)
        except Exception as e:
            if slimItem:
                self.LogException('Couldnt generate name for bracket, slimItem is not None')
            else:
                self.LogException('Couldnt generate name for bracket, slimItem is None')
            return None

        groupID = slimItem.groupID
        categoryID = slimItem.categoryID
        if groupID == const.groupStation:
            displayName = uix.EditStationName(displayName, usename=1)
        elif groupID == const.groupStargate:
            uthread.new(self.PrimeLocations, slimItem)
        elif groupID == const.groupHarvestableCloud:
            displayName = localization.GetByLabel('UI/Generic/HarvestableCloud', item=slimItem.typeID)
        if not util.IsOrbital(categoryID) and slimItem.corpID:
            displayName = self.DisplayName(slimItem, displayName)
        return displayName

    @telemetry.ZONE_METHOD
    def SetupBracketProperties(self, bracket, ball, slimItem, props = None):
        if props is None:
            props = self.GetBracketProps(slimItem, ball)
        _iconNo, _dockType, _minDist, _maxDist, _iconOffset, _logflag = props
        tracker = bracket.projectBracket
        tracker.trackBall = ball
        tracker.name = unicode(cfg.evelocations.Get(ball.id).locationName)
        tracker.parent = uicore.layer.inflight.GetRenderObject()
        tracker.dock = _dockType
        tracker.marginRight = tracker.marginLeft + bracket.width
        tracker.marginBottom = tracker.marginTop + bracket.height
        bracket.data = props
        bracket.dock = _dockType
        bracket.minDispRange = _minDist
        bracket.maxDispRange = _maxDist
        bracket.inflight = True
        bracket.ball = ball
        bracket.invisible = False

    @telemetry.ZONE_METHOD
    def UpdateLabels(self):
        self.shipLabels = sm.GetService('state').GetShipLabels()
        self.hideCorpTicker = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName('hideCorpTicker', True)
        for bracket in self.brackets:
            slimItem = self.brackets[bracket].slimItem
            if not slimItem:
                continue
            if slimItem.corpID:
                self.brackets[slimItem.itemID].displayName = self.GetDisplayNameForBracket(slimItem)
                if slimItem.groupID == const.groupPlanet:
                    self.brackets[slimItem.itemID].displaySubLabel = localization.GetByLabel('UI/DustLink/ControlledBy', corpName=cfg.eveowners.Get(slimItem.corpID).name)
                elif HasBountyEscrowComponent(slimItem.typeID):
                    self.brackets[slimItem.itemID].displaySubLabel = GetBountyEscrowSubLabel(slimItem)

    @telemetry.ZONE_METHOD
    def RenewFlags(self):
        uthread.pool('BracketMgr::RenewFlags', self._RenewFlags)

    def _RenewFlags(self):
        for bracket in self.brackets.values():
            if bracket.destroyed:
                continue
            if bracket.itemID not in self.updateBrackets:
                if bracket.slimItem is None or bracket.slimItem.groupID not in const.containerGroupIDs:
                    continue
            bracket.Load_update(bracket.slimItem)
            blue.pyos.BeNice()

    def RenewSingleFlag(self, charID):
        uthread.new(self._RenewSingleFlag, charID)

    def _RenewSingleFlag(self, charID):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        for bracket in self.brackets.itervalues():
            slimItem = bracket.slimItem
            if slimItem is None:
                continue
            if bracket.itemID not in self.updateBrackets:
                if slimItem.groupID not in const.containerGroupIDs:
                    continue
            if getattr(slimItem, 'ownerID', None) == charID:
                bracket.Load_update(slimItem)
            elif getattr(slimItem, 'charID', None) == charID:
                bracket.Load_update(slimItem)
            blue.pyos.BeNice()

    def OnBallparkCall(self, funcName, args):
        if funcName == 'SetBallFree':
            itemID, isFree = args
            bracket = self.GetBracket(itemID)
            if bracket:
                slimItem = bracket.slimItem
                if slimItem:
                    bracket.SetBracketAnchoredState(slimItem)

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        if isRelease:
            for itemID, bracket in self.brackets.iteritems():
                if bracket is not None and not bracket.destroyed:
                    bracket.Close()

            self.capturePoints = {}
            self.brackets = {}
            self.updateBrackets = {}
            return
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return
        self.LogInfo('DoBallRemove::bracketMgr', ball.id)
        self.RemoveBracket(ball.id)
        if ball.id in getattr(self, 'capturePoints', {}).keys():
            del self.capturePoints[ball.id]

    def DoBallClear(self, solitem):
        self.brackets = {}
        self.updateBrackets = {}
        for bracket in uicore.layer.bracket.children:
            bracket.Close()

    def OnUIScalingChange(self, *args):
        self.Reload()

    def OnDestinationSet(self, destinationID = None):
        focusOn = []
        updateGroups = (const.groupStation, const.groupStargate)
        for each in uicore.layer.bracket.children:
            if not getattr(each, 'IsBracket', 0) or each.destroyed:
                continue
            if not each.slimItem or each.slimItem.groupID not in updateGroups:
                continue
            each.UpdateIconColor(each.slimItem)
            if each.sr.icon and each.sr.icon.GetRGB() != const.OVERVIEW_NORMAL_COLOR:
                focusOn.append(each)

        for each in focusOn:
            each.SetOrder(0)

    def OnFleetStateChange(self, fleetState):
        if fleetState:
            for itemID, tag in fleetState.targetTags.iteritems():
                bracket = self.GetBracket(itemID)
                if not bracket:
                    continue
                if bracket.slimItem:
                    bracket.Load_update(bracket.slimItem)

    def OnFleetJoin_Local(self, member, *args):
        self.UpdateWrecksAndContainers(member)

    def OnFleetLeave_Local(self, member, *args):
        self.UpdateWrecksAndContainers(member)

    def UpdateWrecksAndContainers(self, member):
        if member.charID == session.charid:
            for bracket in self.brackets.values():
                if bracket.slimItem and bracket.slimItem.groupID in (const.groupWreck, const.groupCargoContainer):
                    bracket.Load_update(bracket.slimItem)

    def OnStateChange(self, itemID, flag, flagState, *args):
        if flag in (state.selected, state.targeted, state.targeting):
            slimItem = uix.GetBallparkRecord(itemID)
            if not slimItem:
                return
            IsWanted = self.IsWanted(slimItem.itemID, slimItem=slimItem)
            if flagState:
                self.AddBracketIfWanted(slimItem)
            elif not IsWanted:
                self.RemoveBracket(slimItem.itemID)
                if self.SlimItemIsDungeonObjectWithTriggers(slimItem):
                    self.AddBracketIfWanted(slimItem)
                return
        bracket = self.GetBracket(itemID)
        if bracket:
            try:
                bracket.OnStateChange(itemID, flag, flagState, *args)
            except AttributeError:
                pass

    def OnAttribute(self, attributeName, item, newValue):
        if item.itemID == session.shipid and attributeName == 'scanResolution':
            for targetID in sm.GetService('target').GetTargeting():
                bracket = self.GetBracket(targetID)
                if bracket and hasattr(bracket, 'OnAttribute'):
                    bracket.OnAttribute(attributeName, item, newValue)

    def OnAttributes(self, changeList):
        for t in changeList:
            self.OnAttribute(*t)

    def OnPostCfgDataChanged(self, what, data):
        if what == 'evelocations':
            bracket = self.GetBracket(data[0])
            if bracket is not None:
                bracket.displayName = None

    def OnCaptureChanged(self, ballID, captureID, lastIncident, points, captureTime, lastCapturing):
        bracket = self.GetBracket(ballID)
        if not hasattr(self, 'capturePoints'):
            self.capturePoints = {}
        self.capturePoints[ballID] = {'captureID': captureID,
         'lastIncident': blue.os.GetSimTime(),
         'points': points,
         'captureTime': captureTime,
         'lastCapturing': lastCapturing}
        if bracket:
            bracket.UpdateCaptureProgress(self.capturePoints[ballID])

    def ResetOverlaps(self):
        for each in self.overlaps:
            if not getattr(each, 'IsBracket', 0):
                continue
            projectBracket = each.projectBracket
            if projectBracket:
                projectBracket.bracket = each.GetRenderObject()
                each.KillLabel()
                each.opacity = getattr(each, '_pervious_opacity', 1.0)
                each.SetAlign(uiconst.NOALIGN)

        for each in self.overlapsHidden:
            bubble = each.sr.bubble
            if bubble:
                bubble.state = uiconst.UI_PICKCHILDREN

        self.overlaps = []
        self.overlapsHidden = []

    def GetOverlapOverlap(self, sameX, minY, maxY):
        overlaps = []
        stillLeft = []
        for bracket in sameX:
            if bracket.absoluteTop > minY - 16 and bracket.absoluteBottom < maxY + 16:
                if bracket.displayName:
                    overlaps.append((bracket.displayName.lower(), bracket))
                else:
                    overlaps.append(('', bracket))
            else:
                stillLeft.append(bracket)

        return (overlaps, stillLeft)

    def CheckingOverlaps(self):
        return self.checkingOverlaps

    @telemetry.ZONE_METHOD
    def CheckOverlaps(self, sender, hideRest = 0):
        self.checkingOverlaps = sender.itemID
        self.ResetOverlaps()
        overlaps = []
        excludedC = (const.categoryAsteroid,)
        excludedG = (const.groupHarvestableCloud,)
        sameX = []
        LEFT = 0
        TOP = 1
        BOTTOM = 2
        RIGHT = 3
        BRACKETSIZE = 16
        MAXEXPANDED = 15

        @util.Memoized
        def GetAbsolute(bracket):
            ro = bracket.GetRenderObject()
            x, y = uicore.ReverseScaleDpi(ro.displayX), uicore.ReverseScaleDpi(ro.displayY)
            centerX = x + bracket.width / 2
            centerY = y + bracket.height / 2
            return (centerX - 8,
             centerY - 8,
             centerY + 8,
             centerX + 8)

        s = GetAbsolute(sender)
        topMargin, bottomMargin = sender.GetLockedPositionTopBottomMargin()
        sender._topMargin = topMargin
        sender._bottomMargin = bottomMargin
        totalHeight = BRACKETSIZE + topMargin
        for bracket in sender.parent.children:
            if not getattr(bracket, 'IsBracket', 0) or not bracket.display or bracket.invisible or bracket.categoryID in excludedC or bracket.groupID in excludedG or bracket == sender:
                continue
            b = GetAbsolute(bracket)
            overlapx = not (b[RIGHT] <= s[LEFT] or b[LEFT] >= s[RIGHT])
            overlapy = not (b[BOTTOM] <= s[TOP] or b[TOP] >= s[BOTTOM])
            if overlapx and overlapy and bracket.displayName:
                topMargin, bottomMargin = bracket.GetLockedPositionTopBottomMargin()
                bracket._topMargin = topMargin
                bracket._bottomMargin = bottomMargin
                totalHeight += topMargin + BRACKETSIZE + bottomMargin
                overlaps.append((bracket.displayName.lower(), bracket))
            elif overlapx and not overlapy:
                sameX.append(bracket)
            if len(overlaps) == MAXEXPANDED:
                break

        if not overlaps:
            self.checkingOverlaps = None
            sender.parent.state = uiconst.UI_PICKCHILDREN
            return
        if sameX:
            while len(overlaps) < MAXEXPANDED:
                minY = s[TOP] - totalHeight
                maxY = s[BOTTOM]
                oo, sameX = self.GetOverlapOverlap(sameX, minY, maxY)
                if not oo or not sameX:
                    break
                for overlap in oo:
                    overlaps.append(overlap)
                    topMargin, bottomMargin = overlap[1].GetLockedPositionTopBottomMargin()
                    overlap[1]._topMargin = topMargin
                    overlap[1]._bottomMargin = bottomMargin
                    totalHeight += topMargin + BRACKETSIZE + bottomMargin
                    if len(overlaps) == MAXEXPANDED:
                        break

        overlaps = uiutil.SortListOfTuples(overlaps, reverse=True)

        def LockBracketPosition(bracket, left, top):
            projectBracket = bracket.projectBracket
            if projectBracket:
                projectBracket.bracket = None
            bracket.SetAlign(uiconst.TOPLEFT)
            bracket.left = left - bracket.width / 2
            lockedTopPos = top - (bracket.height - 16) / 2
            bracket.top = lockedTopPos
            bracket._lockedTopPos = lockedTopPos
            bracket.displayX = left
            bracket._pervious_opacity = bracket.opacity
            bracket.opacity = 1.0
            bracket.SetOrder(0)
            if hasattr(bracket, 'UpdateSubItems'):
                bracket.UpdateSubItems()

        top = s[TOP]
        left = s[LEFT] + BRACKETSIZE / 2
        sender._lockedTopPos = top
        self.overlaps = [sender] + overlaps
        for overlapBracket in self.overlaps:
            hasBubble = bool(overlapBracket.sr.bubble)
            if not hasBubble:
                overlapBracket.ShowLabel()
            if overlapBracket is not sender:
                top -= overlapBracket._bottomMargin
            LockBracketPosition(overlapBracket, left, top)
            top -= overlapBracket._topMargin + BRACKETSIZE

        self.overlapsHidden = []
        if hideRest:
            for bracket in sender.parent.children:
                if bracket is sender or bracket in overlaps or not getattr(bracket, 'IsBracket', 0) or bracket.state != uiconst.UI_PICKCHILDREN or bracket.invisible:
                    continue
                bubble = bracket.sr.bubble
                if bubble:
                    bubble.state = uiconst.UI_HIDDEN
                    self.overlapsHidden.append(bracket)

        if top < 0:
            for overlapBracket in self.overlaps:
                overlapBracket.top = -top + overlapBracket._lockedTopPos - BRACKETSIZE

        sender.parent.state = uiconst.UI_PICKCHILDREN
        self.checkingOverlaps = None
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.OnGlobalMouseDown)

    def OnGlobalMouseDown(self, *args):
        mo = uicore.uilib.mouseOver
        for bracket in self.overlaps:
            if mo in (bracket, bracket.label):
                return True

        self.ResetOverlaps()

    def GetBracket(self, bracketID):
        if getattr(self, 'brackets', None) is not None:
            return self.brackets.get(bracketID, None)

    def ClearBracket(self, id, *args, **kwds):
        self.RemoveBracket(id)

    def GetScanSpeed(self, source = None, target = None):
        if source is None:
            source = eve.session.shipid
        if not source:
            return
        myitem = sm.GetService('godma').GetItem(source)
        scanSpeed = None
        if myitem.scanResolution and target:
            slimItem = target
            targetitem = sm.GetService('godma').GetType(slimItem.typeID)
            if targetitem.AttributeExists('signatureRadius'):
                radius = targetitem.signatureRadius
            else:
                radius = 0
            if radius <= 0.0:
                bp = sm.GetService('michelle').GetBallpark()
                radius = bp.GetBall(slimItem.itemID).radius
                if radius <= 0.0:
                    radius = evetypes.GetRadius(targetitem.typeID)
                    if radius <= 0.0:
                        radius = 1.0
            scanSpeed = 40000000.0 / myitem.scanResolution / math.log(radius + math.sqrt(radius * radius + 1)) ** 2.0
        if scanSpeed is None:
            scanSpeed = 2000
            log.LogWarn('GetScanSpeed returned the defauly scanspeed of %s ms ... missing scanResolution?' % scanSpeed)
        return min(scanSpeed, 180000)

    def GetCaptureData(self, ballID):
        if hasattr(self, 'capturePoints'):
            return self.capturePoints.get(ballID, None)

    def OnBSDTablesChanged(self, tableDataUpdated):
        if 'dungeon.triggers' in tableDataUpdated.iterkeys():
            if IsJessicaOpen():
                for slimItem in self.scenarioMgr.GetDunObjects():
                    self.RemoveBracket(slimItem.itemID)
                    self.AddBracketIfWanted(slimItem)

    def ProcessShipEffect(self, godmaStm, effectState):
        moduleID, characterID, shipID, targetID, otherID, areaIDs, effectID = effectState.environment
        if effectID == const.effectHackOrbital:
            bracket = self.GetBracket(targetID)
            if bracket:
                slimItem = bracket.slimItem
                if effectState.active:
                    progress = sm.GetService('planetInfo').GetMyHackProgress(targetID)
                    bracket.BeginHacking()
                    bracket.UpdateHackProgress(progress)
                    if slimItem:
                        bracket.UpdateOrbitalState(slimItem)
                else:
                    progress = sm.GetService('planetInfo').GetMyHackProgress(targetID)
                    bracket.StopHacking(success=progress is not None and progress >= 1.0)

    def ProcessBountyInfoUpdated(self, itemIDs):
        for itemID in itemIDs:
            try:
                self.brackets[itemID].RefreshBounty()
            except KeyError:
                pass

    @telemetry.ZONE_METHOD
    def OnDamageMessages(self, dmgmsgs):
        for msg in dmgmsgs:
            self.OnDamageMessage(*msg[1:])

    @telemetry.ZONE_METHOD
    def OnDamageMessage(self, damageMessagesArgs):
        attackerID = damageMessagesArgs.get('attackerID', None)
        if attackerID is None:
            attackType = damageMessagesArgs.get('attackType', 'me')
            if attackType != 'me':
                self.LogWarn('No attacker found! - damageMessagesArgs = ', damageMessagesArgs)
            return
        damage = damageMessagesArgs['damage']
        s = blue.os.GetSimTime() / const.SEC
        if attackerID not in self.damageByBracketID:
            self.damageByBracketID[attackerID] = collections.defaultdict(long)
        self.damageByBracketID[attackerID][s] += int(damage)
        if damage:
            self.TryBlinkAttacker(attackerID)

    def DisableShowingDamageDealers(self, *args):
        if self.damageDealerTimer is None:
            return
        self.damageDealerTimer = None
        if not session.shipid:
            return
        oldDamageDealers = self.biggestDamageDealers[:]
        self.RemoveDamageIndicatorFromBrackets(oldDamageDealers, [])

    def EnableShowingDamageDealers(self, *args):
        if self.damageDealerTimer is None:
            self.ShowBiggestDamageDealers_thread()
            self.damageDealerTimer = base.AutoTimer(1000, self.ShowBiggestDamageDealers_thread)

    def TryBlinkAttacker(self, attackerID, *args):
        if attackerID not in self.biggestDamageDealers:
            return
        bracket = self.GetBracket(attackerID)
        if not bracket:
            return
        sprite = bracket.GetHitSprite(create=False)
        if sprite:
            uicore.animations.FadeTo(sprite, startVal=sprite.baseOpacity + 0.05, endVal=sprite.baseOpacity, duration=0.75, loops=1, curveType=uiconst.ANIM_OVERSHOT)

    def ShowBiggestDamageDealers_thread(self, *args):
        oldDamageDealers = self.biggestDamageDealers[:]
        newDamageDealers = self.FindBiggestDamageDealers()
        alphas = [0.25,
         0.2,
         0.15,
         0.12,
         0.08]
        size = [100,
         90,
         80,
         75,
         70]
        counter = 0
        self.biggestDamageDealers = []
        for damage, bracketID in newDamageDealers:
            bracket = self.GetBracket(bracketID)
            if bracket:
                sprite = bracket.GetHitSprite()
                currentPlace = getattr(sprite, 'currentPlace', None)
                duration = 0.2
                newOpacity = alphas[counter]
                sprite.baseOpacity = newOpacity
                newSize = size[counter]
                if currentPlace is None:
                    sprite.width = sprite.height = newSize
                    uicore.animations.FadeTo(sprite, startVal=0, endVal=newOpacity, duration=duration)
                else:
                    uicore.animations.FadeTo(sprite, startVal=sprite.opacity, endVal=newOpacity, duration=duration)
                    uicore.animations.MorphScalar(sprite, 'width', startVal=sprite.width, endVal=newSize, duration=duration)
                    uicore.animations.MorphScalar(sprite, 'height', startVal=sprite.height, endVal=newSize, duration=duration)
                sprite.currentPlace = counter
                self.biggestDamageDealers.append(bracketID)
                if getattr(prefs, 'showDamageOnTarget', False):
                    label = getattr(bracket, 'debugLabel', None)
                    if not label:
                        label = bracket.debugLabel = uicontrols.EveLabelSmall(text='', parent=bracket, top=42, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED)
                    label.text = damage
            counter += 1

        self.RemoveDamageIndicatorFromBrackets(oldDamageDealers, self.biggestDamageDealers)

    def RemoveDamageIndicatorFromBrackets(self, oldDamageDealers, newDamageDealers, *args):
        for bracketID in oldDamageDealers:
            if bracketID in newDamageDealers:
                continue
            bracket = self.GetBracket(bracketID)
            if bracket is None:
                continue
            sprite = bracket.GetHitSprite(create=False)
            if sprite:
                sprite.Close()
            label = getattr(bracket, 'debugLabel', None)
            if label:
                label.Close()

    def FindBiggestDamageDealers(self, *args):
        numDamageDealers = NUMBER_OF_DAMAGEDEALERS
        now = blue.os.GetSimTime() / const.SEC
        timeline = now - RECORDED_DAMAGE_PERIOD_SECONDS
        attackersToRemove = []
        damageSumAndAttackerID = []
        for attackerID in self.damageByBracketID:
            latestAttacks = collections.defaultdict(long)
            for timestamp, value in self.damageByBracketID[attackerID].iteritems():
                if timestamp > timeline:
                    latestAttacks[timestamp] = value

            if len(latestAttacks) == 0:
                attackersToRemove.append(attackerID)
                continue
            self.damageByBracketID[attackerID] = latestAttacks
            if attackerID in self.brackets:
                totalDamage = sum(latestAttacks.itervalues())
                if totalDamage == 0:
                    continue
                attackersDamageTuple = (totalDamage, attackerID)
                damageSumAndAttackerID.append(attackersDamageTuple)

        for attackerID in attackersToRemove:
            del self.damageByBracketID[attackerID]

        damageSumAndAttackerID.sort(reverse=True)
        results = damageSumAndAttackerID[:numDamageDealers]
        return results

    def DisableInTargetRange(self, *args):
        if self.inTargetRangeTimer is None:
            return
        self.inTargetRangeTimer = None
        if not session.shipid:
            return
        for key, bracket in self.brackets.items():
            canTargetSprite = bracket.GetCanTargetSprite(create=False)
            if canTargetSprite:
                canTargetSprite.Close()

    def EnableInTargetRange(self, *args):
        if self.inTargetRangeTimer is None:
            self.ShowInTargetRange()
            self.inTargetRangeTimer = base.AutoTimer(1000, self.ShowInTargetRange)

    def ShowInTargetRange(self, *args):
        if not session.shipid:
            return
        bp = sm.GetService('michelle').GetBallpark()
        ship = sm.GetService('godma').GetItem(session.shipid)
        if ship is None:
            return
        maxTargetRange = ship.maxTargetRange
        for key, bracket in self.brackets.items():
            if not bracket or bracket.destroyed or key == session.shipid:
                continue
            if bracket.categoryID not in (const.categoryShip, const.categoryEntity, const.categoryDrone):
                continue
            settingConfigName = 'showCategoryInTargetRange_%s' % bracket.categoryID
            showCategory = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName(settingConfigName, True)
            distance = self.GetBallDistanceFromBracketKey(bp, key)
            if distance is None:
                continue
            canTargetSprite = bracket.GetCanTargetSprite()
            if canTargetSprite is not None:
                if distance > maxTargetRange or not showCategory:
                    newOpacity = 0.0
                    canTargetSprite.display = False
                    continue
                elif getattr(bracket, 'brighterForRange', False):
                    newOpacity = 1.0
                else:
                    newOpacity = 0.15
                canTargetSprite.display = True
                if canTargetSprite.opacity != newOpacity:
                    canTargetSprite.opacity = newOpacity or 0

    def ShowModuleRange(self, moduleID, rangeDistance, *args):
        showInTargetRange = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName('showInTargetRange', True)
        if not showInTargetRange:
            return
        bp = sm.GetService('michelle').GetBallpark()
        maxTargetRange = sm.GetService('godma').GetItem(session.shipid).maxTargetRange
        for key, bracket in self.brackets.items():
            if not bracket or bracket.destroyed or key == session.shipid:
                continue
            if bracket.categoryID not in (const.categoryShip, const.categoryEntity, const.categoryDrone):
                continue
            distance = self.GetBallDistanceFromBracketKey(bp, key)
            if distance is None:
                continue
            if distance <= rangeDistance and distance <= maxTargetRange:
                bracket.brighterForRange = True
                canTargetSprite = bracket.GetCanTargetSprite()
                if canTargetSprite is not None:
                    canTargetSprite.opacity = 1.0

    def ShowHairlinesForModule(self, moduleID, reverse = False):
        showHairlines = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName('showModuleHairlines', True)
        if not showHairlines:
            if self.hairlinesTimer:
                self.hairlinesTimer = None
                self.StopShowingHairlines()
                ship = sm.GetService('michelle').GetBall(session.shipid)
                for moduleID in ship.modules:
                    self.ResetModuleIcon(moduleID)

            return
        for target in sm.GetService('target').targetsByID.itervalues():
            if not isinstance(target, (xtriui.Target, uicls.TargetInBar)):
                continue
            if target is None or target.destroyed:
                continue
            if target.activeModules.get(moduleID, False):
                weapon = target.GetWeapon(moduleID)
                if isinstance(target, xtriui.Target):
                    icon = weapon
                else:
                    icon = weapon.icon
                icon.SetAlpha(1.5)
                bracket = self.brackets.get(target.itemID)
                if bracket is None:
                    return
                self.ShowHairlines(moduleID, bracket, target, reverse)
                return

    def ShowHairlines(self, moduleID, bracket, target, reverse, *args):
        if getattr(self, 'vectorLines', None) is None:
            self.vectorLines = bracketUtils.TargetingHairlines()
            self.vectorLines.CreateHairlines(moduleID, bracket, target)
        self.vectorLines.UpdateHairlinePoints(moduleID, bracket, target)
        self.vectorLines.StartAnimation(reverse=reverse)
        self.hairlinesTimer = base.AutoTimer(50, self.AnimateVectorLine, moduleID, bracket, target)

    def AnimateVectorLine(self, moduleID, bracket, target, *args):
        if getattr(self, 'vectorLines', None) is None:
            return
        if bracket.destroyed:
            self.vectorLines.StopAnimations()
            self.vectorLines.HideLines()
            self.hairlinesTimer = None
            return
        self.vectorLines.UpdateHairlinePoints(moduleID, bracket, target)

    def StopShowingModuleRange(self, moduleID, *args):
        for key, bracket in self.brackets.items():
            if not bracket or bracket.destroyed:
                continue
            if getattr(bracket, 'brighterForRange', False):
                canTargetSprite = bracket.GetCanTargetSprite()
                if canTargetSprite is not None:
                    canTargetSprite.opacity = 0.3
                bracket.brighterForRange = False

        self.StopShowingHairlines()
        self.ResetModuleIcon(moduleID)

    def ResetModuleIcon(self, moduleID, *args):
        for target in sm.GetService('target').GetTargets().itervalues():
            if not isinstance(target, uicls.TargetInBar):
                continue
            target.ResetModuleIcon(moduleID)

    def StopShowingHairlines(self, *args):
        self.hairlinesTimer = None
        if getattr(self, 'vectorLines', None) is not None:
            self.vectorLines.HideLines()
            self.vectorLines.StopAnimations()

    def GetBallDistanceFromBracketKey(self, bp, bracketKey, *args):
        ball = bp.GetBall(bracketKey)
        if ball is None:
            return
        try:
            distance = int(ball.surfaceDist)
        except ValueError:
            return

        return distance
