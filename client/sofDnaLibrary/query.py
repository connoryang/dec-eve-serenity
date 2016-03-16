#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sofDnaLibrary\query.py
from sofDnaLibrary.dataLookup import GetDefaultTypeDnaInfoForDnaQuery, GetTypeFactionOverridesThatMatchFaction
import time
queryResultCache = {}

def GenerateDnaString(hull, faction, race, dnaAddition = ''):
    dna = '%s:%s:%s' % (hull, faction, race)
    if dnaAddition != '':
        dna += ':%s' % dnaAddition
    return dna


def GetSkinnedDnaOfTypes(hullQuery = '.*', factionQuery = '.*', raceQuery = '.*'):
    typesWithFactionOverrides = GetTypeFactionOverridesThatMatchFaction(factionQuery)
    typesMatchingHullAndRace = GetDefaultTypeDnaInfoForDnaQuery(hullQuery, '.*', raceQuery)
    typeDna = {}
    for typeID, factionOverrideList in typesWithFactionOverrides.iteritems():
        typeInfo = typesMatchingHullAndRace.get(typeID, None)
        if typeInfo is not None:
            typeDna[typeID] = typeDna.get(typeID, [])
            for factionOverride in factionOverrideList:
                typeDna[typeID].append(GenerateDnaString(typeInfo['hull'], factionOverride, typeInfo['race'], typeInfo.get('dnaAddition', '')))

    return typeDna


def GetDefaultDnaOfTypes(hullQuery = '.*', factionQuery = '.*', raceQuery = '.*'):
    typesMatchingHullFactionAndRace = GetDefaultTypeDnaInfoForDnaQuery(hullQuery, factionQuery, raceQuery)
    typeDna = {}
    for typeID, typeInfo in typesMatchingHullFactionAndRace.iteritems():
        typeDna[typeID] = GenerateDnaString(typeInfo['hull'], typeInfo['faction'], typeInfo['race'], typeInfo.get('dnaAddition', ''))

    return typeDna


def GetAllVariationsOfDnaOfTypes(hullQuery = '.*', factionQuery = '.*', raceQuery = '.*'):
    dnaString = GenerateDnaString(hullQuery, factionQuery, raceQuery)
    print "Getting skinned dna for types that match the following dna string '%s'" % dnaString
    skinnedTypeDna = GetSkinnedDnaOfTypes(hullQuery, factionQuery, raceQuery)
    defaultTypeDna = GetDefaultDnaOfTypes(hullQuery, factionQuery, raceQuery)
    typeDna = skinnedTypeDna
    for typeID, dnaString in defaultTypeDna.iteritems():
        typeDna[typeID] = typeDna.get(typeID, [])
        typeDna[typeID].append(dnaString)

    return typeDna


def GetDnaStringMatchingQuery(hullQuery = '.*', factionQuery = '.*', raceQuery = '.*'):
    dnaQuery = GenerateDnaString(hullQuery, factionQuery, raceQuery)
    if dnaQuery in queryResultCache:
        print "Returning cached results for '%s'" % dnaQuery
        return queryResultCache[dnaQuery]
    typeDna = GetAllVariationsOfDnaOfTypes(hullQuery, factionQuery, raceQuery)
    dnaList = []
    for typeDnaList in typeDna.values():
        for dna in typeDnaList:
            if dna not in dnaList:
                dnaList.append(dna)

    queryResultCache[dnaQuery] = dnaList
    return dnaList


if __name__ == '__main__':
    start = time.time()
    dnaResult = GetDnaStringMatchingQuery(hullQuery='asd1_t1', raceQuery='amarr')
    print dnaResult
