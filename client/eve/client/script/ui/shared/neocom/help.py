#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\help.py
import blue
from eve.client.script.ui.control.eveWindowUnderlay import BumpedUnderlay
from eve.client.script.ui.control.themeColored import LineThemeColored
import service
import uiprimitives
import uicontrols
import util
import urllib
from eve.client.script.ui.control.entries import Generic as GenericListEntry, Get as GetListEntry
import carbonui.const as uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import Label, EveLabelMedium, EveLabelMediumBold, EveLabelLargeBold
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.shared.videowindow import VideoPlayerWindow
import eve.client.script.ui.control.entries as listentry
import localization
import uthread
import utillib
from videoplayer.index import VideoIndex
import unicodedata
if boot.region == 'optic':
    TUTORIAL_VIDEOS_INDEX = VideoIndex('http://cdnpatcheve.tiancity.cn/video/flightacademy/index.json')
else:
    TUTORIAL_VIDEOS_INDEX = VideoIndex('http://cdn1.eveonline.com/academy/index.json')

class _TutorialVideoItem(SE_BaseClassCore):
    __guid__ = 'listentry.TutorialVideoItem'
    __params__ = ['label']
    isDragObject = True

    def Startup(self, *etc):
        _textCont = ContainerAutoSize(parent=self, align=uiconst.TOALL, padLeft=20, padTop=4, clipChildren=True)
        self.label = EveLabelMediumBold(text='', parent=_textCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padRight=40)
        self.text = EveLabelMedium(text='', parent=_textCont, align=uiconst.TOTOP, padRight=40)
        self.infoicon = ButtonIcon(left=2, parent=self, idx=0, iconSize=32, align=uiconst.CENTERRIGHT)
        self.infoicon.SetTexturePath('res:/ui/texture/icons/bigplay.png')

    def Load(self, node):

        def play():
            HelpWindow.PlayVideo(node)

        self.node = node
        self.label.text = self.node.title
        self.infoicon.node = node
        self.text.text = node.description
        self.label.OnClick = play
        self.infoicon.func = play

    def _Click(self):
        HelpWindow.PlayVideo(self.node)

    def GetDragData(self, *args):
        return (self.node,)

    def GetDynamicHeight(node, width):
        return max(32, EveLabelMedium.MeasureTextSize(node.description, width=width - 60)[1] + EveLabelMediumBold.MeasureTextSize(node.title, width=width - 60)[1] + 8)


class _RelatedItem(uiprimitives.Container):

    def ApplyAttributes(self, attributes):

        def play():
            HelpWindow.PlayVideoId(attributes['videoid'])

        uiprimitives.Container.ApplyAttributes(self, attributes)
        textCont = ContainerAutoSize(parent=self, align=uiconst.TOALL, padLeft=40, clipChildren=True)
        self.label = EveLabelLargeBold(parent=textCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.label.OnClick = play
        self.text = EveLabelMediumBold(parent=textCont, align=uiconst.TOTOP)
        playicon = ButtonIcon(parent=self, idx=0, iconSize=32, align=uiconst.CENTERLEFT, func=play)
        playicon.SetTexturePath('res:/ui/texture/icons/bigplay.png')
        self.label.text = attributes.get('title', '')
        self.text.text = attributes.get('description', '')

    def SetSizeAutomatically(self):
        width = self.displayRect[2]
        height = EveLabelMediumBold.MeasureTextSize(self.text.text, width=width - 40)[1] + EveLabelLargeBold.MeasureTextSize(self.label.text, width=width - 40)[1]
        self.height = height

    def UpdateAlignment(self, *args, **kwds):
        budget = uiprimitives.Container.UpdateAlignment(self, *args, **kwds)
        self.SetSizeAutomatically()
        return budget

    def GetAbsoluteSize(self):
        self.SetSizeAutomatically()
        return uiprimitives.Container.GetAbsoluteSize(self)


class _RelatedContainer(uiprimitives.Container):

    def _OnResize(self, *args):
        width = self.displayRect[2]
        for each in self.children:
            each.width = width


class HelpWindow(uicontrols.Window):
    __guid__ = 'form.HelpWindow'
    __notifyevents__ = ['ProcessSessionChange']
    default_width = 300
    default_height = 400
    default_windowID = 'help'
    default_captionLabelPath = 'Tooltips/Neocom/Help'
    default_descriptionLabelPath = 'Tooltips/Neocom/Help_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/help.png'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.SetScope('station_inflight')
        self.SetWndIcon(self.default_iconNum)
        self.SetMinSize([300, 400], 1)
        self.LockWidth(300)
        self.SetTopparentHeight(64)
        self.MakeUnpinable()
        self.MouseDown = self.OnWndMouseDown
        self.supportLoaded = False
        self.tutorialsLoaded = False
        self.tutorialVideosLoaded = False
        supportPar = uiprimitives.Container(name='supportPar', parent=self.sr.main, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding)
        videoPar = uiprimitives.Container(name='videoPar', parent=self.sr.main, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding)
        tabs = []
        if sm.GetService('experimentClientSvc').IsTutorialEnabled():
            tutorialsPar = uiprimitives.Container(name='tutorialPar', parent=self.sr.main, pos=(0, 0, 0, 0))
            tabs = [[localization.GetByLabel('UI/Help/Support'),
              supportPar,
              self,
              ('support',)], [localization.GetByLabel('UI/Help/Tutorials'),
              tutorialsPar,
              self,
              ('tutorials',)], [localization.GetByLabel('UI/Help/TutorialVideos'),
              videoPar,
              self,
              ('videos',)]]
        else:
            tabs = [[localization.GetByLabel('UI/Help/Support'),
              supportPar,
              self,
              ('support',)], [localization.GetByLabel('UI/Help/TutorialVideos'),
              videoPar,
              self,
              ('videos',)]]
        tabs = uicontrols.TabGroup(name='tabparent', parent=self.sr.main, idx=0, tabs=tabs, autoselecttab=0)
        tabs.ShowPanelByName(attributes.showPanel or localization.GetByLabel('UI/Help/Support'))
        self.sr.mainTabs = tabs
        uicontrols.CaptionLabel(text=localization.GetByLabel('UI/Help/EveHelp'), parent=self.sr.topParent, align=uiconst.CENTERLEFT, left=70)

    def ProcessSessionChange(self, isremote, session, change):
        if session.charid is None:
            self.Close()

    def LoadTabPanel(self, args, panel, tabgroup):
        if args:
            key = args[0]
            if key == 'tutorials':
                self.LoadTutorials(panel)
            elif key == 'support':
                self.LoadSupport(panel)
            elif key == 'videos':
                self.LoadTutorialVideos(panel)

    def LoadTutorials(self, panel, *args):
        if self.tutorialsLoaded:
            return
        scroll = uicontrols.Scroll(parent=panel, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding)
        scroll.multiSelect = 0
        scroll.OnSelectionChange = self.OnScrollSelectionChange
        scroll.Confirm = self.OpenSelectedTutorial
        byCategs = sm.GetService('tutorial').GetTutorialsByCategory()
        categsNames = []
        for categoryID in byCategs.keys():
            if categoryID is not None:
                categoryInfo = sm.GetService('tutorial').GetCategory(categoryID)
                categoryName = localization.GetByMessageID(categoryInfo.categoryNameID)
                categoryDesc = localization.GetByMessageID(categoryInfo.descriptionID)
                categsNames.append((categoryName, (categoryID, categoryDesc)))
            else:
                categsNames.append(('-- No category Set! --', (categoryID, '')))

        categsNames.sort()
        scrolllist = []
        for label, (categoryID, hint) in categsNames:
            if categoryID is None and not eve.session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
                continue
            data = {'GetSubContent': self.GetTutorialGroup,
             'label': label,
             'id': ('tutorial', categoryID),
             'groupItems': byCategs[categoryID],
             'showicon': 'hide',
             'BlockOpenWindow': 1,
             'state': 'locked',
             'showlen': 0,
             'hint': hint}
            scrolllist.append(GetListEntry('Group', data))

        scroll.Load(contentList=scrolllist)
        buttonList = [[localization.GetByLabel('UI/Help/OpenTutorial'), self.OpenSelectedTutorial, ()], [localization.GetByLabel('UI/Help/ShowCareerAgents'), self.ShowTutorialAgents, ('tutorials',)]]
        if session.role & service.ROLE_CONTENT:
            buttonList.append(['Clear Cache', self.CloseTutorialService, ()])
        btns = uicontrols.ButtonGroup(btns=buttonList, line=1, unisize=0)
        panel.children.insert(0, btns)
        tutorialBtn = btns.sr.Get(localization.GetByLabel('UI/Help/ShowCareerAgents') + 'Btn')
        if tutorialBtn:
            tutorialBtn.hint = localization.GetByLabel('UI/Help/CareerAgentExplanation')
        self.sr.tutorialBtns = btns
        self.sr.tutorialScroll = scroll
        self.tutorialsLoaded = True

    def LoadTutorialVideos(self, panel, *args):
        if self.tutorialVideosLoaded:
            return

        def GetSubContent(group):
            scrolllist = []
            for each in TUTORIAL_VIDEOS_INDEX.get_videos_in_group(group.index):
                scrolllist.append(listentry.Get(data=each, decoClass=_TutorialVideoItem))

            return scrolllist

        scrolllist = []
        for index, each in TUTORIAL_VIDEOS_INDEX.get_groups():
            data = {'GetSubContent': GetSubContent,
             'BlockOpenWindow': True,
             'label': each,
             'showicon': 'hide',
             'showlen': 0,
             'index': index,
             'state': 'locked',
             'id': 'tutorialvideocat_%s' % index}
            scrolllist.append(listentry.Get('Group', data))

        scroll = uicontrols.Scroll(parent=panel, align=uiconst.TOALL)
        scroll.LoadContent(contentList=scrolllist)
        self.tutorialVideosLoaded = True

    @classmethod
    def PlayVideoId(cls, videoid):
        desc = TUTORIAL_VIDEOS_INDEX.get_video_by_id(videoid)
        if desc:
            cls.PlayVideo(utillib.KeyVal(desc))

    @classmethod
    def PlayVideo(cls, node):

        def showRelated(parent):
            moreContainer = uiprimitives.Container(parent=parent, align=uiconst.TOBOTTOM, height=50)
            more = EveLabelMediumBold(text=localization.GetByLabel('UI/Help/ShowMoreTutorials'), parent=moreContainer, align=uiconst.CENTER, state=uiconst.UI_NORMAL)
            more.OnClick = lambda : HelpWindow.Open(showPanel=localization.GetByLabel('UI/Help/TutorialVideos'))
            relatedParent = _RelatedContainer(parent=parent, align=uiconst.TOALL, padding=(100, 40, 100, 40))
            relatedContainer = ContainerAutoSize(parent=relatedParent, align=uiconst.CENTER)
            for each in TUTORIAL_VIDEOS_INDEX.get_related(node.id):
                _RelatedItem(align=uiconst.TOTOP, parent=relatedContainer, title=each['fullTitle'], description=each['description'], videoid=each['id'])

        VideoPlayerWindow.Open(windowID='VideoPlayer').PlayVideo(node.url, title=node.fullTitle, subtitles=node.subtitles, onFinish=showRelated)
        cls.LogPlayVideo(node.id)

    @classmethod
    def LogPlayVideo(cls, videoIdUnicode):
        videoIdString = unicodedata.normalize('NFKD', videoIdUnicode).encode('ascii', 'ignore')
        videoId = videoIdString.rsplit('_')[0]
        languageId = localization.util.GetLanguageID()
        sm.GetService('infoGatheringSvc').LogInfoEvent(eventTypeID=const.infoEventVideoPlayed, itemID=session.charid, itemID2=session.userid, int_1=videoId, char_1=languageId)

    def CloseTutorialService(self):
        sm.StopService('tutorial')
        self.CloseByUser()

    def GetTutorialGroup(self, nodedata, newitems = 0):
        if not len(nodedata.groupItems):
            return []
        scrolllist = []
        for tutorialData in nodedata.groupItems:
            label = localization.GetByMessageID(tutorialData.tutorialNameID)
            data = {'label': label,
             'sublevel': 1,
             'OnDblClick': self.OpenTutorial,
             'tutorialData': tutorialData,
             'tutorialID': tutorialData.tutorialID}
            if tutorialData.otherRace:
                data['fontColor'] = (1, 1, 1, 0.5)
            entry = GetListEntry('TutorialEntry', data)
            scrolllist.append(entry)

        return scrolllist

    def OnScrollSelectionChange(self, selected, *args):
        openBtn = self.sr.tutorialBtns.sr.Get(localization.GetByLabel('UI/Help/EveHelp') + 'Btn')
        if openBtn:
            if selected:
                openBtn.state = uiconst.UI_NORMAL
            else:
                openBtn.state = uiconst.UI_HIDDEN

    def ShowTutorialAgents(self, fromWhere = '', *args):
        if util.IsWormholeSystem(eve.session.solarsystemid) or eve.session.solarsystemid == const.solarSystemPolaris:
            raise UserError('NoAgentsInWormholes')
        sm.StartService('tutorial').ShowCareerFunnel()
        self.LogHelpWindowEvents('openCareerFunnel', fromWhere)

    def LogHelpWindowEvents(self, eventType, fromWhere):
        sm.GetService('infoGatheringSvc').LogInfoEvent(eventTypeID=const.infoEventCareerFunnel, itemID=session.charid, itemID2=session.userid, int_1=1, char_1=eventType, char_2=fromWhere)

    def CreateBugReport(self, *args):
        self.Close()
        blue.pyos.synchro.SleepWallclock(10)
        sm.GetService('bugReporting').StartCreateBugReport()

    def OpenSelectedTutorial(self, *args):
        sel = self.sr.tutorialScroll.GetSelected()
        if sel:
            tutorialData = getattr(sel[0], 'tutorialData', None)
            if tutorialData is None:
                return
            sm.GetService('tutorial').OpenTutorial(tutorialData.tutorialID)
        else:
            info = localization.GetByLabel('UI/Help/MustSelectSomething')
            raise UserError('CustomInfo', {'info': info})

    def OpenTutorial(self, entry):
        tutorialData = entry.sr.node.tutorialData
        sm.GetService('tutorial').OpenTutorial(tutorialData.tutorialID)

    def _LoadSupportHelpChannel(self, parent):
        helpchannelpar = uiprimitives.Container(name='helpchannelpar', parent=parent, align=uiconst.TOTOP)
        helpchannelpar.padTop = 4
        helptext = uicontrols.EveLabelMedium(name='label', text=localization.GetByLabel('UI/Help/JoinChannelHint'), parent=helpchannelpar, align=uiconst.TOPLEFT, pos=(8, 0, 280, 0), state=uiconst.UI_NORMAL)
        helpchannelpar.height = helptext.textheight + 4
        helpbtnparent = uiprimitives.Container(name='helpbtnparent', parent=parent, align=uiconst.TOTOP)
        helpbtnparent.padTop = 4
        helpchannelbtn = uicontrols.Button(parent=helpbtnparent, label=localization.GetByLabel('UI/Help/JoinChannel'), func=self.JoinHelpChannel, btn_default=0, align=uiconst.TOPRIGHT)
        helpchannelbtn.left = 6
        helpbtnparent.height = helpchannelbtn.height + 4
        return helpchannelpar.height + helpbtnparent.height + 8

    def _LoadSupportPetitions(self, parent):
        petpar = uiprimitives.Container(name='petitionpar', parent=parent, align=uiconst.TOTOP)
        petpar.padTop = 4
        petbtnparent = uiprimitives.Container(name='petbtnparent', parent=parent, align=uiconst.TOTOP)
        petbtnparent.padTop = 4
        petitioner = sm.RemoteSvc('petitioner')
        if petitioner.IsSerenity():
            pettext = uicontrols.EveLabelMedium(name='label', text=localization.GetByLabel('UI/Help/OpenPetitions'), parent=petpar, align=uiconst.TOPLEFT, pos=(8, 0, 280, 0), state=uiconst.UI_NORMAL)
            petpar.height = pettext.textheight + 4
            petbtn = uicontrols.Button(parent=petbtnparent, label=localization.GetByLabel('UI/Help/FilePetition'), func=self.FilePetition, btn_default=0, align=uiconst.TOPRIGHT)
            petbtn.left = 6
            petbtnparent.height = petbtn.height + 4
        elif petitioner.IsZendeskSwapEnabled():
            pettext = uicontrols.EveLabelMedium(name='label', text=localization.GetByLabel('UI/Help/HelpCenterDescription'), parent=petpar, align=uiconst.TOPLEFT, pos=(8, 0, 280, 0), state=uiconst.UI_NORMAL)
            sumheight = pettext.textheight + 4
            if petitioner.HasOpenTickets():
                petlink = uicontrols.EveLabelMedium(name='labellink', text=localization.GetByLabel('UI/Help/OpenOldPetitions'), parent=petpar, align=uiconst.TOPLEFT, pos=(8,
                 sumheight + 4,
                 280,
                 0), state=uiconst.UI_NORMAL)
                sumheight += petlink.textheight + 4
            petpar.height = sumheight + 4
            hdbtn = uicontrols.Button(parent=petbtnparent, label=localization.GetByLabel('UI/Help/OpenHelpCenterFinal'), func=self.OpenHelpCenter, btn_default=0, align=uiconst.TOPRIGHT)
            hdbtn.left = 6
            petbtnparent.height = hdbtn.height + 4
        else:
            pettext = uicontrols.EveLabelMedium(name='label', text=localization.GetByLabel('UI/Help/OpenPetitions'), parent=petpar, align=uiconst.TOPLEFT, pos=(8, 0, 280, 0), state=uiconst.UI_NORMAL)
            petpar.height = pettext.textheight + 4
            petbtn = uicontrols.Button(parent=petbtnparent, label=localization.GetByLabel('UI/Help/FilePetition'), func=self.FilePetition, btn_default=0, align=uiconst.TOPRIGHT)
            petbtn.left = 6
            petbtnparent.height = petbtn.height + 4
            if petitioner.IsZendeskEnabled() and eve.session.languageID.lower() == 'en':
                hdbtn = uicontrols.Button(parent=petbtnparent, label=localization.GetByLabel('UI/Help/OpenHelpCenter'), func=self.OpenHelpCenter, btn_default=0, align=uiconst.TOPRIGHT)
                hdbtn.left = 6
                hdbtn.top = petbtn.height + 4
                petbtnparent.height += hdbtn.height + 4
        return petpar.height + petbtnparent.height + 8

    def _LoadSupportCareer(self, parent):
        funnelpar = uiprimitives.Container(name='funnelpar', parent=parent, align=uiconst.TOTOP)
        funnelpar.padTop = 4
        funneltext = uicontrols.EveLabelMedium(name='label', text=localization.GetByLabel('UI/Help/CareerAdvancementFull'), parent=funnelpar, align=uiconst.TOPLEFT, pos=(8, 0, 280, 0), state=uiconst.UI_NORMAL)
        funnelpar.height = funneltext.textheight + 4
        funnelbtnparent = uiprimitives.Container(name='funnelbtnparent', parent=parent, align=uiconst.TOTOP, width=96)
        funnelbtnparent.padTop = 4
        funnelbtn = uicontrols.Button(parent=funnelbtnparent, label=localization.GetByLabel('UI/Help/ShowCareerAgents'), func=self.ShowTutorialAgents, args=('support',), pos=(6, 0, 0, 0), align=uiconst.TOPRIGHT)
        funnelbtnparent.height = funnelbtn.height + 4
        return funnelpar.height + funnelbtnparent.height + 8

    def _LoadSupportBugReport(self, parent):
        bugreportpar = uiprimitives.Container(name='bugreportpar', parent=parent, align=uiconst.TOTOP)
        bugreportpar.padTop = 4
        bugreporttext = uicontrols.EveLabelMedium(name='label', text=localization.GetByLabel('UI/Help/ReportBugFull'), parent=bugreportpar, align=uiconst.TOPLEFT, pos=(8, 0, 280, 0), state=uiconst.UI_NORMAL)
        bugreportpar.height = bugreporttext.textheight + 4
        bugreportbtnparent = uiprimitives.Container(name='bugreportbtnparent', parent=parent, align=uiconst.TOTOP, width=96)
        bugreportbtnparent.padTop = 4
        bugreportbtn = uicontrols.Button(parent=bugreportbtnparent, label=localization.GetByLabel('UI/Help/ReportBug'), func=self.CreateBugReport, pos=(6, 0, 0, 0), align=uiconst.TOPRIGHT)
        bugreportbtnparent.height = bugreportbtn.height + 4
        return bugreportpar.height + bugreportbtnparent.height + 8

    def LoadSupport(self, panel, *args):
        if self.supportLoaded:
            return
        subpar = uiprimitives.Container(name='subpar', parent=panel, align=uiconst.TOALL)
        sumHeight = 0
        sumHeight += self._LoadSupportHelpChannel(subpar)
        LineThemeColored(parent=subpar, align=uiconst.TOTOP)
        sumHeight += self._LoadSupportPetitions(subpar) + 1
        LineThemeColored(parent=subpar, align=uiconst.TOTOP)
        sumHeight += self._LoadSupportCareer(subpar) + 1
        if int(sm.GetService('machoNet').GetGlobalConfig().get('bugReporting_ShowButton', 0)) > 0:
            LineThemeColored(parent=subpar, align=uiconst.TOTOP)
            sumHeight += self._LoadSupportBugReport(subpar) + 1
        self.SetMinSize([self.minsize[0], self.sr.topParent.height + self.sr.headerParent.height + sumHeight + 32])
        BumpedUnderlay(bgParent=panel)
        self.supportLoaded = True

    def OpenHelpCenter(self, *args):
        import webbrowser
        if eve.Message('HelpCenterOpenWarning', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
            petitioner = sm.RemoteSvc('petitioner')
            webbrowser.open_new(petitioner.GetZendeskJwtLink())

    def FilePetition(self, *args):
        sm.GetService('petition').NewPetition()

    def JoinHelpChannel(self, *etc):
        channels = []
        lsc = sm.StartService('LSC')
        if eve.session.role & service.ROLE_NEWBIE:
            channels.append(lsc.rookieHelpChannel)
        if eve.session.languageID == 'DE':
            channels.append(lsc.helpChannelDE)
        elif eve.session.languageID == 'RU':
            channels.append(lsc.helpChannelRU)
        elif eve.session.languageID == 'JA':
            channels.append(lsc.helpChannelJA)
        else:
            channels.append(lsc.helpChannelEN)
        sm.GetService('LSC').JoinChannels(channels)

    def OnWndMouseDown(self, *args):
        sm.GetService('neocom').BlinkOff('help')

    def _OnClose(self, *args):
        if getattr(self, 'sr', None) and self.sr.Get('form', None):
            self.sr.form.Close()


class TutorialEntry(GenericListEntry):
    __guid__ = 'listentry.TutorialEntry'
    isDragObject = True

    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes
