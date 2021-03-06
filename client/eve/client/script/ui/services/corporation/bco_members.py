#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\corporation\bco_members.py
import util
import corpObject
import uthread

class PagedCorpMembers(util.PagedCollection):
    __notifyevents__ = ['OnCorporationMemberChanged']

    def __init__(self, totalCount):
        super(PagedCorpMembers, self).__init__()
        self.notify = []
        self.additions = []
        self.totalCount = totalCount
        sm.RegisterNotify(self)
        self.charIdIdx = {}

    def PopulatePage(self, page):
        if not self.page or page > self.page:
            rs = sm.GetService('corp').GetMembersPaged(page)
            self.Add(rs)
        start = self.perPage * (page - 1)
        return self[start:start + self.perPage]

    def GetMember(self, memberID):
        return self.charIdIdx.get(memberID)

    def FetchByKey(self, memberIDs):
        missingKeys = []
        hasKeys = []
        for id in memberIDs:
            if id in self.charIdIdx:
                hasKeys.append(id)
            else:
                missingKeys.append(id)

        rows = sm.GetService('corp').GetMembersByIds(missingKeys)
        for member in rows:
            self.charIdIdx[member.characterID] = member

        for id in hasKeys:
            rows.append(self.charIdIdx.get(id))

        return rows

    def GetByKey(self, memberID):
        return self.charIdIdx.get(memberID)

    def Add(self, resultSet):
        super(PagedCorpMembers, self).Add(resultSet)
        for character in resultSet:
            self.charIdIdx[character.characterID] = character

    def OnCorporationMemberChanged(self, corporationID, memberID, changes):
        member = self.GetMember(memberID)
        if 'corporationID' in changes:
            oldCorpID, newCorpID = changes['corporationID']
            if oldCorpID == eve.session.corpid:
                if not member:
                    self.totalCount -= 1
                    return
                try:
                    self.remove(member)
                except ValueError:
                    pass

            elif newCorpID == eve.session.corpid:
                if self.page == self.PageCount():
                    newMember = sm.GetService('corp').GetMembersByIds([memberID])[0]
                    if newMember.characterID not in (i.characterID for i in self.collection):
                        self.append(newMember)
                else:
                    self.totalCount += 1
        elif member:
            for key, values in changes.iteritems():
                if hasattr(member, key):
                    oldValue, newValue = values
                    member[key] = newValue

        for listener in self.notify:
            listener.DataChanged(memberID, changes)

    def AddListener(self, listener):
        if listener not in self.notify:
            self.notify.append(listener)

    def RemoveListener(self, listener):
        if listener in self.notify:
            self.notify.remove(listener)


class CorporationMembersO(corpObject.base):
    __guid__ = 'corpObject.members'

    def __init__(self, boundObject):
        corpObject.base.__init__(self, boundObject)
        self.__lock = uthread.Semaphore()
        self.__members = None
        self.__memberIDs = None
        self.MemberCanRunForCEO_ = None

    def DoSessionChanging(self, isRemote, session, change):
        if 'corpid' in change:
            self.__members = None
            self.__memberIDs = None
            self.MemberCanRunForCEO_ = None

    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' not in change:
            return
        oldID, newID = change['corpid']
        if newID is None:
            return
        self.__PrimeEveOwners()

    def PrimeCorpInformation(self):
        self.GetMemberIDs()
        self.corp__corporations.GetCorporation()

    def __PrimeEveOwners(self):
        self.__lock.acquire()
        try:
            eveowners = self.GetCorpRegistry().GetEveOwners()
            self.__memberIDs = []
            for owner in eveowners:
                if not cfg.eveowners.data.has_key(owner.ownerID):
                    cfg.eveowners.data[owner.ownerID] = list(owner) + [None]
                self.__memberIDs.append(owner.ownerID)

        finally:
            self.__lock.release()

    def __len__(self):
        return len(self.GetMembers())

    def GetMemberIDs(self):
        if self.__memberIDs is None:
            self.__PrimeEveOwners()
        return self.__memberIDs

    def GetMembers(self):
        memberCount = len(self.GetMemberIDs())
        if self.__members is None:
            self.__members = PagedCorpMembers(totalCount=memberCount)
        return self.__members

    def GetMember(self, charID):
        if charID not in self.GetMemberIDs():
            return
        if self.__members is not None:
            member = self.__members.GetMember(charID)
            if member:
                return member
        return self.GetCorpRegistry().GetMember(charID)

    def GetMembersPaged(self, page):
        return self.GetCorpRegistry().GetMembersPaged(page)

    def GetMembersByIds(self, memberIDs):
        return self.GetCorpRegistry().GetMembersByIds(memberIDs)

    def GetMembersAsEveOwners(self):
        return [ cfg.eveowners.Get(charID) for charID in self.GetMemberIDs() ]

    def MemberCanRunForCEO(self):
        if not sm.GetService('skills').GetSkill(const.typeCorporationManagement):
            return 0
        if self.MemberCanRunForCEO_ is None:
            self.MemberCanRunForCEO_ = self.GetCorpRegistry().MemberCanRunForCEO()
        return self.MemberCanRunForCEO_

    def MemberCanCreateCorporation(self):
        if sm.GetService('wallet').GetWealth() < const.corporationStartupCost:
            return 0
        if not sm.GetService('skills').GetSkill(const.typeCorporationManagement):
            return 0
        if self.corp__corporations.GetCorporation().ceoID == eve.session.charid:
            return 0
        return 1

    def GetMyGrantableRoles(self):
        charIsCEO = self.corp__corporations.GetCorporation().ceoID == eve.session.charid
        charIsActiveCEO = charIsCEO and eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector
        grantableRoles = 0
        grantableRolesAtHQ = 0
        grantableRolesAtBase = 0
        grantableRolesAtOther = 0
        member = self.GetMember(eve.session.charid)
        if member is not None:
            if charIsActiveCEO or const.corpRoleDirector == member.roles & const.corpRoleDirector:
                locationalRoles = self.boundObject.GetLocationalRoles()
                for role in self.boundObject.GetRoles():
                    if role.roleID not in locationalRoles:
                        if role.roleID == const.corpRoleDirector:
                            if charIsActiveCEO:
                                grantableRoles = grantableRoles | role.roleID
                        else:
                            grantableRoles = grantableRoles | role.roleID
                    else:
                        grantableRolesAtHQ = grantableRolesAtHQ | role.roleID
                        grantableRolesAtBase = grantableRolesAtBase | role.roleID
                        grantableRolesAtOther = grantableRolesAtOther | role.roleID

            elif charIsCEO:
                pass
            else:
                grantableRoles = long(member.grantableRoles)
                grantableRolesAtHQ = long(member.grantableRolesAtHQ)
                grantableRolesAtBase = long(member.grantableRolesAtBase)
                grantableRolesAtOther = long(member.grantableRolesAtOther)
                if member.titleMask:
                    for titleID, title in self.corp__titles.GetTitles().iteritems():
                        if member.titleMask & titleID == titleID:
                            grantableRoles = grantableRoles | title.grantableRoles
                            grantableRolesAtHQ = grantableRolesAtHQ | title.grantableRolesAtHQ
                            grantableRolesAtBase = grantableRolesAtBase | title.grantableRolesAtBase
                            grantableRolesAtOther = grantableRolesAtOther | title.grantableRolesAtOther

        return (grantableRoles,
         grantableRolesAtHQ,
         grantableRolesAtBase,
         grantableRolesAtOther)

    def OnSkillsChanged(self, skillInfos):
        for skillItem in skillInfos.itervalues():
            if skillItem and skillItem.typeID == const.typeCorporationManagement:
                self.MemberCanRunForCEO_ = None
                break

    def OnAttribute(self, attributeName, item, value):
        if attributeName == 'corporationMemberLimit':
            self.MemberCanRunForCEO_ = None

    def OnAttributes(self, changes):
        for change in changes:
            if change[0] == 'corporationMemberLimit':
                self.MemberCanRunForCEO_ = None

    def OnShareChange(self, shareholderID, corporationID, change):
        if shareholderID == eve.session.charid:
            self.MemberCanRunForCEO_ = None

    def OnCorporationMemberChanged(self, corporationID, memberID, change):
        if self.__memberIDs is None:
            return
        if 'corporationID' in change:
            oldCorpID, newCorpID = change['corporationID']
            if oldCorpID == eve.session.corpid:
                if memberID in self.__memberIDs:
                    self.__memberIDs.remove(memberID)
            elif newCorpID == eve.session.corpid:
                if memberID not in self.__memberIDs:
                    self.__memberIDs.append(memberID)

    def UpdateMember(self, charIDToUpdate, title = None, divisionID = None, squadronID = None, roles = None, grantableRoles = None, rolesAtHQ = None, grantableRolesAtHQ = None, rolesAtBase = None, grantableRolesAtBase = None, rolesAtOther = None, grantableRolesAtOther = None, baseID = None, titleMask = None, blockRoles = None):
        return self.GetCorpRegistry().UpdateMember(charIDToUpdate, title, divisionID, squadronID, roles, grantableRoles, rolesAtHQ, grantableRolesAtHQ, rolesAtBase, grantableRolesAtBase, rolesAtOther, grantableRolesAtOther, baseID, titleMask, blockRoles)

    def UpdateMembers(self, rows):
        return self.GetCorpRegistry().UpdateMembers(rows)

    def SetAccountKey(self, accountKey):
        return self.GetCorpRegistry().SetAccountKey(accountKey)

    def ExecuteActions(self, targetIDs, actions):
        remoteActions = []
        for action in actions:
            verb, property, value = action
            if verb != const.CTV_COMMS:
                remoteActions.append(action)
                continue

        return self.GetCorpRegistry().ExecuteActions(targetIDs, remoteActions)

    def MemberBlocksRoles(self):
        blocksRoles = 0
        member = self.GetMember(eve.session.charid)
        if member is not None:
            if member.blockRoles is not None:
                blocksRoles = member.blockRoles
        return blocksRoles

    def GetNumberOfPotentialCEOs(self):
        return self.GetCorpRegistry().GetNumberOfPotentialCEOs()
