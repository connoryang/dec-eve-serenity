#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\fittableDogmaItem.py
from dogma.dogmaLogging import *
from baseDogmaItem import BaseDogmaItem
from ccpProfile import TimedFunction

class FittableDogmaItem(BaseDogmaItem):

    @TimedFunction('FittableDogmaItem::Unload')
    def Unload(self):
        super(FittableDogmaItem, self).Unload()
        if self.location:
            try:
                locationFittedItems = self.location.fittedItems
            except AttributeError:
                LogTraceback('FittableDogmaItem loaded in something (%s) that is not a proper location -- %s' % (self.locationID, self.location))
                return

            if self.itemID in locationFittedItems:
                del locationFittedItems[self.itemID]
