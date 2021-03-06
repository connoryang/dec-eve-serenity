#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\sys\dbrow.py
import util
from timerstuff import ClockThis
import telemetry

def LookupConstValue(name, default = '.exception'):
    return ClockThis('SKITMIX::LookupConstValue', _LookupConstValue, name, default, False)


def ConstValueExists(name):
    return ClockThis('SKITMIX::LookupConstValue', _LookupConstValue, name, '', True)


constMap = {}

@telemetry.ZONE_FUNCTION
def _LookupConstValue(name, default, justChecking):
    if not constMap:

        @telemetry.ZONE_FUNCTION
        def MakeReverseConstValues(constMap):
            sets = [[[],
              'category',
              '_categoryName',
              'categoryID'],
             [[],
              'group',
              '_groupName',
              'groupID'],
             [cfg.invmetagroups.data.itervalues(),
              'metaGroup',
              '_metaGroupName',
              'metaGroupID'],
             [[],
              'type',
              '_typeName',
              'typeID'],
             [cfg.dgmattribs,
              'attribute',
              'attributeName',
              'attributeID'],
             [cfg.dgmeffects,
              'effect',
              'effectName',
              'effectID']]
            for rs, prefix, colName, constID in sets:
                for row in rs:
                    constMap[util.MakeConstantName(getattr(row, colName, ''), prefix)] = getattr(row, constID, 0)

        ClockThis('^boot::MakeReverseConstValues', MakeReverseConstValues, constMap)
    if justChecking:
        return name in constMap or name in const.__dict__
    if name in constMap:
        return constMap[name]
    if name in const.__dict__:
        return const.__dict__[name]
    if default != '.exception':
        return default
    raise AttributeError("There's no legacy const value called '%s'" % name)


exports = {'util.LookupConstValue': LookupConstValue,
 'util.ConstValueExists': ConstValueExists}
