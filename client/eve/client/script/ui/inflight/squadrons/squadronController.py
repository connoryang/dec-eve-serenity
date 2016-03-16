#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\squadronController.py
import fighters

class SquadronController(object):

    def __init__(self):
        pass

    def GetSquadronSpeed(self):
        return 1337

    def GetSquadronAction(self):
        return 'Orbiting 10km'

    def GetAbilities(self, fighterTypeID):
        if fighterTypeID:
            abilities = fighters.IterTypeAbilities(fighterTypeID)
            return abilities

    def GetEffects(self):
        return ['effect1', 'effect2', 'effect3']

    def GetSquadronHealth(self):
        return (12, 1, 4)
