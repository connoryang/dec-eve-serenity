#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\dogma\clientDogmaStaticSvc.py
import svc
import evetypes
from collections import defaultdict

class AttributesByTypeLookupDict(defaultdict):

    def __init__(self, typeID, *args, **kwargs):
        defaultdict.__init__(self, *args, **kwargs)
        self.typeID = typeID

    def __missing__(self, attributeID):
        for attribute in cfg.dgmtypeattribs.get(self.typeID, []):
            if attribute.attributeID == attributeID:
                return attribute.value

        ret = None
        if attributeID == const.attributeMass:
            ret = evetypes.GetMass(self.typeID)
        elif attributeID == const.attributeCapacity:
            ret = evetypes.GetCapacity(self.typeID)
        elif attributeID == const.attributeVolume:
            ret = evetypes.GetVolume(self.typeID)
        if ret is None:
            raise KeyError(attributeID)
        else:
            self[attributeID] = ret
            return ret


class AttributesByTypeAttribute(defaultdict):

    def __missing__(self, typeID):
        if typeID not in cfg.dgmtypeattribs:
            raise KeyError(typeID)
        return AttributesByTypeLookupDict(typeID)


class ClientDogmaStaticSvc(svc.baseDogmaStaticSvc):
    __guid__ = 'svc.clientDogmaStaticSvc'

    def LoadTypeAttributes(self, *args, **kwargs):
        self.attributesByTypeAttribute = AttributesByTypeAttribute()

    def TypeHasAttribute(self, typeID, attributeID):
        try:
            for row in cfg.dgmtypeattribs[typeID]:
                if row.attributeID == attributeID:
                    return True

            return False
        except KeyError:
            return False
