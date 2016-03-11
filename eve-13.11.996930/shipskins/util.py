#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\shipskins\util.py
import fsdlite

def repr(obj, exclude = []):
    exclude.append('__immutable__')
    if hasattr(obj, '__slots__'):
        return '<shipskins.{} {}>'.format(obj.__class__.__name__, ' '.join([ '{}={}'.format(key.strip('_'), getattr(obj, key, None)) for key in obj.__slots__ if key not in exclude ]))
    elif hasattr(obj, '__dict__'):
        return '<shipskins.{} {}>'.format(obj.__class__.__name__, ' '.join([ '{}={}'.format(key.strip('_'), value) for key, value in obj.__dict__.iteritems() if key not in exclude ]))
    else:
        return str(obj)


class Base(object):

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, *args, **kwargs):
        object.__init__(self)
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        return repr(self)

    @classmethod
    def extend(cls, mixin):
        fsdlite.extend_class(cls, mixin)
