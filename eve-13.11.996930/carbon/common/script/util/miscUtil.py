#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\util\miscUtil.py
import blue

def GetCommonResourcePath(path):
    return path


def GetCommonResource(path):
    resourceFile = blue.ResFile()
    path = GetCommonResourcePath(path)
    result = resourceFile.Open(path)
    if result:
        return resourceFile
    else:
        return None


def CommonResourceExists(path):
    path = GetCommonResourcePath(path)
    return blue.paths.exists(path)


def IsInstance_BlueType(obj, name):
    return hasattr(obj, '__bluetype__') and obj.__bluetype__.find(name) >= 0


def Flatten(l, ltypes = (list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]

        i += 1

    return ltype(l)


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('miscUtil', locals())
