#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\util\typeConversion.py
conversionTable = {'int': int,
 'float': float,
 'str': str,
 'unicode': unicode}

class ConvertVariableException(Exception):
    pass


def CastValue(type, value):
    if type in conversionTable:
        return conversionTable[type](value)
    raise ConvertVariableException, 'Unknown conversion type -%s-' % type


exports = {'util.CastValue': CastValue}
