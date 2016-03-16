#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\dogmaWrappers.py
from dogma.dogmaLogging import *
global_seq_id = 0
global_nesting_level = 0
global_traceback_threshold = -1

def WrappedMethod(m):

    def Wrapped_method(self, *args, **kwargs):
        global global_seq_id
        global global_nesting_level
        my_seq_id = global_seq_id
        global_seq_id += 1
        try:
            selfDescription = str(self)
        except (AttributeError, KeyError):
            selfDescription = '<{} at {:#x}>'.format(self.__class__.__name__, id(self))

        LogNotice('{:04}'.format(my_seq_id), 'PAT: Wrap:', '*' * global_nesting_level, 'Enter', m.__name__, 'with self=', selfDescription, 'args=', args, 'kwargs=', kwargs, 'seq_id=', my_seq_id)
        if global_nesting_level <= global_traceback_threshold:
            LogTraceback('Traceback from WrappedMethod')
        global_nesting_level += 1
        res = m(self, *args, **kwargs)
        global_nesting_level -= 1
        LogNotice('{:04}'.format(my_seq_id), 'PAT: Wrap:', '-' * global_nesting_level, 'Exit', m.__name__, 'returning res=', res, 'seq_id=', my_seq_id)
        return res

    Wrapped_method.__isWrapped__ = True
    LogNotice('PAT: Wrapping old method {} with new {}'.format(m, Wrapped_method))
    return Wrapped_method


def WrappedClass(c):
    LogNotice('PAT: WRAPPING CLASS', c)
    import types
    for k, v in c.__dict__.items():
        if k in {'__str__', '__repr__'}:
            LogNotice('Skipping un-wrappable function:', k, ':', v)
            continue
        if isinstance(v, types.FunctionType):
            if hasattr(v, '__isWrapped__'):
                LogNotice('Skipping already wrapped function:', k, ':', v)
            else:
                setattr(c, k, WrappedMethod(v))

    return c
