#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\trinutils\fisutils.py
import os
import blue
import osutils
import trinity
import uthread2
BOOSTER_RES_PATH = 'res:/dx9/model/ship/booster'

def GetBoosternames():
    fpgen = [ str(x) for x in blue.paths.listdir(BOOSTER_RES_PATH) if x.lower().endswith('.red') ]
    file_names = map(osutils.GetFilenameWithoutExt, fpgen)
    base_names = map(os.path.basename, file_names)
    race_names = map(lambda n: n.rsplit('_', 1)[-1], base_names)
    return map(lambda n: n.title(), race_names)


def ApplyBoosters(trinobjs, race):
    validobjs = filter(lambda o: hasattr(o, 'boosters'), trinobjs)
    if not validobjs:
        return

    def clearbooster(obj):
        obj.boosters = None

    if race is None:
        uthread2.map(clearbooster, validobjs)
        return
    booster_filepath = '%s/booster_%s.red' % (BOOSTER_RES_PATH, race)
    booster = trinity.Load(booster_filepath)
    if not booster:
        raise IOError("Could not load file '%s'" % booster_filepath)

    def loadit(obj):
        boost = trinity.Load(booster_filepath)
        obj.boosters = boost
        obj.boosters.alwaysOn = True
        obj.RebuildBoosterSet()

    uthread2.map(lambda o: uthread2.start_tasklet(loadit, o), validobjs)


def SafeCallMethod(trinobj, methodname, *args, **kwargs):
    f = getattr(trinobj, methodname, None)
    if f is None or not callable(f):
        return
    f(*args, **kwargs)
