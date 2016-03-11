#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\vgs\events.py
from eveexceptions.exceptionEater import ExceptionEater
import uthread

def LogOpenOffer(offerID):
    _LogEvent(['offerID'], 'OpenOffer', offerID)


def LogPurchaseAurum(balance, location):
    _LogEvent(['aurumBalance', 'location'], 'PurchaseAurum', balance, location)


def LogPurchaseOffer(offerID, quantity):
    _LogEvent(['offerID', 'quantity'], 'PurchaseOffer', offerID, quantity)


def _LogEvent(columnNames, eventName, *args):
    with ExceptionEater('eventLog'):
        uthread.new(sm.ProxySvc('eventLog').LogClientEvent, 'vgs', columnNames, eventName, *args)
