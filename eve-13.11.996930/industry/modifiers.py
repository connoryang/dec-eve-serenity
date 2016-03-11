#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\industry\modifiers.py
import industry

class Modifier(industry.Base):

    def __init__(self, amount, reference = None, activity = None, output = False, blueprints = None, categoryID = None, groupID = None):
        self.amount = amount
        self.reference = reference
        self.activity = activity
        self.output = output
        self.blueprints = set(blueprints or [])
        self.categoryID = categoryID
        self.groupID = groupID


class MaterialModifier(Modifier):
    pass


class TimeModifier(Modifier):
    pass


class CostModifier(Modifier):
    pass


class ProbabilityModifier(Modifier):
    pass


class MaxRunsModifier(Modifier):
    pass


class SlotModifier(Modifier):
    pass
