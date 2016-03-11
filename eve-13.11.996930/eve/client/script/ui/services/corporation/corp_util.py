#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\corporation\corp_util.py
from carbonui.const import NOT_CHECKED, FULL_CHECKED, HALF_CHECKED
import const
VIEW_ROLES = 0
VIEW_GRANTABLE_ROLES = 1
VIEW_TITLES = 2
GROUP_GENERAL_ROLES = 0
GROUP_DIVISIONAL_ACCOUNTING_ROLES = 1
GROUP_DIVISIONAL_HANGAR_ROLES_AT_HQ = 2
GROUP_DIVISIONAL_CONTAINER_ROLES_AT_HQ = 3
GROUP_DIVISIONAL_HANGAR_ROLES_AT_BASE = 4
GROUP_DIVISIONAL_CONTAINER_ROLES_AT_BASE = 5
GROUP_DIVISIONAL_HANGAR_ROLES_AT_OTHER = 6
GROUP_DIVISIONAL_CONTAINER_ROLES_AT_OTHER = 7
RECRUITMENT_GROUP_PRIMARY_LANGUAGE = 10
DIV_HQ_HANGAR = 4
DIV_HQ_CONT = 5
DIV_BASED_HANGAR = 6
DIV_BASED_CONT = 7
DIV_OTHER_HANGAR = 8
DIV_OTHER_CONT = 9
DIV_HANGAR = [DIV_HQ_HANGAR, DIV_BASED_HANGAR, DIV_OTHER_HANGAR]
DIV_CONT = [DIV_HQ_CONT, DIV_BASED_CONT, DIV_OTHER_CONT]
CB_OFFSET = {DIV_HQ_HANGAR: 0,
 DIV_HQ_CONT: 2,
 DIV_BASED_HANGAR: 3,
 DIV_BASED_CONT: 5,
 DIV_OTHER_HANGAR: 6,
 DIV_OTHER_CONT: 8}
hangerAccessQueryHQ = 1
hangerAccessTakeHQ = 2
containerAccessTakeHQ = 3
hangerAccessQueryBase = 4
hangerAccessTakeBase = 5
containerAccessTakeBase = 6
hangerAccessQueryOther = 7
hangerAccessTakeOther = 8
containerAccessTakeOther = 9
ACCESS_TYPES_INFO = {hangerAccessQueryHQ: 'hanger access query HQ',
 hangerAccessTakeHQ: 'hanger access take HQ',
 containerAccessTakeHQ: 'container acccess take HQ',
 hangerAccessQueryBase: 'hanger acces query base',
 hangerAccessTakeBase: 'hanger access take base',
 containerAccessTakeBase: 'container access take base',
 hangerAccessQueryOther: 'hanger access query other',
 hangerAccessTakeOther: 'hanger access take other',
 containerAccessTakeOther: 'container access take other'}
ROLES = 'roles'
ROLES_AT_HQ = 'rolesAtHQ'
ROLES_AT_BASE = 'rolesAtBase'
ROLES_AT_OTHER = 'rolesAtOther'
GRANTABLE_ROLES = 'grantableRoles'
GRANTABLE_ROLES_AT_HQ = 'grantableRolesAtHQ'
GRANTABLE_ROLES_AT_BASE = 'grantableRolesAtBase'
GRANTABLE_ROLES_AT_OTHER = 'grantableRolesAtOther'
NAME_COL_WIDTH = 100
BASE_COL_WIDTH = 100
CHECKBOX_COL_WIDTH = 45
ACCESS_COL_WIDTH = 80

def CanEditRole(roleID, grantable, playerIsCEO, playerIsDirector, IAmCEO, viewRoleGroupingID, myBaseID, playersBaseID, myGrantableRoles, myGrantableRolesAtHQ, myGrantableRolesAtBase, myGrantableRolesAtOther, roleGroupings = None):
    if grantable:
        if roleID == const.corpRoleDirector:
            return 0
        if eve.session.corprole & const.corpRoleDirector != const.corpRoleDirector:
            return 0
        if playerIsCEO:
            return 0
        if playerIsDirector:
            return 0
        return 1
    elif playerIsCEO:
        return 0
    elif playerIsDirector and not IAmCEO:
        return 0
    elif playerIsDirector and roleID & const.corpRoleDirector != const.corpRoleDirector:
        return 0
    else:
        if not roleGroupings:
            roleGroupings = sm.GetService('corp').GetRoleGroupings()
        if not roleGroupings.has_key(viewRoleGroupingID):
            raise RuntimeError('UnknownViewType')
        roleGroup = roleGroupings[viewRoleGroupingID]
        if roleGroup.appliesTo == 'roles':
            if myGrantableRoles & roleID != roleID:
                return 0
        elif roleGroup.appliesTo == 'rolesAtHQ':
            if myGrantableRolesAtHQ & roleID != roleID:
                return 0
        elif roleGroup.appliesTo == 'rolesAtBase':
            if IAmCEO:
                return 1
            if const.corpRoleDirector & eve.session.corprole == const.corpRoleDirector and not playerIsDirector:
                return 1
            if myBaseID != playersBaseID:
                return 0
            if myGrantableRolesAtBase & roleID != roleID:
                return 0
        elif roleGroup.appliesTo == 'rolesAtOther':
            if myGrantableRolesAtOther & roleID != roleID:
                return 0
        return 1


def CanEditBase(playerIsCEO, IAmCEO, IAmDirector):
    if playerIsCEO:
        if IAmCEO:
            return 1
    else:
        if IAmCEO:
            return 1
        if IAmDirector:
            return 1
    return 0


def GetCheckStateForRole(roles, grantableRoles, role):
    isRolesChecked = roles & role.roleID == role.roleID
    isGrantableChecked = grantableRoles & role.roleID == role.roleID
    isDirector = roles & role.roleID == const.corpRoleDirector
    checkValue = NOT_CHECKED
    if isDirector:
        checkValue = HALF_CHECKED
    elif isGrantableChecked:
        checkValue = FULL_CHECKED
    elif isRolesChecked:
        checkValue = HALF_CHECKED
    return checkValue


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('corputil', locals())
exports = {'corputil.CanEditRole': CanEditRole,
 'corputil.CanEditBase': CanEditBase,
 'corputil.GetCheckStateForRole': GetCheckStateForRole}
