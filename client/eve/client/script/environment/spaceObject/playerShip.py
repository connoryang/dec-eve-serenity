#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\playerShip.py
import trinity
import math
import carbon.common.script.util.format as fmtutil
from eve.client.script.parklife.states import lookingAt
from eve.client.script.environment.spaceObject.ship import Ship
import evegraphics.utils as gfxutils

class PlayerShip(Ship):

    def __init__(self):
        Ship.__init__(self)
        self._dirtTimeStamp = None
        self._killCounter = None

    def Assemble(self):
        Ship.Assemble(self)
        self.FitBoosters()
        self.UpdateDirtLevel()
        self.UpdateKillCounter()

    def UpdateDirtLevel(self):
        slimItem = self.typeData.get('slimItem')
        self._dirtTimeStamp = getattr(slimItem, 'dirtTime', None)
        if self._dirtTimeStamp is not None:
            dirtLevel = gfxutils.CalcDirtLevelFromAge(self._dirtTimeStamp)
            if self.model is not None:
                self.model.dirtLevel = dirtLevel

    def UpdateKillCounter(self):
        slimItem = self.typeData.get('slimItem')
        self._killCounter = getattr(slimItem, 'kills', None)
        if self._killCounter is not None:
            if self.model is not None:
                self.model.displayKillCounterValue = min(self._killCounter, 999)

    def OnSlimItemUpdated(self, slimItem):
        Ship.OnSlimItemUpdated(self, slimItem)
        self.UpdateDirtLevel()
        self.UpdateKillCounter()

    def IsLookedAt(self):
        return self.id == self.sm.GetService('state').GetExclState(lookingAt)

    def GetDirtTimeStampAsStr(self):
        if self._dirtTimeStamp is not None:
            return fmtutil.FmtDateEng(self._dirtTimeStamp)
        return 'None'
