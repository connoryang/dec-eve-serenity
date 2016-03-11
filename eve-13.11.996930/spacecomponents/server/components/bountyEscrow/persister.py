#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\bountyEscrow\persister.py


class Persister(object):

    def __init__(self, solarSystemID, itemID, dbspacecomponent):
        self.isDirty = False
        self.itemID = itemID
        self.solarSystemID = solarSystemID
        self.dbspacecomponent = dbspacecomponent

    def _GetBountiesParameters(self, bountyContributors):
        charIDs = []
        bounties = []
        for charID, isk in bountyContributors.iteritems():
            charIDs.append(str(charID))
            bounties.append(str(isk))

        charIDsAsString = ','.join(charIDs)
        bountiesAsString = ','.join(bounties)
        return (charIDsAsString, bountiesAsString)

    def PersistEverything(self, bountyContributors, bountyBonus):
        if not self.isDirty:
            return
        bountyArgs = self._GetBountiesParameters(bountyContributors)
        self.dbspacecomponent.BountyEscrow_PersistState(self.solarSystemID, self.itemID, bountyBonus, *bountyArgs)
        self.isDirty = False

    def GetStateForSystem(self):
        bonusRows, bounties = self.dbspacecomponent.BountyEscrow_GetState(self.solarSystemID, self.itemID)
        if not bonusRows:
            bonus = 0.0
        else:
            bonus = bonusRows[0].bountyEscrowBonus
        return (bonus, {r.characterID:r.iskValue for r in bounties})

    def MarkDirty(self):
        self.isDirty = True
