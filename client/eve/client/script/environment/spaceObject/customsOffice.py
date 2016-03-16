#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\customsOffice.py
import blue
import trinity
import uthread
import eve.common.script.sys.eveCfg as util
from eve.client.script.environment.spaceObject.LargeCollidableStructure import LargeCollidableStructure
CUSTOMSOFFICE_SPACEPORT = 4579
CUSTOMSOFFICE_SPACEELEVATOR = 4580

class CustomsOffice(LargeCollidableStructure):

    def __init__(self):
        LargeCollidableStructure.__init__(self)
        self.modelLists = {1: CUSTOMSOFFICE_SPACEPORT,
         2: CUSTOMSOFFICE_SPACEELEVATOR}

    def Assemble(self):
        self.SetStaticRotation()
        self.SetupSharedAmbientAudio()

    def LoadModel(self):
        self.LogInfo('CustomsOffice LoadModel ')
        self.level = self.ballpark.slimItems[self.id].level
        self.DoModelChange()

    def OnSlimItemUpdated(self, slimItem):
        self.level = self.ballpark.slimItems[self.id].level
        uthread.pool('CustomsOffice::DoModelChange', self.DoModelChange)

    def DoModelChange(self):
        oldModel = self.model
        if self.level is None or self.level not in self.modelLists:
            LargeCollidableStructure.LoadModel(self)
        else:
            modelName = util.GraphicFile(self.modelLists[self.level])
            LargeCollidableStructure.LoadModel(self, modelName)
            if self.model is None:
                LargeCollidableStructure.LoadModel(self)
        self.SetStaticRotation()
        if oldModel is not None:
            uthread.pool('CustomsOffice::DelayedRemove', self.DelayedRemove, oldModel, int(1000))
        if self.model is not None:
            self.model.display = True

    def DelayedRemove(self, model, delay):
        model.name = model.name + '_removing'
        model.display = False
        trinity.WaitForResourceLoads()
        blue.pyos.synchro.SleepWallclock(delay)
        self.RemoveAndClearModel(model)
