#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\squadronManagementController.py


class SquadronMgmtController(object):

    def __init__(self):
        self.fighterSvc = sm.GetService('fighters')

    def LoadFightersToTube(self, fighterID, tubeFlagID):
        self.fighterSvc.LoadFightersToTube(fighterID, tubeFlagID)

    def UnloadTubeToFighterBay(self, tubeFlagID):
        self.fighterSvc.UnloadTubeToFighterBay(tubeFlagID)

    def LaunchFightersFromTube(self, tubeFlagID):
        self.fighterSvc.LaunchFightersFromTube(tubeFlagID)

    def ScoopFightersToTube(self, fighterID, tubeFlagID):
        self.fighterSvc.ScoopFightersToTube(fighterID, tubeFlagID)
