#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\serverInfo.py
import logmodule
import utillib

def _GetServerIP(serverName):
    return '{}.servers.eveonline.com'.format(serverName)


LIVE_SERVER = _GetServerIP('tranquility')
TEST_SERVER1 = _GetServerIP('singularity')
TEST_SERVER2 = _GetServerIP('multiplicity')
TEST_SERVER3 = _GetServerIP('duality')
WEB_EVE = 'http://client.eveonline.com'
SERVERS = [('Tranquility', LIVE_SERVER),
 ('Test Server (Singularity)', TEST_SERVER1),
 ('Test Server (Multiplicity)', TEST_SERVER2),
 ('Test Server (Duality)', TEST_SERVER3),
 ('Singularity', TEST_SERVER1),
 ('Multiplicity', TEST_SERVER2),
 ('Duality', TEST_SERVER3)]
if boot.region == 'optic':
    LIVE_SERVER1 = '211.144.214.72'
    LIVE_SERVER2 = '114.80.74.72'
    TEST_SERVER1 = 'beta.eve.gtgame.com.cn'
    TEST_SERVER2 = None
    TEST_SERVER3 = None
    WEB_EVE = 'http://eve.tiancity.com/client'
    SERVERS = [(u'\u6668\u66e6', LIVE_SERVER1), (u'\u6df7\u6c8c', LIVE_SERVER2)]

def GetServerIP(checkServerName):
    for serverName, serverIP in SERVERS:
        if checkServerName.lower() == serverName.lower():
            return serverIP

    return checkServerName


def GetServerName(checkServerIP):
    for serverName, serverIP in SERVERS:
        if serverIP.lower() == checkServerIP.lower():
            return serverName

    return checkServerIP


def GetServerInfo():
    serverName = utillib.GetServerName()
    ip = GetServerIP(serverName)
    servers = [['Tranquility', _GetServerIP('tranquility'), _GetServerIP('tranquilityesp')],
     ['Multiplicity', _GetServerIP('multiplicity'), _GetServerIP('multiplicityesp')],
     ['Singularity', _GetServerIP('singularity'), _GetServerIP('singularityesp')],
     ['Duality', _GetServerIP('duality'), _GetServerIP('dualityesp')],
     ['Chaos', _GetServerIP('chaos'), _GetServerIP('chaosesp')],
     ['Buckingham', _GetServerIP('buckingham'), _GetServerIP('buckinghamesp')],
     ['Adam', 'Adam', 'Adam'],
     ['localhost', 'localhost', 'localhost']]
    foundServerInfo = False
    espUrl = ip
    for s in servers:
        if s[1] == ip:
            espUrl = s[2]
            serverName = s[0]
            foundServerInfo = True
            break

    if ':' not in espUrl:
        espUrl += ':50001'
    isLive = True
    if boot.region != 'optic' and not IsLiveServer(ip):
        isLive = False
    try:
        inf = None
        import __builtin__
        if hasattr(__builtin__, 'sm') and 'machoNet' in sm.services:
            inf = sm.GetService('machoNet').GetGlobalConfig().get('serverInfo')
            if inf:
                lst = inf.split(',')
                if len(lst) != 4:
                    logmodule.general.Log("Broken Server info in Global Config! It should contain 'serverName,ip,espIP:espPort,isLive'", logmodule.LGERR)
                else:
                    l = lst[3]
                    if l.lower() == 'false':
                        l = 0
                    elif l.lower() == 'true':
                        l = 1
                    isLive = bool(int(l))
                    serverName = lst[0]
                    ip = lst[1]
                    foundServerInfo = True
                    espUrl = lst[2]
                    if ':' not in espUrl:
                        logmodule.general.Log("Broken Server info in Global Config! ESP URL missing port. Full config should be 'serverName,ip,espIP:espPort,isLive'. Defaulting to port 50001", logmodule.LGWARN)
                        espUrl += ':50001'
                    logmodule.general.Log('Returning Server info from Global Config. serverName = %s, IP = %s, espUrl = %s, live = %s' % (serverName,
                     ip,
                     espUrl,
                     isLive))
            elif not foundServerInfo:
                logmodule.general.Log('The server you are connected to, %s, does not supply serverInfo. This can be configured in globalconfig: serverInfo=serverName,ip,espIP:espPort,isLive' % ip)
    except Exception as e:
        logmodule.general.Log('Could not get server info from server. Info: %s, Error: %s' % (inf, e), logmodule.LGERR)

    def safeGetEveAttr(attr):
        try:
            return getattr(eve, attr)
        except (NameError, AttributeError):
            return None

    serverInfo = utillib.KeyVal(name=serverName, IP=ip, espUrl=espUrl, isLive=isLive, version=safeGetEveAttr('serverVersion'), build=safeGetEveAttr('serverBuild'))
    return serverInfo


def IsLiveServer(ip):
    return ip in (LIVE_SERVER, '87.237.38.200')
