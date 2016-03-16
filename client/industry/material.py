#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\industry\material.py
import fsdlite
import industry

class Material(industry.Base):
    __metaclass__ = fsdlite.Immutable
    typeID = industry.Property('_typeID', 'on_updated')
    quantity = industry.Property('_quantity', 'on_updated')
    base = industry.Property('_base')
    available = industry.Property('_available')
    errors = industry.Property('_errors')
    options = industry.Property('_options', 'on_updated')
    modifiers = industry.Property('_modifiers', 'on_updated')
    probability = industry.Property('_probability', 'on_updated')

    def __new__(cls, *args, **kwargs):
        obj = industry.Base.__new__(cls)
        obj._typeID = None
        obj._quantity = 0
        obj._available = 0
        obj._original = 0
        obj._errors = []
        obj._options = []
        obj._modifiers = []
        obj._probability = 1
        obj.on_updated = fsdlite.Signal()
        obj.on_errors = fsdlite.Signal()
        obj.on_select = fsdlite.Signal()
        return obj

    def __init__(self, *args, **kwargs):
        industry.Base.__init__(self, *args, **kwargs)
        self.base = self.quantity

    def __setstate__(self, data):
        self.typeID = data.get('typeID')
        self.quantity = data.get('quantity')
        self.probability = data.get('probability')
        self.base = self.quantity

    def __repr__(self):
        return industry.repr(self, exclude=['on_updated',
         'on_errors',
         'on_select',
         '_parent',
         '_errors'])

    def add_error(self, error, *args):
        self._errors.append((error, args))

    def _get_valid(self):
        return not self.errors

    valid = property(_get_valid)

    def _get_missing(self):
        return max(self.quantity - self.available, 0)

    missing = property(_get_missing)

    def _get_ratio(self):
        if self.quantity:
            return 1.0 - float(self.missing) / float(self.quantity)
        elif self.typeID:
            return 0.0
        else:
            return 1.0

    ratio = property(_get_ratio)

    def all_types(self):
        values = set([ m.typeID for m in self.options ])
        values.add(self.typeID)
        values.discard(None)
        return list(values)

    def update_available(self, materials):
        self._available = materials.get(self.typeID, 0)
        for material in self.options:
            material.update_available(materials)

    def _get_errors(self):
        self._errors, existing = [], self._errors
        if self.typeID and self.missing:
            self.add_error(industry.Error.MISSING_MATERIAL, self.typeID, self.quantity, self.available, self.missing)
        if existing != self._errors:
            self.on_errors(self, self._errors)
        return self._errors

    errors = property(_get_errors)

    def select(self, value):
        for material in self._options:
            if value in (material, material.typeID):
                self._typeID = material.typeID
                self._quantity = material.quantity
                self._available = material.available
                self._base = material.base
                self._modifiers = material.modifiers
                self.on_select(self)
                self.on_updated(self)
                return
