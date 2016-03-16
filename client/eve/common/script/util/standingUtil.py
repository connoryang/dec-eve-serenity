#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\util\standingUtil.py
CRIMINAL_FACTIONS = (500010, 500011, 500012, 500019, 500020)

def GetStandingBonus(fromStanding, fromFactionID, skills):
    bonus = 0.0
    bonusType = None
    if fromStanding < 0.0:
        skill = skills.get(const.typeDiplomacy, None)
        if skill:
            bonus = skill.skillLevel * 0.4
        bonusType = const.typeDiplomacy
    elif fromStanding > 0.0:
        if fromFactionID is not None and fromFactionID in (500010, 500011, 500012, 500019, 500020):
            skill = skills.get(const.typeCriminalConnections, None)
            if skill:
                bonus = skill.skillLevel * 0.4
            bonusType = const.typeCriminalConnections
        else:
            skill = skills.get(const.typeConnections, None)
            if skill:
                bonus = skill.skillLevel * 0.4
            bonusType = const.typeConnections
    return (bonusType, bonus)


exports = {'standingUtil.GetStandingBonus': GetStandingBonus}
