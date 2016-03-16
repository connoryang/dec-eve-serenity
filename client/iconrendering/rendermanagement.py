#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\iconrendering\rendermanagement.py
import contextlib
import os
import time
import yaml
import iconrendering
import iconrendering.photo as photo
import iconrendering.rendersetup as rendersetup
from iconrendering import USAGE_IEC_ICON, USAGE_IEC_RENDER, USAGE_INGAME_ICON
from fsdhelpers import LoadFSDFromResFile

class RenderCancelledError(iconrendering.IconRenderingException):
    pass


class RenderManager(object):

    def __init__(self, resmapper, inventorymapper, logger, outdir, takeonly = None):
        self.logger = logger
        self.outdir = outdir
        self.takeonly = takeonly
        self.resmapper = resmapper
        self.inventoryMapper = inventorymapper
        self.stop = False
        self.blueprintGraphicIDs = None
        logger.info('Starting %s', iconrendering.APPNAME)
        logger.info('Output: %s', outdir)

    def RenderIEC(self):
        with self._TimeIt('All Renderings'):
            self.RenderRenders()
            self.RenderTypes(32)
            self.RenderTypes(64)
            self.CopyIcons()

    def RenderInGameIcons(self):
        with self._TimeIt('In Game Icon Renderings'):
            self._RenderInGame()

    def RenderTypes(self, size):
        with self._TimeIt('Types'):
            self._RenderAllTypes('Types', size, filterFunc=rendersetup.FilterForTypes, usage=USAGE_IEC_ICON)

    def RenderRenders(self):
        with self._TimeIt('Renders'):
            self._RenderAllTypes('Renders', 512, filterFunc=rendersetup.FilterForRenders, usage=USAGE_IEC_RENDER)

    def CopyIcons(self):
        with self._TimeIt('Icons'):
            rendersetup.CopyIconDirs(self.outdir)

    def _RenderInGame(self):
        blueprintIDs = self.GetBlueprintGraphicIDs()
        for vals in rendersetup.YieldAllRenderFuncsAndArgsForGraphics(self.resmapper, self.outdir, self.logger, blueprintIDs):
            if vals is None:
                continue
            func, funcargs, funckwargs = vals
            funcname = getattr(func, '__name__', 'no func name')
            if self.stop:
                raise RenderCancelledError()
            try:
                if os.path.exists(funcargs[0]):
                    self.logger.debug('File exists! %s' % funcargs[0])
                else:
                    self.logger.debug('Invoking: %s, %s', funcname, funcargs)
                    func(*funcargs, **funckwargs)
            except Exception:
                self.logger.warn('Failed to render: %s, %s, %s', funcname, funcargs, funckwargs)

    def _YieldRenderFuncAndArgsForTypes(self, outdir, size, **kwargs):
        return rendersetup.YieldAllRenderFuncsAndArgsForTypes(self.resmapper, self.inventoryMapper, outdir, size, self.logger, **kwargs)

    def _RenderAllTypes(self, subdir, size, **yieldKwargs):
        outdir = os.path.join(self.outdir, subdir)
        renderCount = 0
        if self.takeonly:
            self.logger.warn('Rendering only %s images.', self.takeonly)
        if self.stop:
            raise RenderCancelledError()
        for vals in self._YieldRenderFuncAndArgsForTypes(outdir, size, **yieldKwargs):
            if self.takeonly and renderCount > self.takeonly:
                break
            if vals is None:
                continue
            func, funcargs, funckwargs = vals
            funcname = getattr(func, '__name__', 'no func name')
            if self.stop:
                raise RenderCancelledError()
            try:
                if os.path.exists(funcargs[0]):
                    self.logger.debug('File exists! %s' % funcargs[0])
                else:
                    self.logger.debug('Invoking: %s, %s', funcname, funcargs)
                    self._Invoke(func, funcargs, funckwargs)
            except Exception:
                self._OnRenderError(size, funcname, funcargs)

            renderCount += 1

    def _Invoke(self, func, funcargs, funckwargs):
        return func(*funcargs, **funckwargs)

    def RenderSingle(self, resPath = None, dnaString = None):
        if resPath is None and dnaString is None:
            self.logger.warn('Neither resPath nor dna was supplied!')
            return
        with self._TimeIt('RenderSingle'):
            self._RenderSingle([64, 128], resPath=resPath, dnaString=dnaString)

    def _RenderSingle(self, sizes, resPath = None, dnaString = None):
        graphicIDs = self.resmapper.GetGraphicIdsForGraphicFile(resPath)
        graphicIDs += self.resmapper.GetGraphicIdsForSOFData(dnaString)
        if len(graphicIDs) == 0:
            self.logger.warn('No graphicIDs found for resPath: "%s" and dnaString: "%s"' % (resPath, dnaString))
            self.logger.warn('No icons generated')
            return
        blueprintIDs = self.GetBlueprintGraphicIDs()
        for vals in rendersetup.YieldAllRenderFuncsAndArgsForGraphics(self.resmapper, self.outdir, self.logger, blueprintIDs, graphicIDs=graphicIDs):
            if vals is None:
                continue
            func, funcargs, funckwargs = vals
            funcname = getattr(func, '__name__', 'no func name')
            size = funckwargs['size']
            if self.stop:
                raise RenderCancelledError()
            try:
                if os.path.exists(funcargs[0]):
                    self.logger.debug('File exists! %s' % funcargs[0])
                else:
                    self.logger.debug('Invoking: %s, %s', funcname, funcargs, funckwargs)
                    func(*funcargs, **funckwargs)
            except Exception:
                self._OnRenderError(size, funcname, funcargs)

    def Stop(self):
        self.logger.info('Stop requested.')
        self.stop = True

    def _OnRenderError(self, size, funcname, funcargs, funckwargs = {}):
        self.logger.error('Error: %s, %s, %s', funcname, funcargs, funckwargs)
        self.logger.debug('Fallback: RenderIcon(%s size=%s)', funcargs[0], size)
        photo.RenderIcon(funcargs[0], size=size, iconPath=rendersetup.FALLBACK_ICON)

    def _CollectBlueprintGraphicIDs(self):
        graphicIDs = set()
        root = os.path.abspath('../../eve/staticData/blueprints')
        for file in os.listdir(root):
            if not file.endswith('.staticdata'):
                continue
            with open(os.path.join(root, file)) as stream:
                blueprintData = yaml.load(stream)
                activities = blueprintData.get('activities', {})
                manufacturing = activities.get('manufacturing', {})
                products = manufacturing.get('products', [])
                for product in products:
                    typeID = product['typeID']
                    graphicIDs.add(self.resmapper.GetGraphicIDForTypeID(typeID))

        self.blueprintGraphicIDs = graphicIDs

    def GetBlueprintGraphicIDs(self):
        if self.blueprintGraphicIDs is None:
            with self._TimeIt('Collecting blueprint graphicIDs'):
                self._CollectBlueprintGraphicIDs()
        return self.blueprintGraphicIDs

    @contextlib.contextmanager
    def _TimeIt(self, name):
        t = time.clock()
        self.logger.info('Starting %s', name)
        yield
        self.logger.info('Finished %s in %ds', name, time.clock() - t)
