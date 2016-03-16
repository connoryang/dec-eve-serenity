#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\corporation\corp_ui_member_newroles.py
from carbon.common.script.util.commonutils import StripTags
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from carbonui.util.stringManip import ReplaceStringWithTags
from eve.client.script.ui.control.buttonGroup import ButtonGroup
from eve.client.script.ui.control.buttons import ToggleButtonGroup, BrowseButton
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.searchinput import SearchInput
from eve.client.script.ui.services.corporation.corp_util import GetCheckStateForRole, CHECKBOX_COL_WIDTH, NAME_COL_WIDTH, BASE_COL_WIDTH, ACCESS_COL_WIDTH
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_roleentry import RoleAccessEntry, RoleHeaderEntry, RoleEntry, TitleEntry, VerticalScrollHeader
from eve.client.script.ui.util import searchUtil
from eve.common.script.sys.rowset import Rowset
from localization import GetByLabel
import blue
import carbonui.const as uiconst
import uthread
PERMISSIONS = 1
STATION_SERVICE = 2
ACCOUNTING = 3
ACCESS = 4
GROUPS = 5
MEMBERS_PER_PAGE = 200

class CorpRolesNew(Container):
    __guid__ = 'form.CorpRolesNew'
    __nonpersistvars__ = []

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.corpSvc = sm.GetService('corp')
        self.membersToShow = []
        self.corp = attributes.corp
        self.viewFrom = 0
        self.isSearched = False
        self.isCleared = False
        self.isBrowsed = False
        self.memberIDs = None
        self.roleGroupings = self.corpSvc.GetRoleGroupings()
        self.divisions = self.corpSvc.GetDivisionNames()
        self.titles = self.corpSvc.GetTitles()
        self.myBaseID = self.corpSvc.GetMember(session.charid).baseID
        self.myGrantableRoles = self.corpSvc.GetMyGrantableRoles()
        self.bases = self.GetBaseOptions()
        self.lastClickedBtn = None
        buttons = [[GetByLabel('UI/Common/Buttons/SaveChanges'),
          self.SaveChanges,
          (),
          81]]
        btns = ButtonGroup(btns=buttons)
        self.children.insert(0, btns)
        self.mainCont = Container(parent=self, padding=4)
        self.topCont = Container(parent=self.mainCont, height=40, align=uiconst.TOTOP)
        self.browseCont = Container(name='browseCont', parent=self.mainCont, align=uiconst.TOBOTTOM, height=22, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         0), state=uiconst.UI_NORMAL)

    def Load(self, populateView = 1, *args):
        sm.GetService('corpui').LoadTop('res:/ui/Texture/WindowIcons/corporationmembers.png', GetByLabel('UI/Corporations/Common/Members'))
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            self.roleScroll = Scroll(parent=self.mainCont, id='rolesScroll')
            self.roleScroll.adjustableColumns = False
            self.roleScroll.sr.id = 'CorpRolesMembers'
            self.rolesSortHeaders = VerticalScrollHeader(parent=self.roleScroll.sr.maincontainer, settingsID='memberRoles', idx=0, scroll=self.roleScroll)
            self.rolesSortHeaders.OnSortingChange = self.ChangeRolesSort
            self.accessScroll = Scroll(parent=self.mainCont, id='accessScroll')
            self.accessScroll.sr.id = 'CorpAccessRolesMembers'
            self.accessSortHeaders = VerticalScrollHeader(parent=self.accessScroll.sr.maincontainer, settingsID='memberAccess', idx=0, scroll=self.accessScroll)
            self.accessSortHeaders.OnSortingChange = self.ChangeAccessSort
            self.titlesScroll = Scroll(parent=self.mainCont, id='accessScroll')
            self.titlesScroll.sr.id = 'CorpTitlesRolesMembers'
            self.titlesSortHeaders = VerticalScrollHeader(parent=self.titlesScroll.sr.maincontainer, settingsID='membertitles', idx=0, scroll=self.titlesScroll)
            self.titlesSortHeaders.OnSortingChange = self.ChangeTitlesSort
            self.members = self.corpSvc.GetMembers()
            self.serverMembers = self.members.PopulatePage(1)
            self.GetMembersToShow(updateState=False)
            self.roleGroupsBtns = ToggleButtonGroup(name='roleGroupsBtns', parent=self.topCont, align=uiconst.TOPLEFT, top=4, width=400, callback=self.ChangeState)
            self.AddRoleGroupButtons(self.roleGroupsBtns)
            selectedState = self.GetSelectedState()
            self.roleGroupsBtns.SelectByID(selectedState)
            self.searchInput = SearchInput(name='search', parent=self.topCont, maxLength=100, width=120, top=8, align=uiconst.TOPRIGHT, GetSearchEntries=self.Search, OnSearchEntrySelected=self.OnSearchEntrySelected, hinttext=GetByLabel('UI/EVEMail/MailingLists/SearchByName'))
            self.searchInput.displayHistory = False
            self.prevBtn = BrowseButton(parent=self.browseCont, prev=True, state=uiconst.UI_NORMAL, func=self.BrowseRoles)
            self.nextBtn = BrowseButton(parent=self.browseCont, prev=False, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT, func=self.BrowseRoles)
            self.prevBtn.Disable()
            self.pageNrLabel = EveLabelMedium(parent=self.browseCont, align=uiconst.CENTER)
            self.UpdatePageNrText()
            if self.members.totalCount < MEMBERS_PER_PAGE:
                self.browseCont.display = False
        else:
            self.UpdateScroll(self.GetSelectedState())

    def OnSearchEntrySelected(self, result, *args, **kwargs):
        owner = result[0].info
        self.isSearched = True
        self.isCleared = False
        self.GetMembersToShow(owner.ownerID)

    def ClearSearch(self):
        self.isSearched = False
        self.isCleared = True
        self.GetMembersToShow()

    def Search(self, searchString):
        if searchString == '':
            self.ClearSearch()
            return
        else:
            if self.memberIDs is None:
                self.memberIDs = self.corpSvc.GetMemberIDs()
            if len(searchString) < 3:
                return []
            return searchUtil.SearchCharactersInCorp(searchString, self.memberIDs)

    def ChangeSort(self, scroll, activeColumn, activeDirection):
        scroll.Sort(activeColumn, activeDirection)

    def ChangeRolesSort(self, *args):
        activeColumn, activeDirection = self.rolesSortHeaders.GetCurrentActive()
        self.ChangeSort(self.roleScroll, activeColumn, activeDirection)

    def ChangeAccessSort(self, *args):
        activeColumn, activeDirection = self.accessSortHeaders.GetCurrentActive()
        self.ChangeSort(self.accessScroll, activeColumn, activeDirection)

    def ChangeTitlesSort(self, *args):
        activeColumn, activeDirection = self.titlesSortHeaders.GetCurrentActive()
        self.ChangeSort(self.titlesScroll, activeColumn, activeDirection)

    def AddRoleGroupButtons(self, roleGroupsBtns):
        roleGroupsBtns.AddButton(PERMISSIONS, GetByLabel('UI/Corporations/RoleManagement/Permissions'))
        roleGroupsBtns.AddButton(STATION_SERVICE, GetByLabel('UI/Corporations/RoleManagement/StationService'))
        roleGroupsBtns.AddButton(ACCOUNTING, GetByLabel('UI/Corporations/RoleManagement/Accounting'))
        roleGroupsBtns.AddButton(ACCESS, GetByLabel('UI/Corporations/RoleManagement/Access'))
        roleGroupsBtns.AddButton(GROUPS, GetByLabel('UI/Corporations/Common/Titles'))

    def GetMembersToShow(self, searchedCharID = None, updateState = True):
        self.membersToShow = []
        if self.isSearched and searchedCharID:
            self.membersToShow.append(self.corpSvc.GetMember(searchedCharID))
        else:
            count = min(MEMBERS_PER_PAGE, self.members.totalCount - self.viewFrom)
            serverPage = self.viewFrom / self.members.perPage + 1
            self.serverMembers = self.members.PopulatePage(serverPage)
            for number in xrange(count):
                index = (number + self.viewFrom) % self.members.perPage
                currentServerPage = (number + self.viewFrom) / self.members.perPage + 1
                if serverPage != currentServerPage:
                    self.serverMembers = self.members.PopulatePage(currentServerPage)
                    serverPage = currentServerPage
                self.membersToShow.append(self.serverMembers[index])

        if updateState:
            self.ChangeState(self.GetSelectedState())

    def UpdatePageNrText(self):
        viewPage, viewPagesTotal = self.GetViewPageAndTotalPages()
        self.pageNrLabel.text = '%s/%s' % (viewPage, viewPagesTotal)

    def GetViewPageAndTotalPages(self):
        viewPage = self.viewFrom / MEMBERS_PER_PAGE + 1
        viewPagesTotal = self.members.totalCount / MEMBERS_PER_PAGE + 1
        return (viewPage, viewPagesTotal)

    def BrowseRoles(self, btn, *args):
        self.isBrowsed = True
        browse = btn.backforth
        self.viewFrom = self.viewFrom + browse * MEMBERS_PER_PAGE
        if self.viewFrom < 0:
            self.viewFrom = 0
        self.ShowHideBrowseButtons()
        self.UpdatePageNrText()
        self.GetMembersToShow()

    def ShowHideBrowseButtons(self):
        viewPage, viewPagesTotal = self.GetViewPageAndTotalPages()
        if viewPage < viewPagesTotal:
            self.nextBtn.Enable()
        else:
            self.nextBtn.Disable()
        if viewPage == 1:
            self.prevBtn.Disable()
        else:
            self.prevBtn.Enable()

    def GetSelectedState(self):
        return settings.user.ui.Get('selectedRoleGroupState', PERMISSIONS)

    def LoadScroll(self, scroll, sortHeaders, headers, fixedHeaders, scrollList):
        sortHeaders.CreateColumns(headers, fixedHeaders)
        currentActive, currentDirection = sortHeaders.GetCurrentActive()
        scroll.sr.headers = sortHeaders.GetCurrentColumns()
        scroll.Load(contentList=scrollList, sortby=currentActive, reversesort=currentDirection)
        scroll.HideLoading()

    def LoadRolesScroll(self):
        headers = self.GetRoleHeaders()
        self.LoadScroll(self.roleScroll, self.rolesSortHeaders, headers, self.GetFixedColumns(headers), self.GetRolesScrollList())

    def LoadAccessScroll(self):
        self.accessScroll.ShowLoading()
        blue.synchro.Yield()
        headers = self.GetAccessRoleHeaders()
        self.LoadScroll(self.accessScroll, self.accessSortHeaders, headers, self.GetFixedAccessHeaders(headers), self.GetAccessScrollList())

    def LoadTitlesScroll(self):
        headers = self.GetTitleHeaders()
        self.LoadScroll(self.titlesScroll, self.titlesSortHeaders, headers, self.GetFixedColumns(headers), self.GetTitlesScrollList())

    def GetFixedColumns(self, headers):
        fixedHeaders = {GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'): NAME_COL_WIDTH,
         GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase'): BASE_COL_WIDTH}
        for header in headers[2:]:
            fixedHeaders[header] = CHECKBOX_COL_WIDTH

        return fixedHeaders

    def GetTitleHeaders(self):
        header = [GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'), GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase')]
        for title in sorted(self.titles.itervalues(), key=lambda x: x.titleID):
            header.append(title.titleName)

        return header

    def GetAccessRoleHeaders(self):
        header = [GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'), GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase'), GetByLabel('UI/Corporations/RoleManagement/Type')]
        for divisionID in xrange(1, 8):
            header.append(self.divisions[divisionID])

        return header

    def GetFixedAccessHeaders(self, headers):
        fixedHeaders = {GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'): NAME_COL_WIDTH,
         GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase'): BASE_COL_WIDTH,
         GetByLabel('UI/Corporations/RoleManagement/Type'): 50}
        for header in headers[3:]:
            fixedHeaders[header] = ACCESS_COL_WIDTH

        return fixedHeaders

    def GetRoleHeaders(self):
        header = [GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'), GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase')]
        for column in self.roleGroupings[self.GetSelectedState()].columns:
            columnName, subColumns = column
            colName = ReplaceStringWithTags(columnName)
            header.append(colName)

        return header

    def ChangeState(self, selectedState):
        selectedBtn = self.roleGroupsBtns.GetSelected()
        isSearchedOrClearedOrBrowsed = self.isSearched or self.isCleared or self.isBrowsed
        if self.lastClickedBtn == selectedBtn and not isSearchedOrClearedOrBrowsed:
            return
        self.lastClickedBtn = selectedBtn
        if len(self.GetNodesToUpdate()):
            if eve.Message('CrpMembersSaveChanges', {}, uiconst.YESNO) == uiconst.ID_YES:
                self.SaveChanges()
            else:
                for node in self.GetNodesToUpdate():
                    self.ClearRoleChanges(node)

        settings.user.ui.Set('selectedRoleGroupState', selectedState)
        self.isCleared = False
        self.isSearched = False
        self.isBrowsed = False
        uthread.new(self.UpdateScroll, selectedState)

    def GetBaseOptions(self):
        offices = self.corpSvc.GetMyCorporationsOffices()
        offices.Fetch(0, len(offices))
        bases = [('-', None)]
        if offices:
            for office in offices:
                bases.append((cfg.evelocations.Get(office.stationID).locationName, office.stationID))

        return bases

    def UpdateScroll(self, selectedState):
        if selectedState == ACCESS:
            self.roleScroll.display = False
            self.titlesScroll.display = False
            self.accessScroll.display = True
            self.LoadAccessScroll()
        elif selectedState == GROUPS:
            self.roleScroll.display = False
            self.accessScroll.display = False
            self.titlesScroll.display = True
            self.LoadTitlesScroll()
        else:
            self.accessScroll.display = False
            self.titlesScroll.display = False
            self.roleScroll.display = True
            self.LoadRolesScroll()

    def GetScrollList(self, decoClass, sortFunction, roleGroup = None, titles = None, divisionNames = None):
        scrollList = []
        for member in self.membersToShow:
            scrollList.append(Bunch(decoClass=decoClass, member=member, charID=member.characterID, corp=self.corp, label=cfg.eveowners.Get(member.characterID).ownerName, roleGroup=roleGroup, GetSortValue=sortFunction, roleGroupings=self.roleGroupings, myBaseID=self.myBaseID, myGrantableRoles=self.myGrantableRoles, titles=titles, divisionNames=divisionNames, bases=self.bases))
            blue.pyos.BeNice()
            if self.destroyed:
                return scrollList

        return scrollList

    def GetHeaderSortValue(self, node, columnID, sortDirection):
        sortValue = (0, None)
        if sortDirection:
            sortValue = (1000, None)
        node.Set('sort_%s' % columnID, sortValue)
        return self.GetSortValue(node, columnID, sortDirection)

    def GetAccessSortValue(self, node, columnID, sortDirection):
        self.SetNameAndBaseSorting(node)
        if node.Get('sort_%s' % columnID, None) is None:
            roleGrouping = self.roleGroupings
            totalValue = 0
            for divisionID in xrange(4, 10):
                roleGroup = roleGrouping[divisionID]
                rolesAppliesTo = getattr(node.member, roleGroup.appliesTo)
                grantableRolesAppliesTo = getattr(node.member, roleGroup.appliesToGrantable)
                if self.CheckIfDirectorOrCEO(node, node.member.roles):
                    rolesAppliesTo |= roleGroup.roleMask
                    grantableRolesAppliesTo |= roleGroup.roleMask
                for columnName, subColumns in roleGroup.columns:
                    if columnName.replace(' ', '') != StripTags(columnID).replace(' ', ''):
                        continue
                    for _, role in subColumns:
                        checkValue = GetCheckStateForRole(rolesAppliesTo, grantableRolesAppliesTo, role)
                        totalValue += checkValue

            node.Set('sort_%s' % columnID, (0, totalValue))
        return self.GetSortValue(node, columnID, sortDirection)

    def GetTitlesSortValue(self, node, columnID, sortDirection):
        self.SetNameAndBaseSorting(node)
        if node.Get('sort_%s' % columnID, None) is None:
            for title in sorted(self.titles.itervalues(), key=lambda x: x.titleID):
                isChecked = node.member.titleMask & title.titleID == title.titleID
                node.Set('sort_%s' % title.titleName, (0, isChecked))

        return self.GetSortValue(node, columnID, sortDirection)

    def GetRolesSortValue(self, node, columnID, sortDirection):
        self.SetNameAndBaseSorting(node)
        if node.Get('sort_%s' % columnID, None) is None:
            roles = getattr(node.member, node.roleGroup.appliesTo)
            grantableRoles = getattr(node.member, node.roleGroup.appliesToGrantable)
            if self.CheckIfDirectorOrCEO(node, roles):
                roles |= node.roleGroup.roleMask
                grantableRoles |= node.roleGroup.roleMask
            for columnName, subColumns in node.roleGroup.columns:
                for subColumnName, role in subColumns:
                    if columnName.replace(' ', '') == StripTags(columnID).replace(' ', ''):
                        checkValue = GetCheckStateForRole(roles, grantableRoles, role)
                        node.Set('sort_%s' % columnID, (0, checkValue))

        return self.GetSortValue(node, columnID, sortDirection)

    def CheckIfDirectorOrCEO(self, node, roles):
        isCEO = node.member.characterID == node.corp.ceoID
        isDirector = roles & const.corpRoleDirector == const.corpRoleDirector
        return isDirector or isCEO

    def GetSortValue(self, node, columnID, sortDirection):
        return node.Get('sort_%s' % columnID, (0, 0))

    def SetNameAndBaseSorting(self, node):
        node.Set('sort_%s' % GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'), (0, node.charLabel))
        if node.member and node.member.baseID:
            locationName = cfg.evelocations.Get(node.member.baseID).locationName
        else:
            locationName = ''
        node.Set('sort_%s' % GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase'), (0, locationName))

    def GetTitlesScrollList(self):
        titles = self.corpSvc.GetTitles()
        return self.GetScrollList(TitleEntry, self.GetTitlesSortValue, titles=titles)

    def GetRolesScrollList(self):
        roleGroup = self.roleGroupings[self.GetSelectedState()]
        return self.GetScrollList(RoleEntry, self.GetRolesSortValue, roleGroup)

    def GetAccessScrollList(self):
        divisionNames = self.corpSvc.GetDivisionNames()
        scrollList = [Bunch(decoClass=RoleHeaderEntry, member=None, GetSortValue=self.GetHeaderSortValue)]
        scrollList.extend(self.GetScrollList(RoleAccessEntry, self.GetAccessSortValue, divisionNames=divisionNames))
        return scrollList

    def HaveRolesChanged(self, node):
        if node.rec.roles != node.rec.oldRoles:
            return True
        if node.rec.grantableRoles != node.rec.oldGrantableRoles:
            return True
        if node.rec.rolesAtHQ != node.rec.oldRolesAtHQ:
            return True
        if node.rec.grantableRolesAtHQ != node.rec.oldGrantableRolesAtHQ:
            return True
        if node.rec.rolesAtBase != node.rec.oldRolesAtBase:
            return True
        if node.rec.grantableRolesAtBase != node.rec.oldGrantableRolesAtBase:
            return True
        if node.rec.rolesAtOther != node.rec.oldRolesAtOther:
            return True
        if node.rec.grantableRolesAtOther != node.rec.oldGrantableRolesAtOther:
            return True
        if node.rec.baseID != node.rec.oldBaseID:
            return True
        if node.rec.titleMask != node.rec.oldTitleMask:
            return True
        return False

    def GetNodesToUpdate(self):
        nodesToUpdate = []
        try:
            sm.GetService('loading').Cycle(GetByLabel('UI/Common/PreparingToUpdate'))
            nodesToUpdate.extend(self.GetNodesList(self.accessScroll.GetNodes()))
            nodesToUpdate.extend(self.GetNodesList(self.roleScroll.GetNodes()))
            nodesToUpdate.extend(self.GetNodesList(self.titlesScroll.GetNodes()))
        finally:
            sm.GetService('loading').StopCycle()

        return nodesToUpdate

    def GetNodesList(self, nodesList):
        nodesToUpdate = []
        for node in nodesList:
            if not node or not node.rec:
                continue
            if self.HaveRolesChanged(node):
                nodesToUpdate.append(node)

        return nodesToUpdate

    def _CreateRowsToUpdate(self, node):
        entry = node.rec
        characterID = entry.characterID
        roles = entry.roles
        grantableRoles = entry.grantableRoles
        rolesAtHQ = entry.rolesAtHQ
        grantableRolesAtHQ = entry.grantableRolesAtHQ
        rolesAtBase = entry.rolesAtBase
        grantableRolesAtBase = entry.grantableRolesAtBase
        rolesAtOther = entry.rolesAtOther
        grantableRolesAtOther = entry.grantableRolesAtOther
        baseID = entry.baseID
        titleMask = entry.titleMask
        if entry.titleMask == entry.oldTitleMask:
            titleMask = None
        if roles & const.corpRoleDirector == const.corpRoleDirector:
            roles = const.corpRoleDirector
            grantableRoles = 0
            rolesAtHQ = 0
            grantableRolesAtHQ = 0
            rolesAtBase = 0
            grantableRolesAtBase = 0
            rolesAtOther = 0
            grantableRolesAtOther = 0
        row = [characterID,
         None,
         None,
         None,
         roles,
         grantableRoles,
         rolesAtHQ,
         grantableRolesAtHQ,
         rolesAtBase,
         grantableRolesAtBase,
         rolesAtOther,
         grantableRolesAtOther,
         baseID,
         titleMask]
        return row

    def ClearRoleChanges(self, node):
        node.rec.roles = node.rec.oldRoles
        node.rec.grantableRoles = node.rec.oldGrantableRoles
        node.rec.rolesAtHQ = node.rec.oldRolesAtHQ
        node.rec.grantableRolesAtHQ = node.rec.oldGrantableRolesAtHQ
        node.rec.rolesAtBase = node.rec.oldRolesAtBase
        node.rec.grantableRolesAtBase = node.rec.oldGrantableRolesAtBase
        node.rec.rolesAtOther = node.rec.oldRolesAtOther
        node.rec.grantableRolesAtOther = node.rec.oldGrantableRolesAtOther
        node.rec.baseID = node.rec.oldBaseID
        node.rec.titleMask = node.rec.oldTitleMask

    def UpdateOldRolesForNode(self, node):
        node.rec.oldRoles = node.rec.roles
        node.rec.oldGrantableRoles = node.rec.grantableRoles
        node.rec.oldRolesAtHQ = node.rec.rolesAtHQ
        node.rec.oldGrantableRolesAtHQ = node.rec.grantableRolesAtHQ
        node.rec.oldRolesAtBase = node.rec.rolesAtBase
        node.rec.oldGrantableRolesAtBase = node.rec.grantableRolesAtBase
        node.rec.oldRolesAtOther = node.rec.rolesAtOther
        node.rec.oldGrantableRolesAtOther = node.rec.grantableRolesAtOther
        node.rec.oldBaseID = node.rec.baseID
        node.rec.oldTitleMask = node.rec.titleMask

    def SaveChanges(self, *args):
        nodesToUpdate = self.GetNodesToUpdate()
        nCount = len(nodesToUpdate)
        if nCount == 0:
            return
        try:
            sm.GetService('loading').ProgressWnd(GetByLabel('UI/Common/Updating'), '', 0, nCount)
            blue.pyos.synchro.Yield()
            rows = None
            myRow = None
            for node in nodesToUpdate:
                row = self._CreateRowsToUpdate(node)
                if node.rec.characterID == eve.session.charid:
                    if myRow is None:
                        myRow = Rowset(self.GetRowHeader())
                    myRow.append(row)
                else:
                    if rows is None:
                        rows = Rowset(self.GetRowHeader())
                    rows.append(row)

            if rows is not None:
                self.corpSvc.UpdateMembers(rows)
                sm.ScatterEvent('OnRoleEdit', rows)
            if myRow is not None:
                sm.GetService('sessionMgr').PerformSessionChange('corp.UpdateMembers', self.corpSvc.UpdateMembers, myRow)
        finally:
            if nCount:
                for node in nodesToUpdate:
                    self.UpdateOldRolesForNode(node)

                sm.GetService('loading').ProgressWnd(GetByLabel('UI/Common/Updated'), '', nCount - 1, nCount)
                blue.pyos.synchro.SleepWallclock(500)
                sm.GetService('loading').ProgressWnd(GetByLabel('UI/Common/Updated'), '', nCount, nCount)
                blue.pyos.synchro.Yield()

    def GetRowHeader(self):
        return ['characterID',
         'title',
         'divisionID',
         'squadronID',
         'roles',
         'grantableRoles',
         'rolesAtHQ',
         'grantableRolesAtHQ',
         'rolesAtBase',
         'grantableRolesAtBase',
         'rolesAtOther',
         'grantableRolesAtOther',
         'baseID',
         'titleMask']

    def OnTabDeselect(self):
        if not self.sr.Get('inited', 0):
            return
        if len(self.GetNodesToUpdate()):
            if eve.Message('CrpMembersSaveChanges', {}, uiconst.YESNO) == uiconst.ID_YES:
                self.SaveChanges()
