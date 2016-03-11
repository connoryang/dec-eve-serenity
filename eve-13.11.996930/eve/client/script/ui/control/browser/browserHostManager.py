#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\browser\browserHostManager.py
import corebrowserutil
import svc
try:
    import ccpBrowserHost
except ImportError:
    pass

class BrowserHostManager(svc.browserHostManager):
    __guid__ = 'svc.eveBrowserHostManager'
    __replaceservice__ = 'browserHostManager'
    __startupdependencies__ = ['settings']

    def AppRun(self, *args):
        pass

    def AppGetBrowserCachePath(self):
        return settings.public.generic.Get('BrowserCache', corebrowserutil.DefaultCachePath())
