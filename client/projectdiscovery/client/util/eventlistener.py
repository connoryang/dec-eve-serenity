#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\util\eventlistener.py
import logging
logger = logging.getLogger(__name__)
METHOD_EVENT_MARKER = '__event_id__'

def eventlistener(register = '__init__', unregister = '_OnClose'):

    def decorator(cls):
        events = []
        for key in cls.__dict__.keys():
            val = cls.__dict__[key]
            if hasattr(val, '__call__') and hasattr(val, METHOD_EVENT_MARKER):
                event = getattr(val, METHOD_EVENT_MARKER)
                events.append(event)
                setattr(cls, event, val)

        if events:
            setattr(cls, '__notifyevents__', events)
            setattr(cls, register, _registerer(getattr(cls, register, None), sm.RegisterNotify))
            setattr(cls, unregister, _registerer(getattr(cls, unregister, None), sm.UnregisterNotify))
        return cls

    return decorator


def on_event(event_id):

    def decorator(f):
        setattr(f, METHOD_EVENT_MARKER, event_id)
        return f

    return decorator


def _registerer(method, func):

    def wrapped(self, *args, **kwargs):
        func(self)
        if method:
            method(self, *args, **kwargs)

    return wrapped
