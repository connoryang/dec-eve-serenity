#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\inifile.py
import blue
import sys
blue.pyos.taskletTimer.active = True
sys.setmemcontextsactive(True)
import os
import warnings
from eveprefs import DEFAULT_ENCODING, Handler
from eveprefs.iniformat import IniIniFile as IniFile
import whitelistpickle
import builtinmangler
builtinmangler.MangleBuiltins()
os.stat_float_times(False)
whitelistpickle.patch_cPickle()

class InstallWarningHandler(object):

    def __init__(self):
        self.oldhandler = warnings.showwarning
        warnings.showwarning = self.ShowWarning

    def __del__(self):
        if warnings:
            warnings.showwarning = self.oldhandler

    def ShowWarning(self, message, category, filename, lineno, file = None):
        import logmodule
        string = warnings.formatwarning(message, category, filename, lineno)
        logmodule.LogTraceback(extraText=string, severity=logmodule.LGWARN, nthParent=3)
        if not file:
            file = sys.stderr
        print >> file, string


warningHandler = InstallWarningHandler()

def SetClusterPrefs(prefsinst):
    if prefsinst.GetValue('clusterName', None) is None:
        prefsinst.clusterName = blue.pyos.GetEnv().get('COMPUTERNAME', 'LOCALHOST') + '@' + blue.pyos.GetEnv().get('USERDOMAIN', 'NODOMAIN')
    if prefsinst.GetValue('clusterMode', None) is None:
        prefsinst.clusterMode = 'LOCAL'
    prefsinst.clusterName = prefsinst.clusterName.upper()
    prefsinst.clusterMode = prefsinst.clusterMode.upper()


boot = None
prefs = None

def Init():
    global prefs
    global boot
    import __builtin__
    if hasattr(__builtin__, 'prefs'):
        return (boot, prefs)
    if blue.pyos.packaged and 'client' in blue.paths.ResolvePath(u'app:/'):
        handler = Handler(IniFile('start', blue.paths.ResolvePath(u'root:/'), 1))
    else:
        handler = Handler(IniFile('start', blue.paths.ResolvePath(u'app:/'), 1))
    __builtin__.boot = handler
    boot = handler
    packagedClient = blue.pyos.packaged and handler.role == 'client'
    commonPath = blue.paths.ResolvePath(u'root:/common/')
    if packagedClient:
        commonPath = blue.paths.ResolvePath(u'root:/')
    handler.keyval.update(IniFile('common', commonPath, 1).keyval)
    settingsProfile = blue.os.GetStartupArgValue('settingsprofile')
    if settingsProfile != '':
        settingsProfile = '_' + settingsProfile
    settingsProfile = settingsProfile.replace('\\', '_').replace('/', '_')
    if '/LUA:OFF' in blue.pyos.GetArg() or boot.GetValue('role', None) != 'client':
        if boot.GetValue('role', None) == 'client':
            blue.paths.SetSearchPath('cache', blue.paths.ResolvePathForWriting(u'root:/cache'))
            blue.paths.SetSearchPath('settings', blue.paths.ResolvePathForWriting(u'root:/settings%s' % settingsProfile))
        else:
            blue.paths.SetSearchPath('cache', blue.paths.ResolvePathForWriting(u'app:/cache'))
            blue.paths.SetSearchPath('settings', blue.paths.ResolvePathForWriting(u'app:/settings%s' % settingsProfile))
        cachepath = blue.paths.ResolvePathForWriting(u'cache:/')
        settingspath = blue.paths.ResolvePathForWriting(u'settings:/')
        prefsfilepath = cachepath
    else:
        import utillib as util
        cachedir = util.GetClientUniqueFolderName()
        root = blue.sysinfo.GetUserApplicationDataDirectory() + u'\\CCP\\EVE\\'
        root = root.replace('\\', '/')
        root = root + cachedir + u'/'
        settingspath = root + u'settings%s/' % settingsProfile
        cachepath = root + u'cache/'
        blue.paths.SetSearchPath('cache', cachepath)
        blue.paths.SetSearchPath('settings', settingspath)
        prefsfilepath = settingspath.replace('\\', '/')
    for path in (settingspath, cachepath):
        try:
            os.makedirs(path)
        except OSError:
            pass

    handler = Handler(IniFile('prefs', prefsfilepath))
    __builtin__.prefs = handler
    prefs = handler
    sys.setdefaultencoding(DEFAULT_ENCODING)
    if boot.role == 'server':
        if '/proxy' in blue.pyos.GetArg():
            boot.role = 'proxy'
    SetClusterPrefs(handler)
    if boot.role in ('proxy', 'server') and prefs.GetValue('mpi', False):
        import MPI
    return (boot, prefs)
