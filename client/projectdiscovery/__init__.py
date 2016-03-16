#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\__init__.py


def IsProjectDiscoveryEnabled():
    return bool(int(sm.GetService('machoNet').GetGlobalConfig().get('isProjectDiscoveryEnabled', False)))
