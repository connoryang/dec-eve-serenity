#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\GameWorld\__init__.py
import blue
args = blue.pyos.GetArg()
dev = None
gpuEnabled = True
for arg in args:
    if arg.startswith('/gameworlddev'):
        dev = 1
    if arg == '/physxNoGpu':
        gpuEnabled = False
else:
    if boot.keyval.get('gameworlddev', None):
        dev = int(boot.keyval['trinitydev'].split('=', 1)[1])

if dev:
    print 'Starting up GameWorld through _GameWorld_dev.dll ...'
    try:
        from _GameWorld_dev import *
        dllToTest = '_GameWorld_dev'
        print 'Success!'
    except ImportError:
        print 'not found, fallback to _GameWorld'
        from _GameWorld import *

else:
    from _GameWorld import *
PhysXSetGpuEnabled(gpuEnabled)
Manager = GameWorldManager()
if boot.role == 'client':
    ActionTree = ActionTreeManagerClient()
else:
    ActionTree = ActionTreeManagerServer()
ActionTree.Initialize()

def CreateStaticMeshAndWait(gw, resPath, location, rotation):
    if resPath and resPath == 'None':
        return
    timer = blue.pyos.taskletTimer.EnterTasklet('GameWorld::CreateStaticMeshAndWait')
    mesh = None
    blue.resMan.SetUrgentResourceLoads(True)
    mesh = gw.CreateStaticMesh(resPath)
    blue.resMan.SetUrgentResourceLoads(False)
    while not mesh.loaded and not mesh.Failed():
        blue.synchro.Yield()

    if mesh.Failed():
        gw.RemoveStaticShape(mesh)
        mesh = None
    else:
        mesh.positionComponent = PositionComponent()
        mesh.positionComponent.position = location
        mesh.positionComponent.rotation = rotation
        mesh.AddToScene()
    blue.pyos.taskletTimer.ReturnFromTasklet(timer)
    return mesh
