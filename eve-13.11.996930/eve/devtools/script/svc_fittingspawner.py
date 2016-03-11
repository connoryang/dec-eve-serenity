#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\svc_fittingspawner.py
from eve.client.script.ui.shared.fitting.fittingWnd import FittingWindow2
import uix
import blue
from service import Service, ROLE_WORLDMOD

class FittingSpawner(Service):
    __guid__ = 'svc.fittingspawner'
    __startupdependencies__ = ['invCache',
     'loading',
     'gameui',
     'station']

    def MassSpawnFitting(self, ownerID, fitting):
        quantity = uix.QtyPopup(maxvalue=50, minvalue=1, caption='Mass Spawn Fitting', label='', hint='Specify amount of ships to spawn (Max. 50).<br>Note: this function cannot be aborted once running.')
        self.SpawnFitting(ownerID, fitting, quantity['qty'])

    def SpawnFitting(self, ownerID, fitting, quantity = 1):
        self.fittingSvc = sm.GetService('fittingSvc')
        if session.stationid is None:
            raise UserError('CannotLoadFittingInSpace')
        if fitting is None:
            raise UserError('FittingDoesNotExist')
        wnd = FittingWindow2.GetIfOpen()
        wasOpen = False
        if wnd:
            wasOpen = True
            wnd.Close()
        try:
            subsystems = []
            for i, (typeID, flag, qty) in enumerate(fitting.fitData):
                self.loading.ProgressWnd('Preparing ship', 'MAking items...', i, len(fitting.fitData))
                itemID = sm.RemoteSvc('slash').SlashCmd('/createitem %d %d %d' % (typeID, qty * quantity, session.stationid))
                if flag >= const.flagSubSystemSlot0 and flag <= const.flagSubSystemSlot7:
                    subsystems.append(itemID)

            self.loading.StopCycle()
            for i in xrange(quantity):
                self.loading.ProgressWnd('Preparing ship', 'Fitting ship', 1, 2)
                shipID = sm.RemoteSvc('slash').SlashCmd('/createitem %d 1 %d' % (fitting.shipTypeID, session.stationid))
                self.gameui.GetShipAccess().AssembleShip(shipID, fitting.name, subSystems=subsystems)
                shipItem = self.invCache.GetInventoryFromId(shipID, locationID=session.stationid2).GetItem()
                self.station.TryActivateShip(shipItem)
                blue.pyos.synchro.SleepWallclock(100)
                self.fittingSvc.LoadFittingFromFittingID(ownerID, fitting.fittingID)

        finally:
            self.loading.StopCycle()
            if wasOpen:
                self.fittingSvc.simulated = False
                FittingWindow2.Open()
