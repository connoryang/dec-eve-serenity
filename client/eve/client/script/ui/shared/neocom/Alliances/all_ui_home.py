#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\Alliances\all_ui_home.py
from eve.client.script.ui.control.entries import LabelTextSides
from eve.client.script.ui.control.eveLabel import EveLabelSmall
import blue
import uiprimitives
import uicontrols
import uthread
import form
from eve.client.script.ui.control import entries as listentry
import log
import uicls
import carbonui.const as uiconst
import localization

class FormAlliancesHome(uiprimitives.Container):
    __guid__ = 'form.AlliancesHome'
    __nonpersistvars__ = []

    def CreateWindow(self):
        btns = []
        self.toolbarContainer = uiprimitives.Container(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
        if eve.session.allianceid is None:
            corporation = sm.GetService('corp').GetCorporation(eve.session.corpid)
            if corporation.ceoID == eve.session.charid:
                createAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CreateAlliance')
                btns.append([createAllianceLabel,
                 self.CreateAllianceForm,
                 None,
                 None])
        elif eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector:
            editAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/EditAlliance')
            declareWarLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/DeclareWar')
            btns.append([editAllianceLabel,
             self.EditAllianceForm,
             None,
             None])
            btns.append([declareWarLabel,
             self.DeclareWarForm,
             None,
             None])
        if len(btns):
            buttons = uicontrols.ButtonGroup(btns=btns, parent=self.toolbarContainer)
        self.toolbarContainer.height = 20 if not len(btns) else buttons.height
        self.sr.scroll = uicontrols.Scroll(parent=self, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        if eve.session.allianceid is None:
            corpNotInAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CorporationNotInAlliance', corpName=cfg.eveowners.Get(eve.session.corpid).ownerName)
            self.sr.scroll.Load(fixedEntryHeight=19, contentList=[], noContentHint=corpNotInAllianceLabel)
            return
        self.LoadScroll()

    def LoadScroll(self):
        if self is None or self.destroyed:
            return
        if not self.sr.Get('scroll'):
            return
        try:
            scrolllist = []
            sm.GetService('corpui').ShowLoad()
            self.ShowMyAllianceDetails(scrolllist)
            self.sr.scroll.Load(contentList=scrolllist)
        except:
            log.LogException()
            sys.exc_clear()
        finally:
            sm.GetService('corpui').HideLoad()

    def ShowMyAllianceDetails(self, scrolllist):
        sm.GetService('corpui').ShowLoad()
        try:
            data = {'GetSubContent': self.ShowDetails,
             'label': localization.GetByLabel('UI/Common/Details'),
             'groupItems': None,
             'id': ('alliance', 'details'),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide'}
            scrolllist.append(listentry.Get('Group', data))
            uicore.registry.SetListGroupOpenState(('alliance', 'details'), 1)
        finally:
            sm.GetService('corpui').HideLoad()

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def ShowDetails(self, nodedata, *args):
        log.LogInfo('ShowDetails')
        try:
            sm.GetService('corpui').ShowLoad()
            eHint = ''
            if eve.session.allianceid is None:
                corporation = sm.GetService('corp').GetCorporation(eve.session.corpid)
                if corporation.ceoID != eve.session.charid:
                    eHint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CEODeclareWarOnlyHint')
            if not eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector:
                eHint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/DirectorsCanEdit')
            alliancesLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Alliances')
            sm.GetService('corpui').LoadTop('res:/ui/Texture/WindowIcons/alliances.png', alliancesLabel, eHint)
            scrolllist = []
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/NoDetailsFound')
            if self is None or self.destroyed:
                log.LogInfo('ShowMembers Destroyed or None')
                hint = '\xfe\xfa s\xe1st mig ekki.'
            elif eve.session.allianceid is None:
                hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CorporationNotInAllianceATM', corpName=cfg.eveowners.Get(eve.session.corpid).ownerName)
            else:
                rec = sm.GetService('alliance').GetAlliance()
                owners = [rec.allianceID, rec.creatorCorpID, rec.creatorCharID]
                if rec.executorCorpID is not None:
                    owners.append(rec.executorCorpID)
                if len(owners):
                    cfg.eveowners.Prime(owners)
                label = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/AllianceName')
                text = cfg.eveowners.Get(rec.allianceID).ownerName
                params = {'line': 1,
                 'label': label,
                 'text': text,
                 'typeID': const.typeAlliance,
                 'itemID': rec.allianceID}
                scrolllist.append(listentry.Get('LabelTextTop', params))
                executor = cfg.eveowners.GetIfExists(rec.executorCorpID)
                label = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/Executor')
                if executor is not None:
                    params = {'line': 1,
                     'label': label,
                     'text': executor.ownerName,
                     'typeID': const.typeCorporation,
                     'itemID': rec.executorCorpID}
                else:
                    params = {'line': 1,
                     'label': label,
                     'text': '-'}
                scrolllist.append(listentry.Get('LabelTextTop', params))
                label = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/ShortName')
                params = {'line': 1,
                 'label': label,
                 'text': rec.shortName}
                scrolllist.append(listentry.Get('LabelTextTop', params))
                label = localization.GetByLabel('UI/Common/URL')
                if rec.url is not None:
                    params = {'line': 1,
                     'label': label,
                     'text': '<url=%s>%s</url>' % (rec.url, rec.url)}
                scrolllist.append(listentry.Get('LabelTextTop', params))
                label = localization.GetByLabel('UI/Common/Description')
                params = {'line': 1,
                 'label': label,
                 'text': rec.description}
                scrolllist.append(listentry.Get('LabelTextTop', params))
                label = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CreatedByCorporation')
                params = {'line': 1,
                 'label': label,
                 'text': cfg.eveowners.Get(rec.creatorCorpID).ownerName,
                 'typeID': const.typeCorporation,
                 'itemID': rec.creatorCorpID}
                scrolllist.append(listentry.Get('LabelTextTop', params))
                label = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CreatedBy')
                params = {'line': 1,
                 'label': label,
                 'text': cfg.eveowners.Get(rec.creatorCharID).ownerName,
                 'typeID': const.typeCharacterAmarr,
                 'itemID': rec.creatorCharID}
                scrolllist.append(listentry.Get('LabelTextTop', params))
                label = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/Dictatorial')
                yesLabel = localization.GetByLabel('UI/Common/Buttons/Yes')
                noLabel = localization.GetByLabel('UI/Common/Buttons/No')
                text = [noLabel, yesLabel][rec.dictatorial]
                params = {'line': 1,
                 'label': label,
                 'text': text}
                scrolllist.append(listentry.Get('LabelTextTop', params))
            self.sr.scroll.adjustableColumns = 1
            self.sr.scroll.sr.id = 'alliances_members'
            if not scrolllist:
                self.SetHint(hint)
            return scrolllist
        finally:
            sm.GetService('corpui').HideLoad()

    def OnAllianceChanged(self, allianceID, change):
        log.LogInfo('OnAllianceChanged allianceID', allianceID, 'change', change)
        if eve.session.allianceid != allianceID:
            return
        if self.state != uiconst.UI_NORMAL:
            log.LogInfo('OnAllianceChanged state != UI_NORMAL')
            return
        if self.sr.scroll is None:
            log.LogInfo('OnAllianceChanged no scroll')
            return
        self.ShowDetails()

    def CreateAllianceForm(self, *args):
        wnd = form.CreateAllianceWnd.Open()

    def EditAllianceForm(self, *args):
        wnd = form.EditAllianceWnd.Open()

    def DeclareWarForm(self, *args):
        sm.GetService('menu').DeclareWar()


class FormAlliancesBulletins(uiprimitives.Container):
    __guid__ = 'form.AlliancesBulletins'
    __nonpersistvars__ = []

    def CreateWindow(self):
        btns = []
        self.toolbarContainer = uiprimitives.Container(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
        if eve.session.allianceid is None:
            corporation = sm.GetService('corp').GetCorporation(eve.session.corpid)
            if corporation.ceoID == eve.session.charid:
                createAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CreateAlliance')
                btns.append([createAllianceLabel,
                 self.CreateAllianceForm,
                 None,
                 None])
        elif const.corpRoleChatManager & eve.session.corprole == const.corpRoleChatManager:
            addBulletinLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/AddBulletin')
            btns.append([addBulletinLabel,
             self.AddBulletin,
             None,
             None])
        if len(btns):
            buttons = uicontrols.ButtonGroup(btns=btns, parent=self.toolbarContainer)
        self.toolbarContainer.height = 20 if not len(btns) else buttons.height
        bulletinParent = uiprimitives.Container(name='bulletinParent', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        uiprimitives.Container(name='push', parent=bulletinParent, align=uiconst.TOLEFT, width=const.defaultPadding)
        self.messageArea = uicontrols.Scroll(parent=bulletinParent)
        self.messageArea.HideBackground()
        self.messageArea.RemoveActiveFrame()
        if session.allianceid is not None:
            self.LoadBulletins()

    def AddBulletin(self, *args):
        sm.GetService('corp').EditBulletin(None, isAlliance=True)

    def LoadBulletins(self):
        scrollEntries = sm.GetService('corp').GetBulletinEntries(isAlliance=True)
        self.messageArea.LoadContent(contentList=scrollEntries, noContentHint=localization.GetByLabel('UI/Corporations/BaseCorporationUI/NoBulletins'))


class CreateAllianceWnd(uicontrols.Window):
    __guid__ = 'form.CreateAllianceWnd'
    default_width = 320
    default_height = 275
    default_minSize = (default_width, default_height)
    default_windowID = 'CreateAllianceWindow'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Confirm, cancelFunc=self.Cancel)
        wndCaption = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CreateAlliance')
        self.SetCaption(wndCaption)
        self.SetTopparentHeight(0)
        self.MakeUnResizeable()
        self.ConstructLayout()

    def ConstructLayout(self):
        cont = uiprimitives.Container(parent=self.sr.main, align=uiconst.TOALL, padding=const.defaultPadding)
        if boot.region == 'optic':
            nameValue = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/NameAlliance', allianceName=cfg.eveowners.Get(session.corpid).ownerName)
        else:
            nameValue = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/NameAlliance', languageID=localization.const.LOCALE_SHORT_ENGLISH, allianceName=cfg.eveowners.Get(session.corpid).ownerName)
        self.nameEdit = uicontrols.SinglelineEdit(parent=cont, label=localization.GetByLabel('UI/Common/Name'), align=uiconst.TOTOP, maxLength=100, padTop=12, setvalue=nameValue)
        shortNameCont = uiprimitives.Container(parent=cont, align=uiconst.TOTOP, height=30, padTop=20)
        suggestBtn = uicontrols.Button(parent=shortNameCont, align=uiconst.TOPRIGHT, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/SuggestCommand'), func=self.GetSuggestedTickerNames)
        editWidth = self.width - suggestBtn.width - 16
        self.shortNameEdit = uicontrols.SinglelineEdit(parent=shortNameCont, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/ShortName'), align=uiconst.TOPLEFT, maxLength=5, width=editWidth)
        self.urlEdit = uicontrols.SinglelineEdit(parent=cont, label=localization.GetByLabel('UI/Common/URL'), align=uiconst.TOTOP, maxLenght=2048, padTop=12)
        editLabel = uicontrols.EveLabelSmall(parent=cont, text=localization.GetByLabel('UI/Common/Description'), height=16, align=uiconst.TOTOP, padTop=12)
        self.descriptionEdit = uicls.EditPlainText(parent=cont, align=uiconst.TOTOP, maxLength=5000, height=80)

    def GetSuggestedTickerNames(self, *args):
        wnd = form.SetShortNameWnd.Open(allianceName=self.nameEdit.GetValue())
        if wnd.ShowModal() == 1:
            retval = wnd.result
        else:
            retval = None
        if retval is None:
            return
        self.shortNameEdit.SetValue(retval)

    def Confirm(self, *args):
        allianceName = self.nameEdit.GetValue()
        shortName = self.shortNameEdit.GetValue()
        url = self.urlEdit.GetValue()
        description = self.descriptionEdit.GetValue()
        uthread.new(sm.GetService('sessionMgr').PerformSessionChange, 'alliance.addalliance', sm.GetService('corp').CreateAlliance, allianceName, shortName, description, url)
        self.Close()

    def Cancel(self, *args):
        self.Close()


class SetShortNameWnd(uicontrols.Window):
    __guid__ = 'form.SetShortNameWnd'
    default_width = 250
    default_height = 265
    default_minSize = (default_width, default_height)
    default_windowID = 'SetShortNameWindow'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.allianceName = attributes.get('allianceName')
        self.checkBoxes = []
        self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Confirm, cancelFunc=self.Cancel)
        wndCaption = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/SuggestedShortName')
        self.SetCaption(wndCaption)
        self.SetTopparentHeight(0)
        self.MakeUnResizeable()
        self.ConstructLayout()

    def ConstructLayout(self):
        cont = uiprimitives.Container(parent=self.sr.main, align=uiconst.TOTOP, padding=const.defaultPadding, height=16)
        checkBoxCont = uicontrols.ContainerAutoSize(parent=self.sr.main, name='checkBoxCont', align=uiconst.TOTOP, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         const.defaultPadding))
        selectLabel = uicontrols.EveLabelSmallBold(parent=cont, text=localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/SelectShortName'), height=16, align=uiconst.TOTOP)
        shortNames = sm.GetService('corp').GetSuggestedAllianceShortNames(self.allianceName)
        checked = True
        for shortNameRow in shortNames:
            shortName = shortNameRow.shortName
            if shortName is None:
                continue
            checkBox = uicontrols.Checkbox(text=shortName, parent=checkBoxCont, configName='shortNames', retval=shortName, checked=checked, groupname='state', align=uiconst.TOTOP, height=19)
            self.checkBoxes.append(checkBox)
            checked = False

        self.height = checkBoxCont.height + 70

    def Confirm(self, *args):
        shortName = ''
        for checkBox in self.checkBoxes:
            if checkBox.checked:
                shortName = checkBox.data['value']
                break

        self.result = shortName
        self.SetModalResult(1)

    def Cancel(self, *args):
        self.result = None
        self.SetModalResult(0)


class EditAllianceWnd(uicontrols.Window):
    __guid__ = 'form.EditAllianceWnd'
    default_width = 320
    default_height = 193
    default_minSize = (default_width, default_height)
    default_windowID = 'EditAllianceWindow'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Confirm, cancelFunc=self.Cancel)
        wndCaption = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/UpdateAlliance')
        self.SetCaption(wndCaption)
        self.SetTopparentHeight(0)
        self.MakeUnResizeable()
        self.ConstructLayout()

    def ConstructLayout(self):
        alliance = sm.GetService('alliance').GetAlliance()
        cont = uiprimitives.Container(parent=self.sr.main, align=uiconst.TOALL, padding=const.defaultPadding)
        self.urlEdit = uicontrols.SinglelineEdit(parent=cont, label=localization.GetByLabel('UI/Common/URL'), align=uiconst.TOTOP, maxLength=2048, padTop=12, setvalue=alliance.url)
        editLabel = uicontrols.EveLabelSmall(parent=cont, text=localization.GetByLabel('UI/Common/Description'), height=16, align=uiconst.TOTOP, padTop=12)
        self.descriptionEdit = uicls.EditPlainText(parent=cont, align=uiconst.TOTOP, maxLength=5000, height=80, setvalue=alliance.description)

    def Confirm(self, *args):
        url = self.urlEdit.GetValue()
        description = self.descriptionEdit.GetValue()
        self.result = (url, description)
        sm.GetService('alliance').UpdateAlliance(description, url)
        self.Close()

    def Cancel(self, *args):
        self.Close()


class PrimeTimeHourEntryHorizontal(LabelTextSides):
    __guid__ = 'listentry.PrimeTimeHourEntryHorizontal'

    def Startup(self, *args):
        listentry.LabelTextSides.Startup(self, args)
        self.primeTimeInfo = None

    def Load(self, node):
        self.primeTimeInfo = node.primeTimeInfo
        text, infoText = self.GetText()
        node.text = text
        LabelTextSides.Load(self, node)
        if infoText:
            self.sr.infoLabel = EveLabelSmall(text=infoText, parent=self, top=6, state=uiconst.UI_DISABLED, align=uiconst.CENTERRIGHT, left=8)
            self.sr.text.top = -6

    def GetCurrentPrimeHour(self):
        currentPrimeHour = 0
        if self.primeTimeInfo and self.primeTimeInfo.currentPrimeHour is not None:
            currentPrimeHour = self.primeTimeInfo.currentPrimeHour
        return currentPrimeHour

    def GetText(self):
        infoText = ''
        if self.primeTimeInfo is None or self.primeTimeInfo.currentPrimeHour is None:
            text = localization.GetByLabel('UI/Common/Unknown')
        else:
            newPrimeHour = self.primeTimeInfo.newPrimeHour
            validAfter = self.primeTimeInfo.newPrimeHourValidAfter
            now = blue.os.GetWallclockTime()
            if newPrimeHour and now < validAfter:
                text = localization.GetByLabel('UI/Sovereignty/VulnerabilityTimerChangesTime', hour=self.primeTimeInfo.currentPrimeHour, newHour=self.primeTimeInfo.newPrimeHour)
                infoText = localization.GetByLabel('UI/Sovereignty/VulnerabilityTimerChangesInfo', validAfterDate=self.primeTimeInfo.newPrimeHourValidAfter)
            else:
                currentPrimeHour = self.GetCurrentPrimeHour()
                text = localization.GetByLabel('UI/Sovereignty/VulnerabilityTime', hour=currentPrimeHour)
        return (text, infoText)
