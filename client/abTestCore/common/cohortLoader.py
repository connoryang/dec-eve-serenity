#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\abTestCore\common\cohortLoader.py
from abTestCore.common.cohorts import CohortGroup, Cohort

class CohortLoader:

    def _LoadRawData(self):
        import fsdSchemas.binaryLoader as fsdBinaryLoader
        return fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/cohorts.static')

    def GetCohortGroupDictWithCohorts(self):
        data = self._LoadRawData()
        cohortGroupDict = {}
        for key, value in data.iteritems():
            group = CohortGroup.FromFSDData(value)
            cohortGroupDict[key] = group

        return cohortGroupDict

    def GetCohortDictionary(self):
        cohortGroups = self.GetCohortGroupDictWithCohorts()
        cohortDict = {}
        for group in cohortGroups.itervalues():
            for cohort in group.cohorts:
                cohortDict[cohort.cohortID] = cohort

        return cohortDict
