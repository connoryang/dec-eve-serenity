#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\common\componentregistry.py
from collections import defaultdict
from componentmessenger import ComponentMessenger
from eveexceptions.exceptionEater import ExceptionEater
from spacecomponents.common.componentclass import ComponentClass

class UnregisteredComponentError(Exception):
    pass


class ComponentInstanceAlreadyExists(Exception):
    pass


def ExportCall(func):
    func.isExportedComponentCall = True
    return func


def CreateComponentMapping(attributeLoader, componentDict):
    componentClassTypes = {}
    typeIDToClassMapping = defaultdict(list)
    for componentName, componentClass in componentDict.iteritems():
        RegisterComponentClass(attributeLoader, componentClassTypes, typeIDToClassMapping, ComponentClass(componentName, componentClass))

    return (componentClassTypes, typeIDToClassMapping)


def RegisterComponentClass(attributeLoader, componentClassTypes, typeIDToClassMapping, componentClass):
    componentClassTypes[componentClass.componentName] = componentClass
    for typeID in attributeLoader.GetTypeIDsForComponentName(componentClass.componentName):
        typeIDToClassMapping[typeID].append(componentClass)


class ComponentRegistry(object):
    asyncFuncs = None

    def __init__(self, attributeLoader, asyncFuncs, eventLogger, componentClassTypes, typeIDToClassMapping):
        self.attributeLoader = attributeLoader
        self.asyncFuncs = asyncFuncs
        self.eventLogger = eventLogger
        self.componentClassTypes = componentClassTypes
        self.typeIDToClassMapping = typeIDToClassMapping
        self.itemIDToComponentInstances = {}
        self.componentNameToItemIDs = defaultdict(dict)
        self.messenger = ComponentMessenger()

    def RegisterComponentClass(self, componentClass):
        RegisterComponentClass(self.attributeLoader, self.componentClassTypes, self.typeIDToClassMapping, componentClass)

    def GetComponentClassesForTypeID(self, typeID):
        return self.typeIDToClassMapping[typeID]

    def GetComponentsByItemID(self, itemID):
        return self.itemIDToComponentInstances[itemID]

    def CreateComponentInstances(self, itemID, typeID):
        componentClassesForTypeID = self.typeIDToClassMapping[typeID]
        components = self._GetComponentsByItemId(itemID)
        for componentClass in componentClassesForTypeID:
            if componentClass.componentName in components:
                continue
            attributes = self.attributeLoader.GetAttributes(typeID, componentClass.componentName)
            with ExceptionEater('Error creating a component %s' % componentClass.componentName):
                instance = componentClass.factoryMethod(itemID, typeID, attributes, self)
                components[componentClass.componentName] = instance
                self.componentNameToItemIDs[componentClass.componentName][itemID] = instance

        return components

    def _GetComponentsByItemId(self, itemId):
        if itemId in self.itemIDToComponentInstances:
            components = self.itemIDToComponentInstances[itemId]
        else:
            components = {}
            self.itemIDToComponentInstances[itemId] = components
        return components

    def AddComponentInstanceToItem(self, componentName, itemId, typeID, attributes):
        components = self._GetComponentsByItemId(itemId)
        componentClass = self.componentClassTypes[componentName]
        instance = componentClass.factoryMethod(itemId, typeID, attributes, self)
        components[componentName] = instance
        self.componentNameToItemIDs[componentName][itemId] = instance
        return instance

    def DeleteComponentInstances(self, itemID):
        self.messenger.DeleteSubscriptionsForItem(itemID)
        instance = self.itemIDToComponentInstances.pop(itemID)
        for componentName in instance:
            del self.componentNameToItemIDs[componentName][itemID]

    def GetInstancesWithComponentClass(self, componentName):
        return self.componentNameToItemIDs[componentName].values()

    def SendMessageToItem(self, itemID, messageName, *args, **kwargs):
        self.messenger.SendMessageToItem(itemID, messageName, *args, **kwargs)

    def SubscribeToItemMessage(self, itemID, messageName, messageHandler):
        self.GetComponentsByItemID(itemID)
        self.messenger.SubscribeToItemMessage(itemID, messageName, messageHandler)

    def GetComponentForItem(self, itemID, componentClassID):
        return self.itemIDToComponentInstances[itemID][componentClassID]

    def UnsubscribeFromItemMessage(self, itemID, messageName, messageHandler):
        self.messenger.UnsubscribeFromItemMessage(itemID, messageName, messageHandler)

    def CallComponent(self, session, itemID, componentClassName, methodName, *args, **kwargs):
        try:
            component = self.GetComponentForItem(itemID, componentClassName)
        except KeyError:
            return

        method = getattr(component, methodName)
        if not getattr(method, 'isExportedComponentCall', False):
            raise RuntimeError("The method '%s' is not exported on component '%s'" % (methodName, componentClassName))
        return method(session, *args, **kwargs)
