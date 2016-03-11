#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\util\slimItem.py
import evetypes

class SlimItem:
    __guid__ = 'foo.SlimItem'
    __passbyvalue__ = 1
    baseAttributes = ['itemID',
     'ballID',
     'charID',
     'ownerID',
     'typeID',
     'groupID',
     'categoryID']

    def __init__(self, itemID = None, typeID = None, ownerID = None, groupID = None, categoryID = None):
        if itemID is not None:
            self.itemID = itemID
        if typeID is not None:
            self.typeID = typeID
        if ownerID is not None:
            self.ownerID = ownerID

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        if name == 'groupID':
            groupID = evetypes.GetGroupID(self.typeID)
            self.groupID = groupID
            return groupID
        if name == 'categoryID':
            categoryID = evetypes.GetCategoryID(self.typeID)
            self.categoryID = categoryID
            return categoryID
        if name == 'radius':
            return evetypes.GetRadius(self.typeID)
        if name == 'modules':
            self.modules = []
            return self.modules
        if name == 'jumps':
            self.jumps = []
            return self.jumps
        if name == 'ballID' or name == 'bounty':
            return 0
        if name[:2] != '__':
            return None
        raise AttributeError(name)

    def __repr__(self):
        extras = ','.join([ '%s=%s' % (key, strx(value) if isinstance(value, basestring) else value) for key, value in self.__dict__.items() if key not in self.baseAttributes and not key.startswith('__') ])
        if extras:
            extras = ',' + extras
        return '<slimItem: itemID=%s,ballID=%s,charID=%s,ownerID=%s,typeID=%s,groupID=%s,categoryID=%s%s>' % (self.itemID,
         self.ballID,
         self.charID,
         self.ownerID,
         self.typeID,
         self.groupID,
         self.categoryID,
         extras)
