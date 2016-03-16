#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\infrastructureHub.py
from appConst import IHUB_BILLING_DURATION_DAYS, IHUB_DAILY_UPKEEP_BASE_COST
from dogma.const import attributeDevIndexSovereignty, attributeDevIndexMilitary, attributeDevIndexIndustrial, attributeSovBillSystemCost
from eve.client.script.ui.control.eveLabel import EveLabelMedium
import evetypes
from inventorycommon.const import categoryInfrastructureUpgrade, flagStructureActive
from sovDashboard.devIndexHints import SetNormalBoxHint, SetStrategyHint
from sovDashboard.indexBars import IndexBars
import uicontrols
import localization
import uiprimitives
import uix
import uiutil
import uthread
import util
import carbonui.const as uiconst
from eve.client.script.ui.control import entries as listentry
import uicls
import log
import form
UPGRADE_ALL = 0
UPGRADE_LOCKED = 1
UPGRADE_UNLOCKED = 2
UPGRADE_INSTALLED = 3
FILLED_COLOR = (1.0, 1.0, 1.0, 0.5)
EMPTY_COLOR = (0.15, 0.15, 0.15, 0.5)
PARTIAL_COLOR = (0.5, 0.5, 0.5, 0.5)
LEVEL_SIZE = 20

def SetDeltaSprite(deltaSprite, indexInfo):
    if indexInfo.remainder > 0:
        if indexInfo.increasing:
            texturePath = 'res:/UI/Texture/Icons/73_16_211.png'
            textPath = 'UI/InfrastructureHub/ValueChangeUp'
        else:
            texturePath = 'res:/UI/Texture/Icons/73_16_212.png'
            textPath = 'UI/InfrastructureHub/ValueChangeDown'
        deltaSprite.texturePath = texturePath
        deltaSprite.hint = localization.GetByLabel(textPath)
        deltaSprite.display = True
    else:
        deltaSprite.display = False


class InfrastructureHubWnd(uicontrols.Window):
    __guid__ = 'form.InfrastructureHubWnd'
    __notifyevents__ = ['OnItemChange', 'OnEntrySelected', 'OnBallparkCall']
    default_width = 320
    default_height = 70
    default_windowID = 'infrastructhubman'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        hubID = attributes.hubID
        self.devIndices = sm.GetService('sov').GetDevelopmentIndicesForSystem(session.solarsystemid2)
        self.SetCaption(localization.GetByLabel('UI/InfrastructureHub/InfrastructureHubManagement'))
        self.SetMinSize([440, 320])
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.id = self.hubID = hubID
        self.upgradeListMode = UPGRADE_ALL
        self.billingCost = 0
        self.CreateUpgradeCache()
        self.ConstructLayout()

    def GetDevIndices(self):
        if self.devIndices is None:
            self.devIndices = sm.GetService('sov').GetDevelopmentIndicesForSystem(session.solarsystemid2)
        return self.devIndices

    def ConstructLayout(self):
        self.indexCont = uiprimitives.Container(parent=self.sr.main, name='indexCont', align=uiconst.TOTOP, top=15, height=36)
        costCont = uiprimitives.Container(parent=self.sr.main, name='costCont', align=uiconst.TOTOP, height=26)
        self.costLabel = EveLabelMedium(parent=costCont, text='', left=12, align=uiconst.BOTTOMLEFT)
        self.sr.upgradesTab = uiprimitives.Container(name='upgradesTab', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.upgrades = uiprimitives.Container(name='upgrades', parent=self.sr.upgradesTab, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.upgrades.state = uiconst.UI_NORMAL
        self.sr.infoContainer = uiprimitives.Container(name='infoContainer', parent=self.sr.upgrades, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 90), padding=(0, 5, 0, 0))
        self.sr.upgradesContainer = uiprimitives.Container(name='upgradesContainer', parent=self.sr.upgrades, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.DrawUpgrades()
        self.DrawIndexes()
        uthread.new(self.UpdateIndexes)
        self.DrawInfo()

    def DrawIndexes(self):
        self.industryCont = uiprimitives.Container(parent=self.indexCont, align=uiconst.CENTERRIGHT, pos=(10, 0, 101, 36))
        self.industryBars, self.industryDeltaSprite = self.AddIndexBarsAndIcon(parent=self.industryCont, texturePath='res:/UI/Texture/classes/Sov/industryIndex.png', hint=localization.GetByLabel('UI/Sovereignty/IndustryIndex'), extraHint=localization.GetByLabel('UI/Sovereignty/IndustryIndexExplanation'), tooltipFunc=SetNormalBoxHint)
        self.strategicCont = uiprimitives.Container(parent=self.indexCont, align=uiconst.CENTERLEFT, pos=(10, 0, 101, 36))
        self.strategicBars, _ = self.AddIndexBarsAndIcon(parent=self.strategicCont, texturePath='res:/UI/Texture/classes/Sov/strategicIndex.png', hint=localization.GetByLabel('UI/Sovereignty/StrategicIndex'), extraHint=localization.GetByLabel('UI/Sovereignty/StrategicIndexExplanation'), tooltipFunc=SetStrategyHint)
        self.militaryCont = uiprimitives.Container(parent=self.indexCont, align=uiconst.CENTER, pos=(0, 0, 101, 36))
        self.militaryBars, self.militaryDeltaSprite = self.AddIndexBarsAndIcon(parent=self.militaryCont, texturePath='res:/UI/Texture/classes/Sov/militaryIndex.png', hint=localization.GetByLabel('UI/Sovereignty/MilitaryIndex'), extraHint=localization.GetByLabel('UI/Sovereignty/MilitaryIndexExplanation'), tooltipFunc=SetNormalBoxHint)

    def UpdateIndexes(self, indexID = None):
        indexConstsAndBars = [(attributeDevIndexSovereignty, self.strategicBars, None), (attributeDevIndexMilitary, self.militaryBars, self.militaryDeltaSprite), (attributeDevIndexIndustrial, self.industryBars, self.industryDeltaSprite)]
        for indexID, bar, deltaSprite in indexConstsAndBars:
            devIndex = self.GetDevIndices().get(indexID, None)
            indexInfo = sm.GetService('sov').GetLevelInfoForIndex(indexID, devIndex=devIndex)
            bar.SetIndexStatus(indexInfo.level, partial=indexInfo.remainder)
            if deltaSprite:
                SetDeltaSprite(deltaSprite, indexInfo)

    def AddIndexBarsAndIcon(self, parent, texturePath, hint, extraHint, tooltipFunc):
        indexBars = IndexBars(parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, boxTooltipFunc=tooltipFunc, top=2)
        changeSprite = uiprimitives.Sprite(parent=parent, align=uiconst.TOPRIGHT, pos=(0, 0, 16, 16))
        indexSprite = uiprimitives.Sprite(name='indexSprite', parent=parent, pos=(-9, 20, 16, 16), align=uiconst.CENTERTOP, texturePath=texturePath, state=uiconst.UI_NORMAL)
        indexSprite.hint = '%s<br>%s' % (hint, extraHint)
        return (indexBars, changeSprite)

    def DrawUpgrades(self):
        comboBoxContainer = uiprimitives.Container(name='comboBoxContainer', parent=self.sr.upgradesContainer, align=uiconst.TOTOP, pos=(0, 0, 0, 20), padding=(10, 10, 10, 0))
        text = uiprimitives.Container(name='text', parent=self.sr.upgradesContainer, align=uiconst.TOTOP, pos=(0, 0, 0, 20), padding=(10, 4, 10, 0))
        uicontrols.EveLabelMedium(text=localization.GetByLabel('UI/InfrastructureHub/DropUpgrades'), parent=text, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED)
        updatesScrollContainer = uiprimitives.Container(name='updatesScrollContainer', parent=self.sr.upgradesContainer, align=uiconst.TOALL, padding=(10, 0, 10, 0))
        self.sr.scroll = uicontrols.Scroll(name='scroll', parent=updatesScrollContainer)
        comboValues = ((localization.GetByLabel('UI/InfrastructureHub/AllUpgrades'), UPGRADE_ALL),
         (localization.GetByLabel('UI/InfrastructureHub/InstalledUpgrades'), UPGRADE_INSTALLED),
         (localization.GetByLabel('UI/InfrastructureHub/UnlockedUpgrades'), UPGRADE_UNLOCKED),
         (localization.GetByLabel('UI/InfrastructureHub/LockedUpgrades'), UPGRADE_LOCKED))
        self.upgradeListMode = settings.user.ui.Get('InfrastructureHubUpgradeCombo', UPGRADE_ALL)
        combo = uicontrols.Combo(parent=comboBoxContainer, name='combo', select=self.upgradeListMode, align=uiconst.TOALL, callback=self.OnComboChange, options=comboValues, idx=0)
        self.UpdateUpgrades()

    def CreateUpgradeCache(self):
        upgradeGroups = {}
        sovSvc = sm.GetService('sov')
        itemData = sovSvc.GetInfrastructureHubItemData(self.hubID)
        self.billingCost = self.GetBillingCost(itemData)
        potentialGroupIDs = evetypes.GetGroupIDsByCategory(categoryInfrastructureUpgrade)
        groupIDsToAdd = set()
        for groupID in potentialGroupIDs:
            if evetypes.IsGroupPublishedByGroup(groupID):
                groupIDsToAdd.add(groupID)

        for eachGroupID in groupIDsToAdd:
            groupName = evetypes.GetGroupNameByGroup(eachGroupID)
            potentialTypeIDs = evetypes.GetTypeIDsByGroup(eachGroupID)
            typesForGroup = []
            for eachTypeID in potentialTypeIDs:
                if evetypes.IsPublished(eachTypeID):
                    typeInfo = self.GetTypeInfo(eachTypeID, itemData, sovSvc)
                    typesForGroup.append(typeInfo)

            upgradeGroups[eachGroupID] = util.KeyVal(groupID=eachGroupID, groupName=groupName, types=typesForGroup)

        self.upgradeGroups = upgradeGroups.values()
        self.upgradeGroups.sort(key=lambda g: g.groupName)
        for groupInfo in self.upgradeGroups:
            groupInfo.types.sort(key=lambda t: t.typeName)

    def GetTypeInfo(self, eachTypeID, itemData, sovSvc):
        typeInfo = util.KeyVal(typeID=eachTypeID, typeName=evetypes.GetName(eachTypeID))
        typeInfo.item = itemData.get(eachTypeID, None)
        if typeInfo.item is None:
            canInstall = sovSvc.CanInstallUpgrade(eachTypeID, self.hubID, devIndices=self.devIndices)
            if canInstall:
                typeState = UPGRADE_UNLOCKED
            else:
                typeState = UPGRADE_LOCKED
        else:
            typeState = UPGRADE_INSTALLED
            canInstall = None
        typeInfo.state = typeState
        typeInfo.canInstall = canInstall
        return typeInfo

    def GetTypesInStateForGroup(self, groupID, state):
        types = []
        groupInfo = None
        for g in self.upgradeGroups:
            if g.groupID == groupID:
                groupInfo = g
                break
        else:
            return types

        if state == UPGRADE_ALL:
            types = groupInfo.types
        else:
            for typeInfo in groupInfo.types:
                if typeInfo.state == state:
                    types.append(typeInfo)

        return types

    def UpdateUpgrades(self):
        scrolllist = []
        for group in self.upgradeGroups:
            types = self.GetTypesInStateForGroup(group.groupID, self.upgradeListMode)
            data = {'GetSubContent': self.GetSubContent,
             'label': group.groupName,
             'id': ('upgrades', group.groupID),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide',
             'showlen': 0,
             'groupID': group.groupID,
             'types': types,
             'BlockOpenWindow': 1}
            scrolllist.append(listentry.Get('Group', data))

        self.sr.scroll.Load(contentList=scrolllist)
        self.costLabel.text = localization.GetByLabel('UI/InfrastructureHub/WeeklyBillCost', billingCost=self.billingCost)

    def GetSubContent(self, groupData, *args):
        scrolllist = []
        for typeInfo in groupData.types:
            data = {}
            data['typeInfo'] = typeInfo
            data['hubID'] = self.hubID
            data['groupID'] = groupData.groupID
            scrolllist.append(listentry.Get('BaseUpgradeEntry', data))

        return scrolllist

    def DrawInfo(self):
        self.sr.info = uiprimitives.Container(name='info', parent=self.sr.infoContainer, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(10, 2, 10, 10))
        self.sr.icon = uiprimitives.Container(name='icon', parent=self.sr.info, align=uiconst.TOLEFT, pos=(0, 0, 64, 0), padding=(0, 0, 0, 0))
        self.sr.desc = uicls.EditPlainText(parent=self.sr.info, readonly=1)
        self.sr.desc.HideBackground()
        self.sr.desc.RemoveActiveFrame()

    def OnComboChange(self, combo, key, value, *args):
        self.upgradeListMode = value
        settings.user.ui.Set('InfrastructureHubUpgradeCombo', value)
        self.UpdateUpgrades()

    def OnItemChange(self, item, change):
        if self.hubID in (item.itemID, item.locationID):
            log.LogInfo('InfrastructureHub hub item changed')
            sm.GetService('invCache').InvalidateLocationCache(self.hubID)
            self.CreateUpgradeCache()
            self.UpdateUpgrades()

    def OnEntrySelected(self, typeID):
        uix.Flush(self.sr.icon)
        typeIcon = uicontrols.Icon(parent=self.sr.icon, align=uiconst.TOPLEFT, pos=(0, 10, 64, 64), ignoreSize=True, typeID=typeID, size=64)
        text = evetypes.GetDescription(typeID)
        info = localization.GetByLabel('UI/InfrastructureHub/EntryDescription', item=typeID, description=text)
        self.sr.desc.SetValue(info)

    def OnBallparkCall(self, functionName, args):
        if functionName == 'WarpTo':
            self.Close()

    def GetBillingCost(self, itemData):
        godma = sm.GetService('godma')
        dailyCost = IHUB_DAILY_UPKEEP_BASE_COST
        for item in itemData.itervalues():
            if item.flagID == flagStructureActive:
                dailyCost += godma.GetTypeAttribute(item.typeID, attributeSovBillSystemCost, 0)

        return dailyCost * IHUB_BILLING_DURATION_DAYS
