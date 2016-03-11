#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\statsPanel.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
import dogma.const as dogmaConst
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.expandablemenu import ExpandableMenuContainer
from eve.client.script.ui.shared.fitting.fittingUtil import GetFittingDragData
from eve.client.script.ui.shared.fittingGhost.ghostFittingPanels.capacitorPanel import CapacitorPanel
from eve.client.script.ui.shared.fittingGhost.ghostFittingPanels.defensePanel import DefensePanel
from eve.client.script.ui.shared.fittingGhost.ghostFittingPanels.dronePanel import DronePanel
from eve.client.script.ui.shared.fittingGhost.ghostFittingPanels.navigationPanel import NavigationPanel
from eve.client.script.ui.shared.fittingGhost.ghostFittingPanels.offensePanel import OffensePanel
from eve.client.script.ui.shared.fittingGhost.ghostFittingPanels.targetingPanel import TargetingPanel
from eve.client.script.ui.shared.fitting.storedFittingsButtons import StoredFittingsButtons
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
import evetypes
import inventorycommon.const as invConst
from localization import GetByLabel
import uthread
NO_HILITE_GROUPS_DICT = {invConst.groupRemoteSensorBooster: [dogmaConst.attributeCpu, dogmaConst.attributePower],
 invConst.groupRemoteSensorDamper: [dogmaConst.attributeCpu, dogmaConst.attributePower]}

class StatsPanelGhost(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.controller.on_new_itemID.connect(self.OnNewItemID)
        self.controller.on_stats_changed.connect(self.UpdateStats)
        self.controller.on_name_changed.connect(self.UpdateShipName)
        self.controller.on_item_ghost_fitted.connect(self.UpdateStats)
        self.ConstructNameCaption()
        self.ConstructStoredFittingsButtons()
        self.CreateCapacitorPanel()
        self.CreateOffensePanel()
        self.CreateDefensePanel()
        self.CreateTargetingPanel()
        self.CreateNavigationPanel()
        self.CreateDronePanel()
        self.CreateExpandableMenus()
        uthread.new(self.UpdateStats)

    def ConstructNameCaption(self):
        self.nameCaptionCont = Container(name='shipname', parent=self, align=uiconst.TOTOP, height=12, padBottom=6)
        self.nameCaption = EveLabelMedium(text='', parent=self.nameCaptionCont, width=250, autoFitToText=True, state=uiconst.UI_NORMAL)
        SetTooltipHeaderAndDescription(targetObject=self.nameCaption, headerText='', descriptionText=GetByLabel('Tooltips/FittingWindow/ShipName_description'))
        self.nameCaption.GetDragData = GetFittingDragData
        self.infolink = InfoIcon(left=0, top=0, parent=self.nameCaptionCont, idx=0)
        self.UpdateShipName()

    def UpdateShipName(self):
        typeID = self.controller.GetTypeID()
        itemID = self.controller.GetItemID()
        if isinstance(itemID, long) and isinstance(typeID, int):
            name = cfg.evelocations.Get(itemID).name
            typeName = evetypes.GetName(typeID)
        else:
            name = 'my ship'
            typeName = 'some ship name'
        self.nameCaption.text = name
        self.nameCaption.tooltipPanelClassInfo.headerText = name
        oneLineHeight = self.nameCaptionCont.height
        lines = max(1, self.nameCaption.height / max(1, self.nameCaptionCont.height))
        margin = 3
        self.nameCaptionCont.height = lines * oneLineHeight + margin * (lines - 1)
        self.nameCaption.hint = typeName
        self.infolink.left = self.nameCaption.textwidth + 6
        if self.infolink.left + 50 > self.nameCaptionCont.width:
            self.infolink.left = 0
            self.infolink.SetAlign(uiconst.TOPRIGHT)

    def ConstructStoredFittingsButtons(self):
        self.fittingSvcBtnGroup = StoredFittingsButtons(name='StoredFittingsButtons', parent=self, align=uiconst.TOBOTTOM, controller=self.controller)

    def CreateCapacitorPanel(self):
        self.capacitorStatsParent = CapacitorPanel(name='capacitorStatsParent', controller=self.controller)
        return self.capacitorStatsParent

    def CreateOffensePanel(self):
        self.offenseStatsParent = OffensePanel(name='offenseStatsParent', tooltipName='DamagePerSecond', labelHint=GetByLabel('UI/Fitting/FittingWindow/ShipDpsTooltip'), controller=self.controller)
        return self.offenseStatsParent

    def CreateDefensePanel(self):
        self.defenceStatsParent = DefensePanel(name='defenceStatsParent', state=uiconst.UI_PICKCHILDREN, tooltipName='EffectiveHitPoints', labelHint=GetByLabel('UI/Fitting/FittingWindow/EffectiveHitpoints'), controller=self.controller)
        return self.defenceStatsParent

    def CreateTargetingPanel(self):
        self.targetingStatsParent = TargetingPanel(name='targetingStatsParent', tooltipName='MaxTargetingRange', controller=self.controller)
        return self.targetingStatsParent

    def CreateNavigationPanel(self):
        self.navigationStatsParent = NavigationPanel(name='navigationStatsParent', state=uiconst.UI_PICKCHILDREN, tooltipName='MaximumVelocity', labelHint=GetByLabel('UI/Fitting/FittingWindow/MaxVelocityHint'), controller=self.controller)
        return self.navigationStatsParent

    def CreateDronePanel(self):
        self.droneStatsParent = DronePanel(name='droneStatsParent', tooltipName='DamagePerSecond', labelHint=GetByLabel('UI/Fitting/FittingWindow/ShipDpsTooltip'), controller=self.controller)
        return self.droneStatsParent

    def GetSingleMenuPanelInfo(self, menuDict):
        return (GetByLabel(menuDict['label']),
         menuDict['content'],
         menuDict['callback'],
         None,
         menuDict['maxHeight'],
         menuDict['headerContent'],
         False,
         menuDict.get('expandedByDefault', False))

    def GetMenuData(self):
        capInfo = self.GetSingleMenuPanelInfo({'label': 'UI/Fitting/FittingWindow/Capacitor',
         'content': self.capacitorStatsParent,
         'callback': self.LoadCapacitorStats,
         'maxHeight': 60,
         'headerContent': self.capacitorStatsParent.headerParent,
         'expandedByDefault': True})
        offenseInfo = self.GetSingleMenuPanelInfo({'label': 'UI/Fitting/FittingWindow/Offense',
         'content': self.offenseStatsParent,
         'callback': self.LoadOffenseStats,
         'maxHeight': 56,
         'headerContent': self.offenseStatsParent.headerParent})
        defenseInfo = self.GetSingleMenuPanelInfo({'label': 'UI/Fitting/FittingWindow/Defense',
         'content': self.defenceStatsParent,
         'callback': self.LoadDefenceStats,
         'maxHeight': 150,
         'headerContent': self.defenceStatsParent.headerParent})
        targetingInfo = self.GetSingleMenuPanelInfo({'label': 'UI/Fitting/FittingWindow/Targeting',
         'content': self.targetingStatsParent,
         'callback': self.LoadTargetingStats,
         'maxHeight': 84,
         'headerContent': self.targetingStatsParent.headerParent})
        navigationInfo = self.GetSingleMenuPanelInfo({'label': 'UI/Fitting/FittingWindow/Navigation',
         'content': self.navigationStatsParent,
         'callback': self.LoadNavigationStats,
         'maxHeight': 84,
         'headerContent': self.navigationStatsParent.headerParent})
        droneInfo = self.GetSingleMenuPanelInfo({'label': 'UI/Drones/Drones',
         'content': self.droneStatsParent,
         'callback': self.LoadDroneStats,
         'maxHeight': 84,
         'headerContent': self.droneStatsParent.headerParent})
        menuData = [capInfo,
         offenseInfo,
         defenseInfo,
         targetingInfo,
         navigationInfo,
         droneInfo]
        return menuData

    def CreateExpandableMenus(self):
        em = ExpandableMenuContainer(parent=self, pos=(0, 0, 0, 0), clipChildren=True)
        em.multipleExpanded = True
        menuData = self.GetMenuData()
        em.Load(menuData=menuData, prefsKey='fittingRightside')

    def LoadDroneStats(self, initialLoad = False):
        self.droneStatsParent.LoadPanel(initialLoad=initialLoad)

    def LoadNavigationStats(self, initialLoad = False):
        self.navigationStatsParent.LoadPanel(initialLoad=initialLoad)

    def LoadTargetingStats(self, initialLoad = False):
        self.targetingStatsParent.LoadPanel(initialLoad=initialLoad)

    def LoadOffenseStats(self, initialLoad = False):
        self.offenseStatsParent.LoadPanel(initialLoad)

    def UpdateOffenseStats(self):
        self.offenseStatsParent.UpdateOffenseStats()

    def UpdateDroneStats(self):
        self.droneStatsParent.UpdateDroneStats()

    def LoadDefenceStats(self, initialLoad = False):
        self.defenceStatsParent.LoadPanel(initialLoad)

    def LoadCapacitorStats(self, initialLoad = False):
        self.capacitorStatsParent.LoadPanel(initialLoad)

    def ExpandBestRepair(self, *args):
        self.defenceStatsParent.ExpandBestRepair(*args)

    def UpdateBestRepair(self, item, modulesByGroupInShip, multiplyShieldCapacity, multiplyShieldRecharge):
        return self.defenceStatsParent.UpdateBestRepair(item, modulesByGroupInShip, multiplyShieldCapacity, multiplyShieldRecharge)

    def UpdateNavigationPanel(self):
        self.navigationStatsParent.UpdateNavigationPanel()

    def UpdateTargetingPanel(self):
        self.targetingStatsParent.UpdateTargetingPanel()

    def UpdateCapacitor(self, xtraCapacitor = 0.0, rechargeMultiply = 1.0, multiplyCapacitor = 1.0, reload = 0):
        self.capacitorStatsParent.UpdateCapacitorPanel(self.controller.GetItemID(), xtraCapacitor, rechargeMultiply, multiplyCapacitor, reload)

    def UpdateDefensePanel(self):
        return self.defenceStatsParent.UpdateDefensePanel()

    def UpdateStats(self):
        item = self.controller.GetGhostFittedItem()
        typeID = self.controller.GetGhostFittedTypeID()
        if session.stationid2:
            self.fittingSvcBtnGroup.stripBtn.Enable()
        else:
            self.fittingSvcBtnGroup.stripBtn.Disable()
        multiplyRecharge = 1.0
        xtraCapacitor = 0.0
        multiplyCapacitor = 1.0
        multiplyShieldRecharge = 1.0
        multiplyShieldCapacity = 1.0
        modulesByGroupInShip = self.controller.GetFittedModulesByGroupID()
        typeAttributesByID = {}
        if typeID:
            for attribute in cfg.dgmtypeattribs.get(typeID, []):
                typeAttributesByID[attribute.attributeID] = attribute.value

            dgmAttr = sm.GetService('godma').GetType(typeID)
            doHilite = dgmAttr.groupID not in NO_HILITE_GROUPS_DICT
            allowedAttr = dgmAttr.displayAttributes
            for attribute in allowedAttr:
                if not doHilite and attribute.attributeID not in NO_HILITE_GROUPS_DICT[dgmAttr.groupID]:
                    continue
                elif attribute.attributeID == dogmaConst.attributeCapacitorBonus:
                    xtraCapacitor += attribute.value
                elif attribute.attributeID == dogmaConst.attributeCapacitorCapacityMultiplier:
                    multiplyCapacitor *= attribute.value
                elif attribute.attributeID == dogmaConst.attributeCapacitorCapacityBonus:
                    multiplyCapacitor = 1 + attribute.value / 100
                elif attribute.attributeID == dogmaConst.attributeCapacitorRechargeRateMultiplier:
                    multiplyRecharge = multiplyRecharge * attribute.value
                elif attribute.attributeID == dogmaConst.attributeCapRechargeBonus:
                    multiplyRecharge = 1 + attribute.value / 100
                elif attribute.attributeID == dogmaConst.attributeShieldRechargeRateMultiplier:
                    multiplyShieldRecharge = attribute.value
                elif attribute.attributeID == dogmaConst.attributeShieldCapacityMultiplier:
                    multiplyShieldCapacity *= attribute.value

        dsp = getattr(self, 'defenceStatsParent', None)
        if not dsp or dsp.destroyed:
            return
        self.UpdateDefensePanel()
        self.UpdateBestRepair(item, modulesByGroupInShip, multiplyShieldCapacity, multiplyShieldRecharge)
        self.UpdateNavigationPanel()
        self.UpdateTargetingPanel()
        self.UpdateCapacitor(xtraCapacitor, multiplyRecharge, multiplyCapacitor, reload=1)
        self.UpdateOffenseStats()
        self.UpdateDroneStats()

    def MaxTargetRangeBonusMultiplier(self, typeID):
        typeeffects = cfg.dgmtypeeffects.get(typeID, [])
        for effect in typeeffects:
            if effect.effectID in (dogmaConst.effectShipMaxTargetRangeBonusOnline, dogmaConst.effectmaxTargetRangeBonus):
                return 1

    def ArmorOrShieldMultiplier(self, typeID):
        typeeffects = cfg.dgmtypeeffects.get(typeID, [])
        for effect in typeeffects:
            if effect.effectID == dogmaConst.effectShieldResonanceMultiplyOnline:
                return 1

    def ArmorShieldStructureMultiplierPostPercent(self, typeID):
        typeeffects = cfg.dgmtypeeffects.get(typeID, [])
        ret = []
        for effect in typeeffects:
            if effect.effectID == dogmaConst.effectModifyArmorResonancePostPercent:
                ret.append('armor')
            elif effect.effectID == dogmaConst.effectModifyShieldResonancePostPercent:
                ret.append('shield')
            elif effect.effectID == dogmaConst.effectModifyHullResonancePostPercent:
                ret.append('structure')

        return ret

    def OnNewItemID(self):
        self.UpdateShipName()
        for eachPanel in [self.capacitorStatsParent,
         self.offenseStatsParent,
         self.defenceStatsParent,
         self.targetingStatsParent,
         self.navigationStatsParent,
         self.droneStatsParent]:
            eachPanel.SetDogmaLocation()

        self.UpdateStats()
