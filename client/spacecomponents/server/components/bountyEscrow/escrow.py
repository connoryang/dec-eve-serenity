#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\bountyEscrow\escrow.py
import random
import weakref
import uthread2

class Escrow(object):

    def __init__(self, bountyEscrow, ballpark, iskRegistry, iskMover, itemCreator, persister):
        self.itemID = bountyEscrow.itemID
        self.bountyEscrow = weakref.proxy(bountyEscrow)
        self.ballpark = ballpark
        self.iskRegistry = iskRegistry
        self.iskMover = iskMover
        self.itemCreator = itemCreator
        self.persister = persister
        self.tagSpawnDelay = bountyEscrow.attributes.tagSpawnDelay
        self.lpCorpID = bountyEscrow.attributes.lpCorpID
        self.takePercentage = float(bountyEscrow.attributes.takePercentage) / 100
        self.bonus = float(bountyEscrow.attributes.bonus) / 100
        self.bonusMax = float(bountyEscrow.attributes.bonusMax) / 100
        self.bonusIncrease = float(bountyEscrow.attributes.bonusIncrease) / 100
        self.bonusIncreaseChance = bountyEscrow.attributes.bonusIncreaseChance
        self.lpBase = bountyEscrow.attributes.lpBase
        self.lpBaseBonusFactor = 1000 / bountyEscrow.attributes.lpBaseBonusFactor
        self.SetBonus(self.bonus)

    def EscrowPartOfBounty(self, bountyAmount, charID):
        bountyToTake = bountyAmount * self.takePercentage
        if self.bonus < self.bonusMax and random.random() < self.bonusIncreaseChance:
            self.bonus += self.bonusIncrease
            self.SetBonus(self.bonus)
        bountyBonus = bountyAmount * self.bonus
        self.iskRegistry.RegisterIsk(charID, bountyToTake + bountyBonus)
        self.persister.MarkDirty()
        return bountyAmount - bountyToTake

    def GetLPBounty(self, bountyAmount):
        lpPercentage = self.lpBase + self.bonus / self.lpBaseBonusFactor
        lpBounty = int(bountyAmount * lpPercentage)
        return (lpBounty, self.lpCorpID)

    def PayIsk(self, payingCharID):
        self.iskMover.PayIsk(self.iskRegistry.GetIskContributors(), payingCharID)
        self.ClearIsk()

    def CreateItems(self, charID, shipID):
        self.itemCreator.CreateItems(charID, shipID, self.GetIskContributors())
        self.ClearIsk()

    def GetIskContributors(self):
        return self.iskRegistry.GetIskContributors()

    def SetBonus(self, bonus):
        self.bonus = bonus
        self.ballpark.UpdateSlimItemField(self.itemID, 'bountyEscrowBonus', self.bonus)

    def GetBonus(self):
        return self.bonus

    def ClearIsk(self):
        self.persister.MarkDirty()
        self.iskRegistry.ClearIsk()
        self.SetBonus(0.0)
        self.PersistEverything()

    def GetBounty(self):
        return self.iskRegistry.GetBountyAmount()

    def PersistEverything(self):
        self.persister.PersistEverything(self.GetIskContributors(), self.GetBonus())

    def SetBonusChance(self, bonusChance):
        self.bonusIncreaseChance = bonusChance

    def RegisterForPaymentEvents(self, func):
        self.iskMover.RegisterForPaymentEvents(func)

    def RegisterForItemCreationEvents(self, func):
        self.itemCreator.RegisterForItemCreationEvents(func)

    def RegisterForRegisterIskEvents(self, func):
        self.iskRegistry.RegisterForRegisterIskEvents(func)
