#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\abTestCore\common\cohorts.py


class Cohort(object):

    def __init__(self, cohortID, name, description):
        self.cohortID = cohortID
        self.cohortName = name
        self.description = description

    @staticmethod
    def FromFSDData(dataRow):
        return Cohort(cohortID=dataRow['cohortID'], name=dataRow['cohortName'], description=dataRow['description'])


class CohortGroup(object):

    def __init__(self, groupID, name, description, cohortList):
        self.cohortGroupID = groupID
        self.cohortGroupName = name
        self.description = description
        self.cohorts = []
        self.cohorts.extend(cohortList)

    @staticmethod
    def FromFSDData(dataRow):
        cohortList = []
        cohortData = dataRow['cohorts']
        for cohort in cohortData:
            cohortList.append(Cohort.FromFSDData(cohort))

        return CohortGroup(groupID=dataRow['cohortGroupID'], description=dataRow['description'], name=dataRow['cohortGroupName'], cohortList=cohortList)
