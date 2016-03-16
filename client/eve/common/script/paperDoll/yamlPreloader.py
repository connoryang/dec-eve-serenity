#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\paperDoll\yamlPreloader.py
import telemetry
import cStringIO
import weakref
import yaml
import uthread
import blue
import walk
import copy
import types
from .paperDollCommonFunctions import BeFrameNice, NastyYamlLoad
import log
import whitelistpickle
import cPickle
import copy_reg
import time

class AvatarPartMetaData(object):
    __guid__ = 'paperDoll.AvatarPartMetaData'

    def __init__(self):
        self.dependantModifiers = []
        self.occludesModifiers = []
        self.numColorAreas = 3
        self.forcesLooseTop = False
        self.hidesBootShin = False
        self.swapTops = False
        self.swapBottom = False
        self.swapSocks = False
        self.alternativeTextureSourcePath = ''
        self.soundTag = 0
        self.lod1Replacement = ''
        self.lod2Replacement = ''
        self.defaultMetaData = True

    def __hash__(self):
        t = []
        keys = self.__dict__.keys()
        for key in keys:
            x = self.__dict__[key]
            if type(x) is types.ListType:
                x = tuple(x)
            t.append(x)

        t.sort()
        t = tuple(t)
        return hash(t)

    @staticmethod
    def Load(yamlStr):
        instance = LoadYamlFileNicely(yamlStr)
        t = AvatarPartMetaData()
        for key in t.__dict__.keys():
            if key not in instance.__dict__.keys():
                instance.__dict__[key] = t.__dict__[key]

        return instance

    @staticmethod
    def FillInDefaults(instance):
        t = AvatarPartMetaData()
        for key in t.__dict__.keys():
            if key not in instance.__dict__.keys():
                instance.__dict__[key] = t.__dict__[key]

        dmLen = len(instance.dependantModifiers)
        for i in xrange(dmLen):
            instance.dependantModifiers[i] = instance.dependantModifiers[i].lower()

        if instance.lod1Replacement:
            instance.lod1Replacement = instance.lod1Replacement.lower()
        if instance.lod2Replacement:
            instance.lod2Replacement = instance.lod2Replacement.lower()
        if instance.alternativeTextureSourcePath:
            instance.alternativeTextureSourcePath = instance.alternativeTextureSourcePath.lower()
        return instance


class YamlPreloader(object):
    __guid__ = 'paperDoll.YamlPreloader'
    __metaclass__ = telemetry.ZONE_PER_METHOD
    __shared_state = {}

    @staticmethod
    def YamlPreloaderPDFilter(yamlStr):
        yamlStr = yamlStr.replace('AvatarFactory.paperDollDataManagement.', 'paperDoll.')
        yamlStr = yamlStr.replace('AvatarFactory.', '')
        yamlStr = yamlStr.replace('tattoo.', 'paperDoll.')
        return yamlStr

    def __init__(self):
        self.__dict__ = self.__shared_state
        if not hasattr(self, 'cache'):
            self.cache = {}
            self._tasklets = weakref.WeakKeyDictionary()
            self.preloadedRootFolders = []

    def IsLoading(self):
        return len(self._tasklets.keys()) > 0

    @staticmethod
    def Clear():
        YamlPreloader.__shared_state.clear()

    def Preload(self, rootFolder = None, extensions = None, yamlFilter = None):
        extensions = extensions or ['.yaml']

        def doPreload():
            t = uthread.new(self.Preload_t, *(rootFolder, extensions, yamlFilter))
            self._tasklets[t] = True

        if rootFolder:
            rootFolder = rootFolder.lower()
            if rootFolder not in self.preloadedRootFolders:
                doPreload()
                self.preloadedRootFolders.append(rootFolder)

    def _ReadAndAddToCache(self, path, yamlFilter):
        memStream = blue.paths.GetFileContentsWithYield(path)
        yamlStr = memStream.Read()
        if yamlFilter is not None:
            yamlStr = yamlFilter(yamlStr)
        try:
            yamlInstance = yaml.load(yamlStr, Loader=yaml.CLoader)
            self.AddToCache(path, yamlInstance)
        except:
            log.LogError('paperDoll::YamlPreloader::Preload - Failed loading yaml for path: {0}'.format(path))

    def Preload_t(self, rootFolder, extensions = None, yamlFilter = None):
        yamlFiles = []
        extensions = extensions or ['.yaml']
        for root, dirs, files in walk.walk(rootFolder):
            for fileName in files:
                fileNameLower = fileName.lower()
                if fileNameLower.endswith(extensions):
                    path = '{0}/{1}'.format(root.lower(), fileNameLower)
                    if path not in self.cache:
                        yamlFiles.append(path)

            BeFrameNice()

        for i in xrange(len(yamlFiles)):
            path = yamlFiles[i]
            t = uthread.new(self._ReadAndAddToCache, path, yamlFilter)
            self._tasklets[t] = True

        if rootFolder:
            log.LogInfo('YamlPreloader:', len(yamlFiles), 'yaml files preloaded from', rootFolder)

    def AddToCache(self, path, instance):
        if path and instance:
            if type(instance) == AvatarPartMetaData:
                AvatarPartMetaData.FillInDefaults(instance)
            self.cache[path.lower()] = instance

    def LoadYaml(self, yamlPath):
        yamlData = self.cache.get(yamlPath.lower(), None)
        if yamlData is None:
            log.LogInfo('Yaml cache miss for', yamlPath)
            yamlData = LoadYamlFileNicely(yamlPath, enableCache=False)
            self.AddToCache(yamlPath, yamlData)
        if yamlData:
            return copy.deepcopy(yamlData)

    def SaveCacheAsPickle(self, outputPath):
        if self.IsLoading():
            log.LogWarn('Waiting for yaml preloading to finish before saving cache')
            while self.IsLoading():
                blue.synchro.Yield()

        pathOnDisk = blue.paths.ResolvePathForWriting(outputPath)
        try:
            with open(pathOnDisk, 'wb') as outputStream:
                cPickle.dump(self.cache, outputStream)
            log.LogInfo('Saved yaml preloading cache to %s' % outputPath)
        except IOError:
            log.LogWarn("Couldn't save yaml preloading cache to %s" % outputPath)

    def LoadCacheFromPickle(self, inputPath):
        whitelist = [copy_reg._reconstructor,
         AvatarPartMetaData,
         dict,
         object]

        def get_whitelist():
            return whitelist

        def find_global(moduleName, className):
            return whitelistpickle.find_global(moduleName, className, get_whitelist)

        def tasklet_proc():
            before_load = time.clock()
            memStream = blue.paths.GetFileContentsWithYield(inputPath)
            before_unpickle = time.clock()
            contents = memStream.Read()
            unpickler = whitelistpickle.cPickleUnpickler(cStringIO.StringIO(contents))
            unpickler.find_global = find_global
            self.cache = unpickler.load()
            after = time.clock()
            duration = after - before_load
            unpickle_duration = after - before_unpickle
            log.LogInfo('YamlPreloader: Cache loaded from %s in %.2f seconds (%.2f seconds unpickling)' % (inputPath, duration, unpickle_duration))

        uthread.new(tasklet_proc)


def LoadYamlFileNicely(pathToFile, enableCache = True):
    if enableCache:
        yamlPreloader = YamlPreloader()
        return yamlPreloader.LoadYaml(pathToFile)
    BeFrameNice()
    if blue.paths.exists(pathToFile):
        r = blue.ResFile()
        try:
            r.Open(pathToFile)
            yamlStr = r.Read()
        finally:
            r.Close()

        log.LogInfo('Parsing data from {0}'.format(pathToFile))
        inst = NastyYamlLoad(yamlStr)
        if not inst:
            log.LogError('PaperDoll: Yaml file corrupt: ', pathToFile)
        return inst


exports = {'paperDoll.LoadYamlFileNicely': LoadYamlFileNicely}
