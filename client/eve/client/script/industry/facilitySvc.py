#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\industry\facilitySvc.py
import service
import uthread
import telemetry
from eve.common.script.util import industryCommon

class FacilityService(service.Service):
    __guid__ = 'svc.facilitySvc'
    __servicename__ = 'Facility Service'
    __displayname__ = 'Facility Service'
    __dependencies__ = ['clientPathfinderService']
    __notifyevents__ = ['OnSessionChanged', 'OnFacilitiesUpdated', 'OnFacilityUpdated']

    def Run(self, *args, **kwargs):
        service.Service.Run(self, *args, **kwargs)
        self.facilities = {}
        self.maxActivityModifiers = {}
        self.regionLoaded = False
        self.loading = uthread.Semaphore()
        self.facilityManager = sm.RemoteSvc('facilityManager')

    def OnSessionChanged(self, isRemote, session, change):
        if 'regionid' in change:
            self.Reload()
        if 'solarsystemid2' in change or 'stationid2' in change:
            map(self._UpdateFacilityDistance, self.facilities.itervalues())

    def OnFacilitiesUpdated(self):
        self.Reload()

    def OnFacilityUpdated(self, facilityID):
        self.Reload(facilityID)

    def GetFacilities(self):
        self._PrimeFacilties()
        return self.facilities.values()

    def GetMaxActivityModifier(self, activityID = None):
        self._PrimeFacilties()
        if activityID:
            return self.maxActivityModifiers.get(activityID, 1.0)
        else:
            return max(self.maxActivityModifiers.values()) or 1.0

    def GetFacilityTaxes(self, facilityID):
        return self.facilityManager.GetFacilityTaxes(facilityID, session.corpid)

    def SetFacilityTaxes(self, facilityID, taxRateValues):
        self.facilityManager.SetFacilityTaxes(facilityID, session.corpid, taxRateValues)

    def Reload(self, facilityID = None):
        self.regionLoaded = False
        sm.ScatterEvent('OnFacilityReload', facilityID)

    @telemetry.ZONE_METHOD
    def GetFacility(self, facilityID, prime = True):
        if facilityID:
            self._PrimeFacilties()
            if prime and facilityID and facilityID not in self.facilities:
                self._PrimeFacility(self.facilityManager.GetFacility(facilityID))
            return self.facilities[facilityID]

    def GetFacilityLocations(self, facilityID, ownerID):
        locations = self.facilityManager.GetFacilityLocations(facilityID, ownerID)
        cfg.evelocations.Prime(set([ location.itemID for location in locations ]))
        return locations

    def IsFacility(self, itemID):
        self._PrimeFacilties()
        if itemID in self.facilities:
            return True
        return False

    def _PrimeFacilties(self, force = False):
        if self.regionLoaded and not force:
            return
        with self.loading:
            if self.regionLoaded and not force:
                return
            self.regionLoaded = True
            self.facilities.clear()
            self.maxActivityModifiers = self.facilityManager.GetMaxActivityModifiers()
            for data in self.facilityManager.GetFacilities():
                self._PrimeFacility(data)

            cfg.eveowners.Prime(set([ facility.ownerID for facility in self.facilities.itervalues() ]))
            cfg.evelocations.Prime(set([ facility.facilityID for facility in self.facilities.itervalues() ]))

    def _PrimeFacility(self, data):
        facility = industryCommon.Facility(data)
        self.facilities[facility.facilityID] = facility
        self._UpdateFacilityDistance(facility)

    def _UpdateFacilityDistance(self, facility):
        facility.distance = self.clientPathfinderService.GetJumpCountFromCurrent(facility.solarSystemID)
