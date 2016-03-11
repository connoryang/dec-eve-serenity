#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\brennivin\messenger.py
from collections import defaultdict
from brennivin.signals import Signal

class Messenger(object):

    def __init__(self):
        self.signalsByMessageName = defaultdict(Signal)

    def SendMessage(self, messageName, *args, **kwargs):
        signal = self.signalsByMessageName.get(messageName)
        if signal:
            signal.emit(*args, **kwargs)

    def SubscribeToMessage(self, messageName, handler):
        signal = self.signalsByMessageName[messageName]
        signal.connect(handler)

    def UnsubscribeFromMessage(self, messageName, handler):
        try:
            signal = self.signalsByMessageName[messageName]
            signal.disconnect(handler)
        except ValueError:
            pass

    def Clear(self):
        for signal in self.signalsByMessageName.itervalues():
            signal.clear()

        self.signalsByMessageName.clear()
