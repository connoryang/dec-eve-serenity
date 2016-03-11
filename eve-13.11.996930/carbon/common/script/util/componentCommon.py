#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\util\componentCommon.py


def UnpackStringToTuple(string, conversionFunc = None):
    elementList = eval(string)
    if conversionFunc is not None:
        elementList = [ conversionFunc(element) for element in elementList ]
    return tuple(elementList)


exports = {'util.UnpackStringToTuple': UnpackStringToTuple}
