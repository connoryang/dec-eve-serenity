#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\upgradeEntry.py
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.switch import Switch
import evetypes
import uicontrols
import inventorycommon.const as invconst
import localization
import uiprimitives
import uix
import carbonui.const as uiconst
STATUS_COLOR_BY_FLAGID = {invconst.flagStructureActive: (0.0, 0.8, 0.0),
 invconst.flagStructureInactive: (0.8, 0.0, 0.0),
 invconst.flagStructureOffline: (0.7, 0.5, 0.0)}
STATUS_DESCRIPTION_BY_FLAGID = {invconst.flagStructureActive: 'UI/InfrastructureHub/Online',
 invconst.flagStructureInactive: 'UI/InfrastructureHub/InactiveDueToMissingRequirements',
 invconst.flagStructureOffline: 'UI/InfrastructureHub/Offline'}

class BaseUpgradeEntry(uicontrols.SE_BaseClassCore):
    __guid__ = 'listentry.BaseUpgradeEntry'
    __nonpersistvars__ = ['selection', 'id']

    def Startup(self, *args):
        self.sr.main = uiprimitives.Container(name='main', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.main.OnDropData = self.OnDropData
        self.sr.icons = uiprimitives.Container(name='icons', parent=self.sr.main, align=uiconst.TOLEFT, pos=(0, 0, 40, 0), padding=(1, 0, 2, 0))
        self.sr.textstuff = uiprimitives.Container(name='textstuff', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.infoIcons = uiprimitives.Container(name='textstuff', parent=self.sr.main, align=uiconst.TORIGHT, pos=(0, 0, 20, 0), padding=(0, 0, 0, 0))
        self.sr.status = uiprimitives.Container(name='status', parent=self.sr.icons, align=uiconst.TOLEFT, pos=(0, 0, 18, 0), padding=(0, 0, 0, 0))
        self.sr.icon = uiprimitives.Container(name='icon', parent=self.sr.icons, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.name = uiprimitives.Container(name='name', parent=self.sr.textstuff, align=uiconst.TOTOP, pos=(0, 0, 0, 16), padding=(0, 0, 0, 0))
        self.sr.level = uiprimitives.Container(name='level', parent=self.sr.textstuff, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.nameLabel = uicontrols.EveLabelMedium(text='', parent=self.sr.name, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, maxLines=1)
        self.sr.levelLabel = uicontrols.EveLabelMedium(text='', parent=self.sr.level, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, maxLines=1)
        self.sr.infoicon = InfoIcon(parent=self.sr.infoIcons, idx=0, align=uiconst.CENTERRIGHT, name='infoicon')
        self.sr.infoicon.OnClick = self.ShowInfo

    def Load(self, data):
        uix.Flush(self.sr.icon)
        uix.Flush(self.sr.status)
        self.typeID = data.typeInfo.typeID
        self.typeInfo = data.typeInfo
        self.groupID = data.groupID
        self.item = data.typeInfo.item
        self.hubID = data.hubID
        if self.item is None:
            self.itemID = None
            self.flagID = None
        else:
            self.itemID = self.item.itemID
            self.flagID = self.item.flagID
        if data.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        sovSvc = sm.GetService('sov')
        self.sr.nameLabel.text = '%s' % self.typeInfo.typeName
        info = sovSvc.GetUpgradeLevel(self.typeID)
        if info is None:
            levelText = ''
        else:
            levelText = localization.GetByLabel('UI/InfrastructureHub/LevelX', level=sovSvc.GetUpgradeLevel(self.typeID).level)
        self.sr.levelLabel.text = levelText
        uicontrols.Icon(parent=self.sr.icon, align=uiconst.CENTER, pos=(0, 0, 24, 24), ignoreSize=True, typeID=self.typeID, size=24)
        if self.item is not None:
            statusIconPath = 'ui_38_16_193'
            hint = localization.GetByLabel('UI/InfrastructureHub/UpgradeAlreadyInstalled')
        elif self.typeInfo.canInstall:
            statusIconPath = 'ui_38_16_195'
            hint = localization.GetByLabel('UI/InfrastructureHub/UpgradeMeetsRequirements')
        else:
            statusIconPath = 'ui_38_16_194'
            hint = localization.GetByLabel('UI/InfrastructureHub/UpgradeRequirementsNotMet')
        statusIcon = uicontrols.Icon(icon=statusIconPath, parent=self.sr.status, align=uiconst.CENTER, pos=(0, 0, 16, 16))
        statusIcon.hint = hint
        if self._CanUpgradeBeManuallyToggled():
            self.MakeFlagSwitch()
        else:
            self.SetFlagIcon()
        hinttext = localization.GetByLabel('UI/InfrastructureHub/PrereqsShort', level=sovSvc.GetUpgradeLevel(self.typeID).level)
        preReqs = sovSvc.GetPrerequisite(self.typeID)
        if preReqs is not None:
            hinttext = localization.GetByLabel('UI/InfrastructureHub/PrereqsLong', level=sovSvc.GetUpgradeLevel(self.typeID).level, preReqs=preReqs)
        self.hint = hinttext

    def GetHeight(self, *args):
        node, width = args
        node.height = 32
        return node.height

    def ShowInfo(self, *args):
        sm.GetService('info').ShowInfo(self.typeID, self.itemID)

    def MakeFlagSwitch(self):
        if self.flagID is None:
            if self.sr.Get('flagSwitch', None):
                self.sr.flagSwitch.state = uiconst.UI_HIDDEN
        else:
            if not self.sr.Get('flagSwitch', None):
                if self.flagID == invconst.flagStructureActive:
                    isEnabled = True
                else:
                    isEnabled = False
                self.sr.flagSwitch = Switch(parent=self.sr.name, align=uiconst.TOPRIGHT, left=20, top=10, isEnabled=isEnabled)
                hintLabel = STATUS_DESCRIPTION_BY_FLAGID.get(self.flagID, None)
                if hintLabel:
                    self.sr.flagSwitch.hint = localization.GetByLabel(hintLabel)
                else:
                    self.sr.flagSwitch.hint = None
                self.sr.flagSwitch.OnClick = self.OnFlagToggle
            if self.flagID == invconst.flagStructureInactive:
                self.sr.flagSwitch.Disable()

    def OnFlagToggle(self, *args):
        sov = sm.GetService('sov')
        if self.flagID == invconst.flagStructureOffline:
            sov.SetInfrastructureHubUpgradeOnline(self.hubID, self.itemID, self.typeID)
        elif self.flagID == invconst.flagStructureActive:
            sov.SetInfrastructureHubUpgradeOffline(self.hubID, self.itemID, self.typeID)

    def SetFlagIcon(self):
        if self.flagID is None:
            if self.sr.Get('flagIcon', None):
                self.sr.flagIcon.state = uiconst.UI_HIDDEN
        else:
            if not self.sr.Get('flagIcon', None):
                self.sr.flagIcon = uiprimitives.Sprite(parent=self.sr.name, align=uiconst.TOPRIGHT, pos=(20, 10, 10, 10), texturePath='res:/UI/Texture/classes/Chat/Status.png')
            color = STATUS_COLOR_BY_FLAGID.get(self.flagID, (0.1, 0.1, 0.1))
            self.sr.flagIcon.SetRGB(*color)
            hintLabel = STATUS_DESCRIPTION_BY_FLAGID.get(self.flagID, None)
            if hintLabel:
                self.sr.flagIcon.hint = localization.GetByLabel(hintLabel)
            else:
                self.sr.flagIcon.hint = None
            self.sr.flagIcon.state = uiconst.UI_NORMAL

    def OnClick(self, *args):
        if self.sr.node:
            if self.sr.node.Get('selectable', 1):
                self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)
        sm.ScatterEvent('OnEntrySelected', self.typeID)

    def OnDropData(self, dragObj, nodes):
        if not nodes:
            return
        item = nodes[0]
        if getattr(item, '__guid__', None) not in ('xtriui.InvItem', 'listentry.InvItem') or evetypes.GetCategoryID(item.rec.typeID) != invconst.categoryInfrastructureUpgrade:
            eve.Message('SovInvalidHubUpgrade')
            return
        sm.GetService('sov').AddInfrastructureHubUpgrade(self.hubID, item.itemID, item.rec.typeID, item.rec.locationID)

    def GetMenu(self):
        m = sm.GetService('menu').GetMenuFormItemIDTypeID(self.itemID, self.typeID, ignoreMarketDetails=0)
        if self.itemID and self._CanUpgradeBeManuallyToggled():
            sov = sm.GetService('sov')
            if self.flagID == invconst.flagStructureOffline:
                m += ((localization.GetByLabel('UI/Fitting/PutOnline'), sov.SetInfrastructureHubUpgradeOnline, (self.hubID, self.itemID, self.typeID)),)
            elif self.flagID == invconst.flagStructureActive:
                m += ((localization.GetByLabel('UI/Fitting/PutOffline'), sov.SetInfrastructureHubUpgradeOffline, (self.hubID, self.itemID, self.typeID)),)
        return m

    def _CanUpgradeBeManuallyToggled(self):
        return self.groupID == invconst.groupStrategicUpgrades
