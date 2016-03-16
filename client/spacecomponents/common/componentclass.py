#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\common\componentclass.py


class ComponentClass(object):

    def __init__(self, componentName, factoryMethod):
        self.componentName = componentName
        self.factoryMethod = factoryMethod
