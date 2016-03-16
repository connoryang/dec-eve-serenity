#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\eventLogger.py
from eveexceptions.exceptionEater import ExceptionEater
EVENT_DECAYED = 'spacecomponent::decay_Decayed'
EVENT_BECOMEACTIVE = 'spacecomponent::activate_BecomeActive'

class EventLogger(object):

    def __init__(self, eventLog, solarSystemID):
        self.eventLog = eventLog
        self.solarSystemID = solarSystemID

    def LogDecayed(self, item):
        self.LogItemAndTypeOwnerEvent(EVENT_DECAYED, item)

    def LogBecomeActive(self, item):
        self.LogItemAndTypeOwnerEvent(EVENT_BECOMEACTIVE, item)

    def LogItemAndTypeOwnerEvent(self, eventName, item):
        with ExceptionEater('eventLog'):
            self.eventLog.LogOwnerEvent(eventName, item.ownerID, self.solarSystemID, item.itemID, item.typeID)
            self.eventLog.LogOwnerEventJson(eventName, item.ownerID, self.solarSystemID, componentItemID=item.itemID, componentTypeID=item.typeID)
