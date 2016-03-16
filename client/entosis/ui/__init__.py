#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\entosis\ui\__init__.py


def IsSameCaptureTeam(allianceID, teamID):
    if teamID is None or allianceID is None:
        return False
    if teamID > 0 and teamID == allianceID:
        return True
    if teamID < 0 and -teamID != allianceID:
        return True
    return False
