#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\trinity\renderjobs.py
import decometaclass
from . import _trinity as trinity

class RenderJobs(object):
    __cid__ = 'trinity.Tr2RenderJobs'
    __metaclass__ = decometaclass.BlueWrappedMetaclass

    def __init__(self):
        pass

    def UnscheduleByName(self, name):
        for rj in self.recurring:
            if rj.name == name:
                self.recurring.remove(rj)
                return True

        return False

    def FindByName(self, name):
        for rj in self.recurring:
            if rj.name == name:
                return rj

    def FindStepByName(self, name):

        def FindInJob(rj):
            for step in rj.steps:
                if step.name == name:
                    return step

        for rj in self.recurring:
            ret = FindInJob(rj)
            if ret is not None:
                return ret

    def FindScenes(self, sceneType, filter = lambda x: True):
        results = set({})

        def RecursiveSearch(job):
            for step in job.steps:
                if hasattr(step, 'object') and type(step.object) is sceneType and filter(step.object):
                    results.add(step.object)
                    return
                if type(step) is trinity.TriStepRunJob:
                    RecursiveSearch(step.job)

        for job in self.recurring:
            RecursiveSearch(job)

        return results
