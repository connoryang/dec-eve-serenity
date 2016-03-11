#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\extensions\__init__.py


class Extension:

    def __init__(self, configs = {}):
        self.config = configs

    def getConfig(self, key, default = ''):
        if key in self.config:
            return self.config[key][0]
        else:
            return default

    def getConfigs(self):
        return dict([ (key, self.getConfig(key)) for key in self.config.keys() ])

    def getConfigInfo(self):
        return [ (key, self.config[key][1]) for key in self.config.keys() ]

    def setConfig(self, key, value):
        self.config[key][0] = value

    def extendMarkdown(self, md, md_globals):
        raise NotImplementedError, 'Extension "%s.%s" must define an "extendMarkdown"method.' % (self.__class__.__module__, self.__class__.__name__)
