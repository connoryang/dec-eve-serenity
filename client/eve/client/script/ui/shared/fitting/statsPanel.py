#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\statsPanel.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
import dogma.const as dogmaConst
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.expandablemenu import ExpandableMenuContainer
from eve.client.script.ui.shared.fitting.fittingUtil import GetFittingDragData, FONTCOLOR_DEFAULT2
from eve.client.script.ui.shared.fitting.panels.capacitorPanel import CapacitorPanel
from eve.client.script.ui.shared.fitting.panels.defensePanel import DefensePanel
from eve.client.script.ui.shared.fitting.panels.navigationPanel import NavigationPanel
from eve.client.script.ui.shared.fitting.panels.offensePanel import OffensePanel
from eve.client.script.ui.shared.fitting.panels.targetingPanel import TargetingPanel
from eve.client.script.ui.shared.fitting.storedFittingsButtons import StoredFittingsButtons
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
import evetypes
import inventorycommon.const as invConst
from localization import GetByLabel
import uthread
NO_HILITE_GROUPS_DICT = {invConst.groupRemoteSensorBooster: [dogmaConst.attributeCpu, dogmaConst.attributePower],
 invConst.groupRemoteSensorDamper: [dogmaConst.attributeCpu, dogmaConst.attributePower]}

class StatsPanel(Container):

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
        name = cfg.evelocations.Get(itemID).name
        typeName = evetypes.GetName(typeID)
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
        self.infolink.UpdateInfoLink(typeID, itemID)

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
        menuData = [capInfo,
         offenseInfo,
         defenseInfo,
         targetingInfo,
         navigationInfo]
        return menuData

    def CreateExpandableMenus(self):
        em = ExpandableMenuContainer(parent=self, pos=(0, 0, 0, 0), clipChildren=True)
        em.multipleExpanded = True
        menuData = self.GetMenuData()
        em.Load(menuData=menuData, prefsKey='fittingRightside')

    def LoadNavigationStats(self, initialLoad = False):
        self.navigationStatsParent.LoadPanel(initialLoad=initialLoad)

    def LoadTargetingStats(self, initialLoad = False):
        self.targetingStatsParent.LoadPanel(initialLoad=initialLoad)

    def LoadOffenseStats(self, initialLoad = False):
        self.offenseStatsParent.LoadPanel(initialLoad)

    def UpdateOffenseStats(self):
        self.offenseStatsParent.UpdateOffenseStats()

    def LoadDefenceStats(self, initialLoad = False):
        self.defenceStatsParent.LoadPanel(initialLoad)

    def LoadCapacitorStats(self, initialLoad = False):
        self.capacitorStatsParent.LoadPanel(initialLoad)

    def ExpandBestRepair(self, *args):
        self.defenceStatsParent.ExpandBestRepair(*args)

    def UpdateBestRepair(self, item, modulesByGroupInShip, multiplyShieldCapacity, multiplyShieldRecharge):
        return self.defenceStatsParent.UpdateBestRepair(item, modulesByGroupInShip, multiplyShieldCapacity, multiplyShieldRecharge)

    def UpdateNavigationPanel(self, multiplySpeed, typeAttributesByID):
        self.navigationStatsParent.UpdateNavigationPanel(self.controller.GetItemID(), multiplySpeed, typeAttributesByID)

    def UpdateTargetingPanel(self, maxLockedTargetsAdd, multiplyMaxTargetRange, sensorStrengthAttrs, sensorStrengthBonus, sensorStrengthBonusAttrs, sensorStrengthPercent, sensorStrengthPercentAttrs, typeAttributesByID):
        self.targetingStatsParent.UpdateTargetingPanel(self.controller.GetItemID(), maxLockedTargetsAdd, multiplyMaxTargetRange, sensorStrengthAttrs, sensorStrengthBonus, sensorStrengthBonusAttrs, sensorStrengthPercent, sensorStrengthPercentAttrs, typeAttributesByID)

    def UpdateCapacitor(self, xtraCapacitor = 0.0, rechargeMultiply = 1.0, multiplyCapacitor = 1.0, reload = 0):
        self.capacitorStatsParent.UpdateCapacitorPanel(self.controller.GetItemID(), xtraCapacitor, rechargeMultiply, multiplyCapacitor, reload)

    def UpdateDefensePanel(self, dsp, effectiveHp, effectiveHpColor, multiplyArmor, multiplyResistance, multiplyShieldCapacity, multiplyShieldRecharge, multiplyStructure, xtraArmor, xtraShield, xtraStructure):
        return self.defenceStatsParent.UpdateDefensePanel(dsp, effectiveHp, effectiveHpColor, multiplyArmor, multiplyResistance, multiplyShieldCapacity, multiplyShieldRecharge, multiplyStructure, xtraArmor, xtraShield, xtraStructure)

    def UpdateStats(self):
        item = self.controller.GetGhostFittedItem()
        typeID = self.controller.GetGhostFittedTypeID()
        if session.stationid2:
            self.fittingSvcBtnGroup.stripBtn.Enable()
        else:
            self.fittingSvcBtnGroup.stripBtn.Disable()
        xtraArmor = 0.0
        multiplyArmor = 1.0
        multiplyRecharge = 1.0
        xtraCapacitor = 0.0
        multiplyCapacitor = 1.0
        multiplyShieldRecharge = 1.0
        multiplyShieldCapacity = 1.0
        xtraShield = 0.0
        multiplyStructure = 1.0
        xtraStructure = 0.0
        multiplySpeed = 1.0
        multiplyMaxTargetRange = 1.0
        maxLockedTargetsAdd = 0.0
        multiplyResonance = {}
        multiplyResistance = {}
        sensorStrengthAttrs = [dogmaConst.attributeScanRadarStrength,
         dogmaConst.attributeScanMagnetometricStrength,
         dogmaConst.attributeScanGravimetricStrength,
         dogmaConst.attributeScanLadarStrength]
        sensorStrengthPercent = {}
        sensorStrengthPercentAttrs = [dogmaConst.attributeScanRadarStrengthBonus,
         dogmaConst.attributeScanMagnetometricStrengthBonus,
         dogmaConst.attributeScanGravimetricStrengthBonus,
         dogmaConst.attributeScanLadarStrengthBonus]
        sensorStrengthBonus = {}
        sensorStrengthBonusAttrs = [dogmaConst.attributeScanRadarStrengthPercent,
         dogmaConst.attributeScanMagnetometricStrengthPercent,
         dogmaConst.attributeScanGravimetricStrengthPercent,
         dogmaConst.attributeScanLadarStrengthPercent]
        modulesByGroupInShip = self.controller.GetFittedModulesByGroupID()
        typeAttributesByID = {}
        if typeID:
            for attribute in cfg.dgmtypeattribs.get(typeID, []):
                typeAttributesByID[attribute.attributeID] = attribute.value

            dgmAttr = sm.GetService('godma').GetType(typeID)
            asm = self.ArmorOrShieldMultiplier(typeID)
            asp = self.ArmorShieldStructureMultiplierPostPercent(typeID)
            mtr = self.MaxTargetRangeBonusMultiplier(typeID)
            doHilite = dgmAttr.groupID not in NO_HILITE_GROUPS_DICT
            allowedAttr = dgmAttr.displayAttributes
            for attribute in allowedAttr:
                if not doHilite and attribute.attributeID not in NO_HILITE_GROUPS_DICT[dgmAttr.groupID]:
                    continue
                if attribute.attributeID in sensorStrengthBonusAttrs:
                    sensorStrengthBonus[attribute.attributeID] = attribute
                elif attribute.attributeID in sensorStrengthPercentAttrs:
                    sensorStrengthPercent[attribute.attributeID] = attribute
                elif attribute.attributeID == dogmaConst.attributeCapacityBonus:
                    xtraShield += attribute.value
                elif attribute.attributeID == dogmaConst.attributeArmorHPBonusAdd:
                    xtraArmor += attribute.value
                elif attribute.attributeID == dogmaConst.attributeStructureBonus:
                    xtraStructure += attribute.value
                elif attribute.attributeID == dogmaConst.attributeCapacitorBonus:
                    xtraCapacitor += attribute.value
                elif attribute.attributeID == dogmaConst.attributeCapacitorCapacityMultiplier:
                    multiplyCapacitor *= attribute.value
                elif attribute.attributeID == dogmaConst.attributeCapacitorCapacityBonus:
                    multiplyCapacitor = 1 + attribute.value / 100
                elif attribute.attributeID == dogmaConst.attributeArmorHpBonus:
                    multiplyArmor += attribute.value / 100
                elif attribute.attributeID == dogmaConst.attributeArmorHPMultiplier:
                    multiplyArmor = attribute.value
                elif attribute.attributeID == dogmaConst.attributeMaxVelocityBonus:
                    multiplySpeed = attribute.value
                elif asm is not None and attribute.attributeID == dogmaConst.attributeEmDamageResonanceMultiplier:
                    multiplyResonance['%s_EmDamageResonance' % ['a', 's'][asm]] = attribute.value
                elif asm is not None and attribute.attributeID == dogmaConst.attributeExplosiveDamageResonanceMultiplier:
                    multiplyResonance['%s_ExplosiveDamageResonance' % ['a', 's'][asm]] = attribute.value
                elif asm is not None and attribute.attributeID == dogmaConst.attributeKineticDamageResonanceMultiplier:
                    multiplyResonance['%s_KineticDamageResonance' % ['a', 's'][asm]] = attribute.value
                elif asm is not None and attribute.attributeID == dogmaConst.attributeThermalDamageResonanceMultiplier:
                    multiplyResonance['%s_ThermalDamageResonance' % ['a', 's'][asm]] = attribute.value
                elif asp and attribute.attributeID in (dogmaConst.attributeEmDamageResistanceBonus,
                 dogmaConst.attributeExplosiveDamageResistanceBonus,
                 dogmaConst.attributeKineticDamageResistanceBonus,
                 dogmaConst.attributeThermalDamageResistanceBonus):
                    groupName = {dogmaConst.attributeEmDamageResistanceBonus: 'EmDamageResistance',
                     dogmaConst.attributeExplosiveDamageResistanceBonus: 'ExplosiveDamageResistance',
                     dogmaConst.attributeKineticDamageResistanceBonus: 'KineticDamageResistance',
                     dogmaConst.attributeThermalDamageResistanceBonus: 'ThermalDamageResistance'}.get(attribute.attributeID, '')
                    if 'armor' in asp:
                        multiplyResistance['a_%s' % groupName] = attribute.value
                    if 'shield' in asp:
                        multiplyResistance['s_%s' % groupName] = attribute.value
                    if 'structure' in asp:
                        multiplyResistance['h_%s' % groupName] = attribute.value
                elif attribute.attributeID == dogmaConst.attributeCapacitorRechargeRateMultiplier:
                    multiplyRecharge = multiplyRecharge * attribute.value
                elif attribute.attributeID == dogmaConst.attributeCapRechargeBonus:
                    multiplyRecharge = 1 + attribute.value / 100
                elif attribute.attributeID == dogmaConst.attributeShieldRechargeRateMultiplier:
                    multiplyShieldRecharge = attribute.value
                elif attribute.attributeID == dogmaConst.attributeShieldCapacityMultiplier:
                    multiplyShieldCapacity *= attribute.value
                elif attribute.attributeID == dogmaConst.attributeStructureHPMultiplier:
                    multiplyStructure = attribute.value
                elif attribute.attributeID == dogmaConst.attributeCargoCapacityMultiplier:
                    multiplyCargoCapacity = attribute.value
                elif attribute.attributeID == dogmaConst.attributeMaxTargetRangeMultiplier:
                    multiplyMaxTargetRange = attribute.value
                elif attribute.attributeID == dogmaConst.attributeMaxLockedTargetsBonus:
                    maxLockedTargetsAdd += attribute.value
                elif mtr is not None and attribute.attributeID == dogmaConst.attributeMaxTargetRangeBonus:
                    multiplyMaxTargetRange = abs(1.0 + attribute.value / 100.0)

        effectiveHp = 0.0
        effectiveHpColor = FONTCOLOR_DEFAULT2
        dsp = getattr(self, 'defenceStatsParent', None)
        if not dsp or dsp.destroyed:
            return
        effectiveHp, effectiveHpColor = self.UpdateDefensePanel(dsp, effectiveHp, effectiveHpColor, multiplyArmor, multiplyResistance, multiplyShieldCapacity, multiplyShieldRecharge, multiplyStructure, xtraArmor, xtraShield, xtraStructure)
        coloredEffeciveHpLabel = '<color=%s>' % hex(effectiveHpColor)
        coloredEffeciveHpLabel += GetByLabel('UI/Fitting/FittingWindow/ColoredEffectiveHp', color=hex(effectiveHpColor), effectiveHp=int(effectiveHp))
        coloredEffeciveHpLabel += '</color>'
        self.defenceStatsParent.statusText.text = coloredEffeciveHpLabel
        self.UpdateBestRepair(item, modulesByGroupInShip, multiplyShieldCapacity, multiplyShieldRecharge)
        self.UpdateNavigationPanel(multiplySpeed, typeAttributesByID)
        self.UpdateTargetingPanel(maxLockedTargetsAdd, multiplyMaxTargetRange, sensorStrengthAttrs, sensorStrengthBonus, sensorStrengthBonusAttrs, sensorStrengthPercent, sensorStrengthPercentAttrs, typeAttributesByID)
        self.UpdateCapacitor(xtraCapacitor, multiplyRecharge, multiplyCapacitor, reload=1)
        self.UpdateOffenseStats()

    def MaxTargetRangeBonusMultiplier(self, typeID):
        typeeffects = cfg.dgmtypeeffects.get(typeID, [])
        for effect in typeeffects:
            if effect.effectID in (dogmaConst.effectShipMaxTargetRangeBonusOnline, dogmaConst.effectMaxTargetRangeBonus):
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
        self.UpdateStats()
