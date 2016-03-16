#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\trinutils\boundingsphere.py
import blue
import trinity
import devenv.respathutils as respathutils

class BoundingSphereRadiusZeroError(Exception):

    def __init__(self, geoResPath):
        msg = 'Bounding sphere is 0. It may have failed to rebuild properly.\n%s' % blue.paths.ResolvePath(geoResPath)
        Exception.__init__(self, msg)


def GetBoundingSphere(trinobj):
    try:
        return (trinobj.boundingSphereCenter, trinobj.boundingSphereRadius)
    except AttributeError:
        return (trinobj.boundingSphere[:3], trinobj.boundingSphere[3])


def RebuildBoundingSphere(trinobj):
    bt = trinobj.__bluetype__
    if bt == 'trinity.EveShip2' or bt == 'trinity.EveStation2' or bt == 'trinity.EveMobile':
        _RebuildShip(trinobj)
    elif bt == 'trinity.EveTurretSet':
        _RebuildTurret(trinobj)
    elif bt == 'trinity.EveMissile':
        _RebuildMissile(trinobj)
    elif bt == 'trinity.EveSOFDataHull':
        _RebuildSofHull(trinobj)
    else:
        raise ValueError('Unsupported type: %s' % bt)
    return GetBoundingSphere(trinobj)


def _RebuildTurret(turret):
    turret.FreezeHighDetailLOD()
    trinity.WaitForResourceLoads()
    turret.boundingSphere = (-1, -1, -1, -1)
    turret.RebuildBoundingSphere()
    if turret.boundingSphere[3] <= 0:
        raise BoundingSphereRadiusZeroError(turret.geometryResPath)


def _RebuildShip(ship):
    ship.FreezeHighDetailMesh()
    trinity.WaitForResourceLoads()
    ship.boundingSphereRadius = -1
    ship.RebuildBoundingSphereInformation()
    if ship.boundingSphereRadius <= 0:
        respath = '<No mesh>'
        if ship.meshLod:
            respath = ship.meshLod.geometryRes.highDetailResPath
        raise BoundingSphereRadiusZeroError(respath)


def _RebuildSofHull(sofhull):
    expandedPath = respathutils.ExpandResPath(sofhull.geometryResFilePath)
    hullresource = blue.resMan.GetResource(expandedPath)
    trinity.WaitForResourceLoads()
    hullresource.RecalculateBoundingSphere()
    bSphereCenter, bSphereRad = hullresource.GetBoundingSphere(0)
    sofhull.boundingSphere = (bSphereCenter[0],
     bSphereCenter[1],
     bSphereCenter[2],
     bSphereRad)


def _RebuildMissile(missile):
    missile.FreezeHighDetailMesh()
    trinity.WaitForResourceLoads()
    missile.boundingSphereRadius = -1
    missile.RebuildMissileBoundingSphere()
    if missile.boundingSphereRadius <= 0:
        res = missile.warheads[0].mesh.geometryResPath
        raise BoundingSphereRadiusZeroError(res)
