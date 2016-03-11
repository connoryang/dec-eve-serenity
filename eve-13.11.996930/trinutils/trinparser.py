#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\trinutils\trinparser.py
import blue
import trinity
import yamlext

def DictToTrinityParser(trinityrecipe, persistedAttributesOnly = True):
    dr = blue.DictReader()
    dr.persistedAttributesOnly = persistedAttributesOnly
    result = dr.CreateObject(trinityrecipe)
    blue.resMan.Wait()
    return result


def TrinityToDict(blueobj):
    asStr = blue.resMan.SaveObjectToYamlString(blueobj)
    return yamlext.loads(asStr)
