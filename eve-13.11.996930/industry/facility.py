#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\industry\facility.py
import industry
import collections

class Facility(industry.Base):

    def __init__(self, facilityID = None, typeID = None, ownerID = None, solarSystemID = None, tax = None, distance = None, modifiers = None, online = True):
        self.facilityID = facilityID
        self.typeID = typeID
        self.ownerID = ownerID
        self.solarSystemID = solarSystemID
        self.tax = tax
        self.distance = distance if distance is not None else None
        self.activities = collections.defaultdict(lambda : {'blueprints': set(),
         'categories': set(),
         'groups': set()})
        self.modifiers = modifiers or []
        self.online = online

    def __repr__(self):
        return industry.repr(self, exclude=['activities'])

    def update_activity(self, activityID, blueprints = None, categories = None, groups = None):
        self.activities[activityID]['blueprints'].update(blueprints or [])
        self.activities[activityID]['categories'].update(categories or [])
        self.activities[activityID]['groups'].update(groups or [])
