#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\loggly\__init__.py
import blue
import serverInfo
import carbonui.const as uiconst
import os
LOGGLY_BASE_URL = 'https://logs-01.loggly.com/bulk/5072c2d8-27ea-4721-a513-5d7341ffe23b'

def _IsLogglyWanted():
    server = serverInfo.GetServerInfo()
    if server.isLive:
        wanted = bool(prefs.GetValue('logglyWanted', 0))
    else:
        wanted = True
    return wanted


def Initialize():
    if blue.IsLogglyEnabled():
        return
    if not _IsLogglyWanted():
        return
    accepted = bool(prefs.GetValue('logglyAccepted', 0))
    server = serverInfo.GetServerInfo()
    if server.name == 'localhost':
        accepted = True
    if accepted:
        logglySession = 'ec' + str(blue.os.GetWallclockTimeNow())
        print 'Enabling Loggly logging with session', logglySession
        tags = ['http',
         'eveclient',
         server.name,
         str(boot.build)]
        if server.name == 'localhost':
            computer_name = os.getenv('COMPUTERNAME')
            if computer_name:
                tags.append(computer_name)
        platform = 'Win'
        if blue.sysinfo.isTransgaming:
            platform = 'Mac'
        elif blue.sysinfo.isWine:
            platform = 'Linux'
        tags.append(platform)
        osVersion = '%d.%d.%d' % (blue.sysinfo.os.majorVersion, blue.sysinfo.os.minorVersion, blue.sysinfo.os.buildNumber)
        tags.append(osVersion)
        logglyUrl = LOGGLY_BASE_URL + '/tag/' + ','.join(tags)
        blue.EnableLogglyLogging(2, logglyUrl, logglySession)


def GetPermission():
    if not _IsLogglyWanted():
        return
    accepted = bool(prefs.GetValue('logglyAccepted', 0))
    if accepted:
        return
    if eve.Message('AskLogglyPermission', buttons=uiconst.YESNO) == uiconst.ID_YES:
        prefs.SetValue('logglyAccepted', 1)
    else:
        blue.os.Terminate()
