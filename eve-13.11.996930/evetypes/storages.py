#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evetypes\storages.py
import fsdlite
import collections
_typeAttributes = ['basePrice',
 'capacity',
 'certificateTemplate',
 'copyTypeID',
 'descriptionID',
 'factionID',
 'graphicID',
 'groupID',
 'iconID',
 'isisGroupID',
 'marketGroupID',
 'mass',
 'portionSize',
 'published',
 'raceID',
 'radius',
 'sofMaterialSetID',
 'sofFactionName',
 'soundID',
 'typeID',
 'typeNameID',
 'volume']
_groupAttributes = ['anchorable',
 'anchored',
 'categoryID',
 'fittableNonSingleton',
 'groupID',
 'groupNameID',
 'iconID',
 'published',
 'useBasePrice']
_categoryAttributes = ['categoryID',
 'categoryNameID',
 'iconID',
 'published']
_typeIndexes = ['groupID.(?P<groupID>[0-9]+)$', 'marketGroupID.(?P<marketGroupID>[0-9]+)$']
_groupIndexes = ['categoryID.(?P<categoryID>[0-9]+)$']

def TypeStorage():
    try:
        return TypeStorage._storage
    except AttributeError:
        eveTypeTuple = collections.namedtuple('eveTypeTuple', _typeAttributes)
        TypeStorage._storage = fsdlite.EveStorage(data='evetypes/types', cache='evetypes.static', mapping=[('$', eveTypeTuple)], indexes=_typeIndexes, coerce=int)
        return TypeStorage._storage


def GroupStorage():
    try:
        return GroupStorage._storage
    except AttributeError:
        eveGroupTuple = collections.namedtuple('eveGroupTuple', _groupAttributes)
        GroupStorage._storage = fsdlite.EveStorage(data='evetypes/groups', cache='evegroups.static', mapping=[('$', eveGroupTuple)], indexes=_groupIndexes, coerce=int)
        return GroupStorage._storage


def CategoryStorage():
    try:
        return CategoryStorage._storage
    except AttributeError:
        eveCategoryTuple = collections.namedtuple('eveCategoryTuple', _categoryAttributes)
        CategoryStorage._storage = fsdlite.EveStorage(data='evetypes/categories', cache='evecategories.static', mapping=[('$', eveCategoryTuple)], coerce=int)
        return CategoryStorage._storage


def Close():
    CategoryStorage().cache.close()
    GroupStorage().cache.close()
    TypeStorage().cache.close()
