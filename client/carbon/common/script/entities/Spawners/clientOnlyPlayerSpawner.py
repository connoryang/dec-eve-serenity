#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\entities\Spawners\clientOnlyPlayerSpawner.py
from carbon.common.script.entities.Spawners.baseSpawner import BaseSpawner

class ClientOnlyPlayerSpawner(BaseSpawner):
    __guid__ = 'cef.ClientOnlyPlayerSpawner'

    def __init__(self, sceneID, charID, position, rotation, paperdolldna, pubInfo):
        BaseSpawner.__init__(self, sceneID)
        self.charID = charID
        self.playerTypeID = cfg.eveowners.Get(session.charid).typeID
        self.playerRecipeID = const.cef.PLAYER_RECIPES[self.playerTypeID]
        self.position = position
        self.rotation = rotation
        self.paperdolldna = paperdolldna
        self.pubInfo = pubInfo

    def GetEntityID(self):
        return self.charID

    def GetPosition(self):
        return self.position

    def GetRotation(self):
        return self.rotation

    def GetRecipe(self, entityRecipeSvc):
        overrides = {}
        overrides = self._OverrideRecipePosition(overrides, self.GetPosition(), self.GetRotation())
        overrides[const.cef.INFO_COMPONENT_ID] = {'name': cfg.eveowners.Get(session.charid).ownerName,
         'gender': session.genderID}
        overrides[const.cef.PAPER_DOLL_COMPONENT_ID] = {'gender': self.pubInfo.gender,
         'dna': self.paperdolldna,
         'typeID': self.playerTypeID}
        recipe = entityRecipeSvc.GetRecipe(self.playerRecipeID, overrides)
        if recipe is None:
            raise RuntimeError('Player Recipe is missing for typeID: %d with recipeID: %d' % (self.playerTypeID, self.playerRecipeID))
        return recipe
