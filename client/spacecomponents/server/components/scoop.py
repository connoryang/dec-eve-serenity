#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\scoop.py
from eve.common.script.mgt.appLogConst import eventSpaceComponentScooped

class Scoop(object):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        self.itemID = itemID
        self.typeID = typeID
        self.attributes = attributes
        self.componentRegistry = componentRegistry

    def OnScooped(self, ballpark, characterID, shipID):
        ballpark.dbLog.LogItemGenericEvent(None, eventSpaceComponentScooped, self.itemID, referenceID=ballpark.solarsystemID, int_1=self.typeID, bigint_1=characterID, bigint_2=shipID)
