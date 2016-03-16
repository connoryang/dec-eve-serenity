#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\authoring\__init__.py
from .attributeAuthoring import AttributeAuthoring as GetAttributeAuthoring
from dogma.authoring.data import DogmaData
import yaml
import dogma.const as dgmconst
import dogma.attributes
import evetypes
NAME_BY_OPERATOR_ID = {dgmconst.dgmAssPostPercent: 'PostPercent',
 dgmconst.dgmAssModAdd: 'ModAdd',
 dgmconst.dgmAssModSub: 'ModSub',
 dgmconst.dgmAssPreMul: 'PreMul',
 dgmconst.dgmAssPostMul: 'PostMul',
 dgmconst.dgmAssPreDiv: 'PreDiv',
 dgmconst.dgmAssPostDiv: 'PostDiv',
 dgmconst.dgmAssPreAssignment: 'PreAssignment',
 dgmconst.dgmAssPostAssignment: 'PostAssignment'}
DOMAINS = ['shipID',
 'charID',
 'targetID',
 'otherID',
 None]

def GetReadableOperatorNames(operatorID):
    return NAME_BY_OPERATOR_ID[operatorID]


def GetFormatterForKey(key):
    return {'groupID': evetypes.GetGroupNameByGroup,
     'skillTypeID': evetypes.GetName,
     'operator': GetReadableOperatorNames,
     'modifiedAttributeID': dogma.attributes.GetName,
     'modifyingAttributeID': dogma.attributes.GetName}.get(key, None)


def PrepareModifierInfo(modifierString):
    modifierInfo = yaml.safe_load(modifierString)
    for modifierDict in modifierInfo:
        for key, value in modifierDict.iteritems():
            if GetFormatterForKey(key) is not None:
                modifierDict[key] = int(value.split(' ')[0])

    return yaml.dump(modifierInfo, default_flow_style=False)
