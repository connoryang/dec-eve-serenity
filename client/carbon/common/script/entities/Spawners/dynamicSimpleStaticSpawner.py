#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\entities\Spawners\dynamicSimpleStaticSpawner.py
from carbon.common.script.entities.Spawners.baseSpawner import BaseSpawner

class DynamicSimpleStaticSpawner(BaseSpawner):
    __guid__ = 'cef.DynamicSimpleStaticSpawner'

    def __init__(self, sceneID, spawnRow):
        BaseSpawner.__init__(self, sceneID)
        self.spawnRow = spawnRow

    def GetPosition(self):
        return (self.spawnRow.spawnPointX, self.spawnRow.spawnPointY, self.spawnRow.spawnPointZ)

    def GetRotation(self):
        return (self.spawnRow.spawnRotationY, self.spawnRow.spawnRotationX, self.spawnRow.spawnRotationZ)

    def GetRecipe(self, entityRecipeSvc):
        positionOverrides = self._OverrideRecipePosition({}, self.GetPosition(), self.GetRotation())
        spawnRecipe = entityRecipeSvc.GetRecipe(self.spawnRow.recipeID, positionOverrides)
        return spawnRecipe
