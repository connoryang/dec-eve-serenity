#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evewar\util.py
import blue

def GetWarEntity(corporationID, allianceID):
    if allianceID:
        return allianceID
    else:
        return corporationID


def HasActiveOrPendingWars(wars):
    for war in wars.itervalues():
        if war.timeFinished is None or war.timeFinished > blue.os.GetWallclockTime():
            return True

    return False


def IsWarInHostileState(row, currentTime):
    if row.timeFinished is None or currentTime < row.timeFinished:
        if currentTime > row.timeStarted:
            return 1
    return 0


def IsAtWar(wars, entities, currentTime):
    for war in wars:
        if war.declaredByID not in entities:
            continue
        if not IsWarInHostileState(war, currentTime):
            continue
        if war.againstID in entities:
            return war.warID
        for allyID, row in war.allies.iteritems():
            if allyID in entities:
                if row.timeStarted < currentTime < row.timeFinished:
                    return war.warID
                break

    return False
