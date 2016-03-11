#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\industry\skill.py
import fsdlite
import industry

class Skill(industry.Base):
    __metaclass__ = fsdlite.Immutable

    def __new__(cls, *args, **kwargs):
        obj = industry.Base.__new__(cls)
        obj._typeID = None
        obj._level = None
        obj._errors = []
        obj.on_updated = fsdlite.Signal()
        obj.on_errors = fsdlite.Signal()
        return obj

    typeID = industry.Property('_typeID', 'on_updated')
    level = industry.Property('_level', 'on_updated')
    errors = industry.Property('_errors', 'on_errors')

    def __repr__(self):
        return industry.repr(self, exclude=['on_errors', '_errors'])
