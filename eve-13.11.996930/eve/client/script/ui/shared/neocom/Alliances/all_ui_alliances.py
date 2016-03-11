#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\Alliances\all_ui_alliances.py
from eve.client.script.ui.shared.neocom.Alliances.all_ui_sovereignty import FormAlliancesSovereignty
from eve.client.script.ui.shared.neocom.Alliances.all_ui_systems import FormAlliancesSystems
import form
import carbonui.const as uiconst
import uiprimitives
import uicontrols
import uiutil
import log
from inventorycommon.util import IsNPC
import localization

class FormAlliances(uiprimitives.Container):
    __guid__ = 'form.Alliances'
    __nonpersistvars__ = []
    __notifyevents__ = ['OnSetAllianceStanding', 'OnUpdateCapitalInfo']

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.sr.currentView = None

    def Load(self, key):
        alliancesLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Alliances')
        sm.GetService('corpui').LoadTop('res:/ui/Texture/WindowIcons/alliances.png', alliancesLabel)
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            self.sr.wndViewParent = uiprimitives.Container(name='wndViewParent', align=uiconst.TOALL, pos=(0, 0, 0, 0), parent=self)
            if session.allianceid:
                self.sr.contacts = form.ContactsForm(name='alliancecontactsform', parent=self, pos=(0, 0, 0, 0), startupParams=())
                self.sr.contacts.Setup('alliancecontact')
            else:
                self.sr.contacts = uicontrols.Scroll(name='alliancecontactsform', parent=self, padding=(const.defaultPadding,
                 const.defaultPadding,
                 const.defaultPadding,
                 const.defaultPadding))
            self.sr.tabs = uicontrols.TabGroup(name='tabparent', parent=self, idx=0)
            self.sr.tabs.Startup(self._GetTabs(), 'corpaccounts')
            return
        self.LoadViewClass(key)

    def _GetTabs(self):
        tabs = []
        tabs.append(self._BuildTabParams('UI/Corporations/CorporationWindow/Alliances/Home', self.sr.wndViewParent, 'alliances_home'))
        if session.allianceid is not None:
            tabs.extend([self._BuildTabParams('UI/Corporations/CorporationWindow/Alliances/Bulletins', self.sr.wndViewParent, 'alliances_bulletins'),
             self._BuildTabParams('UI/Corporations/CorporationWindow/Alliances/Members', self.sr.wndViewParent, 'alliances_members'),
             self._BuildTabParams('UI/Corporations/CorporationWindow/Alliances/AllianceContacts', self.sr.contacts, 'alliancecontact'),
             self._BuildTabParams('UI/Neocom/Sovereignty', self.sr.wndViewParent, 'alliance_sovereignty'),
             self._BuildTabParams('UI/Corporations/CorporationWindow/Alliances/Systems', self.sr.wndViewParent, 'alliances_systems')])
        if not IsNPC(session.corpid):
            tabs.append(self._BuildTabParams('UI/Corporations/CorporationWindow/Alliances/Applications', self.sr.wndViewParent, 'alliances_applications'))
        tabs.append(self._BuildTabParams('UI/Corporations/CorporationWindow/Alliances/Rankings', self.sr.wndViewParent, 'alliances_rankings'))
        return tabs

    def _BuildTabParams(self, labelName, parent, tabArgs):
        return [localization.GetByLabel(labelName),
         parent,
         self,
         tabArgs]

    def LoadViewClass(self, tabName):
        self.sr.wndViewParent.Flush()
        visibleTab = None
        if self.sr.tabs:
            visibleTab = self.sr.tabs.GetVisible()
            if tabName == 'alliances':
                tabName = self.sr.tabs.GetSelectedArgs()
        if visibleTab and visibleTab.name == 'alliancecontactsform':
            if session.allianceid:
                self.sr.contacts.LoadContactsForm('alliancecontact')
                return
            else:
                corpNotInAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/CorpNotInAlliance', corpName=cfg.eveowners.Get(eve.session.corpid).ownerName)
                self.sr.contacts.Load(fixedEntryHeight=19, contentList=[], noContentHint=corpNotInAllianceLabel)
                return
        self.sr.contacts.state = uiconst.UI_HIDDEN
        if tabName == 'alliances_home':
            self.sr.currentView = form.AlliancesHome(parent=self.sr.wndViewParent)
        if tabName == 'alliances_systems':
            self.sr.currentView = FormAlliancesSystems(parent=self.sr.wndViewParent)
        elif tabName == 'alliances_rankings':
            self.sr.currentView = form.AlliancesRankings(parent=self.sr.wndViewParent)
        elif tabName == 'alliances_applications':
            self.sr.currentView = form.AlliancesApplications(parent=self.sr.wndViewParent)
        elif tabName == 'alliances_members':
            self.sr.currentView = form.AlliancesMembers(parent=self.sr.wndViewParent, align=uiconst.TOALL)
        elif tabName == 'alliances_bulletins':
            self.sr.currentView = form.AlliancesBulletins(parent=self.sr.wndViewParent)
        elif tabName == 'alliance_sovereignty':
            self.sr.currentView = FormAlliancesSovereignty(parent=self.sr.wndViewParent)
        if self.sr.currentView is not None:
            self.sr.currentView.CreateWindow()

    def OnSetAllianceStanding(self, *args):
        if uiutil.IsVisible(self) and self.sr.Get('inited', False) and self.sr.tabs:
            self.sr.tabs.ReloadVisible()

    def OnAllianceApplicationChanged(self, allianceID, corpID, change):
        log.LogInfo(self.__class__.__name__, 'OnAllianceApplicationChanged')
        function = getattr(self.sr.currentView, 'OnAllianceApplicationChanged', None)
        if function is not None:
            function(allianceID, corpID, change)

    def OnAllianceMemberChanged(self, allianceID, corpID, change):
        log.LogInfo(self.__class__.__name__, 'OnAllianceMemberChanged')
        function = getattr(self.sr.currentView, 'OnAllianceMemberChanged', None)
        if function is not None:
            function(allianceID, corpID, change)

    def OnAllianceRelationshipChanged(self, allianceID, toID, change):
        log.LogInfo(self.__class__.__name__, 'OnAllianceRelationshipChanged')
        function = getattr(self.sr.currentView, 'OnAllianceRelationshipChanged', None)
        if function is not None:
            function(allianceID, toID, change)

    def OnAllianceChanged(self, allianceID, change):
        log.LogInfo(self.__class__.__name__, 'OnAllianceChanged')
        function = getattr(self.sr.currentView, 'OnAllianceChanged', None)
        if function is not None:
            function(allianceID, change)

    def OnUpdateCapitalInfo(self):
        if isinstance(self.sr.currentView, FormAlliancesSystems):
            self.sr.currentView.UpdateCapitalInfo()
