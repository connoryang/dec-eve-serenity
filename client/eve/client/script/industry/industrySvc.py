#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\industry\industrySvc.py
import industry
import service
import weakref
import uthread
import telemetry
import util
import blue
from eve.common.script.util import industryCommon

class IndustryService(service.Service):
    __guid__ = 'svc.industrySvc'
    __servicename__ = 'Industry'
    __displayname__ = 'Industry Service'
    __dependencies__ = ['blueprintSvc', 'facilitySvc', 'clientPathfinderService']
    __notifyevents__ = ['OnCharacterAttributeChanged',
     'OnIndustryMaterials',
     'OnIndustryJob',
     'OnSessionChanged',
     'OnAccountChange',
     'OnSkillLevelChanged']

    def Run(self, *args, **kwargs):
        self.monitoring = weakref.ref(set())
        self.installed = weakref.WeakValueDictionary()
        uthread.new(self._PollJobCompletion)
        service.Service.Run(self, *args, **kwargs)

    def GetJobByID(self, jobID):
        return self._JobInstance(sm.RemoteSvc('industryManager').GetJob(jobID), fetchBlueprint=True)

    @telemetry.ZONE_METHOD
    def GetOwnerJobs(self, ownerID, includeCompleted = False):
        jobs = []
        locations = set()
        for data in sm.RemoteSvc('industryManager').GetJobsByOwner(ownerID, includeCompleted):
            job = self._JobInstance(data, fetchBlueprint=False)
            jobs.append(job)
            if not job.completed:
                locations.add(job.facilityID)

        cfg.evelocations.Prime(locations)
        return jobs

    def GetCharacterJobs(self, includeCompleted = False):
        return self.GetOwnerJobs(session.charid, includeCompleted)

    def GetCorporationJobs(self, includeCompleted = False):
        return self.GetOwnerJobs(session.corpid, includeCompleted)

    @telemetry.ZONE_METHOD
    def CreateJob(self, blueprint, activityID, facilityID, runs = 1):
        job = industry.Job(blueprint, activityID)
        job.runs = runs
        job.status = industry.STATUS_UNSUBMITTED
        job.extras = industryCommon.GetOptionalMaterials(job)
        job.prices = industryCommon.JobPrices()
        industryCommon.AttachSessionToJob(job, session)
        self._UpdateSkills(job)
        self._UpdateSlots(job)
        self._UpdateModifiers(job)
        self._UpdateDistance(job)
        self._UpdateAccounts(job)
        job.on_facility.connect(self.LoadLocations)
        job.on_delete.connect(self.DisconnectJob)
        job.on_input_location.connect(self.ConnectJob)
        job.facility = self.facilitySvc.GetFacility(facilityID)
        self._ApplyJobSettings(job)
        return job

    def RecreateJob(self, existing):
        try:
            blueprint = self.blueprintSvc.GetBlueprintItem(existing.blueprintID)
            if blueprint.ownerID != existing.ownerID:
                raise UserError
        except UserError:
            blueprint = self.blueprintSvc.GetBlueprintType(existing.blueprintTypeID, not existing.blueprint.original)

        job = self.CreateJob(blueprint, existing.activityID, existing.facilityID)
        job.outputLocation = industryCommon.MatchLocation(job, existing.outputLocationID, existing.outputFlagID)
        job.productTypeID = existing.productTypeID
        job.runs = existing.runs
        job.licensedRuns = existing.licensedRuns
        for material in job.optional_materials:
            material.select(None)
            if getattr(existing, 'optionalTypeID', None) in material.all_types():
                material.select(existing.optionalTypeID)
            if getattr(existing, 'optionalTypeID2', None) in material.all_types():
                material.select(existing.optionalTypeID2)

        return job

    def JobDataWithBlueprint(self, existing):
        job = self._JobInstance(existing.data, fetchBlueprint=True)
        job.extras = industryCommon.GetOptionalMaterials(job)
        return job

    def InstallJob(self, job):
        sm.RemoteSvc('industryManager').InstallJob(job.dump())

    def CompleteJob(self, jobID):
        sm.RemoteSvc('industryManager').CompleteJob(int(jobID))

    def CompleteJobs(self, jobs):
        uthread.parallel([ (self.CompleteJob, (jobID,)) for jobID in jobs ])

    def CancelJob(self, jobID):
        sm.RemoteSvc('industryManager').CancelJob(int(jobID))

    def _PollJobCompletion(self):
        while self.state == service.SERVICE_RUNNING:
            uthread.new(self._PollJobCompletionThreaded)
            blue.pyos.synchro.SleepWallclock(1000)

    def _PollJobCompletionThreaded(self):
        for job in self.installed.values():
            if job.status == industry.STATUS_INSTALLED and util.DateToBlue(job.endDate) < blue.os.GetWallclockTime():
                job.status = industry.STATUS_READY
                sm.ScatterEvent('OnIndustryJob', job.jobID, job.ownerID, job.blueprintID, job.installerID, job.status, None)

    def _JobInstance(self, data, fetchBlueprint = False):
        if fetchBlueprint:
            blueprint = self.blueprintSvc.GetBlueprint(data.blueprintID, data.blueprintTypeID)
        else:
            blueprint = self.blueprintSvc.GetBlueprintType(data.blueprintTypeID, data.blueprintCopy)
        job = industryCommon.JobData(data, blueprint)
        self._UpdateSkills(job)
        self._UpdateSlots(job)
        self._UpdateModifiers(job)
        self._UpdateDistance(job)
        if job.status == industry.STATUS_INSTALLED:
            self.installed[job.jobID] = job
        else:
            self.installed.pop(job.jobID, None)
        return job

    @telemetry.ZONE_METHOD
    def _UpdateModifiers(self, job):
        if job:
            modifiers = industryCommon.GetJobModifiers(job)
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            for modifier, attribute, activity in industryCommon.ATTRIBUTE_MODIFIERS:
                if job.activityID == activity:
                    amount = dogmaLocation.GetAttributeValue(session.charid, attribute)
                    modifiers.append(modifier(amount=amount, activity=activity, reference=industry.Reference.SKILLS))

            job.modifiers = modifiers

    @telemetry.ZONE_METHOD
    def _UpdateDistance(self, job):
        if job and isinstance(job, industry.JobData):
            job._distance = self.clientPathfinderService.GetJumpCountFromCurrent(job.solarSystemID)

    @telemetry.ZONE_METHOD
    def _UpdateSkills(self, job):
        if job:
            skills = {}
            mySkills = sm.GetService('skills').GetSkill
            for typeID in [ skill.typeID for skill in job.all_skills ]:
                skillInfo = mySkills(typeID)
                skills[typeID] = skillInfo.skillLevel if skillInfo else 0

            job.skills = skills

    @telemetry.ZONE_METHOD
    def _UpdateSlots(self, job = None, force = False):
        if not hasattr(self, 'slots'):
            self.slots = {}
        if not len(self.slots) or force:
            self.slots = sm.RemoteSvc('industryManager').GetJobCounts(session.charid)
        if job:
            job.slots = self.slots

    @telemetry.ZONE_METHOD
    def _UpdateAccounts(self, job, ownerID = None, account = None, balance = None):
        if job:
            accounts = {(session.charid, const.accountingKeyCash): sm.GetService('wallet').GetWealth()}
            if session.corpAccountKey and sm.GetService('wallet').HaveAccessToCorpWalletDivision(session.corpAccountKey):
                if ownerID and account and balance and session.corpid == ownerID and session.corpAccountKey == account:
                    accounts[session.corpid, session.corpAccountKey] = balance
                else:
                    accounts[session.corpid, session.corpAccountKey] = sm.GetService('wallet').GetCorpWealthCached1Min(session.corpAccountKey)
            job.accounts = accounts
            if job.account not in job.accounts:
                for accountOwner, accountKey in job.accounts.keys():
                    if job.ownerID == accountOwner:
                        job.account = (accountOwner, accountKey)
                        return

                job.account = job.accounts.keys()[0]

    def OnCharacterAttributeChanged(self, attributeID, oldValue, value):
        if attributeID in [ attribute for _, attribute, _ in industryCommon.ATTRIBUTE_MODIFIERS ]:
            self._UpdateModifiers(self.monitoring())

    def OnSessionChanged(self, isRemote, session, change):
        industryCommon.AttachSessionToJob(self.monitoring(), session)
        if 'corpAccountKey' in change:
            self._UpdateAccounts(self.monitoring())
        if 'corprole' in change:
            self._UpdateAccounts(self.monitoring())
            self.LoadLocations(self.monitoring())

    def OnAccountChange(self, accountKey, ownerID, balance):
        self._UpdateAccounts(self.monitoring(), ownerID, sm.GetService('account').GetAccountKeyID(accountKey), balance)

    def OnSkillLevelChanged(self, typeID, oldValue, newValue):
        self._UpdateSkills(self.monitoring())
        self._UpdateModifiers(self.monitoring())

    def OnIndustryJob(self, jobID, ownerID, blueprintID, installerID, status, successfulRuns):
        if installerID == session.charid:
            self._UpdateSlots(self.monitoring(), force=True)

    @telemetry.ZONE_METHOD
    def ConnectJob(self, job):
        self.monitoring = weakref.ref(job)
        job.monitorID, job.available = sm.RemoteSvc('industryMonitor').ConnectJob(job.dump())

    @telemetry.ZONE_METHOD
    def DisconnectJob(self, job):
        if self.monitoring() == job:
            sm.RemoteSvc('industryMonitor').DisconnectJob(job.monitorID)

    @telemetry.ZONE_METHOD
    def LoadLocations(self, job):
        if job:
            job.locations = self.facilitySvc.GetFacilityLocations(job.facilityID, job.ownerID)
            if len(job.locations):
                self._ApplyJobSettings(job)

    def OnIndustryMaterials(self, jobID, materials):
        job = self.monitoring()
        if job and job.monitorID == jobID:
            job.available = materials

    def _UpdateJobSettings(self, job):
        settings.char.ui.Set('industry_b:%s_a:%s_runs' % (job.blueprint.blueprintTypeID, job.activityID), job.runs)
        settings.char.ui.Set('industry_b:%s_a:%s_productTypeID' % (job.blueprint.blueprintTypeID, job.activityID), job.productTypeID)
        settings.char.ui.Set('industry_b:%s_a:%s_licensedRuns' % (job.blueprint.blueprintTypeID, job.activityID), job.licensedRuns)
        settings.char.ui.Set('industry_account:%s' % (job.ownerID,), job.account)
        if job.inputLocation is not None and job.facility is not None:
            settings.char.ui.Set('industry_b:%s_a:%s_f:%s_input' % (job.blueprint.blueprintTypeID, job.activityID, job.facility.facilityID), (job.inputLocation.itemID, job.inputLocation.flagID))
        if job.outputLocation is not None and job.facility is not None:
            settings.char.ui.Set('industry_b:%s_a:%s_f:%s_output' % (job.blueprint.blueprintTypeID, job.activityID, job.facility.facilityID), (job.outputLocation.itemID, job.outputLocation.flagID))
        if len(job.optional_materials):
            settings.char.ui.Set('industry_b:%s_a:%s_materials' % (job.blueprint.blueprintTypeID, job.activityID), list([ material.typeID for material in job.optional_materials if material.typeID ]))

    def _ApplyJobSettings(self, job):
        job.runs = settings.char.ui.Get('industry_b:%s_a:%s_runs' % (job.blueprint.blueprintTypeID, job.activityID), 1)
        job.productTypeID = settings.char.ui.Get('industry_b:%s_a:%s_productTypeID' % (job.blueprint.blueprintTypeID, job.activityID), None)
        job.licensedRuns = min(job.maxLicensedRuns, settings.char.ui.Get('industry_b:%s_a:%s_licensedRuns' % (job.blueprint.blueprintTypeID, job.activityID), job.maxLicensedRuns))
        account = settings.char.ui.Get('industry_account:%s' % (job.ownerID,), job.account)
        job.account = account if account in job.accounts else job.account
        if job.facility:
            job.inputLocation = industryCommon.MatchLocation(job, *settings.char.ui.Get('industry_b:%s_a:%s_f:%s_input' % (job.blueprint.blueprintTypeID, job.activityID, job.facility.facilityID), (job.blueprint.location.itemID, job.blueprint.location.flagID)))
            job.outputLocation = industryCommon.MatchLocation(job, *settings.char.ui.Get('industry_b:%s_a:%s_f:%s_output' % (job.blueprint.blueprintTypeID, job.activityID, job.facility.facilityID), (job.blueprint.location.itemID, job.blueprint.location.flagID)))
        materials = settings.char.ui.Get('industry_b:%s_a:%s_materials' % (job.blueprint.blueprintTypeID, job.activityID), [])
        for material in job.materials:
            for option in material.options:
                if option.typeID in materials:
                    material.select(option)

        job.on_updated.connect(self._UpdateJobSettings)
