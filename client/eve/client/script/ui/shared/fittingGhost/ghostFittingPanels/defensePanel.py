#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostFittingPanels\defensePanel.py
from collections import defaultdict
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.util.various_unsorted import IsUnder, GetAttrs
from eve.client.script.ui.control.damageGaugeContainers import DamageGaugeContainerFitting
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label
from eve.client.script.ui.control.eveWindowUnderlay import WindowUnderlay
from eve.client.script.ui.shared.fitting.fittingUtil import PASSIVESHIELDRECHARGE, GetMultiplyColor2, ARMORREPAIRRATEACTIVE, HULLREPAIRRATEACTIVE, SHIELDBOOSTRATEACTIVE, FONTCOLOR_DEFAULT2, FONTCOLOR_HILITE2, GetDefensiveLayersInfo, GetShipAttributeWithDogmaLocation
from eve.client.script.ui.shared.fittingGhost.fittingUtilGhost import GetColoredText
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from eve.client.script.ui.shared.fitting.panels.basePanel import BaseMenuPanel
from dogma import const as dogmaConst
from localization import GetByLabel, GetByMessageID
MAXDEFENCELABELWIDTH = 62
MAXDEFENCELABELHEIGHT = 32
BAR_COLORS = [(0.1, 0.37, 0.55, 1.0),
 (0.55, 0.1, 0.1, 1.0),
 (0.45, 0.45, 0.45, 1.0),
 (0.55, 0.37, 0.1, 1.0)]
resAttributeIDs = ((dogmaConst.attributeEmDamageResonance, 'ResistanceHeaderEM'),
 (dogmaConst.attributeThermalDamageResonance, 'ResistanceHeaderThermal'),
 (dogmaConst.attributeKineticDamageResonance, 'ResistanceHeaderKinetic'),
 (dogmaConst.attributeExplosiveDamageResonance, 'ResistanceHeaderExplosive'))
rowsInfo = [('UI/Common/Shield', 'shield', 'ui_1_64_13', 'UI/Fitting/FittingWindow/ShieldHPAndRecharge'), ('UI/Common/Armor', 'armor', 'ui_1_64_9', 'UI/Common/Armor'), ('UI/Fitting/Structure', 'structure', 'ui_2_64_12', 'UI/Fitting/Structure')]

class DefensePanel(BaseMenuPanel):
    col1Width = 90

    def ApplyAttributes(self, attributes):
        BaseMenuPanel.ApplyAttributes(self, attributes)

    def LoadPanel(self, initialLoad = False):
        self.Flush()
        self.ResetStatsDicts()
        self.display = True
        tRow = Container(name='topRow', parent=self, align=uiconst.TOTOP, height=32, padTop=5)
        self.AddBestRepairPicker(tRow)
        self.AddColumnHeaderIcons(tRow)
        for idx in xrange(len(rowsInfo)):
            self.AddRow(idx)

        BaseMenuPanel.FinalizePanelLoading(self, initialLoad)

    def AddBestRepairPicker(self, tRow):
        self.bestRepairPickerPanel = None
        bestPar = Container(name='bestPar', parent=tRow, align=uiconst.TOPLEFT, height=32, width=self.col1Width, state=uiconst.UI_NORMAL)
        bestPar.OnClick = self.ExpandBestRepair
        SetFittingTooltipInfo(targetObject=bestPar, tooltipName='ActiveDefenses')
        expandIcon = Icon(name='expandIcon', icon='ui_38_16_229', parent=bestPar, state=uiconst.UI_DISABLED, align=uiconst.BOTTOMRIGHT)
        numPar = Container(name='numPar', parent=bestPar, pos=(4, 17, 11, 11), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        numLabel = EveLabelMedium(text='', parent=numPar, atop=-1, state=uiconst.UI_DISABLED, align=uiconst.CENTER, shadowOffset=(0, 0))
        Fill(parent=numPar, color=BAR_COLORS[1])
        self.activeBestRepairNumLabel = numLabel
        icon = Icon(parent=bestPar, state=uiconst.UI_DISABLED, width=32, height=32)
        statusLabel = Label(name='statusLabel', text='', parent=bestPar, left=icon.left + icon.width, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        self.activeBestRepairLabel = statusLabel
        self.activeBestRepairParent = bestPar
        self.activeBestRepairIcon = icon

    def AddColumnHeaderIcons(self, tRow):
        l, t, w, h = self.GetAbsolute()
        step = (w - self.col1Width) / 4
        left = self.col1Width
        for attributeID, tooltipName in resAttributeIDs:
            attribute = cfg.dgmattribs.Get(attributeID)
            icon = Icon(graphicID=attribute.iconID, parent=tRow, pos=(left + (step - 32) / 2 + 4,
             0,
             0,
             0), idx=0, hint=attribute.displayName)
            SetFittingTooltipInfo(icon, tooltipName=tooltipName, includeDesc=True)
            left += step

    def AddRow(self, idx):
        labelPath, what, iconNo, labelHintPath = rowsInfo[idx]
        rowName = 'row_%s' % what
        row = Container(name='row_%s' % rowName, parent=self, align=uiconst.TOTOP, height=32)
        mainIcon = Icon(icon=iconNo, parent=row, pos=(0, 0, 32, 32), ignoreSize=True)
        mainIcon.hint = GetByLabel(labelPath)
        statusLabel = Label(text='', parent=row, left=mainIcon.left + mainIcon.width, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT, width=62)
        statusLabel.hint = GetByLabel(labelHintPath)
        self.statsLabelsByIdentifier[what] = statusLabel
        dmgContainer = Container(parent=row, name='dmgContainer', left=self.col1Width)
        gaugeCont = DamageGaugeContainerFitting(parent=dmgContainer)
        self.statsContsByIdentifier[what] = gaugeCont

    def SetEffectiveHpHeader(self):
        effectiveHpInfo = self.controller.GetEffectiveHp()
        text = GetByLabel('UI/Fitting/FittingWindow/ColoredEffectiveHp', color='', effectiveHp=effectiveHpInfo.value)
        coloredText = GetColoredText(isBetter=effectiveHpInfo.isBetterThanBefore, text=text)
        self.SetStatusText(coloredText)

    def UpdateDefensePanel(self):
        self.SetEffectiveHpHeader()
        allDefensiveLayersInfo = GetDefensiveLayersInfo(self.controller)
        for whatLayer, layerInfo in allDefensiveLayersInfo.iteritems():
            hpInfo = layerInfo.hpInfo
            isRechargable = layerInfo.isRechargable
            layerResistancesInfo = layerInfo.resistances
            if not hpInfo:
                continue
            self.SetDefenseLayerText(hpInfo, whatLayer, isRechargable)
            self.UpdateGaugesForLayer(layerResistancesInfo, whatLayer)

    def UpdateGaugesForLayer(self, layerResistancesInfo, whatLayer):
        dmgGaugeCont = self.statsContsByIdentifier.get(whatLayer, None)
        for dmgType, valueInfo in layerResistancesInfo.iteritems():
            value = valueInfo.value
            if self.state != uiconst.UI_HIDDEN and dmgGaugeCont:
                text = GetByLabel('UI/Fitting/FittingWindow/ColoredResistanceLabel', number=100 - int(value * 100))
                coloredText = GetColoredText(isBetter=valueInfo.isBetterThanBefore, text=text)
                attributeInfo = cfg.dgmattribs.Get(valueInfo.attributeID)
                tooltipTitleID = attributeInfo.tooltipTitleID
                if tooltipTitleID:
                    tooltipText = GetByMessageID(attributeInfo.tooltipTitleID)
                else:
                    tooltipText = attributeInfo.displayName
                info = {'value': 1.0 - value,
                 'valueText': coloredText,
                 'text': tooltipText,
                 'dmgType': dmgType}
                dmgGaugeCont.UpdateGauge(info, animate=True)

    def SetDefenseLayerText(self, statusInfo, what, isRechargable):
        label = self.statsLabelsByIdentifier.get(what, None)
        if not label:
            return
        if isRechargable:
            rechargeTimeInfo = self.controller.GetRechargeRate()
            text = GetByLabel('UI/Fitting/FittingWindow/ColoredHitpointsAndRechargeTime', hp=int(statusInfo.value), rechargeTime=int(rechargeTimeInfo.value * 0.001), startColorTag1='', startColorTag2='', endColorTag='')
        else:
            text = GetByLabel('UI/Fitting/FittingWindow/ColoredHp', hp=int(statusInfo.value))
        coloredText = GetColoredText(isBetter=statusInfo.isBetterThanBefore, text=text)
        maxTextHeight = MAXDEFENCELABELHEIGHT
        maxTextWidth = MAXDEFENCELABELWIDTH
        textWidth, textHeight = label.MeasureTextSize(coloredText)
        fontsize = label.default_fontsize
        while textWidth > maxTextWidth or textHeight > maxTextHeight:
            fontsize -= 1
            textWidth, textHeight = label.MeasureTextSize(coloredText, fontsize=fontsize)

        label.fontsize = fontsize
        label.text = coloredText

    def ExpandBestRepair(self, *args):
        if self.bestRepairPickerPanel is not None:
            self.PickBestRepair(None)
            return
        self.sr.bestRepairPickerCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp_BestRepair)
        bestRepairParent = self.activeBestRepairParent
        l, t, w, h = bestRepairParent.GetAbsolute()
        bestRepairPickerPanel = Container(parent=uicore.desktop, name='bestRepairPickerPanel', align=uiconst.TOPLEFT, width=150, height=100, left=l, top=t + h, state=uiconst.UI_NORMAL, idx=0, clipChildren=1)
        subpar = Container(parent=bestRepairPickerPanel, name='subpar', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, pos=(0, 0, 0, 0))
        active = settings.user.ui.Get('activeBestRepair', PASSIVESHIELDRECHARGE)
        top = 0
        mw = 32
        for flag, hint, iconNo in ((ARMORREPAIRRATEACTIVE, GetByLabel('UI/Fitting/FittingWindow/ArmorRepairRate'), 'ui_1_64_11'),
         (HULLREPAIRRATEACTIVE, GetByLabel('UI/Fitting/FittingWindow/HullRepairRate'), 'ui_1337_64_22'),
         (PASSIVESHIELDRECHARGE, GetByLabel('UI/Fitting/FittingWindow/PassiveShieldRecharge'), 'ui_22_32_7'),
         (SHIELDBOOSTRATEACTIVE, GetByLabel('UI/Fitting/FittingWindow/ShieldBoostRate'), 'ui_2_64_3')):
            entry = Container(name='entry', parent=subpar, align=uiconst.TOTOP, height=32, state=uiconst.UI_NORMAL)
            icon = Icon(icon=iconNo, parent=entry, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), ignoreSize=True)
            label = Label(text=hint, parent=entry, left=icon.left + icon.width, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
            entry.OnClick = (self.PickBestRepair, entry)
            entry.OnMouseEnter = (self.OnMouseEnterBestRepair, entry)
            entry.bestRepairFlag = flag
            entry.sr.hilite = Fill(parent=entry, state=uiconst.UI_HIDDEN)
            if active == flag:
                Fill(parent=entry, color=(1.0, 1.0, 1.0, 0.125))
            top += 32
            mw = max(label.textwidth + label.left + 6, mw)

        bestRepairPickerPanel.width = mw
        bestRepairPickerPanel.height = 32
        bestRepairPickerPanel.opacity = 0.0
        WindowUnderlay(bgParent=bestRepairPickerPanel)
        self.bestRepairPickerPanel = bestRepairPickerPanel
        uicore.effect.MorphUI(bestRepairPickerPanel, 'height', top, 250.0)
        uicore.effect.MorphUI(bestRepairPickerPanel, 'opacity', 1.0, 250.0, float=1)

    def UpdateBestRepair(self, item, modulesByGroupInShip, multiplyShieldCapacity, multiplyShieldRecharge):
        if not self.panelLoaded:
            return
        activeRepairLabel = self.activeBestRepairLabel
        activeBestRepairParent = self.activeBestRepairParent
        activeBestRepairNumLabel = self.activeBestRepairNumLabel
        activeBestRepairIcon = self.activeBestRepairIcon
        if activeRepairLabel:
            activeBestRepair = settings.user.ui.Get('activeBestRepair', PASSIVESHIELDRECHARGE)
            if activeBestRepair == PASSIVESHIELDRECHARGE:
                shieldCapacity = self.GetShipAttribute(dogmaConst.attributeShieldCapacity)
                shieldRR = self.GetShipAttribute(dogmaConst.attributeShieldRechargeRate)
                activeRepairText = '<color=%s>' % hex(GetMultiplyColor2(multiplyShieldRecharge))
                activeRepairText += GetByLabel('UI/Fitting/FittingWindow/ColoredPassiveRepairRate', hpPerSec=int(2.5 * (shieldCapacity * multiplyShieldCapacity) / (shieldRR * multiplyShieldRecharge / 1000.0)))
                activeRepairText += '</color>'
                activeRepairLabel.text = activeRepairText
                activeBestRepairParent.hint = GetByLabel('UI/Fitting/FittingWindow/PassiveShieldRecharge')
                activeBestRepairNumLabel.parent.state = uiconst.UI_HIDDEN
                activeBestRepairIcon.LoadIcon(cfg.dgmattribs.Get(dogmaConst.attributeShieldCapacity).iconID, ignoreSize=True)
            else:
                dataSet = {ARMORREPAIRRATEACTIVE: (GetByLabel('UI/Fitting/FittingWindow/ArmorRepairRate'),
                                         (const.groupArmorRepairUnit, const.groupFueledArmorRepairer),
                                         dogmaConst.attributeArmorDamageAmount,
                                         'ui_1_64_11'),
                 HULLREPAIRRATEACTIVE: (GetByLabel('UI/Fitting/FittingWindow/HullRepairRate'),
                                        (const.groupHullRepairUnit,),
                                        dogmaConst.attributeStructureDamageAmount,
                                        'ui_1337_64_22'),
                 SHIELDBOOSTRATEACTIVE: (GetByLabel('UI/Fitting/FittingWindow/ShieldBoostRate'),
                                         (const.groupShieldBooster, const.groupFueledShieldBooster),
                                         dogmaConst.attributeShieldBonus,
                                         'ui_2_64_3')}
                hint, groupIDs, attributeID, iconNum = dataSet[activeBestRepair]
                activeBestRepairParent.hint = hint
                modules = []
                for groupID, modules2 in modulesByGroupInShip.iteritems():
                    if groupID in groupIDs:
                        modules.extend(modules2)

                color = FONTCOLOR_DEFAULT2
                if item and item.groupID in groupIDs:
                    modules += [item]
                    color = FONTCOLOR_HILITE2
                if modules:
                    data = self.CollectDogmaAttributes(modules, (dogmaConst.attributeHp,
                     dogmaConst.attributeShieldBonus,
                     dogmaConst.attributeArmorDamageAmount,
                     dogmaConst.attributeStructureDamageAmount,
                     dogmaConst.attributeDuration))
                    durations = data.get(dogmaConst.attributeDuration, None)
                    hps = data.get(attributeID, None)
                    if durations and hps:
                        commonCycleTime = None
                        for _ct in durations:
                            if commonCycleTime and _ct != commonCycleTime:
                                commonCycleTime = None
                                break
                            commonCycleTime = _ct

                        if commonCycleTime:
                            duration = commonCycleTime
                            activeRepairLabel.text = GetByLabel('UI/Fitting/FittingWindow/ColoredHitpointsAndDuration', startColorTag='<color=%s>' % hex(color), endColorTag='</color>', hp=sum(hps), duration=duration / 1000.0)
                        else:
                            total = 0
                            for hp, ct in zip(hps, durations):
                                total += hp / (ct / 1000.0)

                            activeRepairText = '<color=%s>' % color
                            activeRepairText += GetByLabel('UI/Fitting/FittingWindow/ColoredPassiveRepairRate', hpPerSec=total)
                            activeRepairText += '</color>'
                            activeRepairLabel.text = activeRepairText
                    else:
                        activeRepairLabel.text = 0
                    activeBestRepairNumText = '<color=%s>' % color
                    activeBestRepairNumText += GetByLabel('UI/Fitting/FittingWindow/ColoredBestRepairNumber', numberOfModules=len(modules))
                    activeBestRepairNumText += '</color>'
                    activeBestRepairNumLabel.bold = True
                    activeBestRepairNumLabel.text = activeBestRepairNumText
                    activeBestRepairNumLabel.parent.state = uiconst.UI_DISABLED
                else:
                    activeRepairLabel.text = GetByLabel('UI/Fitting/FittingWindow/NoModule')
                    activeBestRepairNumLabel.text = GetByLabel('UI/Fitting/FittingWindow/NoModuleNumber')
                    activeBestRepairNumLabel.parent.state = uiconst.UI_DISABLED
                activeBestRepairIcon.LoadIcon(iconNum, ignoreSize=True)

    def CollectDogmaAttributes(self, modules, attributes):
        ret = defaultdict(list)
        for module in modules:
            dogmaItem = self.dogmaLocation.dogmaItems.get(module.itemID, None)
            include = self.IncludeModuleInCalculation(dogmaItem)
            if not include:
                continue
            if dogmaItem and dogmaItem.locationID == self.controller.GetItemID():
                for attributeID in attributes:
                    ret[attributeID].append(self.dogmaLocation.GetAccurateAttributeValue(dogmaItem.itemID, attributeID))

            else:
                for attributeID in attributes:
                    ret[attributeID].append(self.dogmaLocation.dogmaStaticMgr.GetTypeAttribute2(module.typeID, attributeID))

        return ret

    def IncludeModuleInCalculation(self, module):
        if not sm.GetService('fittingSvc').IsShipSimulated():
            return True
        defaultEffect, overloadEffect = sm.GetService('ghostFittingSvc').GetDefaultAndOverheatEffect(module.typeID)
        if not defaultEffect:
            return True
        if not module.IsActive():
            return False
        return True

    def GetShipAttribute(self, attributeID):
        dogmaLocation = self.controller.GetDogmaLocation()
        return GetShipAttributeWithDogmaLocation(dogmaLocation, self.controller.GetItemID(), attributeID)

    def OnGlobalMouseUp_BestRepair(self, fromwhere, *etc):
        if self.bestRepairPickerPanel:
            if uicore.uilib.mouseOver == self.bestRepairPickerPanel or IsUnder(fromwhere, self.bestRepairPickerPanel) or fromwhere == self.activeBestRepairParent:
                import log
                log.LogInfo('Combo.OnGlobalClick Ignoring all clicks from comboDropDown')
                return 1
        if self.bestRepairPickerPanel and not self.bestRepairPickerPanel.destroyed:
            self.bestRepairPickerPanel.Close()
        self.bestRepairPickerPanel = None
        if self.sr.bestRepairPickerCookie:
            uicore.event.UnregisterForTriuiEvents(self.sr.bestRepairPickerCookie)
        self.sr.bestRepairPickerCookie = None
        return 0

    def PickBestRepair(self, entry):
        if entry:
            settings.user.ui.Set('activeBestRepair', entry.bestRepairFlag)
            sm.ScatterEvent('OnFittingUpdateStatsNeeded')
        if self.bestRepairPickerPanel and not self.bestRepairPickerPanel.destroyed:
            self.bestRepairPickerPanel.Close()
        self.bestRepairPickerPanel = None
        if self.sr.bestRepairPickerCookie:
            uicore.event.UnregisterForTriuiEvents(self.sr.bestRepairPickerCookie)
        self.sr.bestRepairPickerCookie = None

    def OnMouseEnterBestRepair(self, entry):
        for each in entry.parent.children:
            if GetAttrs(each, 'sr', 'hilite'):
                each.sr.hilite.state = uiconst.UI_HIDDEN

        entry.sr.hilite.state = uiconst.UI_DISABLED
