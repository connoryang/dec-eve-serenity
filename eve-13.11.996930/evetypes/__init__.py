#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evetypes\__init__.py
import storages
from evetypes.storages import TypeStorage, GroupStorage, CategoryStorage, Close
from evetypes.localizationUtils import GetLocalizedTypeName, GetLocalizedTypeDescription, GetLocalizedCategoryName, GetLocalizedGroupName
import inventorycommon.const
try:
    import blue

    def BeNice():
        blue.pyos.BeNice()


except ImportError:

    def BeNice():
        pass


class TypeNotFoundException(Exception):
    pass


class GroupNotFoundException(Exception):
    pass


class CategoryNotFoundException(Exception):
    pass


class TypeAttributeNotFoundException(Exception):
    pass


class GroupAttributeNotFoundException(Exception):
    pass


class CategoryAttributeNotFoundException(Exception):
    pass


def _Get(typeID):
    try:
        return TypeStorage()[typeID]
    except KeyError as e:
        raise TypeNotFoundException(e)


def _GetGroup(groupID):
    try:
        return GroupStorage()[groupID]
    except KeyError as e:
        raise GroupNotFoundException(e)


def _GetCategory(categoryID):
    try:
        return CategoryStorage()[categoryID]
    except KeyError as e:
        raise CategoryNotFoundException(e)


def _GetAttributeForType(typeID, attribute):
    try:
        return getattr(_Get(typeID), attribute)
    except AttributeError as e:
        raise TypeAttributeNotFoundException(e)


def _GetAttributeForGroup(groupID, attribute):
    try:
        return getattr(_GetGroup(groupID), attribute)
    except AttributeError as e:
        raise GroupAttributeNotFoundException(e)


def _GetAttributeForCategory(categoryID, attribute):
    try:
        return getattr(_GetCategory(categoryID), attribute)
    except AttributeError as e:
        raise CategoryAttributeNotFoundException(e)


def GetAttributeForType(typeID, attribute):
    if attribute == 'radius':
        return GetRadius(typeID)
    return _GetAttributeForType(typeID, attribute)


def GetTotalTypeCount():
    return len(TypeStorage())


def GetTotalGroupCount():
    return len(GroupStorage())


def GetTotalCategoryCount():
    return len(CategoryStorage())


def Exists(typeID):
    return typeID in TypeStorage()


def GroupExists(groupID):
    return groupID in GroupStorage()


def CategoryExists(categoryID):
    return categoryID in CategoryStorage()


def Iterate():
    for typeID in TypeStorage().iterkeys():
        yield int(typeID)


def IterateGroups():
    for groupID in GroupStorage().iterkeys():
        yield int(groupID)


def IterateCategories():
    for categoryID in CategoryStorage().iterkeys():
        yield int(categoryID)


def GetAllTypeIDs():
    return [ int(typeID) for typeID in TypeStorage() ]


def GetAllGroupIDs():
    return [ int(groupID) for groupID in GroupStorage() ]


def GetAllCategoryIDs():
    return [ int(categoryID) for categoryID in CategoryStorage() ]


def RaiseIFNotExists(typeID):
    if typeID not in TypeStorage():
        raise TypeNotFoundException(typeID)


def GetRaceID(typeID):
    return _GetAttributeForType(typeID, 'raceID')


def GetGroupID(typeID):
    return _GetAttributeForType(typeID, 'groupID')


def GetVolume(typeID):
    return _GetAttributeForType(typeID, 'volume')


def GetIconID(typeID):
    return _GetAttributeForType(typeID, 'iconID')


def GetGraphicID(typeID):
    return _GetAttributeForType(typeID, 'graphicID')


def GetFactionID(typeID):
    return _GetAttributeForType(typeID, 'factionID')


def GetIsisGroupID(typeID):
    return _GetAttributeForType(typeID, 'isisGroupID')


def GetNameID(typeID):
    return _GetAttributeForType(typeID, 'typeNameID')


def GetDescriptionID(typeID):
    return _GetAttributeForType(typeID, 'descriptionID')


def GetCapacity(typeID):
    return _GetAttributeForType(typeID, 'capacity')


def GetBasePrice(typeID):
    return _GetAttributeForType(typeID, 'basePrice')


def GetPortionSize(typeID):
    return _GetAttributeForType(typeID, 'portionSize')


def GetMarketGroupID(typeID):
    return _GetAttributeForType(typeID, 'marketGroupID')


def GetSoundID(typeID):
    return _GetAttributeForType(typeID, 'soundID')


def GetMass(typeID):
    return _GetAttributeForType(typeID, 'mass')


def GetSofMaterialSetIDOrNone(typeID):
    try:
        sofMaterialSetID = _GetAttributeForType(typeID, 'sofMaterialSetID')
        if sofMaterialSetID is not None:
            return sofMaterialSetID
    except TypeNotFoundException:
        return


def GetSofFactionNameOrNone(typeID):
    try:
        sofFactionName = _GetAttributeForType(typeID, 'sofFactionName')
        if sofFactionName is not None:
            return str(sofFactionName)
    except TypeNotFoundException:
        return


def IsPublished(typeID):
    return _GetAttributeForType(typeID, 'published')


def GetRadius(typeID):
    radius = _GetAttributeForType(typeID, 'radius')
    return radius or 1.0


def IsGroupPublished(typeID):
    groupID = GetGroupID(typeID)
    return IsGroupPublishedByGroup(groupID)


def GetCategoryID(typeID):
    groupID = GetGroupID(typeID)
    return _GetAttributeForGroup(groupID, 'categoryID')


def GetCategoryNameID(typeID):
    categoryID = GetCategoryID(typeID)
    return _GetAttributeForCategory(categoryID, 'categoryNameID')


def GetDescription(typeID, languageID = None):
    descriptionID = GetDescriptionID(typeID)
    return GetLocalizedTypeDescription(descriptionID, languageID)


def GetDescriptionOrNone(typeID):
    try:
        return GetDescription(typeID)
    except TypeNotFoundException:
        return None


def GetName(typeID, languageID = None):
    nameID = GetNameID(typeID)
    return GetLocalizedTypeName(nameID, languageID)


def GetNameOrNone(typeID):
    try:
        return GetName(typeID)
    except TypeNotFoundException:
        return None


def GetEnglishName(typeID):
    return GetName(typeID, 'en-us')


def IsCategoryPublished(typeID):
    categoryID = GetCategoryID(typeID)
    return _GetAttributeForCategory(categoryID, 'published')


def GetCategoryName(typeID, languageID = None):
    categoryID = GetCategoryID(typeID)
    categoryNameID = _GetAttributeForCategory(categoryID, 'categoryNameID')
    return GetLocalizedCategoryName(categoryNameID, languageID=languageID)


def UseGroupBasePrice(typeID):
    groupID = GetGroupID(typeID)
    return _GetAttributeForGroup(groupID, 'useBasePrice')


def GetGroupName(typeID, languageID = None):
    groupID = GetGroupID(typeID)
    groupNameID = _GetAttributeForGroup(groupID, 'groupNameID')
    return GetLocalizedGroupName(groupNameID, languageID=languageID)


def GetGroupNameID(typeID):
    groupID = GetGroupID(typeID)
    return _GetAttributeForGroup(groupID, 'groupNameID')


def GetCertificateTemplate(typeID):
    return _GetAttributeForType(typeID, 'certificateTemplate')


def GetTypeIDsByMarketGroup(marketGroupID):
    return set((int(typeID) for typeID in TypeStorage().filter_keys('marketGroupID', marketGroupID)))


def GetTypeIDsByGroup(groupID):
    return set((int(typeID) for typeID in TypeStorage().filter_keys('groupID', groupID)))


def GetTypeIDsByGroups(groupIDs):
    typeIDs = set()
    for groupID in groupIDs:
        typeIDs.update(GetTypeIDsByGroup(groupID))

    return typeIDs


def UseGroupBasePriceByGroup(groupID):
    return _GetAttributeForGroup(groupID, 'useBasePrice')


def GetGroupNameByGroup(groupID, languageID = None):
    groupNameID = _GetAttributeForGroup(int(groupID), 'groupNameID')
    return GetLocalizedGroupName(groupNameID, languageID=languageID)


def GetCategoryIDByGroup(groupID):
    return _GetAttributeForGroup(groupID, 'categoryID')


def GetGroupNameIDByGroup(groupID):
    return _GetAttributeForGroup(groupID, 'groupNameID')


def GetIsGroupFittableNonSingletonByGroup(groupID):
    return _GetAttributeForGroup(groupID, 'fittableNonSingleton')


def GetIsGroupAnchorableByGroup(groupID):
    return _GetAttributeForGroup(groupID, 'anchorable')


def GetIsGroupAnchoredByGroup(groupID):
    return _GetAttributeForGroup(groupID, 'anchored')


def IsGroupPublishedByGroup(groupID):
    return _GetAttributeForGroup(groupID, 'published')


def GetGroupIconIDByGroup(groupID):
    return _GetAttributeForGroup(int(groupID), 'iconID')


def GetCategoryNameByGroup(groupID, languageID = None):
    categoryID = GetCategoryIDByGroup(groupID)
    categoryNameID = _GetAttributeForCategory(categoryID, 'categoryNameID')
    return GetLocalizedCategoryName(categoryNameID, languageID=languageID)


def IsCategoryPublishedByCategory(categoryID):
    return _GetAttributeForCategory(categoryID, 'published')


def GetCategoryIconIDByCategory(categoryID):
    return _GetAttributeForCategory(categoryID, 'iconID')


def IsCategoryHardwareByCategory(categoryID):
    return categoryID in (inventorycommon.const.categoryModule, inventorycommon.const.categoryImplant, inventorycommon.const.categorySubSystem)


def GetTypeIDsByCategory(categoryID):
    typeIDs = set()
    groupIDs = GetGroupIDsByCategory(categoryID)
    for groupID in groupIDs:
        typeIDs.update(GetTypeIDsByGroup(groupID))

    return typeIDs


def GetTypeIDsByCategories(categoryIDs):
    typeIDs = set()
    for categoryID in categoryIDs:
        typeIDs.update(GetTypeIDsByCategory(categoryID))

    return typeIDs


def GetCategoryNameIDByCategory(categoryID):
    return _GetAttributeForCategory(categoryID, 'categoryNameID')


def GetCategoryNameByCategory(categoryID, languageID = None):
    categoryNameID = GetCategoryNameIDByCategory(categoryID)
    return GetLocalizedCategoryName(categoryNameID, languageID=languageID)


def GetGroupIDsByCategory(categoryID):
    return set((int(groupID) for groupID in GroupStorage().filter_keys('categoryID', categoryID)))


def GetGroupIDsByCategories(categoryIDs):
    groupIDs = set()
    for categoryID in categoryIDs:
        groupIDs.update(GetGroupIDsByCategory(categoryID))

    return groupIDs


def GetTypeIDByNameDict():
    typeIDsByName = getattr(GetTypeIDByNameDict, '_typeIDsByName', {})
    if not typeIDsByName:
        storage = TypeStorage()
        for typeID in Iterate():
            BeNice()
            name = GetLocalizedTypeName(storage[typeID].typeNameID, None)
            if name is not None:
                typeIDsByName[name.lower()] = typeID

        GetTypeIDByNameDict._typeIDsByName = typeIDsByName
    return typeIDsByName


def GetTypeIDByName(typeName):
    try:
        return GetTypeIDByNameDict()[typeName.lower()]
    except KeyError as e:
        raise TypeNotFoundException(e)


def GetGroupIDByGroupName(groupName):
    groupIDsByName = getattr(GetGroupIDByGroupName, '_groupIDsByName', {})
    if not groupIDsByName:
        storage = GroupStorage()
        for groupID in IterateGroups():
            name = GetLocalizedGroupName(storage[groupID].groupNameID, None)
            if name is not None:
                groupIDsByName[name.lower()] = groupID

        GetGroupIDByGroupName._groupIDsByName = groupIDsByName
    try:
        return groupIDsByName[groupName.lower()]
    except KeyError as e:
        raise GroupNotFoundException(e)
