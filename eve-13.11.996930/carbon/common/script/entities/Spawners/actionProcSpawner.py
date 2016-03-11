#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\entities\Spawners\actionProcSpawner.py
import GameWorld
from carbon.common.script.entities.Spawners.runtimeSpawner import RuntimeSpawner

class ActionProcSpawner(RuntimeSpawner):
    __guid__ = 'cef.ActionProcSpawner'

    def __init__(self, entitySceneID, dynamicSpawnID, recipeTypeID, posProp, rotProp):
        position = GameWorld.GetPropertyForCurrentPythonProc(posProp)
        rotation = GameWorld.GetPropertyForCurrentPythonProc(rotProp)
        RuntimeSpawner.__init__(self, entitySceneID, dynamicSpawnID, recipeTypeID, position, rotation)
