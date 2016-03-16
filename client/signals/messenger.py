#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\signals\messenger.py
import signals
import collections

class Messenger(object):

    def __init__(self):
        self.signals = collections.defaultdict(signals.Signal)

    def SendMessage(self, name, *args, **kwargs):
        signal = self.signals.get(name)
        if signal:
            signal(*args, **kwargs)

    def SubscribeToMessage(self, name, handler):
        self.signals[name].connect(handler)

    def UnsubscribeFromMessage(self, name, handler):
        self.signals[name].disconnect(handler)

    def UnsubscribeAllFromMessage(self, name):
        self.signals[name].clear()

    def Clear(self):
        self.signals.clear()
