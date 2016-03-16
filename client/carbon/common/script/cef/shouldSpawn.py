#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\cef\shouldSpawn.py
from carbon.common.script.cef.baseComponentView import BaseComponentView

def ShouldSpawnOn(componentIDList, spawnLoc):
    shouldSpawn = False
    for componentID in componentIDList:
        componentView = BaseComponentView.GetComponentViewByID(componentID)
        spawnHere = componentView.__SHOULD_SPAWN__.get(spawnLoc, None)
        if spawnHere is False:
            return False
        if spawnHere:
            shouldSpawn = True

    return shouldSpawn


exports = {'cef.ShouldSpawnOn': ShouldSpawnOn}
