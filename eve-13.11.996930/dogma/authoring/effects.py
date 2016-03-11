#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\authoring\effects.py
import yaml
effectAttributeIDs = {'durationAttributeID',
 'trackingSpeedAttributeID',
 'dischargeAttributeID',
 'rangeAttributeID',
 'falloffAttributeID',
 'npcUsageChanceAttributeID',
 'npcActivationChanceAttributeID',
 'fittingUsageChanceAttributeID'}

def GetAttributesRelatedToEffect(effectID, data):
    effect = data.GetEffect(effectID)
    attributeIDs = set()
    for attribute in effectAttributeIDs:
        attributeID = getattr(effect, attribute)
        if attributeID:
            attributeIDs.add(attributeID)

    if effect.modifierInfo is not None:
        for expression in yaml.safe_load(effect.modifierInfo):
            attributeIDs.add(int(expression['modifyingAttributeID']))

    return attributeIDs
