#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\authoring\attributeAuthoring.py
import ast

class AttributeAuthoring(object):

    def __init__(self, BSD, attributeInfo):
        self.BSD = BSD
        self.attributeInfo = attributeInfo

    def TypeSetAttribute(self, userID, typeID, attributeID, value, skipReload = 0, changeID = None):
        try:
            value = ast.literal_eval(value)
        except ValueError:
            pass

        value = float(value)
        isBasicAttribute = self.attributeInfo.IsBasicAttribute(attributeID)
        if isBasicAttribute:
            self.TypeModifyBasicAttribute(userID, typeID, attributeID, value, skipReload, changeID)
        elif attributeID in self.attributeInfo.GetAttributesByTypeID(typeID):
            if not self._IsTypeAttributeValueUnchanged(typeID, attributeID, value):
                self.TypeModifyAttribute(userID, typeID, attributeID, value, skipReload, changeID)
        elif not isBasicAttribute:
            self.TypeAddAttribute(userID, typeID, attributeID, value, skipReload)
        else:
            raise RuntimeError('ModifyingTypeTableNotImplemented', typeID, attributeID)

    def TypeAddAttribute(self, userID, typeID, attributeID, value, skipReload = 0):
        self.BSD.RevisionAddKey(userID, None, 'dogma', 'typeAttributesTx', typeID, attributeID, None, valueFloat=value)

    def TypeModifyAttribute(self, userID, typeID, attributeID, value, skipReload, changeID):
        self.BSD.RevisionEditKey(userID, changeID, 'dogma', 'typeAttributesTx', typeID, attributeID, None, valueFloat=value)

    def TypeModifyBasicAttribute(self, userID, typeID, attributeID, value, skipReload, changeID):
        attributeName = self.attributeInfo.GetAttributeName(attributeID)
        kwargs = {attributeName: value}
        self.BSD.RevisionEditKey(userID, changeID, 'inventory', 'typesTx', typeID, None, None, **kwargs)

    def TypeRemoveAttribute(self, userID, typeID, attributeID, skipReload = 0):
        if attributeID in self.attributeInfo.GetAttributesByTypeID(typeID):
            self.BSD.RevisionDeleteKey(userID, None, 'dogma', 'typeAttributesTx', typeID, attributeID)

    def GroupSetAttribute(self, userID, groupID, attributeID, value, skipReload = 0):
        for row in self.attributeInfo.GetTypesByGroupID(groupID):
            self.TypeSetAttribute(userID, row.typeID, attributeID, value, skipReload=skipReload)

    def GroupRemoveAttribute(self, userID, groupID, attributeID, skipReload = 0):
        for row in self.attributeInfo.GetTypesByGroupID(groupID):
            self.TypeRemoveAttribute(userID, row.typeID, attributeID)

    def _IsTypeAttributeValueUnchanged(self, typeID, attributeID, newValue):
        currentValue = self.attributeInfo.GetAttributeValueByTypeID(typeID, attributeID)
        return currentValue == newValue

    def TypeAddEffect(self, userID, typeID, effectID, isDefault = 0, skipReload = 0):
        if effectID not in self.attributeInfo.GetEffectIDsByTypeID(typeID):
            self.BSD.RevisionAddKey(userID, None, 'dogma', 'typeEffectsTx', typeID, effectID, None, isDefault=isDefault)

    def TypeRemoveEffect(self, userID, typeID, effectID, skipReload = 0):
        if effectID in self.attributeInfo.GetEffectIDsByTypeID(typeID):
            self.BSD.RevisionDeleteKey(userID, None, 'dogma', 'typeEffectsTx', typeID, effectID)

    def GroupAddEffect(self, userID, groupID, effectID, isDefault = 0, skipReload = 0):
        for row in self.attributeInfo.GetTypesByGroupID(groupID):
            self.TypeAddEffect(userID, row.typeID, effectID, isDefault, skipReload)

    def GroupRemoveEffect(self, userID, groupID, effectID, skipReload = 0):
        for row in self.attributeInfo.GetTypesByGroupID(groupID):
            self.TypeRemoveEffect(userID, row.typeID, effectID, skipReload)

    def TypeAddAttributesAndEffects(self, userID, typeID, attributes, effects):
        self._TypeSetAttributes(userID, typeID, attributes)
        self._TypeAddEffects(userID, typeID, effects)

    def _TypeSetAttributes(self, userID, typeID, attributes):
        for attributeID, value in attributes.iteritems():
            self.TypeSetAttribute(userID, typeID, attributeID, value)

    def _TypeAddEffects(self, userID, typeID, effects):
        for effectID in effects:
            self.TypeAddEffect(userID, typeID, effectID, isDefault=0)

    def TypeRemoveAttributesAndEffects(self, userID, typeID, attributes, effects):
        self._TypeRemoveAttributes(userID, typeID, attributes)
        self._TypeRemoveEffects(userID, typeID, effects)

    def _TypeRemoveAttributes(self, userID, typeID, attributes):
        for attributeID in attributes:
            self.TypeRemoveAttribute(userID, typeID, attributeID)

    def _TypeRemoveEffects(self, userID, typeID, effects):
        for effectID in effects:
            self.TypeRemoveEffect(userID, typeID, effectID)

    def TypeSetBasicAttribute(self, userID, revisionID, typeID, basicAttributes):
        updatedAttributes = self._GetUpdatedBasicAttributesByTypeID(typeID, basicAttributes)
        if updatedAttributes:
            self.BSD.RevisionEdit(userID, None, revisionID, **updatedAttributes)

    def _GetUpdatedBasicAttributesByTypeID(self, typeID, basicAttributes):
        typeBasicAttributes = self.attributeInfo.GetBasicAttributesByTypeID(typeID)
        updatedAttributes = dict(set(basicAttributes.items()) - set(typeBasicAttributes.items()))
        return updatedAttributes
