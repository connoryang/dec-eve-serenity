#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\autoexec.py
import inifile
inifile.Init()
import blue
if blue.pyos.packaged:
    blue.paths.RegisterFileSystemBeforeLocal('Remote')
else:
    blue.paths.RegisterFileSystemAfterLocal('Remote')
import __builtin__
import iocp
import _slsocket as _socket
import os
import sys
import codereloading
if iocp.UsingIOCP():
    import carbonio
    select = None
    _socket.use_carbonio(True)
    carbonio._socket = _socket
    print 'Network layer using: CarbonIO'
    if iocp.LoggingCarbonIO():
        import blue
        print 'installing CarbonIO logging callbacks'
        blue.net.InstallLoggingCallbacks()
else:
    import stacklessio
    import slselect as select
    _socket.use_carbonio(False)
    stacklessio._socket = _socket
sys.modules['_socket'] = _socket
sys.modules['select'] = select
from stacklesslib import monkeypatch
monkeypatch.patch_ssl()
if not blue.pyos.packaged:
    import debuggingutils.pydevdebugging as pydevdebugging
    __builtin__.GOPYCHARM = pydevdebugging.ConnectExeFileToDebugger3
    __builtin__.GOPYCHARM4 = pydevdebugging.ConnectExeFileToDebugger4
    __builtin__.NOPYCHARM = pydevdebugging.StopPycharm
    allArgs = blue.pyos.GetArg()
    containsToolParam = False
    for arg in allArgs:
        if arg.startswith('/tools='):
            containsToolParam = True
            break

    if not blue.sysinfo.isTransgaming and '/jessica' not in allArgs and not containsToolParam:
        import devenv
        sys.path.append(os.path.join(devenv.SHARED_TOOLS_PYTHONDIR, 'lib27xccp'))
        import packageaddwatcher
        packageaddwatcher.guard_metapath(boot.role)
    from debuggingutils.coverageutils import start_coverage_if_enabled
    start_coverage_if_enabled(prefs, blue, boot.role)
if prefs.ini.GetValue('GOPYCHARM', False):
    GOPYCHARM()
try:
    blue.SetCrashKeyValues(u'role', unicode(boot.role))
    blue.SetCrashKeyValues(u'build', unicode(boot.build))
    orgArgs = blue.pyos.GetArg()
    args = ''
    for each in orgArgs:
        if not each.startswith('/path'):
            args += each
            args += ' '

    blue.SetCrashKeyValues(u'startupArgs', unicode(args))
    bitCount = blue.sysinfo.cpu.bitCount
    computerInfo = {'memoryPhysical': blue.os.GlobalMemoryStatus()[1][1] / 1024,
     'cpuArchitecture': blue.pyos.GetEnv().get('PROCESSOR_ARCHITECTURE', None),
     'cpuIdentifier': blue.pyos.GetEnv().get('PROCESSOR_IDENTIFIER', None),
     'cpuLevel': int(blue.pyos.GetEnv().get('PROCESSOR_LEVEL', 0)),
     'cpuRevision': int(blue.pyos.GetEnv().get('PROCESSOR_REVISION', 0), 16),
     'cpuCount': int(blue.pyos.GetEnv().get('NUMBER_OF_PROCESSORS', 0)),
     'cpuMHz': int(round(blue.os.GetCycles()[1] / 1000.0, 1)),
     'cpuBitCount': bitCount,
     'osMajorVersion': blue.sysinfo.os.majorVersion,
     'osMinorVersion': blue.sysinfo.os.minorVersion,
     'osBuild': blue.sysinfo.os.buildNumber,
     'osPatch': blue.sysinfo.os.patch,
     'osPlatform': 2}
    for key, val in computerInfo.iteritems():
        blue.SetCrashKeyValues(unicode(key), unicode(val))

except RuntimeError:
    pass

if '/disableSake' not in blue.pyos.GetArg():
    codereloading.InstallSakeAutocompiler()
import inittools
tool = inittools.gettool()
if tool is None:
    __import__('autoexec_%s' % boot.role)
else:

    def run():
        inittools.run_(tool)
