#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\menuSvcExtras\modelDebugFunctions.py
import uix
import log
import blue
import geo2
import trinity
import math
import eveclientqatools.blueobjectviewer as blueViewer
UNLOAD_COLLISION_INFO = 0
SHOW_COLLISION_DATA = 1
SHOW_DESTINY_BALL = 2
SHOW_MODEL_SPHERE = 3
SHOW_BOUNDING_SPHERE = 4

def SaveRedFile(ball, graphicFile):
    dlgRes = uix.GetFileDialog(multiSelect=False, selectionType=uix.SEL_FOLDERS)
    if dlgRes is not None:
        path = dlgRes.Get('folders')[0]
        graphicFile = graphicFile.split('/')[-1]
        graphicFile = graphicFile.replace('.blue', '.red')
        savePath = path + '\\' + graphicFile
        trinity.Save(ball.model, savePath)
        log.LogError('GM menu: Saved object as:', savePath)


def GetGMModelInfoMenuItem(itemID = None):

    def GetModelHandler(*args):
        model = sm.StartService('michelle').GetBall(itemID).GetModel()
        blueViewer.Show(model)

    return ('Inspect model', GetModelHandler, (None,))


def GetGMBallsAndBoxesMenu(itemID = None, *args, **kwargs):
    spaceMgr = sm.StartService('space')
    partMenu = [('Stop partition box display ', spaceMgr.StopPartitionDisplayTimer, ()),
     None,
     ('Start partition box display limit = 0', spaceMgr.StartPartitionDisplayTimer, (0,)),
     ('Start partition box display limit = 1', spaceMgr.StartPartitionDisplayTimer, (1,)),
     ('Start partition box display limit = 2', spaceMgr.StartPartitionDisplayTimer, (2,)),
     ('Start partition box display limit = 3', spaceMgr.StartPartitionDisplayTimer, (3,)),
     ('Start partition box display limit = 4', spaceMgr.StartPartitionDisplayTimer, (4,)),
     ('Start partition box display limit = 5', spaceMgr.StartPartitionDisplayTimer, (5,)),
     ('Start partition box display limit = 6', spaceMgr.StartPartitionDisplayTimer, (6,)),
     ('Start partition box display limit = 7', spaceMgr.StartPartitionDisplayTimer, (7,)),
     None,
     ('Show single level', ChangePartitionLevel, (0,)),
     ('Show selected level and up', ChangePartitionLevel, (1,))]
    subMenu = [('Balls & Boxes', [('Hide Collision Info', ShowDestinyBalls, (itemID, UNLOAD_COLLISION_INFO)),
       ('Show Collision Info', ShowDestinyBalls, (itemID, SHOW_COLLISION_DATA)),
       None,
       ('Wireframe Destiny Ball', ShowDestinyBalls, (itemID, SHOW_DESTINY_BALL)),
       ('Wireframe BoundingSphere', ShowDestinyBalls, (itemID, SHOW_BOUNDING_SPHERE)),
       None,
       ('Partition', partMenu)]), ('Damage Locators', [('Toggle damage locators', ShowDamageLocators, (itemID,)), ('Toggle shield ellipsoid', ShowShieldEllipsoid, (itemID,))]), ('Invulnerability Link', [('Remove link', RemoveLink, (itemID,)), ('Link player', AddLink, (itemID,))])]
    return subMenu


def RemoveLink(itemID):
    ball = sm.StartService('michelle').GetBall(itemID)
    if hasattr(ball, 'EnableLink'):
        ball.EnableLink(None)


def AddLink(itemID):
    tgtBall = sm.StartService('michelle').GetBall(itemID)
    playerBall = sm.StartService('michelle').GetBall(session.shipid)
    if hasattr(playerBall, 'EnableLink'):
        playerBall.EnableLink(tgtBall, 2.0 * tgtBall.radius, 2000.0)


def ChangePartitionLevel(level):
    settings.user.ui.Set('partition_box_showall', level)


def ShowShieldEllipsoid(itemID):
    ball = sm.StartService('michelle').GetBall(itemID)
    model = getattr(ball, 'model', None)
    if model is not None:
        impactEffect = getattr(model, 'impactOverlay', None)
        if impactEffect is not None:
            if impactEffect.overallShieldImpact < 0.0:
                impactEffect.overallShieldImpact = 0.1
            else:
                impactEffect.overallShieldImpact = -1.0


def ShowDestinyBalls(itemID, showType):
    miniballObject = None
    scene = sm.GetService('sceneManager').GetRegisteredScene('default')
    nameOfMiniballs = 'collisionInfo_for_' + str(itemID)
    for each in scene.objects:
        if each.name == nameOfMiniballs:
            miniballObject = each
            break

    if miniballObject is not None:
        scene.objects.remove(miniballObject)
    if miniballObject and showType == UNLOAD_COLLISION_INFO:
        return
    ball = sm.StartService('michelle').GetBall(itemID)
    if showType == SHOW_COLLISION_DATA:
        graphicObject = CreateMiniCollisionObject(nameOfMiniballs, ball.miniBalls, ball.miniCapsules, ball.miniBoxes)
        graphicObject.translationCurve = ball
        graphicObject.rotationCurve = ball
        scene.objects.append(graphicObject)
    elif showType == SHOW_DESTINY_BALL:
        graphicObject = CreateRadiusObject(nameOfMiniballs, ball.radius)
        graphicObject.translationCurve = ball
        scene.objects.append(graphicObject)
    elif showType == SHOW_BOUNDING_SPHERE:
        graphicObject = CreateRadiusObject(nameOfMiniballs, ball.model.GetBoundingSphereRadius())
        pos = ball.model.GetBoundingSphereCenter()
        graphicObject.translation = (pos[0], pos[1], pos[2])
        graphicObject.translationCurve = ball
        graphicObject.rotationCurve = ball
        scene.objects.append(graphicObject)


def ShowDamageLocators(itemID):
    ball = sm.StartService('michelle').GetBallpark().GetBall(itemID)
    ship = ball.model
    if not ship:
        return
    if getattr(ball, 'visualizingDamageLocators', False):
        toRemove = []
        for child in ship.children:
            if child.name == 'DamageLocatorVisualization':
                toRemove.append(child)
            elif child.name == 'ImpactDirectionVisualization':
                toRemove.append(child)

        for tr in toRemove:
            ship.children.remove(tr)

        setattr(ball, 'visualizingDamageLocators', False)
    else:
        scale = ship.boundingSphereRadius / 10
        for i in range(len(ship.damageLocators)):
            damageLocator = ship.damageLocators[i]
            sphere = trinity.Load('res:/model/global/damageLocator.red')
            sphere.translation = damageLocator[0]
            sphere.scaling = [scale, scale, scale]
            ship.children.append(sphere)
            impacDir = damageLocator[1]
            direction = trinity.Load('res:/model/global/impactDirection.red')
            direction.translation = damageLocator[0]
            direction.scaling = [scale, scale, scale]
            direction.rotation = impacDir
            ship.children.append(direction)

        setattr(ball, 'visualizingDamageLocators', True)


def CreateMiniCollisionObject(name, miniballs, minicapsules, miniboxes):
    t = trinity.EveRootTransform()
    sphere = blue.resMan.LoadObject('res:/Model/Global/Miniball.red')
    capsule = blue.resMan.LoadObject('res:/Model/Global/Minicapsule.red')
    box = blue.resMan.LoadObject('res:/Model/Global/Minibox.red')
    if len(miniballs) > 0:
        for miniball in miniballs:
            mball = sphere.CopyTo()
            mball.translation = (miniball.x, miniball.y, miniball.z)
            r = miniball.radius * 2
            mball.scaling = (r, r, r)
            t.children.append(mball)

    for minicapsule in minicapsules:
        mcapsule = capsule.CopyTo()
        pointA = (minicapsule.ax, minicapsule.ay, minicapsule.az)
        pointB = (minicapsule.bx, minicapsule.by, minicapsule.bz)
        dir = geo2.Vec3Subtract(pointA, pointB)
        length = geo2.Vec3Length(dir)
        mcapsule.translation = geo2.Vec3Scale(geo2.Vec3Add(pointA, pointB), 0.5)
        radius = minicapsule.radius
        pitch = math.acos(dir[1] / length)
        yaw = math.atan2(dir[0], dir[2])
        quat = geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, 0)
        mcapsule.rotation = quat
        for each in mcapsule.children:
            if each.name == 'Cylinder':
                height = length * each.scaling[1]
                rscaling = geo2.Vec3Scale((each.scaling[0], each.scaling[2]), radius)
                each.scaling = (rscaling[0], height, rscaling[1])
            else:
                each.scaling = geo2.Vec3Scale(each.scaling, radius)
                each.translation = geo2.Vec3Scale(each.translation, length)

        t.children.append(mcapsule)

    for minibox in miniboxes:
        mbox = box.CopyTo()
        corner = (minibox.c0, minibox.c1, minibox.c2)
        xAxis = (minibox.x0, minibox.x1, minibox.x2)
        yAxis = (minibox.y0, minibox.y1, minibox.y2)
        zAxis = (minibox.z0, minibox.z1, minibox.z2)
        xyzAxis = geo2.Vec3Add(xAxis, geo2.Vec3Add(yAxis, zAxis))
        center = geo2.Vec3Add(corner, geo2.Vec3Scale(xyzAxis, 0.5))
        xNormalized = geo2.Vec3Normalize(xAxis)
        yNormalized = geo2.Vec3Normalize(yAxis)
        xRot = geo2.QuaternionRotationArc((1, 0, 0), xNormalized)
        yRot = geo2.QuaternionRotationArc((0, 1, 0), yNormalized)
        mbox.translation = center
        mbox.scaling = geo2.Vec3Transform((1, 1, 1), geo2.MatrixScaling(geo2.Vec3Length(xAxis), geo2.Vec3Length(yAxis), geo2.Vec3Length(zAxis)))
        mbox.rotation = geo2.QuaternionNormalize(geo2.QuaternionMultiply(xRot, yRot))
        t.children.append(mbox)

    t.name = name
    return t


def CreateRadiusObject(name, radius):
    t = trinity.EveRootTransform()
    t.name = name
    s = blue.resMan.LoadObject('res:/model/global/gridSphere.red')
    radius = radius * 2
    s.scaling = (radius, radius, radius)
    t.children.append(s)
    return t
