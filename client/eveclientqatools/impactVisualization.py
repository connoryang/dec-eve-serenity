#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveclientqatools\impactVisualization.py
import threading
import uicontrols
import trinity
import geo2
import math
import random
import carbonui.const as uiconst
from eve.client.script.ui.control.buttons import Button, ButtonIcon
from eve.client.script.ui.control.checkbox import Checkbox
from carbonui.primitives.container import Container
from carbonui.primitives.gridcontainer import GridContainer
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit

class ImpactVisualizer():

    def __init__(self):
        self.name = 'Impact Visualizer'
        self.windowID = 'ImpactVisualizer_ ' + self.name
        self.damageLocatorID = 0
        self.impactVelocity = [0.0, -1000.0, 0.0]
        self.impactObjectMass = 100000
        self.shipId = None
        self.shipInput = None
        self.impactArrow = None
        self.arrowModel = None
        self.impactArrowBoundingRadius = 0.0
        self.impactRotation = geo2.QuaternionRotationSetYawPitchRoll(0.0, math.pi, 0.0)
        self.damageLocatorPos = (0.0, 0.0, 0.0)
        self.arrowPositionUpdater = None
        self.lockVelocity = True
        self.randomize = False
        self.arrowModel = trinity.Load('res:/Model/global/impactDirection.red')

    def SetupImpactArrow(self):
        self.impactArrow = trinity.EveRootTransform()
        self.impactArrow.name = 'DebugImpactArrow'
        self.impactArrow.children.append(self.arrowModel)
        self.arrowPositionUpdater = ArrowPositionUpdater(self.impactArrow)

    def GetImpactArrowBoundingRadius(self):
        geometry = self.arrowModel.mesh.geometry
        geometry.RecalculateBoundingSphere()
        self.impactArrowBoundingRadius = geometry.GetBoundingSphere(0)[1]

    def _OnClose(self):
        self.RemoveImpactArrowFromScene()
        self.arrowPositionUpdater.Stop()

    def GetBall(self, ballID = None):
        if ballID is None:
            ballID = self.shipId
        return sm.GetService('michelle').GetBall(ballID)

    def ShowUI(self):
        self.SetupImpactArrow()
        uicontrols.Window.CloseIfOpen(windowID=self.windowID)
        wnd = uicontrols.Window.Open(windowID=self.windowID)
        wnd.SetTopparentHeight(0)
        wnd.SetMinSize([500, 100])
        wnd.SetCaption(self.name)
        wnd._OnClose = self._OnClose
        main = wnd.GetMainArea()
        headerCont = Container(name='headerCont', parent=main, align=uiconst.TOTOP, height=30, padBottom=10)
        bottomCont = Container(name='bottomCont', parent=main, align=uiconst.TOBOTTOM, height=30)
        self.shipIdLabel = EveLabelSmall(name='shipIDLabel', align=uiconst.CENTER, parent=headerCont, text='Ship ID: %s' % self.shipId)
        Button(name='apply_button', align=uiconst.CENTER, parent=bottomCont, label='Apply Physical Impact', func=self._OnApplyPhysicalImpact)
        mainContainer = GridContainer(name='mainCont', parent=main, align=uiconst.TOALL, columns=4, rows=3)
        container = Container(name='impactVelocityLockAndLabel', align=uiconst.TOALL, parent=mainContainer, padRight=10)
        self.lockVelocityButton = ButtonIcon(name='MyButtonIcon', parent=container, align=uiconst.TOPLEFT, width=16, height=16, iconSize=16, padLeft=10, texturePath='res:/UI/Texture/Icons/bookmark.png', func=self.OnLockVelocity)
        EveLabelSmall(name='impactVelocity', align=uiconst.TORIGHT, parent=container, padRight=10, text='Impact Velocity')
        self.impactVelocityXInput = SinglelineEdit(name='xVelocity', align=uiconst.TOTOP, label='X', parent=mainContainer, padRight=10, setvalue=str(self.impactVelocity[0]), OnFocusLost=self.OnSetImpactVelocityX, OnReturn=self.OnSetImpactVelocityX)
        self.impactVelocityYInput = SinglelineEdit(name='yVelocity', align=uiconst.TOTOP, label='Y', parent=mainContainer, padRight=10, setvalue=str(self.impactVelocity[1]), OnFocusLost=self.OnSetImpactVelocityY, OnReturn=self.OnSetImpactVelocityY)
        self.impactVelocityZInput = SinglelineEdit(name='zVelocity', align=uiconst.TOTOP, label='Z', parent=mainContainer, padRight=10, setvalue=str(self.impactVelocity[2]), OnFocusLost=self.OnSetImpactVelocityZ, OnReturn=self.OnSetImpactVelocityZ)
        EveLabelSmall(name='shipIDInputLabel', parent=mainContainer, align=uiconst.TORIGHT, padRight=10, text='Ship ID')
        self.shipInput = SinglelineEdit(name='shipIdInput', parent=mainContainer, align=uiconst.TOTOP, padRight=10, setvalue=str(session.shipid), OnFocusLost=self.OnSetShipId, OnReturn=self.OnSetShipId)
        EveLabelSmall(name='damageLocatorLabel', align=uiconst.TORIGHT, padRight=10, parent=mainContainer, text='Damage Locator')
        self.damageLocatorInput = SinglelineEdit(name='damageLocator', align=uiconst.TOTOP, label='', parent=mainContainer, padRight=10, setvalue=str(self.damageLocatorID), ints=(0, 0), OnChange=self.OnSetDamageLocator)
        EveLabelSmall(name='impactMassLabel', align=uiconst.TORIGHT, padRight=10, parent=mainContainer, text='Impact Mass')
        self.impactMassInput = SinglelineEdit(name='impactMass', align=uiconst.TOTOP, label='', parent=mainContainer, padRight=10, setvalue=str(self.impactObjectMass), OnChange=self.OnSetImpactMass)
        self.randomizeDL = Checkbox(name='myCheckbox', parent=mainContainer, text='Randomize Damage Locators', checked=self.randomize, callback=self.OnRandomize)
        self.AddImpactArrowToScene()
        self.OnSetShipId()

    def OnSetShipId(self, *args):
        try:
            shipId = long(self.shipInput.GetValue())
        except ValueError:
            print "Could not set shipId to '%s'" % self.shipInput.GetValue()
            return

        if self.shipId == shipId:
            return
        if sm.GetService('michelle').GetBall(shipId) is None:
            print "No ball with id '%d' found in ballpark" % shipId
            return
        print 'Setting ship ID to %d' % shipId
        self.shipId = shipId
        self.shipIdLabel.SetText('Ship ID: %s' % self.shipId)
        self.arrowPositionUpdater.SetBall(self.GetBall())
        self.damageLocatorInput.IntMode(minint=0, maxint=len(self.GetBall().model.damageLocators))
        if len(self.GetBall().model.damageLocators) >= self.damageLocatorID:
            self.damageLocatorInput.SetValue(str(self.damageLocatorID))
        else:
            self.damageLocatorInput.SetValue(str(0))
        self.OnSetDamageLocator()

    def OnSetImpactVelocityX(self, *args):
        self.impactVelocity = (float(self.impactVelocityXInput.GetValue()), self.impactVelocity[1], self.impactVelocity[2])
        self.arrowPositionUpdater.SetArrowDirection(self.impactVelocity)

    def OnSetImpactVelocityY(self, *args):
        self.impactVelocity = (self.impactVelocity[0], float(self.impactVelocityYInput.GetValue()), self.impactVelocity[2])
        self.arrowPositionUpdater.SetArrowDirection(self.impactVelocity)

    def OnSetImpactVelocityZ(self, *args):
        self.impactVelocity = (self.impactVelocity[0], self.impactVelocity[1], float(self.impactVelocityZInput.GetValue()))
        self.arrowPositionUpdater.SetArrowDirection(self.impactVelocity)

    def OnLockVelocity(self, *args):
        self.lockVelocity = not self.lockVelocity
        if self.lockVelocity:
            self.lockVelocityButton.SetRotation(0)
        else:
            self.lockVelocityButton.SetRotation(-20)

    def OnSetDamageLocator(self, *args):
        self.damageLocatorID = int(self.damageLocatorInput.GetValue())
        self.arrowPositionUpdater.SetDamageLocator(self.damageLocatorID)
        if not self.lockVelocity:
            _, rotation = self.GetBall().model.damageLocators[self.damageLocatorID]
            self.impactVelocity = geo2.QuaternionTransformVector(rotation, (0.0, geo2.Vec3Length(self.impactVelocity), 0.0))
            self.impactVelocity = (-self.impactVelocity[0], -self.impactVelocity[1], -self.impactVelocity[2])
            self.impactVelocityXInput.SetValue(str(self.impactVelocity[0]))
            self.impactVelocityYInput.SetValue(str(self.impactVelocity[1]))
            self.impactVelocityZInput.SetValue(str(self.impactVelocity[2]))
            self.arrowPositionUpdater.SetArrowDirection(self.impactVelocity)

    def OnSetImpactMass(self, *args):
        self.impactObjectMass = float(self.impactMassInput.GetValue())

    def OnRandomize(self, *args):
        self.randomize = not self.randomize
        if self.randomize and self.lockVelocity:
            self.OnLockVelocity()

    def RemoveImpactArrowFromScene(self):
        scene = sm.GetService('sceneManager').GetActiveScene()
        objectsToRemove = []
        for o in scene.objects:
            if o.name == 'DebugImpactArrow':
                objectsToRemove.append(o)

        for o in objectsToRemove:
            scene.objects.remove(o)

    def AddImpactArrowToScene(self):
        scene = sm.GetService('sceneManager').GetActiveScene()
        scene.objects.append(self.impactArrow)

    def _OnApplyPhysicalImpact(self, *args):
        if self.randomize:
            newDamageLocatorID = random.randint(0, len(self.GetBall().model.damageLocators) - 1)
            while newDamageLocatorID == self.damageLocatorID:
                newDamageLocatorID = random.randint(0, len(self.GetBall().model.damageLocators) - 1)

            self.damageLocatorID = newDamageLocatorID
            self.damageLocatorInput.SetValue(str(self.damageLocatorID))
            self.OnSetDamageLocator()
        sm.GetService('michelle').GetBall(self.shipId).ApplyTorqueAtDamageLocator(self.damageLocatorID, self.impactVelocity, self.impactObjectMass)


class ArrowPositionUpdater(object):

    def __init__(self, arrowObject):
        self.arrowObject = arrowObject
        self.stop = False
        self.damageLocator = 0
        self.ball = None
        self.arrowScale = 1.0
        self.arrowDirection = (0.0, 1.0, 0.0)
        self.arrowModel = self.arrowObject.children[0]
        arrowGeometry = self.arrowModel.mesh.geometry
        self.arrowPoint = (0.0, arrowGeometry.GetBoundingBox(0)[1][1], 0.0)
        self.arrowRotation = (0.0, 0.0, 0.0, 1.0)
        self.thread = threading.Thread(target=self.Update)
        self.thread.start()

    def SetDamageLocator(self, damageLocatorIndex):
        self.damageLocator = damageLocatorIndex

    def SetBall(self, ball):
        self.ball = ball
        self.arrowScale = ball.model.GetBoundingSphereRadius() * 0.1
        self.arrowModel.scaling = (self.arrowScale, self.arrowScale, self.arrowScale)

    def SetArrowDirection(self, direction):
        impactDir = geo2.Vec3Normalize(direction)
        self.arrowRotation = geo2.QuaternionRotationArc((0, 1, 0), impactDir)
        if impactDir == (0, -1, 0):
            self.arrowRotation = geo2.QuaternionRotationSetYawPitchRoll(0.0, math.pi, 0.0)

    def Stop(self):
        self.stop = True

    def Update(self):
        print 'starting update thread'
        while not self.stop:
            if self.ball:
                arrowCenter = geo2.QuaternionTransformVector(self.arrowRotation, (self.arrowPoint[0] * self.arrowScale, self.arrowPoint[1] * self.arrowScale, self.arrowPoint[2] * self.arrowScale))
                dl = self.ball.GetModel().GetTransformedDamageLocator(self.damageLocator)
                self.arrowObject.rotation = self.arrowRotation
                self.arrowObject.translation = (dl[0] - arrowCenter[0], dl[1] - arrowCenter[1], dl[2] - arrowCenter[2])

        print 'stopping update thread'
