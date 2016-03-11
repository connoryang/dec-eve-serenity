#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\login\charcreation\portraitMaker.py
import trinity
import blue

class PortraitMaker(object):

    def __init__(self, camera, backdropPath):
        self.camera = camera
        self.backdropPath = backdropPath

    def GetPortraitTexture(self, portraitID):
        size = 512
        sceneManager = sm.GetService('sceneManager')
        scene = sceneManager.GetActiveScene()
        backdropPath = self.backdropPath
        if backdropPath:
            backdropScene = trinity.Tr2Sprite2dScene()
            backdropScene.displayWidth = size
            backdropScene.displayHeight = size
            sprite = trinity.Tr2Sprite2d()
            sprite.texturePrimary = trinity.Tr2Sprite2dTexture()
            sprite.texturePrimary.resPath = backdropPath
            sprite.displayWidth = size
            sprite.displayHeight = size
            backdropScene.children.append(sprite)
        target = trinity.Tr2RenderTarget(size, size, 1, trinity.PIXEL_FORMAT.B8G8R8X8_UNORM)
        depth = trinity.Tr2DepthStencil(size, size, trinity.DEPTH_STENCIL_FORMAT.AUTO)
        renderJob = trinity.CreateRenderJob('TakeSnapShot')
        renderJob.PushRenderTarget(target)
        renderJob.PushDepthStencil(depth)
        projection = trinity.TriProjection()
        projection.PerspectiveFov(self.camera.fieldOfView, 1, 0.1, 5.0)
        view = self.camera.viewMatrix
        renderJob.Clear((0.0, 0.0, 0.0, 1.0), 1.0)
        renderJob.SetProjection(projection)
        renderJob.SetView(view)
        if backdropPath:
            renderJob.Update(backdropScene)
            renderJob.RenderScene(backdropScene)
        renderJob.RenderScene(scene)
        trinity.WaitForResourceLoads()
        renderJob.PopDepthStencil()
        renderJob.PopRenderTarget()
        renderJob.ScheduleOnce()
        renderJob.WaitForFinish()
        filename = self.GetPortraitSnapshotPath(portraitID)
        trinity.Tr2HostBitmap(target).Save(filename)
        path = 'cache:/Pictures/Portraits/PortraitSnapshot_%s_%s.jpg' % (portraitID, session.userid)
        blue.motherLode.Delete(path)
        tex = blue.resMan.GetResource(path, 'atlas')
        return tex

    def GetPortraitSnapshotPath(self, portraitID):
        return blue.paths.ResolvePathForWriting(u'cache:/Pictures/Portraits/PortraitSnapshot_%s_%s.jpg' % (portraitID, session.userid))


import cameras
import charactercreator.const as ccConst

class PortraitCameraConfigurator:

    def SetupPortraitCamera(self, camera, avatar, cameraPos = None, storedPortraitCameraSettings = None):
        self.camera = camera
        if self.camera is None:
            self.camera = cameras.CharCreationCamera(avatar, ccConst.CAMERA_MODE_PORTRAIT)
            self.SetupCameraUpdateJob()
        else:
            self.camera.ToggleMode(ccConst.CAMERA_MODE_PORTRAIT, avatar=avatar, transformTime=0)
        if cameraPos:
            self.camera.PlacePortraitCamera(self.cameraPos, self.cameraPoi)
            xFactor, yFactor = self.camera.GetCorrectCameraXandYFactors(self.cameraPos, self.cameraPoi)
            self.camera.xFactor = self.camera.xTarget = xFactor
            self.camera.yFactor = self.camera.yTarget = yFactor
        if storedPortraitCameraSettings:
            self.camera.SetPointOfInterest(self.storedPortraitCameraSettings['poi'])
            self.camera.pitch = self.storedPortraitCameraSettings['pitch']
            self.camera.yaw = self.storedPortraitCameraSettings['yaw']
            self.camera.distance = self.storedPortraitCameraSettings['distance']
            self.camera.xFactor = self.storedPortraitCameraSettings['xFactor']
            self.camera.yFactor = self.storedPortraitCameraSettings['yFactor']
            self.camera.fieldOfView = self.storedPortraitCameraSettings['fieldOfView']

    def RevertToNormalCamera(self, camera, avatar):
        self.camera = camera
        self.camera.ToggleMode(ccConst.CAMERA_MODE_DEFAULT, avatar=avatar)
        self.camera.fieldOfView = 0.3
        self.camera.distance = 8.0
        self.camera.frontClip = 0.5
        self.camera.backclip = 100.0
        self.camera.SetPointOfInterest((0.0, self.camera.avatarEyeHeight / 2.0, 0.0))
