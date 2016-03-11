#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\util\inspect.py
import types

def IsClassMethod(func):
    if type(func) != types.MethodType:
        return False
    if type(func.im_self) is types.TypeType:
        return True
    return False


def IsStaticMethod(func):
    return type(func) == types.FunctionType


def IsNormalMethod(func):
    if type(func) != types.MethodType:
        return False
    if type(func.im_self) is not types.TypeType:
        return True
    return False


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('util', locals())
