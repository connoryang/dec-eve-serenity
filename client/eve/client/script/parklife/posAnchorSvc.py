#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\posAnchorSvc.py
import evetypes
import service
import trinity
import blue
import geo2
import base
import carbonui.const as uiconst
import telemetry

class PosAnchorSvc(service.Service):
    __guid__ = 'svc.posAnchor'
    __exportedcalls__ = {}
    __notifyevents__ = ['DoBallRemove', 'ProcessSessionChange', 'DoBallsRemove']
    __dependencies__ = ['michelle']

    def __init__(self):
        service.Service.__init__(self)
        self.updateTimer = None
        self.cube = None
        self.cursor = None
        self.selection = None
        self.cursorSize = 2500.0
        self.active = 0
        self.posID = None

    def Run(self, memStream = None):
        service.Service.Run(self, memStream)

    def Stop(self, stream):
        self.KillTimer()
        self.HideCursor()
        service.Service.Stop(self)

    def ProcessSessionChange(self, isremote, session, change):
        self.KillTimer()
        self.HideCursor()

    def StartMovingCursor(self):
        pass

    def StopMovingCursor(self):
        pass

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return
        self.LogInfo('DoBallRemove::posAnchorSvc', ball.id)
        if slimItem is None:
            return
        if slimItem.itemID is None or slimItem.itemID < 0:
            return
        if slimItem.itemID == self.posID:
            self.CancelAchorPosSelect()

    def ShowCursor(self):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if scene is None:
            return
        self.cursor = trinity.Load('res:/Model/UI/posCursor.red')
        self.cube = trinity.Load('res:/Model/UI/posGlassCube.red')
        blue.pyos.synchro.SleepWallclock(1)
        self.yCursor = [self.cursor.children[0], self.cursor.children[1]]
        self.xCursor = [self.cursor.children[4], self.cursor.children[5]]
        self.zCursor = [self.cursor.children[2], self.cursor.children[3]]
        self.cube.scaling = (self.boxWidth, self.boxWidth, self.boxWidth)
        self.cursor.scaling = (50, 50, 50)
        self.cursor.useDistanceBasedScale = True
        self.cursor.distanceBasedScaleArg1 = 0.00015
        self.cursor.distanceBasedScaleArg2 = 0
        bp = sm.GetService('michelle').GetBallpark()
        ball = bp.GetBall(self.posID)
        pos = ball.GetVectorAt(blue.os.GetSimTime())
        self.cursor.translation = (pos.x, pos.y, pos.z)
        scene.objects.append(self.cursor)
        scene.objects.append(self.cube)
        self.Update()
        self.active = 1

    def RefreshCursorSize(self):
        if self.cursor:
            self.cursor.scaling.SetXYZ(self.cursorSize, self.cursorSize, self.cursorSize)

    def ScaleCursorUp(self):
        self.cursorSize = self.cursorSize * 1.1
        self.RefreshCursorSize()

    def ScaleCursorDown(self):
        self.cursorSize = max(self.cursorSize / 1.1, 5.0)
        self.RefreshCursorSize()

    def IsActive(self):
        return self.active

    def HideCursor(self):
        self.active = 0
        if not sm.IsServiceRunning('gameui'):
            return
        scene = sm.StartService('sceneManager').GetRegisteredScene('default')
        if self.cursor and self.cursor in scene.objects:
            scene.objects.remove(self.cursor)
        if self.cube and self.cube in scene.objects:
            scene.objects.remove(self.cube)
        self.cursor = None
        self.cube = None

    def MoveCursor(self, tf, dx, dy, camera):
        dev = trinity.device
        X = float(dx) / float(dev.width)
        Y = float(dy) / float(dev.height) * -1
        upVec = geo2.Vec3Scale(camera.GetYAxis(), Y)
        rightVec = geo2.Vec3Scale(camera.GetXAxis(), X)
        pos = geo2.Vec3Add(rightVec, upVec)
        cameraDistance = geo2.Vec3Length(geo2.Vec3Subtract(camera.eyePosition, self.cursor.translation))
        pos = geo2.Vec3Scale(pos, cameraDistance * 3.0)
        if tf in self.yCursor:
            pos = (0.0, pos[1], 0.0)
        elif tf in self.xCursor:
            pos = (pos[0], 0.0, 0.0)
        elif tf in self.zCursor:
            pos = (0.0, 0.0, pos[2])
        self.cursor.translation = geo2.Vec3Add(self.cursor.translation, pos)

    def StartAnchorPosSelect(self, posID):
        if self.IsActive():
            if posID == self.posID:
                return
            self.CancelAchorPosSelect()
        bp = sm.GetService('michelle').GetBallpark()
        slimItem = bp.GetInvItem(posID)
        if slimItem is None:
            return
        self.posID = posID
        typeID = slimItem.typeID
        self.boxWidth = evetypes.GetRadius(typeID)
        item = sm.StartService('michelle').GetItem(posID)
        if item.groupID == const.groupControlTower:
            if eve.Message('ConfirmStructureAnchor', {'item': (const.UE_TYPEID, item.typeID)}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return
            self.SubmitAnchorPosSelect()
        else:
            self.ShowCursor()
            self.StartTimer()

    def CancelAchorPosSelect(self):
        self.KillTimer()
        self.HideCursor()
        self.posID = None

    def SubmitAnchorPosSelect(self):
        typeID = sm.GetService('michelle').GetItem(self.posID).typeID
        anchoringDelay = sm.GetService('godma').GetType(typeID).anchoringDelay
        bp = sm.GetService('michelle').GetBallpark()
        ship = bp.GetBall(eve.session.shipid)
        x = y = z = 0
        if sm.StartService('michelle').GetItem(self.posID).groupID != const.groupControlTower:
            x, y, z = self.cube.translation[0] + ship.x, self.cube.translation[1] + ship.y, self.cube.translation[2] + ship.z
        sm.GetService('pwn').Anchor(self.posID, (x, y, z))
        self.CancelAchorPosSelect()
        eve.Message('AnchoringObject', {'delay': anchoringDelay / 1000.0})

    def StartTimer(self):
        if self.updateTimer:
            return
        self.timerCount = 0
        self.updateTimer = base.AutoTimer(25, self.Update)

    def KillTimer(self):
        self.updateTimer = None

    def Update(self):
        self.cube.translation = self.cursor.translation
