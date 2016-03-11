#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\client\components\jumpPolarization.py
from spacecomponents.client.messages import MSG_ON_ADDED_TO_SPACE, MSG_ON_JUMP_POLARIZATION_UPDATED
from spacecomponents.common.components.component import Component

class JumpPolarization(Component):

    def __init__(self, *args):
        Component.__init__(self, *args)
        self.isPolarized = False
        self.polarizationEndTime = None
        self.polarizationDuration = None
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)

    def OnAddedToSpace(self, slimItem):
        self.UThreadNew(self.UpdatePolarizationAndBroadcast, slimItem)

    def UpdatePolarizationAndBroadcast(self, slimItem):
        polarization = sm.RemoteSvc('wormholeMgr').GetWormholePolarization(slimItem.itemID)
        if polarization is None:
            self.ClearPolarization()
        else:
            self.polarizationEndTime, self.polarizationDuration = polarization
            if self.polarizationEndTime > self.GetSimTime():
                self.isPolarized = True
        self.SendMessage(MSG_ON_JUMP_POLARIZATION_UPDATED, self, slimItem)
        if self.isPolarized:
            sleepDuration = max(self.TimeDiffInMs(self.GetSimTime(), self.polarizationEndTime), 0)
            self.SleepSim(sleepDuration)
            self.isPolarized = False
            self.SendMessage(MSG_ON_JUMP_POLARIZATION_UPDATED, self, slimItem)

    def ClearPolarization(self):
        self.isPolarized = False
        self.polarizationEndTime = None
        self.polarizationDuration = None
