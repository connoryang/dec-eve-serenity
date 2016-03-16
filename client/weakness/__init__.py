#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\weakness\__init__.py
import weakref

class WeakMethod(object):

    def __init__(self, f):
        self.class_method = f.im_func
        self.self_ref = weakref.ref(f.im_self)

    def __call__(self, *args, **kwargs):
        method_self = self.self_ref()
        if method_self is None:
            raise ReferenceError('weakly-referenced method no longer exists')
        return apply(self.class_method, (method_self,) + args, kwargs)

    def __eq__(self, other):
        return self is other or getattr(other, 'im_func', None) is self.class_method and getattr(other, 'im_self', None) == self.self_ref()

    def __ne__(self, other):
        return not self.__eq__(other)


def callable_proxy(callable_object):
    if hasattr(callable_object, 'im_func'):
        return WeakMethod(callable_object)
    else:
        return weakref.proxy(callable_object)
