#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\corporation\corp_ui_member_roleentry.py
import weakref
from carbon.common.script.sys.row import Row
from carbonui.primitives.container import Container
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.sprite import Sprite
import corputil
from carbonui.primitives.transform import Transform
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
import carbonui.const as uiconst
from eve.client.script.ui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveLabelMedium
from eve.client.script.ui.control.themeColored import LineThemeColored, FillThemeColored
from eve.client.script.ui.control.tricheckbox import TriCheckbox
from eve.client.script.ui.services.corporation.corp_util import CB_OFFSET, DIV_HANGAR, ACCESS_TYPES_INFO, ROLES_AT_HQ, ROLES, ROLES_AT_BASE, ROLES_AT_OTHER, GRANTABLE_ROLES, GRANTABLE_ROLES_AT_HQ, GRANTABLE_ROLES_AT_BASE, GRANTABLE_ROLES_AT_OTHER, GetCheckStateForRole, CHECKBOX_COL_WIDTH, ACCESS_COL_WIDTH, NAME_COL_WIDTH, BASE_COL_WIDTH
from localization import GetByLabel
import math
import uthread
import blue

class RoleHeaderEntry(BaseListEntryCustomColumns):
    default_name = 'RoleHeaderEntry'
    default_height = 18

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.AddColName()
        self.AddColBase()
        self.AddColType()
        for i in xrange(7):
            self.AddColDivision()

    def AddColName(self):
        self.AddColumnContainer(width=NAME_COL_WIDTH)

    def AddColBase(self):
        self.AddColumnContainer(width=BASE_COL_WIDTH)

    def AddColType(self):
        self.AddColumnContainer(width=50, padRight=0)

    def AddColDivision(self):
        col = self.AddColumnContainer(width=ACCESS_COL_WIDTH, padRight=0)
        col.padTop = 2
        query = self.GetRoleSprite('query', 'res:/UI/Texture/classes/RoleManagement/query.png', GetByLabel('UI/Corporations/RoleManagement/MemberCanView'))
        query.SetParent(col)
        query.left = -20
        take = self.GetRoleSprite('take', 'res:/UI/Texture/classes/RoleManagement/take.png', GetByLabel('UI/Corporations/RoleManagement/MemberCanTake'))
        take.SetParent(col)
        cont = self.GetRoleSprite('container', 'res:/UI/Texture/classes/RoleManagement/container.png', GetByLabel('UI/Corporations/RoleManagement/MemberCanTakeCont'))
        cont.SetParent(col)
        cont.left = 20

    def GetRoleSprite(self, name, texturePath, hintLabel):
        roleSprite = Sprite(name=name, texturePath=texturePath, width=16, height=16, align=uiconst.CENTER, opacity=0.6)
        roleSprite.hint = hintLabel
        return roleSprite


class BaseRoleEntry(BaseListEntryCustomColumns):

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.charID = self.node.member.characterID
        self.member = self.node.member
        self.charLabel = self.node.label
        self.bases = self.node.bases
        self.checkboxes = []
        self.corpSvc = sm.GetService('corp')
        self.roleGroupings = self.node.roleGroupings
        self.corp = self.node.corp
        self.node.rec = self.GetMembersListData()
        self.AddColumnName()
        self.AddColBase()
        self.AddBaseSorting()
        self.myBaseID = self.node.baseID
        if self.myBaseID is None:
            self.myBaseID = self.corpSvc.GetMember(session.charid).baseID
        grantableRoles, grantableRolesAtHQ, grantableRolesAtBase, grantableRolesAtOther = self.node.myGrantableRoles
        self.myGrantableRoles = grantableRoles
        self.myGrantableRolesAtHQ = grantableRolesAtHQ
        self.myGrantableRolesAtBase = grantableRolesAtBase
        self.myGrantableRolesAtOther = grantableRolesAtOther

    def AddColumnName(self):
        col = self.AddColumnContainer(width=NAME_COL_WIDTH)
        col.state = uiconst.UI_NORMAL
        col.hint = self.charLabel
        nameText = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=self.charLabel, info=('showinfo', const.typeCharacterAmarr, self.charID))
        nameLabel = EveLabelMedium(parent=col, text=nameText, align=uiconst.CENTERLEFT, left=6, autoFadeSides=35)
        nameLabel.state = uiconst.UI_NORMAL

    def AddColBase(self):
        col = self.AddColumnContainer(width=BASE_COL_WIDTH)
        defaultSelectedValue = self.member.baseID
        self.baseCombo = Combo(name='myCombo', parent=col, options=self.bases, select=defaultSelectedValue, align=uiconst.CENTERLEFT, callback=self.OnBaseChange, left=4)

    def AddBaseSorting(self):
        if self.member.baseID:
            locationName = cfg.evelocations.Get(self.member.baseID).locationName
        else:
            locationName = None

    def OnBaseChange(self, *args):
        self.node.rec.baseID = self.baseCombo.GetValue()

    def GetCanEditRole(self, checkbox):
        roleID = checkbox.roleID
        isGrantable = 0
        if checkbox.checked == uiconst.FULL_CHECKED:
            isGrantable = 1
        rec = self.node.rec
        viewRoleGroupingID = settings.user.ui.Get('selectedRoleGroupState', 1)
        return corputil.CanEditRole(roleID, isGrantable, rec.isCEO, rec.isDirector, rec.IAmCEO, viewRoleGroupingID, self.myBaseID, rec.baseID, self.myGrantableRoles, self.myGrantableRolesAtHQ, self.myGrantableRolesAtBase, self.myGrantableRolesAtOther, self.roleGroupings)

    def LoadCBTooltip(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddIconLabel(icon='res:/UI/Texture/classes/RoleManagement/checkNone.png', label=GetByLabel('UI/Corporations/RoleManagement/None'), iconSize=16)
        tooltipPanel.AddIconLabel(icon='res:/UI/Texture/classes/RoleManagement/checkRoles.png', label=GetByLabel('UI/Corporations/RoleManagement/Role'), iconSize=16)
        tooltipPanel.AddIconLabel(icon='res:/UI/Texture/classes/RoleManagement/checkGrantable.png', label=GetByLabel('UI/Corporations/RoleManagement/GrantableRole'), iconSize=16)

    def OnCbClick(self, roleID, roleGroup, checkValue):
        if checkValue == uiconst.FULL_CHECKED:
            setattr(self.node.rec, roleGroup.appliesTo, getattr(self.node.rec, roleGroup.appliesTo) | roleID)
            setattr(self.node.rec, roleGroup.appliesToGrantable, getattr(self.node.rec, roleGroup.appliesToGrantable) | roleID)
        elif checkValue == uiconst.HALF_CHECKED:
            setattr(self.node.rec, roleGroup.appliesToGrantable, getattr(self.node.rec, roleGroup.appliesToGrantable) & ~roleID)
            setattr(self.node.rec, roleGroup.appliesTo, getattr(self.node.rec, roleGroup.appliesTo) | roleID)
        else:
            setattr(self.node.rec, roleGroup.appliesToGrantable, getattr(self.node.rec, roleGroup.appliesToGrantable) & ~roleID)
            setattr(self.node.rec, roleGroup.appliesTo, getattr(self.node.rec, roleGroup.appliesTo) & ~roleID)
        if roleID == const.corpRoleDirector:
            if checkValue:
                self.node.rec.isDirector = self.node.rec.roles & const.corpRoleDirector
                self.node.rec.grantableRoles = self.node.rec.grantableRoles & ~const.corpRoleDirector
                isChecked = uiconst.FULL_CHECKED
                for roleGroup in self.roleGroupings.itervalues():
                    appliesTo = roleGroup.appliesTo
                    appliesToGrantable = roleGroup.appliesToGrantable
                    setattr(self.node.rec, appliesTo, getattr(self.node.rec, appliesTo) | roleGroup.roleMask)
                    setattr(self.node.rec, appliesToGrantable, getattr(self.node.rec, appliesToGrantable) | roleGroup.roleMask)

            else:
                self.node.rec.roles = 0
                self.node.rec.grantableRoles = 0
                self.node.rec.rolesAtHQ = 0
                self.node.rec.grantableRolesAtHQ = 0
                self.node.rec.rolesAtBase = 0
                self.node.rec.grantableRolesAtBase = 0
                self.node.rec.rolesAtOther = 0
                self.node.rec.grantableRolesAtOther = 0
                isChecked = uiconst.NOT_CHECKED
            for checkbox in self.checkboxes:
                if not checkbox.roleID == const.corpRoleDirector:
                    checkbox.SetChecked(isChecked)
                    if checkValue:
                        checkbox.Disable()
                    else:
                        checkbox.Enable()

    def GetRoleHeader(self):
        return ['characterID',
         'name',
         'roles',
         'oldRoles',
         'grantableRoles',
         'oldGrantableRoles',
         'rolesAtHQ',
         'oldRolesAtHQ',
         'grantableRolesAtHQ',
         'oldGrantableRolesAtHQ',
         'rolesAtBase',
         'oldRolesAtBase',
         'grantableRolesAtBase',
         'oldGrantableRolesAtBase',
         'rolesAtOther',
         'oldRolesAtOther',
         'grantableRolesAtOther',
         'oldGrantableRolesAtOther',
         'baseID',
         'oldBaseID',
         'titleMask',
         'oldTitleMask',
         'isCEO',
         'isDirector',
         'IAmCEO',
         'IAmDirector']

    def GetMembersListData(self):
        corporation = self.corpSvc.GetCorporation()
        IAmCEO = corporation.ceoID == session.charid
        IAmDirector = session.corprole & const.corpRoleDirector and not IAmCEO
        member = self.member
        roles = member.roles
        grantableRoles = member.grantableRoles
        rolesAtHQ = member.rolesAtHQ
        grantableRolesAtHQ = member.grantableRolesAtHQ
        rolesAtBase = member.rolesAtBase
        grantableRolesAtBase = member.grantableRolesAtBase
        rolesAtOther = member.rolesAtOther
        grantableRolesAtOther = member.grantableRolesAtOther
        baseID = member.baseID
        titleMask = member.titleMask
        memberIsCEO = member.characterID == corporation.ceoID
        memberIsDirector = roles & const.corpRoleDirector == const.corpRoleDirector
        if memberIsCEO or memberIsDirector:
            roles = 0
            for roleGrouping in self.roleGroupings.itervalues():
                appliesTo = roleGrouping.appliesTo
                appliesToGrantable = roleGrouping.appliesToGrantable
                if appliesTo == ROLES:
                    roles |= roleGrouping.roleMask
                elif appliesTo == ROLES_AT_HQ:
                    rolesAtHQ |= roleGrouping.roleMask
                elif appliesTo == ROLES_AT_BASE:
                    rolesAtBase |= roleGrouping.roleMask
                elif appliesTo == ROLES_AT_OTHER:
                    rolesAtOther |= roleGrouping.roleMask
                if appliesToGrantable == GRANTABLE_ROLES:
                    grantableRoles |= roleGrouping.roleMask
                elif appliesToGrantable == GRANTABLE_ROLES_AT_HQ:
                    grantableRolesAtHQ |= roleGrouping.roleMask
                elif appliesToGrantable == GRANTABLE_ROLES_AT_BASE:
                    grantableRolesAtBase |= roleGrouping.roleMask
                elif appliesToGrantable == GRANTABLE_ROLES_AT_OTHER:
                    grantableRolesAtOther |= roleGrouping.roleMask

            if memberIsDirector:
                grantableRoles = grantableRoles & ~const.corpRoleDirector
        oldBaseID = baseID
        if oldBaseID is not None:
            oldBaseID = long(baseID)
        line = [member.characterID,
         cfg.eveowners.Get(member.characterID).ownerName,
         roles,
         long(roles),
         grantableRoles,
         long(grantableRoles),
         rolesAtHQ,
         long(rolesAtHQ),
         grantableRolesAtHQ,
         long(grantableRolesAtHQ),
         rolesAtBase,
         long(rolesAtBase),
         grantableRolesAtBase,
         long(grantableRolesAtBase),
         rolesAtOther,
         long(rolesAtOther),
         grantableRolesAtOther,
         long(grantableRolesAtOther),
         baseID,
         oldBaseID,
         titleMask,
         int(titleMask),
         memberIsCEO,
         memberIsDirector,
         IAmCEO,
         IAmDirector]
        return Row(self.GetRoleHeader(), line)

    def GetMenu(self, *args):
        self.OnClick()
        return sm.GetService('menu').CharacterMenu(self.node.charID)


class TitleEntry(BaseRoleEntry):
    default_name = 'TitleEntry'
    default_height = 32

    def ApplyAttributes(self, attributes):
        BaseRoleEntry.ApplyAttributes(self, attributes)
        for title in sorted(self.node.titles.itervalues(), key=lambda x: x.titleID):
            self.AddColCheckBox(title)

    def AddColCheckBox(self, title):
        col = self.AddColumnContainer(width=CHECKBOX_COL_WIDTH, padRight=0)
        checkbox = Checkbox(parent=col, align=uiconst.CENTER)
        checkbox.LoadTooltipPanel = self.LoadCBTooltip
        self.SetCbAttributes(checkbox, title)

    def SetCbAttributes(self, checkbox, title):
        isChecked = self.member.titleMask & title.titleID == title.titleID
        checkbox.SetChecked(isChecked)
        checkbox.titleID = title.titleID
        checkbox.OnChange = self.OnCheckboxClick

    def OnCheckboxClick(self, checkbox, *args):
        if checkbox.checked:
            self.node.rec.titleMask |= checkbox.titleID
        else:
            self.node.rec.titleMask &= ~checkbox.titleID


class RoleEntry(BaseRoleEntry):
    default_name = 'RoleEntry'
    default_height = 32

    def ApplyAttributes(self, attributes):
        BaseRoleEntry.ApplyAttributes(self, attributes)
        self.roleGroup = self.node.roleGroup
        self.checkboxes = []
        self.checkValue = uiconst.NOT_CHECKED
        for columnName, subColumns in self.roleGroup.columns:
            self.AddColCheckBox(columnName, subColumns)

    def IsCEO(self):
        return self.member.characterID == self.corp.ceoID

    def IsDirector(self, roles):
        return roles & const.corpRoleDirector == const.corpRoleDirector

    def IsDirectorOrCEO(self, roles):
        isCEO = self.IsCEO()
        isDirector = self.IsDirector(roles)
        return isCEO or isDirector

    def UpdateCheckValue(self, grantableRoles, role, roles):
        checkValue = GetCheckStateForRole(roles, grantableRoles, role)
        self.checkValue = checkValue

    def UpdateCheckboxWithRoles(self, checkbox, grantableRoles, role, roles):
        self.UpdateCheckValue(grantableRoles, role, roles)
        checkbox.SetChecked(self.checkValue)

    def SetCheckboxAttributes(self, checkbox, subColumns):
        roles, grantableRoles = self.GetRoles()
        isCEO = self.IsCEO()
        isDirector = self.IsDirector(roles)
        if isDirector or isCEO:
            roles |= self.roleGroup.roleMask
            grantableRoles |= self.roleGroup.roleMask
        for subColumnName, role in subColumns:
            self.UpdateCheckboxWithRoles(checkbox, grantableRoles, role, roles)
            checkbox.roleID = role.roleID

        if not self.GetCanEditRole(checkbox):
            checkbox.Disable()
        checkbox.OnChange = self.OnCheckboxClick

    def AddColCheckBox(self, columnName, subColumns):
        col = self.AddColumnContainer(width=CHECKBOX_COL_WIDTH, padRight=0)
        isDirector = any([ role.roleID == const.corpRoleDirector for subColumnName, role in subColumns ])
        if isDirector:
            checkbox = Checkbox(parent=col, align=uiconst.CENTER, checkedTexture='res:/UI/Texture/Shared/checkboxHalfChecked.png')
        else:
            checkbox = TriCheckbox(parent=col, align=uiconst.CENTER, pos=(-2, 0, 16, 16))
        checkbox.LoadTooltipPanel = self.LoadCBTooltip
        self.SetCheckboxAttributes(checkbox, subColumns)
        self.checkboxes.append(checkbox)

    def OnCheckboxClick(self, checkbox, *args):
        roleID = checkbox.roleID
        checkValue = checkbox.checked
        if roleID == const.corpRoleDirector and checkValue:
            checkValue = uiconst.HALF_CHECKED
        BaseRoleEntry.OnCbClick(self, roleID, self.roleGroup, checkValue)

    def GetRoles(self):
        roles = getattr(self.member, self.roleGroup.appliesTo)
        grantableRoles = getattr(self.member, self.roleGroup.appliesToGrantable)
        return (roles, grantableRoles)

    @staticmethod
    def GetFixedColumns():
        fixedColumns = {GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase'): 132}
        return fixedColumns


class RoleAccessEntry(BaseRoleEntry):
    default_name = 'RoleAccessEntry'
    default_height = 68

    def ApplyAttributes(self, attributes):
        BaseRoleEntry.ApplyAttributes(self, attributes)
        divisionNames = self.node.divisionNames
        self.AddColType()
        for divisionID in xrange(1, 8):
            self.AddColDivision(divisionName=divisionNames[divisionID])

    def AddColType(self):
        col = self.AddColumnContainer(width=50, padRight=0)
        EveLabelSmall(parent=col, text=GetByLabel('UI/Corporations/RoleManagement/HQ'), top=8, left=4)
        EveLabelSmall(parent=col, text=GetByLabel('UI/Corporations/RoleManagement/Base'), top=28, left=4)
        EveLabelSmall(parent=col, text=GetByLabel('UI/Corporations/RoleManagement/Other'), top=48, left=4)

    def AddColDivision(self, divisionName):
        col = self.AddColumnContainer(width=ACCESS_COL_WIDTH, padRight=0)
        self.roleBoxes = RoleBoxes(parent=col, align=uiconst.CENTER, member=self.member, divisionName=divisionName, corp=self.corp, parentFunc=self.OnCbClick, roleGroupings=self.roleGroupings, myBaseID=self.myBaseID, myGrantableRoles=self.myGrantableRoles, myGrantableRolesAtHQ=self.myGrantableRolesAtHQ, myGrantableRolesAtBase=self.myGrantableRolesAtBase, myGrantableRolesAtOther=self.myGrantableRolesAtOther)

    def OnCbClick(self, roleID, roleGroup, checkValue):
        BaseRoleEntry.OnCbClick(self, roleID, roleGroup, checkValue)

    def GetMenu(self, *args):
        self.OnClick()
        return sm.GetService('menu').CharacterMenu(self.node.charID)


class RoleBoxes(Container):
    __guid__ = 'uicls.RoleBoxes'
    default_height = 60
    default_width = 60

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.member = attributes.member
        self.divisionName = attributes.divisionName
        self.corp = attributes.corp
        self.parentFunc = attributes.parentFunc
        self.roleGroupings = attributes.roleGroupings
        self.myGrantableRoles = attributes.myGrantableRoles
        self.myGrantableRolesAtHQ = attributes.myGrantableRolesAtHQ
        self.myGrantableRolesAtBase = attributes.myGrantableRolesAtBase
        self.myGrantableRolesAtOther = attributes.myGrantableRolesAtOther
        self.myBaseID = attributes.myBaseID
        self.checkBoxes = []
        self.DrawCheckboxes()
        self.GetCheckedRoles()

    def DrawCheckboxes(self):
        for y in xrange(3):
            for x in xrange(3):
                checkbox = TriCheckbox(parent=self, checked=False, callback=self.OnCbClick, align=uiconst.TOPLEFT, pos=(x * 20 + 2,
                 y * 20 + 2,
                 16,
                 16))
                checkbox.LoadTooltipPanel = self.LoadCBTooltip
                self.checkBoxes.append(checkbox)

    def OnCbClick(self, checkbox, *args):
        roleID = checkbox.roleID
        roleGroup = checkbox.roleGroup
        isChecked = checkbox.checked
        self.parentFunc(roleID, roleGroup, isChecked)

    def GetCheckedRoles(self):
        divisions = self.roleGroupings
        IAmCEO = self.corp.ceoID == session.charid
        roles = self.member.roles
        isDirectorOrCEO = self.IsDirectorOrCEO(roles)
        totalValue = 0
        for divisionID in xrange(4, 10):
            roleGroup = divisions[divisionID]
            rolesAppliesTo = getattr(self.member, roleGroup.appliesTo)
            grantableRolesAppliesTo = getattr(self.member, roleGroup.appliesToGrantable)
            if isDirectorOrCEO:
                rolesAppliesTo |= roleGroup.roleMask
                grantableRolesAppliesTo |= roleGroup.roleMask
            for columnName, subColumns in roleGroup.columns:
                if columnName != self.divisionName:
                    continue
                for cbNo, (subColumnName, role) in enumerate(subColumns):
                    cbPlacement = CB_OFFSET.get(divisionID)
                    if divisionID in DIV_HANGAR:
                        cbPlacement += cbNo
                    isRolesChecked = rolesAppliesTo & role.roleID == role.roleID
                    isGrantableChecked = grantableRolesAppliesTo & role.roleID == role.roleID
                    checkValue = uiconst.NOT_CHECKED
                    if isGrantableChecked:
                        checkValue = uiconst.FULL_CHECKED
                    elif isRolesChecked:
                        checkValue = uiconst.HALF_CHECKED
                    totalValue += checkValue
                    self.checkBoxes[cbPlacement].roleID = role.roleID
                    self.checkBoxes[cbPlacement].roleGroup = roleGroup
                    self.checkBoxes[cbPlacement].SetChecked(checkValue)
                    isCEO = self.IsCEO()
                    isDirector = self.IsDirector(roles)
                    if not self.GetCanEditRole(role.roleID, IAmCEO, isCEO, isDirector, checkValue, roleGroup.roleGroupID):
                        self.checkBoxes[cbPlacement].Disable()

    def GetCanEditRole(self, roleID, IAmCEO, isCEO, isDirector, checkValue, roleGroupID):
        isGrantable = 0
        if checkValue == uiconst.FULL_CHECKED:
            isGrantable = 1
        return corputil.CanEditRole(roleID, isGrantable, isCEO, isDirector, IAmCEO, roleGroupID, self.myBaseID, self.member.baseID, self.myGrantableRoles, self.myGrantableRolesAtHQ, self.myGrantableRolesAtBase, self.myGrantableRolesAtOther, self.roleGroupings)

    def IsDirector(self, roles):
        return roles & const.corpRoleDirector == const.corpRoleDirector

    def IsCEO(self):
        return self.member.characterID == self.corp.ceoID

    def IsDirectorOrCEO(self, roles):
        isCEO = self.IsCEO()
        isDirector = self.IsDirector(roles)
        return isCEO or isDirector

    def LoadCBTooltip(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddIconLabel(icon='res:/UI/Texture/classes/RoleManagement/checkNone.png', label=GetByLabel('UI/Corporations/RoleManagement/None'), iconSize=16)
        tooltipPanel.AddIconLabel(icon='res:/UI/Texture/classes/RoleManagement/checkRoles.png', label=GetByLabel('UI/Corporations/RoleManagement/Role'), iconSize=16)
        tooltipPanel.AddIconLabel(icon='res:/UI/Texture/classes/RoleManagement/checkGrantable.png', label=GetByLabel('UI/Corporations/RoleManagement/GrantableRole'), iconSize=16)


class VerticalLabel(Transform):

    def ApplyAttributes(self, attributes):
        Transform.ApplyAttributes(self, attributes)
        labelText = attributes.text
        self.label = EveLabelSmall(text=labelText, parent=self, maxLines=2, wrapWidth=100)
        self.width = self.label.width
        self.height = self.label.height
        self.rotation = math.pi * 0.5
        self.rotationCenter = (0.0, 0.0)


class VerticalScrollHeader(Container):
    default_name = 'VerticalScrollHeader'
    default_align = uiconst.TOTOP
    default_height = 60
    default_state = uiconst.UI_PICKCHILDREN
    default_clipChildren = True
    default_padBottom = 0
    LEFTCENTERED_COLUMNIDS = [GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'), GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase'), GetByLabel('UI/Corporations/RoleManagement/Type')]

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        LineThemeColored(parent=self, align=uiconst.TOBOTTOM, opacity=uiconst.OPACITY_FRAME)
        self.headerContainer = Container(parent=self)
        self.settingsID = attributes.settingsID
        self.columnIDs = []
        self.fixedColumns = None
        self.defaultColumn = None
        self.scroll = weakref.ref(attributes.scroll)

    def SetDefaultColumn(self, columnID, direction):
        self.defaultColumn = (columnID, direction)

    def CreateColumns(self, columns, fixedColumns = None):
        self.headerContainer.Flush()
        self.columnIDs = columns
        if columns:
            for columnID in columns:
                header = Container(parent=self.headerContainer, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
                header.OnClick = (self.ClickHeader, header)
                header.columnID = columnID
                header.sortTriangle = None
                headerDivider = LineThemeColored(parent=header, align=uiconst.TORIGHT, opacity=uiconst.OPACITY_FRAME)
                entry = VerticalLabel(parent=header, text=columnID, align=uiconst.BOTTOMLEFT, state=uiconst.UI_DISABLED)
                entry.top = -entry.label.textheight + const.defaultPadding
                header.label = entry.label
                header.hint = columnID
                header.width = fixedColumns[columnID]
                if columnID in self.LEFTCENTERED_COLUMNIDS:
                    entry.left = 4
                else:
                    entry.left = (header.width - entry.label.textheight) / 2
                header.fill = FillThemeColored(parent=header, colorType=uiconst.COLORTYPE_UIHILIGHT, padLeft=-1, padRight=-1, opacity=0.75)
                header.label.SetRightAlphaFade(fadeEnd=self.height - 10, maxFadeWidth=20)

            self.UpdateActiveState()

    def UpdateActiveState(self):
        currentActive, currentDirection = self.GetCurrentActive()
        for each in self.headerContainer.children:
            if hasattr(each, 'columnID'):
                if each.columnID == currentActive:
                    if not each.sortTriangle:
                        each.sortTriangle = Icon(align=uiconst.CENTERRIGHT, pos=(3, -1, 16, 16), parent=each, name='directionIcon', idx=0)
                    if currentDirection:
                        each.sortTriangle.LoadIcon('ui_1_16_15')
                    else:
                        each.sortTriangle.LoadIcon('ui_1_16_16')
                    each.sortTriangle.state = uiconst.UI_DISABLED
                    each.fill.Show()
                else:
                    each.fill.Hide()
                    if each.sortTriangle:
                        each.sortTriangle.Hide()

    def GetCurrentColumns(self):
        return self.columnIDs

    def GetCurrentActive(self):
        allHeaderSettings = settings.char.ui.Get('SortHeadersSettings', {})
        currentActive, currentDirection = None, True
        if self.settingsID in allHeaderSettings:
            currentActive, currentDirection = allHeaderSettings[self.settingsID]
            if currentActive not in self.columnIDs:
                return (None, True)
            return (currentActive, currentDirection)
        if self.defaultColumn is not None:
            columnID, direction = self.defaultColumn
            if columnID in self.columnIDs:
                return self.defaultColumn
        if self.columnIDs:
            currentActive, currentDirection = self.columnIDs[0], True
        return (currentActive, currentDirection)

    def SetCurrentActive(self, columnID, doCallback = True):
        currentActive, currentDirection = self.GetCurrentActive()
        if currentActive == columnID:
            sortDirection = not currentDirection
        else:
            sortDirection = currentDirection
        allHeaderSettings = settings.char.ui.Get('SortHeadersSettings', {})
        allHeaderSettings[self.settingsID] = (columnID, sortDirection)
        settings.char.ui.Set('SortHeadersSettings', allHeaderSettings)
        self.UpdateActiveState()

    def ClickHeader(self, header):
        self.SetCurrentActive(header.columnID)
        if self.scroll and self.scroll():
            self.scroll().ChangeSortBy(header.columnID)

    def GetCurrentWidth(self):
        current = settings.char.ui.Get('SortHeadersSizes', {}).get(self.settingsID, {})
        if self.fixedColumns:
            current.update(self.fixedColumns)
        for each in self.headerContainer.children:
            if hasattr(each, 'columnID') and each.columnID not in current:
                current[each.columnID] = each.width

        return current

    def GetColumnWidths(self):
        sizesByID = self.GetCurrentWidth()
        return [ sizesByID[each] for each in self.columnIDs ]

    def ColumnIsFixed(self, columnID):
        return columnID in self.fixedColumns

    def RegisterCurrentSizes(self):
        sizes = {}
        for each in self.headerContainer.children:
            if hasattr(each, 'columnID'):
                sizes[each.columnID] = each.width

        all = settings.char.ui.Get('SortHeadersSizes', {})
        all[self.settingsID] = sizes
        settings.char.ui.Set('SortHeadersSizes', all)
        return sizes
