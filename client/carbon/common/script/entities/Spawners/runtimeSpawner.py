#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\entities\Spawners\runtimeSpawner.py
from carbon.common.script.entities.Spawners.baseSpawner import BaseSpawner

class RuntimeSpawner(BaseSpawner):
    __guid__ = 'cef.RuntimeSpawner'

    def __init__(self, entitySceneID, entityID, recipeID, position, rotation):
        self.sceneID = entitySceneID
        self.entityID = entityID
        self.recipeID = recipeID
        self.position = position
        self.rotation = rotation

    def GetEntityID(self):
        return self.entityID

    def GetPosition(self):
        return self.position

    def GetRotation(self):
        return self.rotation

    def GetRecipe(self, entityRecipeSvc):
        positionOverrides = self._OverrideRecipePosition({}, self.GetPosition(), self.GetRotation())
        recipe = entityRecipeSvc.GetRecipe(self.recipeID, positionOverrides)
        return recipe
