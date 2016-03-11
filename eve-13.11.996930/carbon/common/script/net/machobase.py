#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\net\machobase.py
from hashlib import sha1
import sys
import types
import blue
import carbon.common.script.net.GPSExceptions as GPS
import locks
import eve.common.script.net.eveMachoNetVersion as eveMachoNetVersion
import log
mode = boot.role
version = eveMachoNetVersion.machoVersion
packetTypeChannelMap = {const.cluster.MACHONETMSG_TYPE_SESSIONCHANGENOTIFICATION: 'sessionchange',
 const.cluster.MACHONETMSG_TYPE_SESSIONINITIALSTATENOTIFICATION: 'sessionchange'}

def Dumps(packet):
    return blue.marshal.Save(packet, None)


def Loads(packet):
    ret = blue.marshal.Load(packet, skipCrcCheck=True)
    if isinstance(ret, GPS.GPSTransportClosed):
        log.general.Log('Raising a GPSTransportClosed exception from remote')
        raise ret
    return ret


def SanitizedGetObjectID(object):
    if type(object) == types.InstanceType:
        if not isinstance(object, Exception):
            return strx(object)


def SanitizedParseObjectID(objectID):
    return objectID


def DumpsSanitized(what):
    return blue.marshal.Save(what, SanitizedGetObjectID)


def LoadsSanitized(what):
    ret = blue.marshal.Load(what, SanitizedParseObjectID)
    if isinstance(ret, GPS.GPSTransportClosed):
        log.general.Log('Raising a GPSTransportClosed exception from remote')
        raise ret
    return ret


def PasswordHash(userName, password):
    unicodeUserName = unicode(userName).strip()
    unicodePassword = unicode(password)
    salt = buffer(unicodeUserName.lower())
    hash = sha1(buffer(unicodePassword) + salt)
    for i in xrange(1000):
        blue.pyos.BeNice()
        hash = sha1(buffer(hash.digest()) + salt)

    return hash.digest()


def AssignLogName(obj):
    try:
        name = obj.__logname__
    except AttributeError:
        try:
            name = GetLogName(obj)
            setattr(obj, '__logname__', name)
        except StandardError:
            pass

    return name


def GetLogName(obj):
    try:
        if hasattr(obj, '__guid__'):
            name = obj.__guid__
            s = name.split('.')
            if len(s) > 1:
                name = s[1]
        else:
            name = obj.__class__.__name__
    except:
        name = 'CrappyClass %s' % str(obj)
        sys.exc_clear()

    return name


def ThrottledCall(key, boundMethod, *args):
    logger = sm.GetService('machoNet').LogInfo
    with locks.TempLock(key, locks.RLock) as t:
        if hasattr(t, 'result'):
            logger('No need to cross the wire for', key, 'found throttler result from', (blue.os.GetWallclockTime() - t.resultTime) / const.uSEC, 'microseconds ago:', repr(t.result)[:128])
            ret = t.result
            if t.nWaiting == 0:
                logger('No more consumers, invalidating cached result', repr(t.result)[:128])
                del t.result
        else:
            ret = boundMethod(*args)
            if t.nWaiting > 0:
                t.result = ret
                t.resultTime = blue.os.GetWallclockTime()
                logger('Sharing result for call', key, 'at', t.resultTime, 'for', t.nWaiting, 'waiting threads:', repr(t.result)[:128])
    return ret
