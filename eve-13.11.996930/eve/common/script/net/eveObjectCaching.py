#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\net\eveObjectCaching.py
import service
import svc
globals().update(service.consts)

class EveObjectCachingSvc(svc.objectCaching):
    __guid__ = 'svc.eveObjectCaching'
    __replaceservice__ = 'objectCaching'
    __cachedsessionvariables__ = ['regionid',
     'constellationid',
     'stationid',
     'solarsystemid',
     'locationid',
     'languageID']
