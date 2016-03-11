#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\panels\defensePanel.py
from collections import defaultdict
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.util.various_unsorted import IsUnder, GetAttrs
from eve.client.script.ui.control.damageGaugeContainers import DamageGaugeContainerFitting
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label
from eve.client.script.ui.control.eveWindowUnderlay import WindowUnderlay
from eve.client.script.ui.shared.fitting.fittingUtil import PASSIVESHIELDRECHARGE, GetShipAttribute, GetMultiplyColor2, ARMORREPAIRRATEACTIVE, HULLREPAIRRATEACTIVE, SHIELDBOOSTRATEACTIVE, FONTCOLOR_DEFAULT2, FONTCOLOR_HILITE2, GetColor2, GetColor
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

    def UpdateDefensePanel(self, dsp, effectiveHp, effectiveHpColor, multiplyArmor, multiplyResistance, multiplyShieldCapacity, multiplyShieldRecharge, multiplyStructure, xtraArmor, xtraShield, xtraStructure):
        resMap = {'structure': 'h',
         'armor': 'a',
         'shield': 's'}
        for what, attributeID, rechargeAttributeID, hpAddition, hpMultiplier in (('structure',
          dogmaConst.attributeHp,
          None,
          xtraStructure,
          multiplyStructure), ('armor',
          dogmaConst.attributeArmorHP,
          None,
          xtraArmor,
          multiplyArmor), ('shield',
          dogmaConst.attributeShieldCapacity,
          1,
          xtraShield,
          multiplyShieldCapacity)):
            status = self.GetShipAttribute(attributeID)
            if not status:
                continue
            status = (status + hpAddition) * hpMultiplier
            dmgGaugeCont = self.statsContsByIdentifier.get(what, None)
            self.SetDefenseLayerText(hpAddition, hpMultiplier, multiplyShieldRecharge, rechargeAttributeID, status, what)
            minResistance = 0.0
            for i, (dmgType, res) in enumerate([('em', 'EmDamageResonance'),
             ('explosive', 'ExplosiveDamageResonance'),
             ('kinetic', 'KineticDamageResonance'),
             ('thermal', 'ThermalDamageResonance')]):
                modmod = '%s_%s' % (resMap[what], res.replace('Resonance', 'Resistance'))
                multiplierMod = multiplyResistance.get(modmod, 0.0)
                attribute = '%s%s' % ([what, ''][what == 'structure'], res)
                attribute = attribute[0].lower() + attribute[1:]
                attributeInfo = self.dogmaLocation.dogmaStaticMgr.attributesByName[attribute]
                attributeID = attributeInfo.attributeID
                value = self.GetShipAttribute(attributeID)
                if multiplierMod != 0.0:
                    effectiveHpColor = FONTCOLOR_HILITE2
                if value is not None:
                    value = value + value * multiplierMod / 100
                    if dsp.state != uiconst.UI_HIDDEN:
                        if dmgGaugeCont:
                            gaugeText = '<color=%s>' % hex(GetColor2(multiplierMod))
                            gaugeText += GetByLabel('UI/Fitting/FittingWindow/ColoredResistanceLabel', number=100 - int(value * 100))
                            gaugeText += '</color>'
                            if attributeInfo.tooltipTitleID:
                                tooltipText = GetByMessageID(attributeInfo.tooltipTitleID)
                            else:
                                tooltipText = cfg.dgmattribs.Get(attributeID).displayName
                            info = {'value': 1.0 - value,
                             'valueText': gaugeText,
                             'text': tooltipText,
                             'dmgType': dmgType}
                            dmgGaugeCont.UpdateGauge(info, animate=True)
                    minResistance = max(minResistance, value)

            if minResistance:
                effectiveHp += status / minResistance
            if hpMultiplier != 1.0 or hpAddition != 0.0:
                effectiveHpColor = FONTCOLOR_HILITE2

        return (effectiveHp, effectiveHpColor)

    def SetDefenseLayerText(self, hpAddition, hpMultiplier, multiplyShieldRecharge, rechargeAttributeID, status, what):
        label = self.statsLabelsByIdentifier.get(what, None)
        if not label:
            return
        color = GetColor(hpAddition, hpMultiplier)
        if rechargeAttributeID is not None:
            newText = GetByLabel('UI/Fitting/FittingWindow/ColoredHitpointsAndRechargeTime', hp=int(status), rechargeTime=int(self.GetShipAttribute(dogmaConst.attributeShieldRechargeRate) * multiplyShieldRecharge * 0.001), startColorTag1='<color=%s>' % hex(GetColor2(hpAddition, hpMultiplier)), startColorTag2='<color=%s>' % hex(GetMultiplyColor2(multiplyShieldRecharge)), endColorTag='</color>')
            label.top = 2
        else:
            newText = color + GetByLabel('UI/Fitting/FittingWindow/ColoredHp', hp=int(status)) + '</color>'
        maxTextHeight = MAXDEFENCELABELHEIGHT
        maxTextWidth = MAXDEFENCELABELWIDTH
        textWidth, textHeight = label.MeasureTextSize(newText)
        fontsize = label.default_fontsize
        while textWidth > maxTextWidth or textHeight > maxTextHeight:
            fontsize -= 1
            textWidth, textHeight = label.MeasureTextSize(newText, fontsize=fontsize)

        label.fontsize = fontsize
        label.text = newText

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
            if dogmaItem and dogmaItem.locationID == self.controller.GetItemID():
                for attributeID in attributes:
                    ret[attributeID].append(self.dogmaLocation.GetAccurateAttributeValue(dogmaItem.itemID, attributeID))

            else:
                for attributeID in attributes:
                    ret[attributeID].append(self.dogmaLocation.dogmaStaticMgr.GetTypeAttribute2(module.typeID, attributeID))

        return ret

    def GetShipAttribute(self, attributeID):
        return GetShipAttribute(self.controller.GetItemID(), attributeID)

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
