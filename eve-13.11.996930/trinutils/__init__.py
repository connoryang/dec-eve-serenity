#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\trinutils\__init__.py


def ReloadTextures(obj):
    reloadedpaths = set()
    for texresource in obj.Find('trinity.TriTextureParameter'):
        if texresource.resource and texresource.resourcePath.lower() not in reloadedpaths:
            texresource.resource.Reload()
            reloadedpaths.add(texresource.resourcePath.lower())
